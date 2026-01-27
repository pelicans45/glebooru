from typing import Any, Dict, Optional, Tuple

import sqlalchemy as sa

from szurubooru import db, errors, model
from szurubooru.func import util
from szurubooru.search import criteria, tokens
from szurubooru.search.configs import util as search_util
from szurubooru.search.configs.base_search_config import (
    BaseSearchConfig,
    Filter,
)
from szurubooru.search.query import SearchQuery
from szurubooru.search.typing import SaColumn, SaQuery


def _type_transformer(value: str) -> str:
    available_values = {
        "image": model.Post.TYPE_IMAGE,
        "animation": model.Post.TYPE_ANIMATION,
        "animated": model.Post.TYPE_ANIMATION,
        "anim": model.Post.TYPE_ANIMATION,
        "gif": model.Post.TYPE_ANIMATION,
        "video": model.Post.TYPE_VIDEO,
        "webm": model.Post.TYPE_VIDEO,
        "audio": model.Post.TYPE_AUDIO,
        "flash": model.Post.TYPE_FLASH,
        "swf": model.Post.TYPE_FLASH,
    }
    return search_util.enum_transformer(available_values, value)


def _safety_transformer(value: str) -> str:
    available_values = {
        "safe": model.Post.SAFETY_SAFE,
        "sketchy": model.Post.SAFETY_SKETCHY,
        "questionable": model.Post.SAFETY_SKETCHY,
        "unsafe": model.Post.SAFETY_UNSAFE,
    }
    return search_util.enum_transformer(available_values, value)


def _flag_transformer(value: str) -> str:
    available_values = {
        "loop": model.Post.FLAG_LOOP,
        "sound": model.Post.FLAG_SOUND,
    }
    return "%" + search_util.enum_transformer(available_values, value) + "%"


def _source_transformer(value: str) -> str:
    return search_util.wildcard_transformer("*" + value + "*")


def _create_score_filter(score: int) -> Filter:
    def wrapper(
        query: SaQuery,
        criterion: Optional[criteria.BaseCriterion],
        negated: bool,
    ) -> SaQuery:
        # assert criterion
        if not getattr(criterion, "internal", False):
            raise errors.SearchError(
                "Votes cannot be seen publicly. Did you mean %r?"
                % "special:liked"
            )
        user_alias = sa.orm.aliased(model.User)
        score_alias = sa.orm.aliased(model.PostScore)
        expr = score_alias.score == score
        expr = expr & search_util.apply_str_criterion_to_column(
            user_alias.name, criterion
        )
        if negated:
            expr = ~expr
        ret = (
            query.join(score_alias, score_alias.post_id == model.Post.post_id)
            .join(user_alias, user_alias.user_id == score_alias.user_id)
            .filter(expr)
        )
        return ret

    return wrapper


def _user_filter(
    query: SaQuery, criterion: Optional[criteria.BaseCriterion], negated: bool
) -> SaQuery:
    # assert criterion
    if isinstance(criterion, criteria.PlainCriterion) and not criterion.value:
        expr = model.Post.user_id == None  # noqa: E711
        if negated:
            expr = ~expr
        return query.filter(expr)
    return search_util.create_subquery_filter(
        model.Post.user_id,
        model.User.user_id,
        model.User.name,
        search_util.create_str_filter,
    )(query, criterion, negated)


def _tag_name_filter(
    query: SaQuery, criterion: Optional[criteria.BaseCriterion], negated: bool
) -> SaQuery:
    if isinstance(criterion, criteria.PlainCriterion):
        values = [criterion.value]
    elif isinstance(criterion, criteria.ArrayCriterion):
        values = criterion.values
    else:
        raise errors.SearchError(
            "Ranged criterion is invalid in this context. "
            "Did you forget to escape the dots?"
        )

    has_wildcard = False
    for value in values:
        unescaped = search_util.unescape(
            value, make_wildcards_special=True
        )
        if search_util.WILDCARD in unescaped:
            has_wildcard = True
            break

    if has_wildcard:
        tag_filter = search_util.create_subquery_filter(
            model.Post.post_id,
            model.PostTag.post_id,
            model.TagName.name,
            lambda column: search_util.create_lowercase_str_filter(
                column, search_util.wildcard_transformer
            ),
            lambda subquery: subquery.join(model.Tag).join(model.TagName),
        )
        return tag_filter(query, criterion, negated)

    names = [search_util.unescape(value).lower() for value in values]
    if not names:
        return query

    tag_id_cache = search_util.get_tag_id_cache()
    tag_ids = set()
    missing = []
    for name in names:
        if name in tag_id_cache:
            cached_id = tag_id_cache[name]
            if cached_id is not None:
                tag_ids.add(cached_id)
        else:
            missing.append(name)

    if missing:
        rows = (
            db.session.query(model.TagName.name, model.TagName.tag_id)
            .filter(model.TagName.name.in_(missing))
            .all()
        )
        found = {name: tag_id for name, tag_id in rows}
        for name in missing:
            tag_id = found.get(name)
            tag_id_cache[name] = tag_id
            if tag_id is not None:
                tag_ids.add(tag_id)

    if not tag_ids:
        return query if negated else query.filter(sa.sql.false())

    if negated:
        exists_clause = sa.exists().where(
            sa.and_(
                model.PostTag.post_id == model.Post.post_id,
                model.PostTag.tag_id.in_(list(tag_ids)),
            )
        )
        return query.filter(~exists_clause)

    subquery = (
        db.session.query(model.PostTag.post_id.label("foreign_id"))
        .filter(model.PostTag.tag_id.in_(list(tag_ids)))
        .options(sa.orm.lazyload("*"))
    )
    subquery = sa.select(subquery.subquery("t"))
    expression = model.Post.post_id.in_(subquery)
    return query.filter(expression)


def _note_filter(
    query: SaQuery, criterion: Optional[criteria.BaseCriterion], negated: bool
) -> SaQuery:
    # assert criterion
    return search_util.create_subquery_filter(
        model.Post.post_id,
        model.PostNote.post_id,
        model.PostNote.text,
        search_util.create_str_filter,
    )(query, criterion, negated)


def _pool_filter(
    query: SaQuery, criterion: Optional[criteria.BaseCriterion], negated: bool
) -> SaQuery:
    # assert criterion
    return search_util.create_subquery_filter(
        model.Post.post_id,
        model.PoolPost.post_id,
        model.PoolPost.pool_id,
        search_util.create_num_filter,
    )(query, criterion, negated)


# includes the given post itself, also applies sort
def _similar_filter(
    query: SaQuery, criterion: Optional[criteria.BaseCriterion], negated: bool
) -> SaQuery:
    # assert criterion
    filter_func_tag = search_util.create_num_filter(model.PostTag.post_id)
    pt_alias = sa.orm.aliased(model.PostTag)

    # subquery for tags of the given post (post id in criterion)
    tag_query = db.session.query(model.PostTag.tag_id)
    tag_query = filter_func_tag(tag_query, criterion, False)
    tag_subquery = tag_query.subquery("source_tags")
    tag_select = sa.select(tag_subquery.c.tag_id)

    if negated:
        similarity_subquery = (
            db.session.query(
                pt_alias.post_id.label("post_id"),
                sa.func.count(pt_alias.tag_id).label("similarity"),
            )
            .join(tag_subquery, tag_subquery.c.tag_id == pt_alias.tag_id)
            .group_by(pt_alias.post_id)
            .having(sa.func.count(pt_alias.tag_id) > 0)
            .subquery("similar_posts")
        )
        expr = model.Post.post_id.in_(
            sa.select(similarity_subquery.c.post_id)
        )
        return query.filter(~expr)
    else:
        # direct query applies sort
        similarity_subquery = (
            db.session.query(
                pt_alias.post_id.label("post_id"),
                sa.func.count(pt_alias.tag_id).label("similarity"),
            )
            .join(tag_subquery, tag_subquery.c.tag_id == pt_alias.tag_id)
            .group_by(pt_alias.post_id)
            .having(sa.func.count(pt_alias.tag_id) > 0)
            .subquery("similar_posts")
        )
        subquery = query.subquery("main_query")
        return (
            db.session.query(model.Post)
            .join(
                similarity_subquery,
                similarity_subquery.c.post_id == model.Post.post_id,
            )
            .join(subquery, similarity_subquery.c.post_id == subquery.c.id)
            .order_by(similarity_subquery.c.similarity.desc())
        )


def _category_filter(
    query: SaQuery, criterion: Optional[criteria.BaseCriterion], negated: bool
) -> SaQuery:
    # assert criterion

    # Step 1. find the id for the category
    q1 = db.session.query(model.TagCategory.tag_category_id).filter(
        model.TagCategory.name == criterion.value
    )

    # Step 2. find the tags with that category
    q2 = db.session.query(model.Tag.tag_id).filter(
        model.Tag.category_id.in_(q1)
    )

    # Step 3. find all posts that have at least one of those tags
    q3 = db.session.query(model.PostTag.post_id).filter(
        model.PostTag.tag_id.in_(q2)
    )

    # Step 4. profit
    expr = model.Post.post_id.in_(q3)
    if negated:
        expr = ~expr

    return query.filter(expr)


class PostSearchConfig(BaseSearchConfig):
    STATS_NAMED_FILTERS = {
        "score",
        "tag-count",
        "comment-count",
        "fav-count",
        "note-count",
        "relation-count",
        "feature-count",
        "comment-date",
        "comment-time",
        "fav-date",
        "fav-time",
        "feature-date",
        "feature-time",
    }
    STATS_SORT_COLUMNS = {
        "score",
        "tag-count",
        "comment-count",
        "fav-count",
        "note-count",
        "relation-count",
        "feature-count",
        "comment-date",
        "comment-time",
        "fav-date",
        "fav-time",
        "feature-date",
        "feature-time",
    }
    STATS_SPECIAL_TOKENS = {"tumbleweed"}

    def __init__(self) -> None:
        self.user = None  # type: Optional[model.User]
        self._needs_stats_join = False
        self._needs_stats_join_for_count = False

    def on_search_query_parsed(self, search_query: SearchQuery) -> SaQuery:
        new_special_tokens = []
        for token in search_query.special_tokens:
            if token.value in ("fav", "liked", "disliked"):
                # assert self.user
                if self.user.rank == "anonymous":
                    raise errors.SearchError(
                        "Must be logged in to use this feature"
                    )
                criterion = criteria.PlainCriterion(
                    original_text=self.user.name, value=self.user.name
                )
                setattr(criterion, "internal", True)
                search_query.named_tokens.append(
                    tokens.NamedToken(
                        name=token.value,
                        criterion=criterion,
                        negated=token.negated,
                    )
                )
            else:
                new_special_tokens.append(token)
        search_query.special_tokens = new_special_tokens

        def _collect_values(criterion):
            if isinstance(criterion, criteria.PlainCriterion):
                return [criterion.value]
            if isinstance(criterion, criteria.ArrayCriterion):
                return list(criterion.values)
            return None

        merged_negated_values = []
        new_anonymous_tokens = []
        for token in search_query.anonymous_tokens:
            if token.negated:
                values = _collect_values(token.criterion)
                if values is not None:
                    merged_negated_values.extend(values)
                    continue
            new_anonymous_tokens.append(token)
        search_query.anonymous_tokens = new_anonymous_tokens

        new_named_tokens = []
        for token in search_query.named_tokens:
            if token.name == "tag" and token.negated:
                values = _collect_values(token.criterion)
                if values is not None:
                    merged_negated_values.extend(values)
                    continue
            new_named_tokens.append(token)
        search_query.named_tokens = new_named_tokens

        if merged_negated_values:
            merged_criterion = criteria.ArrayCriterion(
                ",".join(merged_negated_values),
                merged_negated_values,
            )
            search_query.named_tokens.append(
                tokens.NamedToken(
                    name="tag",
                    criterion=merged_criterion,
                    negated=True,
                )
            )

        needs_stats_filter = any(
            token.name in self.STATS_NAMED_FILTERS
            for token in search_query.named_tokens
        )
        needs_stats_filter = needs_stats_filter or any(
            token.value in self.STATS_SPECIAL_TOKENS
            for token in search_query.special_tokens
        )
        needs_stats_sort = any(
            token.name in self.STATS_SORT_COLUMNS
            for token in search_query.sort_tokens
        )
        self._needs_stats_join = needs_stats_filter or needs_stats_sort
        self._needs_stats_join_for_count = needs_stats_filter

    def create_around_query(self) -> SaQuery:
        query = db.session.query(model.Post).options(sa.orm.lazyload("*"))
        if self._needs_stats_join:
            query = query.join(model.Post.statistics).options(
                sa.orm.contains_eager(model.Post.statistics)
            )
        return query

    def create_filter_query(self, disable_eager_loads: bool) -> SaQuery:
        query = db.session.query(model.Post).options(sa.orm.lazyload("*"))
        if self._needs_stats_join:
            query = query.join(model.Post.statistics).options(
                sa.orm.contains_eager(model.Post.statistics)
            )
        return query

    def create_count_query(self, _disable_eager_loads: bool) -> SaQuery:
        query = db.session.query(model.Post)
        if self._needs_stats_join_for_count:
            query = query.join(model.Post.statistics)
        return (query, model.Post)

    def finalize_query(self, query: SaQuery) -> SaQuery:
        return query.order_by(model.Post.post_id.desc())

    @property
    def id_column(self) -> SaColumn:
        return model.Post.post_id

    @property
    def anonymous_filter(self) -> Optional[Filter]:
        return _tag_name_filter

    @property
    def named_filters(self) -> Dict[str, Filter]:
        return util.unalias_dict(
            [
                (
                    ["id"],
                    search_util.create_num_filter(model.Post.post_id),
                ),
                (
                    ["tag"],
                    _tag_name_filter,
                ),
                (
                    ["score"],
                    search_util.create_num_filter(
                        model.PostStatistics.score
                    ),
                ),
                (["uploader", "upload", "submit"], _user_filter),
                (
                    ["comment"],
                    search_util.create_subquery_filter(
                        model.Post.post_id,
                        model.Comment.post_id,
                        model.User.name,
                        search_util.create_str_filter,
                        lambda subquery: subquery.join(model.User),
                    ),
                ),
                (
                    ["fav"],
                    search_util.create_subquery_filter(
                        model.Post.post_id,
                        model.PostFavorite.post_id,
                        model.User.name,
                        search_util.create_str_filter,
                        lambda subquery: subquery.join(model.User),
                    ),
                ),
                (["liked"], _create_score_filter(1)),
                (["disliked"], _create_score_filter(-1)),
                (
                    ["source"],
                    search_util.create_str_filter(
                        model.Post.source, _source_transformer
                    ),
                ),
                (
                    ["tag-count"],
                    search_util.create_num_filter(
                        model.PostStatistics.tag_count
                    ),
                ),
                (
                    ["comment-count"],
                    search_util.create_num_filter(
                        model.PostStatistics.comment_count
                    ),
                ),
                (
                    ["fav-count"],
                    search_util.create_num_filter(
                        model.PostStatistics.favorite_count
                    ),
                ),
                (
                    ["note-count"],
                    search_util.create_num_filter(
                        model.PostStatistics.note_count
                    ),
                ),
                (
                    ["relation-count"],
                    search_util.create_num_filter(
                        model.PostStatistics.relation_count
                    ),
                ),
                (
                    ["feature-count"],
                    search_util.create_num_filter(
                        model.PostStatistics.feature_count
                    ),
                ),
                (
                    ["type"],
                    search_util.create_str_filter(
                        model.Post.type, _type_transformer
                    ),
                ),
                (
                    ["content-checksum", "sha1"],
                    search_util.create_str_filter(model.Post.checksum),
                ),
                (
                    ["md5"],
                    search_util.create_str_filter(model.Post.checksum_md5),
                ),
                (
                    ["file-size"],
                    search_util.create_num_filter(model.Post.file_size),
                ),
                (
                    ["image-width", "width"],
                    search_util.create_num_filter(model.Post.canvas_width),
                ),
                (
                    ["image-height", "height"],
                    search_util.create_num_filter(
                        model.Post.canvas_height
                    ),
                ),
                (
                    ["image-area", "area"],
                    search_util.create_num_filter(model.Post.canvas_area),
                ),
                (
                    [
                        "image-aspect-ratio",
                        "image-ar",
                        "aspect-ratio",
                        "ar",
                    ],
                    search_util.create_num_filter(
                        model.Post.canvas_aspect_ratio,
                        transformer=search_util.float_transformer,
                    ),
                ),
                (
                    ["creation-date", "creation-time", "date", "time"],
                    search_util.create_date_filter(
                        model.Post.creation_time
                    ),
                ),
                (
                    [
                        "last-edit-date",
                        "last-edit-time",
                        "edit-date",
                        "edit-time",
                    ],
                    search_util.create_date_filter(
                        model.Post.last_edit_time
                    ),
                ),
                (
                    ["comment-date", "comment-time"],
                    search_util.create_date_filter(
                        model.PostStatistics.last_comment_creation_time
                    ),
                ),
                (
                    ["fav-date", "fav-time"],
                    search_util.create_date_filter(
                        model.PostStatistics.last_favorite_time
                    ),
                ),
                (
                    ["feature-date", "feature-time"],
                    search_util.create_date_filter(
                        model.PostStatistics.last_feature_time
                    ),
                ),
                (
                    ["safety", "rating"],
                    search_util.create_str_filter(
                        model.Post.safety, _safety_transformer
                    ),
                ),
                (["note-text"], _note_filter),
                (
                    ["flag"],
                    search_util.create_str_filter(
                        model.Post.flags_string, _flag_transformer
                    ),
                ),
                (["pool"], _pool_filter),
                (["similar"], _similar_filter),
                (["category"], _category_filter),
            ]
        )

    @property
    def sort_columns(self) -> Dict[str, Tuple[SaColumn, str]]:
        return util.unalias_dict(
            [
                (
                    ["random"],
                    (sa.sql.expression.func.random(), self.SORT_NONE),
                ),
                (["id"], (model.Post.post_id, self.SORT_DESC)),
                (
                    ["score"],
                    (model.PostStatistics.score, self.SORT_DESC),
                ),
                (
                    ["tag-count"],
                    (model.PostStatistics.tag_count, self.SORT_DESC),
                ),
                (
                    ["comment-count"],
                    (
                        model.PostStatistics.comment_count,
                        self.SORT_DESC,
                    ),
                ),
                (
                    ["fav-count"],
                    (
                        model.PostStatistics.favorite_count,
                        self.SORT_DESC,
                    ),
                ),
                (
                    ["note-count"],
                    (model.PostStatistics.note_count, self.SORT_DESC),
                ),
                (
                    ["relation-count"],
                    (
                        model.PostStatistics.relation_count,
                        self.SORT_DESC,
                    ),
                ),
                (
                    ["feature-count"],
                    (
                        model.PostStatistics.feature_count,
                        self.SORT_DESC,
                    ),
                ),
                (["file-size"], (model.Post.file_size, self.SORT_DESC)),
                (
                    ["image-width", "width"],
                    (model.Post.canvas_width, self.SORT_DESC),
                ),
                (
                    ["image-height", "height"],
                    (model.Post.canvas_height, self.SORT_DESC),
                ),
                (
                    ["image-area", "area"],
                    (model.Post.canvas_area, self.SORT_DESC),
                ),
                (
                    ["creation-date", "creation-time", "date", "time"],
                    (model.Post.creation_time, self.SORT_DESC),
                ),
                (
                    [
                        "last-edit-date",
                        "last-edit-time",
                        "edit-date",
                        "edit-time",
                    ],
                    (model.Post.last_edit_time, self.SORT_DESC),
                ),
                (
                    ["comment-date", "comment-time"],
                    (
                        model.PostStatistics.last_comment_creation_time,
                        self.SORT_DESC,
                    ),
                ),
                (
                    ["fav-date", "fav-time"],
                    (
                        model.PostStatistics.last_favorite_time,
                        self.SORT_DESC,
                    ),
                ),
                (
                    ["feature-date", "feature-time"],
                    (
                        model.PostStatistics.last_feature_time,
                        self.SORT_DESC,
                    ),
                ),
            ]
        )

    @property
    def special_filters(self) -> Dict[str, Filter]:
        return {
            # handled by parser
            "fav": self.noop_filter,
            "liked": self.noop_filter,
            "disliked": self.noop_filter,
            "tumbleweed": self.tumbleweed_filter,
        }

    def noop_filter(
        self,
        query: SaQuery,
        _criterion: Optional[criteria.BaseCriterion],
        _negated: bool,
    ) -> SaQuery:
        return query

    def tumbleweed_filter(
        self,
        query: SaQuery,
        _criterion: Optional[criteria.BaseCriterion],
        negated: bool,
    ) -> SaQuery:
        expr = (
            (model.PostStatistics.comment_count == 0)
            & (model.PostStatistics.favorite_count == 0)
            & (model.PostStatistics.score == 0)
        )
        if negated:
            expr = ~expr
        return query.filter(expr)
