from typing import Any, Optional, Tuple, List, Dict, Callable
import sqlalchemy as sa
from szurubooru import config, db, model, errors, rest
from szurubooru.func import util, serialization, tags


class MetricAlreadyExistsError(errors.ValidationError):
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
        tag_name: str,
        min: float,
        max: float) -> model.Metric:
    tag = tags.get_tag_by_name(tag_name)
    if tag.metric is not None:
        raise MetricAlreadyExistsError('Tag already has a metric.')
    metric = model.Metric(tag=tag, min=min, max=max)
    return metric
