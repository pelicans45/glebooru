from typing import Tuple, Dict, List
import sqlalchemy as sa
from szurubooru import db, model
from szurubooru.func import util
from szurubooru.search.typing import SaColumn, SaQuery
from szurubooru.search.configs import util as search_util
from szurubooru.search.configs.base_search_config import (
    BaseSearchConfig, Filter)


class PostMetricSearchConfig(BaseSearchConfig):
    def __init__(self) -> None:
        self.all_metrics = []

    def refresh_metrics(self) -> None:
        self.all_metrics = (
            db.session.query(model.Metric)
            .options(sa.orm.lazyload('*'))
            .all())

    def create_filter_query(self, _disable_eager_loads: bool) -> SaQuery:
        self.refresh_metrics()
        return db.session.query(model.PostMetric).options(sa.orm.lazyload('*'))

    def create_count_query(self, disable_eager_loads: bool) -> SaQuery:
        return self.create_filter_query(disable_eager_loads)

    def create_around_query(self) -> SaQuery:
        return self.create_filter_query()

    def finalize_query(self, query: SaQuery) -> SaQuery:
        return query.order_by(model.PostMetric.value.asc())

    @property
    def anonymous_filter(self) -> Filter:
        return search_util.create_subquery_filter(
            model.PostMetric.tag_id,
            model.TagName.tag_id,
            model.TagName.name,
            search_util.create_str_filter)

    @property
    def named_filters(self) -> Dict[str, Filter]:
        num_filter = search_util.create_num_filter(
            model.PostMetric.value,
            transformer=search_util.float_transformer)
        return {metric.tag_name: num_filter for metric in self.all_metrics}
