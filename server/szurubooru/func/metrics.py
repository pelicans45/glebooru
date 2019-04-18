from typing import Any, Optional, List, Dict, Callable
from szurubooru import db, model, errors, rest
from szurubooru.func import serialization, tags


class MetricDoesNotExistsError(errors.ValidationError):
    pass


class MetricAlreadyExistsError(errors.ValidationError):
    pass


class InvalidMetricError(errors.ValidationError):
    pass


class PostMissingTagError(errors.ValidationError):
    pass


class MetricValueOutOfRangeError(errors.ValidationError):
    pass


class MetricSerializer(serialization.BaseSerializer):
    def __init__(self, metric: model.Metric):
        self.metric = metric

    def _serializers(self) -> Dict[str, Callable[[], Any]]:
        return {
            'min': self.serialize_min,
            'max': self.serialize_max,
        }

    def serialize_min(self) -> Any:
        return self.metric.min

    def serialize_max(self) -> Any:
        return self.metric.max


def serialize_metric(
        metric: model.Metric,
        options: List[str] = []) -> Optional[rest.Response]:
    if not metric:
        return None
    return MetricSerializer(metric).serialize(options)


def try_get_post_metric(
        post: model.Post,
        metric: model.Metric) -> Optional[model.PostMetric]:
    return (
        db.session
        .query(model.PostMetric)
        .filter(model.PostMetric.metric == metric and
                model.PostMetric.post == post)
        .one_or_none())


def try_get_post_metric_range(
        post: model.Post,
        metric: model.Metric) -> Optional[model.PostMetricRange]:
    return (
        db.session
        .query(model.PostMetricRange)
        .filter(model.PostMetricRange.metric == metric and
                model.PostMetricRange.post == post)
        .one_or_none())


def create_metric(
        tag: model.Tag,
        min: float,
        max: float) -> model.Metric:
    assert tag
    if tag.metric is not None:
        raise MetricAlreadyExistsError('Tag already has a metric.')
    if min >= max:
        raise InvalidMetricError('Metric min(%r) >= max(%r)' % (min, max))
    metric = model.Metric(tag=tag, min=min, max=max)
    db.session.add(metric)
    return metric


def update_or_create_metric(
        tag: model.Tag,
        metric_data: Any) -> Optional[model.Metric]:
    assert tag
    for field in ('min', 'max'):
        if field not in metric_data:
            raise InvalidMetricError('Metric is missing %r field.' % field)

    min, max = metric_data['min'], metric_data['max']
    if min >= max:
        raise InvalidMetricError('Metric min(%r) >= max(%r)' % (min, max))
    if tag.metric is not None:
        tag.metric.min = min
        tag.metric.max = max
        return None
    else:
        return create_metric(tag=tag, min=min, max=max)


def update_or_create_post_metric(
        post: model.Post,
        metric: model.Metric,
        value: float) -> model.PostMetric:
    assert post
    assert metric
    if metric.tag not in post.tags:
        raise PostMissingTagError(
            'Post doesn\'t have tag %r' % metric.tag.names[0])
    if value < metric.min or value > metric.max:
        raise MetricValueOutOfRangeError(
            'Metric value %r out of range.' % value)
    post_metric = try_get_post_metric(post, metric)
    if post_metric is None:
        post_metric = model.PostMetric(post=post, metric=metric, value=value)
        db.session.add(post_metric)
    else:
        post_metric.value = value
    return post_metric


def update_or_create_post_metrics(post: model.Post, metrics_data: Any) -> None:
    """
    Overwrites any existing post metrics, deletes other existing post metrics.
    """
    assert post
    post.metrics = []
    for metric_data in metrics_data:
        for field in ('tag_name', 'value'):
            if field not in metric_data:
                raise InvalidMetricError('Metric is missing %r field.' % field)
        value = float(metric_data['value'])
        tag = tags.get_tag_by_name(metric_data['tag_name'])
        if tag.metric is None:
            raise MetricDoesNotExistsError(
                'Tag %r has no metric.' % tag.names[0])
        post_metric = update_or_create_post_metric(post, tag.metric, value)
        post.metrics.append(post_metric)


def update_or_create_post_metric_range(
        post: model.Post,
        metric: model.Metric,
        low: float,
        high: float) -> model.PostMetricRange:
    assert post
    assert metric
    if metric.tag not in post.tags:
        raise PostMissingTagError(
            'Post doesn\'t have tag %r' % metric.tag.names[0])
    for value in (low, high):
        if value < metric.min or value > metric.max:
            raise MetricValueOutOfRangeError(
                'Metric value %r out of range.' % value)
    if low >= high:
        raise InvalidMetricError(
            'Metric range low(%r) >= high(%r)' % (low, high))
    post_metric_range = try_get_post_metric_range(post, metric)
    if post_metric_range is None:
        post_metric_range = model.PostMetricRange(
            post=post, metric=metric, low=low, high=high)
        db.session.add(post_metric_range)
    else:
        post_metric_range.low = low
        post_metric_range.high = high
    return post_metric_range


def update_or_create_post_metric_ranges(
        post: model.Post,
        metric_ranges_data: Any) -> None:
    """
    Overwrites any existing post metrics, deletes other existing post metrics.
    """
    assert post
    post.metrics = []
    for metric_data in metric_ranges_data:
        for field in ('tag_name', 'low', 'high'):
            if field not in metric_data:
                raise InvalidMetricError(
                    'Metric range is missing %r field.' % field)
        low = float(metric_data['low'])
        high = float(metric_data['high'])
        tag = tags.get_tag_by_name(metric_data['tag_name'])
        if tag.metric is None:
            raise MetricDoesNotExistsError(
                'Tag %r has no metric.' % tag.names[0])
        post_metric_range = update_or_create_post_metric_range(
            post, tag.metric, low, high)
        post.metric_ranges.append(post_metric_range)
