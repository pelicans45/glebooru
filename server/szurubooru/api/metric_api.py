from typing import Optional, List, Dict
from szurubooru import db, model, search, rest
from szurubooru.func import auth, metrics, snapshots, serialization, tags


def _serialize(ctx: rest.Context, metric: model.Metric) -> rest.Response:
    return metrics.serialize_metric(
        metric, options=serialization.get_serialization_options(ctx)
    )


@rest.routes.post('/metrics/?')
def create_metric(ctx: rest.Context, params: Dict[str, str] = {}) -> rest.Response:
    auth.verify_privilege(ctx.user, 'metrics:create')
    tag_name = ctx.get_param_as_string('tag_name')
    tag = tags.get_tag_by_name(tag_name)
    min = ctx.get_param_as_float('min')
    max = ctx.get_param_as_float('max')

    metric = metrics.create_metric(tag, min, max)
    ctx.session.flush()
    # snapshots.create(metric, ctx.user)
    ctx.session.commit()
    return _serialize(ctx, metric)
