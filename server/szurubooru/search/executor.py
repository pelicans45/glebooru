from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple, Union, Type

import sqlalchemy as sa
from szurubooru.func import cache
from szurubooru.search import parser, tokens
from szurubooru.search.configs import util as search_util
from szurubooru.search.configs.base_search_config import BaseSearchConfig
from szurubooru.search.query import SearchQuery
from szurubooru.search.typing import SaQuery

from szurubooru import db, errors, model, rest

import logging

@dataclass(frozen=True)
class _CachedSearchResult:
    model: Optional[Type[model.Base]]
    ids: List[object]
    count: Optional[int]
    has_more: Optional[bool]

def _format_dict_keys(source: Dict) -> List[str]:
    return list(sorted(source.keys()))


def _get_order(order: str, default_order: str) -> Union[bool, str]:
    if order == tokens.SortToken.SORT_DEFAULT:
        return default_order or tokens.SortToken.SORT_ASC
    if order == tokens.SortToken.SORT_NEGATED_DEFAULT:
        if default_order == tokens.SortToken.SORT_ASC:
            return tokens.SortToken.SORT_DESC
        elif default_order == tokens.SortToken.SORT_DESC:
            return tokens.SortToken.SORT_ASC
        # assert False
    return order


class Executor:
    """
    Class for search parsing and execution. Handles plaintext parsing and
    delegates sqlalchemy filter decoration to SearchConfig instances.
    """

    AROUND_NEXT = "up"
    AROUND_PREV = "down"

    def __init__(self, search_config: BaseSearchConfig) -> None:
        self.config = search_config
        self.parser = parser.Parser()

    def _unwrap_sort_column(self, column):
        if isinstance(column, search_util.SortColumn):
            return column.column, column.nulls_last
        return column, False

    def _hydrate_cached_entities(
        self, cached: _CachedSearchResult
    ) -> List[model.Base]:
        if not cached.ids or not cached.model:
            return []
        mapper = sa.inspect(cached.model)
        pk_cols = mapper.primary_key
        if len(pk_cols) != 1:
            entities = [db.session.get(cached.model, pk) for pk in cached.ids]
            return [entity for entity in entities if entity is not None]
        pk_col = pk_cols[0]
        rows = (
            db.session.query(cached.model)
            .filter(pk_col.in_(cached.ids))
            .all()
        )
        by_id = {}
        for row in rows:
            identity = sa.inspect(row).identity
            if not identity:
                continue
            key = identity[0] if len(identity) == 1 else identity
            by_id[key] = row
        return [by_id[pk] for pk in cached.ids if pk in by_id]

    def get_around(
        self, query_text: str, entity_id: int
    ) -> Tuple[model.Base, model.Base, model.Base]:
        search_query = self.parser.parse(query_text)
        self.config.on_search_query_parsed(search_query)
        filter_query = self.config.create_around_query().options(
            sa.orm.lazyload("*")
        )
        prev_filter_query = self._prepare_sorted_around_query(
            filter_query, search_query, entity_id, self.AROUND_PREV
        ).limit(1)
        next_filter_query = self._prepare_sorted_around_query(
            filter_query, search_query, entity_id, self.AROUND_NEXT
        ).limit(1)
        # random post
        if "sort:random" not in query_text:
            query_text = "sort:random " + query_text
        count, random_entities = self.execute(query_text, 0, 1)
        return (
            prev_filter_query.one_or_none(),
            next_filter_query.one_or_none(),
            random_entities[0] if random_entities else None,
        )

    def get_around_and_serialize(
        self,
        ctx: rest.Context,
        entity_id: int,
        serializer: Callable[[model.Base], rest.Response],
    ) -> rest.Response:
        if ctx.has_param("query"):
            query_text = ctx.get_param_as_string("query", default="")
        else:
            query_text = ctx.get_param_as_string("q", default="")
        entities = self.get_around(query_text, entity_id)
        return {
            "prev": serializer(entities[0]),
            "next": serializer(entities[1]),
            "random": serializer(entities[2]),
        }

    def _execute_internal(
        self,
        query_text: str,
        offset: int,
        limit: int,
        use_cache: bool = True,
        include_count: bool = True,
        include_has_more: bool = False,
    ) -> Tuple[Optional[int], List[model.Base], Optional[bool]]:
        search_query = self.parser.parse(query_text)
        self.config.on_search_query_parsed(search_query)

        if offset < 0:
            limit = max(0, limit + offset)
            offset = 0

        disable_eager_loads = False
        for token in search_query.sort_tokens:
            if token.name == "random":
                disable_eager_loads = True
                break

        key = (
            id(self.config),
            hash(search_query),
            offset,
            limit,
            include_count,
            include_has_more,
        )
        if use_cache and not disable_eager_loads and cache.has(key):
            cached = cache.get(key)
            if isinstance(cached, _CachedSearchResult):
                return (
                    cached.count,
                    self._hydrate_cached_entities(cached),
                    cached.has_more,
                )
            return (0, [], None)

        filter_query = self.config.create_filter_query(disable_eager_loads)
        # Note: lazyload("*") is already applied in create_filter_query
        # Don't add another one here as it would override specific eager loads
        filter_query = self._prepare_db_query(filter_query, search_query, True)
        query_limit = limit + 1 if include_has_more else limit
        entities = filter_query.offset(offset).limit(query_limit).all()
        has_more = None
        if include_has_more:
            has_more = len(entities) > limit
            if has_more:
                entities = entities[:limit]

        count = None
        if include_count:
            count_query, model = self.config.create_count_query(
                disable_eager_loads
            )
            count_query = count_query.options(sa.orm.lazyload("*"))
            count_query = self._prepare_db_query(count_query, search_query, False)
            count_statement = (
                count_query.statement.select_from(model)
                .with_only_columns(sa.func.count())
                .order_by(None)
            )
            count = db.session.execute(count_statement).scalar()

        ret = (count, entities, has_more)
        if use_cache and not disable_eager_loads:
            cached_ids = []
            for entity in entities:
                identity = sa.inspect(entity).identity
                if not identity:
                    continue
                cached_ids.append(identity[0] if len(identity) == 1 else identity)
            model_cls = type(entities[0]) if entities else None
            cache.put(
                key,
                _CachedSearchResult(
                    model=model_cls,
                    ids=cached_ids,
                    count=count,
                    has_more=has_more,
                ),
            )
        return ret

    def execute(
        self,
        query_text: str,
        offset: int,
        limit: int,
        use_cache: bool = True,
    ) -> Tuple[int, List[model.Base]]:
        count, entities, _has_more = self._execute_internal(
            query_text,
            offset,
            limit,
            use_cache=use_cache,
            include_count=True,
            include_has_more=False,
        )
        return count or 0, entities

    def execute_with_metadata(
        self,
        query_text: str,
        offset: int,
        limit: int,
        use_cache: bool = True,
        include_count: bool = True,
        include_has_more: bool = False,
    ) -> Tuple[Optional[int], List[model.Base], Optional[bool]]:
        return self._execute_internal(
            query_text,
            offset,
            limit,
            use_cache=use_cache,
            include_count=include_count,
            include_has_more=include_has_more,
        )

    def execute_and_serialize(
        self,
        ctx: rest.Context,
        serializer: Callable[[model.Base], rest.Response],
        include_count: bool = True,
        include_has_more: bool = False,
    ) -> rest.Response:
        if ctx.has_param("query"):
            query = ctx.get_param_as_string("query", default="")
        else:
            query = ctx.get_param_as_string("q", default="")
        offset = ctx.get_param_as_int("offset", default=0, min=0)
        limit = ctx.get_param_as_int("limit", default=100, min=1, max=5000)#max=100)
        count, entities, has_more = self.execute_with_metadata(
            query, offset, limit, include_count=include_count, include_has_more=include_has_more
        )
        response = {
            "query": query,
            "offset": offset,
            "limit": limit,
            "total": count,
            "results": [serializer(entity) for entity in entities],
        }
        if include_has_more:
            response["hasMore"] = bool(has_more)
        return response

    def execute_and_serialize_batch(
        self,
        ctx: rest.Context,
        batch_serializer: Callable[[list], list],
        use_cache: bool = True,
        include_count: bool = True,
        include_has_more: bool = False,
    ) -> rest.Response:
        """
        Execute search and serialize results using batch serialization.
        This avoids N+1 queries by allowing the serializer to pre-fetch data.
        """
        if ctx.has_param("query"):
            query = ctx.get_param_as_string("query", default="")
        else:
            query = ctx.get_param_as_string("q", default="")
        offset = ctx.get_param_as_int("offset", default=0, min=0)
        limit = ctx.get_param_as_int("limit", default=100, min=1, max=5000)
        count, entities, has_more = self.execute_with_metadata(
            query,
            offset,
            limit,
            use_cache=use_cache,
            include_count=include_count,
            include_has_more=include_has_more,
        )
        response = {
            "query": query,
            "offset": offset,
            "limit": limit,
            "total": count,
            "results": batch_serializer(entities),
        }
        if include_has_more:
            response["hasMore"] = bool(has_more)
        return response

    def count(self, query_text: str) -> int:
        search_query = self.parser.parse(query_text)
        self.config.on_search_query_parsed(search_query)
        count_query, model = self.config.create_count_query(True)
        count_query = count_query.options(sa.orm.lazyload("*"))
        count_query = self._prepare_db_query(count_query, search_query, False)
        count_statement = count_query.statement.select_from(model).with_only_columns(
            sa.func.count()
        ).order_by(None)
        count = db.session.execute(count_statement).scalar()
        return count

    def _prepare_db_query(
        self, db_query: SaQuery, search_query: SearchQuery, use_sort: bool
    ) -> SaQuery:
        for anon_token in search_query.anonymous_tokens:
            if not self.config.anonymous_filter:
                raise errors.SearchError(
                    "Anonymous tokens are not valid in this context"
                )
            db_query = self.config.anonymous_filter(
                db_query, anon_token.criterion, anon_token.negated
            )

        for named_token in search_query.named_tokens:
            if named_token.name not in self.config.named_filters:
                raise errors.SearchError(
                    'Unknown filter "%s". Available filters: %s'
                    % (
                        named_token.name,
                        ", ".join(
                            _format_dict_keys(self.config.named_filters)
                        ),
                    )
                )
            db_query = self.config.named_filters[named_token.name](
                db_query, named_token.criterion, named_token.negated
            )

        for sp_token in search_query.special_tokens:
            if sp_token.value not in self.config.special_filters:
                raise errors.SearchError(
                    'Unknown special filter "%s". '
                    "Available special tokens: %s"
                    % (
                        sp_token.value,
                        ", ".join(
                            _format_dict_keys(self.config.special_filters)
                        ),
                    )
                )
            db_query = self.config.special_filters[sp_token.value](
                db_query, None, sp_token.negated
            )

        if use_sort:
            for sort_token in search_query.sort_tokens:
                if sort_token.name not in self.config.sort_columns:
                    raise errors.SearchError(
                        'Unknown sort filter "%s". '
                        "Available sort filters: %s"
                        % (
                            sort_token.name,
                            ", ".join(
                                _format_dict_keys(self.config.sort_columns)
                            ),
                        )
                    )
                column, default_order = self.config.sort_columns[
                    sort_token.name
                ]
                column, nulls_last = self._unwrap_sort_column(column)
                order = _get_order(sort_token.order, default_order)
                if order == sort_token.SORT_ASC:
                    order_expr = column.asc()
                elif order == sort_token.SORT_DESC:
                    order_expr = column.desc()
                else:
                    continue
                if nulls_last:
                    order_expr = order_expr.nulls_last()
                db_query = db_query.order_by(order_expr)

        db_query = self.config.finalize_query(db_query)
        return db_query

    def _prepare_sorted_around_query(
        self,
        db_query: SaQuery,
        search_query: SearchQuery,
        entity_id: int,
        direction: str,
    ):
        db_query = self._prepare_db_query(db_query, search_query, False)
        db_query = db_query.order_by(None)
        found_sort_column = False

        for sort_token in search_query.sort_tokens:
            if sort_token.name == "random":
                continue
            if sort_token.name not in self.config.sort_columns:
                raise errors.SearchError(
                    'Unknown sort filter "%s". '
                    "Available sort filters: %s"
                    % (
                        sort_token.name,
                        ", ".join(_format_dict_keys(self.config.sort_columns)),
                    )
                )
            column, default_order = self.config.sort_columns[sort_token.name]
            column, nulls_last = self._unwrap_sort_column(column)
            order = _get_order(sort_token.order, default_order)

            # the order column may be joined, so reuse the config around query
            column_query = (
                self.config.create_around_query()
                .options(sa.orm.lazyload("*"))
                .with_entities(self.config.id_column, column)
                .filter(self.config.id_column == entity_id)
            )
            id, column_value = column_query.one_or_none()
            # it's possible that this entity doesn't have the column
            if not column_value:
                continue
            found_sort_column = True

            if order == sort_token.SORT_ASC:
                if direction == self.AROUND_NEXT:
                    order_expr = column.asc()
                    if nulls_last:
                        order_expr = order_expr.nulls_last()
                    db_query = db_query.order_by(order_expr).filter(
                        column > column_value
                    )
                elif direction == self.AROUND_PREV:
                    order_expr = column.desc()
                    if nulls_last:
                        order_expr = order_expr.nulls_last()
                    db_query = db_query.order_by(order_expr).filter(
                        column < column_value
                    )
            elif order == sort_token.SORT_DESC:
                if direction == self.AROUND_NEXT:
                    order_expr = column.desc()
                    if nulls_last:
                        order_expr = order_expr.nulls_last()
                    db_query = db_query.order_by(order_expr).filter(
                        column < column_value
                    )
                elif direction == self.AROUND_PREV:
                    order_expr = column.asc()
                    if nulls_last:
                        order_expr = order_expr.nulls_last()
                    db_query = db_query.order_by(order_expr).filter(
                        column > column_value
                    )

        if not found_sort_column:
            # no sorting, use default sorting by id
            if direction == self.AROUND_NEXT:
                db_query = db_query.filter(self.config.id_column < entity_id)
            elif direction == self.AROUND_PREV:
                db_query = db_query.filter(self.config.id_column > entity_id)
            db_query = db_query.order_by(
                sa.func.abs(self.config.id_column - entity_id).asc()
            )
            return db_query

        return db_query

class PostSearchExecutor(Executor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
