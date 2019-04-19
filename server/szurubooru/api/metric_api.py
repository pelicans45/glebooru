from typing import Optional, List, Dict
from szurubooru import db, model, search, rest
from szurubooru.func import auth, metrics, snapshots, serialization, tags


_search_executor_config = search.configs.PostMetricSearchConfig()
_search_executor = search.Executor(_search_executor_config)


def _serialize_metric(
        ctx: rest.Context, metric: model.Metric) -> rest.Response:
    return metrics.serialize_metric(
        metric, options=serialization.get_serialization_options(ctx)
    )


def _serialize_post_metric(
        ctx: rest.Context, post_metric: model.PostMetric) -> rest.Response:
    return metrics.serialize_post_metric(
        post_metric, options=serialization.get_serialization_options(ctx)
    )


@rest.routes.get('/metrics/?')
def get_metrics(
        ctx: rest.Context, params: Dict[str, str] = {}) -> rest.Response:
    auth.verify_privilege(ctx.user, 'metrics:list')
    all_metrics = metrics.get_all_metrics()
    return {
        'results': [_serialize_metric(ctx, metric) for metric in all_metrics]
    }


@rest.routes.post('/metrics/?')
def create_metric(
        ctx: rest.Context, params: Dict[str, str] = {}) -> rest.Response:
    auth.verify_privilege(ctx.user, 'metrics:create')
    tag_name = ctx.get_param_as_string('tag_name')
    tag = tags.get_tag_by_name(tag_name)
    min = ctx.get_param_as_float('min')
    max = ctx.get_param_as_float('max')

    metric = metrics.create_metric(tag, min, max)
    ctx.session.flush()
    # snapshots.create(metric, ctx.user)
    ctx.session.commit()
    return _serialize_metric(ctx, metric)


@rest.routes.get('/post-metrics/?')
def get_post_metrics(
        ctx: rest.Context, params: Dict[str, str] = {}) -> rest.Response:
    auth.verify_privilege(ctx.user, 'metrics:list')
    _search_executor_config.user = ctx.user
    return _search_executor.execute_and_serialize(
        ctx, lambda post_metric: _serialize_post_metric(ctx, post_metric))
