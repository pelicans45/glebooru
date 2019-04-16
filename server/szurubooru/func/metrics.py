from typing import Any, Optional, Tuple, List, Dict, Callable
import sqlalchemy as sa
from szurubooru import config, db, model, errors, rest
from szurubooru.func import serialization


class MetricAlreadyExistsError(errors.ValidationError):
    pass


class InvalidMetricError(errors.ValidationError):
    pass


class MetricSeralizer(serialization.BaseSerializer):
    def __init__(self, metric: model.Metric):
        self.metric = metric

    def _serializers(self) -> Dict[str, Callable[[], Any]]:
        return {
            'min': self.metric.min,
            'max': self.metric.max,
        }

    def serialize_min(self) -> Any:
        return self.metric.min

    def serialize_max(self) -> Any:
        return self.metric.max


def serialize_metric(metric: model.Metric, options: List[str] = []) -> Optional[rest.Response]:
    if not metric:
        return None
    return MetricSeralizer(metric).serialize(options)


def create_metric(
        tag: model.Tag,
        min: float,
        max: float) -> model.Metric:
    if tag.metric is not None:
        raise MetricAlreadyExistsError('Tag already has a metric.')
    metric = model.Metric(tag=tag, min=min, max=max)
    return metric


def update_metric(tag: model.Tag, metric_data) -> Optional[model.Metric]:
    for field in ('min', 'max'):
        if field not in metric_data:
            raise InvalidMetricError('Metric is missing %r field.' % field)

    min, max = metric_data['min'], metric_data['max']
    if tag.metric is not None:
        tag.metric.min = min
        tag.metric.max = max
        db.session.add(tag.metric)
        return None
    else:
        metric = model.Metric(tag=tag, min=min, max=max)
        db.session.add(metric)
        return metric
