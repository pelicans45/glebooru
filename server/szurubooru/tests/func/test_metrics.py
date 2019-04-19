import pytest
from szurubooru import db, model
from szurubooru.func import metrics


def test_serialize_metric(tag_factory):
    tag = tag_factory()
    metric = model.Metric(tag=tag, min=1, max=2)
    result = metrics.serialize_metric(metric)
    assert result == {
        'min': 1,
        'max': 2,
    }


def test_serialize_post_metric(tag_factory, metric_factory):
    tag = tag_factory(names=['mytag'])
    metric = metric_factory(tag)
    db.session.add_all([tag, metric])
    db.session.flush()
    post_metric = model.PostMetric(metric=metric, value=-12.3)
    result = metrics.serialize_post_metric(post_metric)
    assert result == {
        'tag_name': 'mytag',
        'value': -12.3,
    }


def test_serialize_post_metric_range(tag_factory, metric_factory):
    tag = tag_factory(names=['mytag'])
    metric = metric_factory(tag)
    db.session.add_all([tag, metric])
    db.session.flush()
    post_metric_range = model.PostMetricRange(metric=metric, low=-1.2, high=3.4)
    result = metrics.serialize_post_metric_range(post_metric_range)
    assert result == {
        'tag_name': 'mytag',
        'low': -1.2,
        'high': 3.4
    }


def test_try_get_post_metric(
        post_factory, metric_factory, post_metric_factory):
    post = post_factory()
    metric = metric_factory()
    metric2 = metric_factory()
    post_metric = post_metric_factory(post=post, metric=metric)
    db.session.add_all([post, metric, metric2, post_metric])
    db.session.flush()
    assert metrics.try_get_post_metric(post, metric2) is None
    assert metrics.try_get_post_metric(post, metric) is post_metric


def test_try_get_post_metric_range(
        post_factory, metric_factory, post_metric_range_factory):
    post = post_factory()
    metric = metric_factory()
    metric2 = metric_factory()
    post_metric_range = post_metric_range_factory(post=post, metric=metric)
    db.session.add_all([post, metric, metric2, post_metric_range])
    db.session.flush()
    assert metrics.try_get_post_metric_range(post, metric2) is None
    assert metrics.try_get_post_metric_range(post, metric) is post_metric_range


def test_get_all_metrics(metric_factory):
    metric1 = metric_factory()
    metric2 = metric_factory()
    metric3 = metric_factory()
    db.session.add_all([metric1, metric2, metric3])
    db.session.flush()
    all_metrics = metrics.get_all_metrics()
    assert len(all_metrics) == 3
    assert metric1 in all_metrics
    assert metric2 in all_metrics
    assert metric3 in all_metrics


def test_create_metric(tag_factory):
    tag = tag_factory()
    db.session.add(tag)
    new_metric = metrics.create_metric(tag, 1, 2)
    assert new_metric is not None
    db.session.flush()
    assert tag.metric is not None
    assert tag.metric.min == 1
    assert tag.metric.max == 2


def test_create_metric_with_existing_metric(tag_factory):
    tag = tag_factory()
    tag.metric = model.Metric()
    with pytest.raises(metrics.MetricAlreadyExistsError):
        metrics.create_metric(tag, 1, 2)


def test_create_metric_with_invalid_params(tag_factory):
    tag = tag_factory()
    with pytest.raises(metrics.InvalidMetricError):
        metrics.create_metric(tag, 2, 1)


def test_update_or_create_metric(tag_factory):
    tag = tag_factory()
    db.session.add(tag)
    new_metric = metrics.update_or_create_metric(tag, {'min': 1, 'max': 2})
    assert new_metric is not None
    db.session.flush()
    assert tag.metric is not None
    assert tag.metric.min == 1
    assert tag.metric.max == 2

    new_metric = metrics.update_or_create_metric(tag, {'min': 3, 'max': 4})
    assert new_metric is None
    db.session.flush()
    assert tag.metric.min == 3
    assert tag.metric.max == 4


@pytest.mark.parametrize('params', [
    {'min': 1}, {'max': 2}, {'min': 2, 'max': 1}
])
def test_update_or_create_metric_with_invalid_params(tag_factory, params):
    tag = tag_factory()
    with pytest.raises(metrics.InvalidMetricError):
        metrics.update_or_create_metric(tag, params)


# Post metrics

def test_update_or_create_post_metric_without_tag(post_factory, metric_factory):
    post = post_factory()
    metric = metric_factory()
    with pytest.raises(metrics.PostMissingTagError):
        metrics.update_or_create_post_metric(post, metric, 1.5)


def test_update_or_create_post_metric_with_value_out_of_range(
        post_factory, tag_factory, metric_factory):
    post = post_factory()
    tag = tag_factory()
    post.tags = [tag]
    metric = metric_factory(tag)
    with pytest.raises(metrics.MetricValueOutOfRangeError):
        metrics.update_or_create_post_metric(post, metric, -99)


def test_update_or_create_post_metric_create(
        post_factory, tag_factory, metric_factory):
    post = post_factory()
    tag = tag_factory()
    post.tags = [tag]
    metric = metric_factory(tag)
    db.session.add(metric)
    db.session.flush()
    post_metric = metrics.update_or_create_post_metric(post, metric, 1.5)
    assert post_metric.value == 1.5


def test_update_or_create_post_metric_update(
        post_factory, tag_factory, metric_factory):
    post = post_factory()
    tag = tag_factory()
    post.tags = [tag]
    metric = metric_factory(tag)
    post_metric = model.PostMetric(post=post, metric=metric, value=1.2)
    db.session.add(post_metric)
    db.session.flush()

    metrics.update_or_create_post_metric(post, metric, 3.4)
    db.session.flush()

    assert post_metric.value == 3.4


def test_update_or_create_post_metrics_missing_tag(
        post_factory, tag_factory, metric_factory):
    post = post_factory()
    tag = tag_factory(names=['tag1'])
    metric = metric_factory(tag)
    db.session.add(metric)
    db.session.flush()
    data = [{'tag_name': 'tag1', 'value': 1.5}]
    with pytest.raises(metrics.PostMissingTagError):
        metrics.update_or_create_post_metrics(post, data)


@pytest.mark.parametrize('params', [
    [{}],
    [{'tag_name': 'tag'}],
    [{'value': 1.5}]
])
def test_update_or_create_post_metrics_with_missing_fields(
        params, post_factory):
    post = post_factory()
    with pytest.raises(metrics.InvalidMetricError):
        metrics.update_or_create_post_metrics(post, params)


def test_update_or_create_post_metrics_with_invalid_tag(
        post_factory, tag_factory):
    post = post_factory()
    tag = tag_factory(names=['tag1'])
    post.tags = [tag]
    db.session.add(tag)
    db.session.flush()
    data = [{'tag_name': 'tag1', 'value': 2}]
    with pytest.raises(metrics.MetricDoesNotExistsError):
        metrics.update_or_create_post_metrics(post, data)


def test_update_or_create_post_metrics(
        post_factory, tag_factory, metric_factory):
    post = post_factory()
    tag1 = tag_factory(names=['tag1'])
    tag2 = tag_factory(names=['tag2'])
    post.tags = [tag1, tag2]
    metric1 = metric_factory(tag1)
    metric2 = metric_factory(tag2)
    db.session.add_all([metric1, metric2])
    db.session.flush()

    data = [
        {'tag_name': 'tag1', 'value': 1.2},
        {'tag_name': 'tag2', 'value': 3.4},
    ]
    metrics.update_or_create_post_metrics(post, data)
    db.session.flush()

    assert len(post.metrics) == 2
    assert post.metrics[0].value == 1.2
    assert post.metrics[1].value == 3.4


# Post metric ranges

def test_update_or_create_post_metric_range_without_tag(
        post_factory, metric_factory):
    post = post_factory()
    metric = metric_factory()
    with pytest.raises(metrics.PostMissingTagError):
        metrics.update_or_create_post_metric_range(post, metric, 2, 3)


@pytest.mark.parametrize('low, high', [
    (-99, 1), (1, 99),
])
def test_update_or_create_post_metric_range_with_values_out_of_range(
        low, high, post_factory, tag_factory, metric_factory):
    post = post_factory()
    tag = tag_factory()
    post.tags = [tag]
    metric = metric_factory(tag)
    with pytest.raises(metrics.MetricValueOutOfRangeError):
        metrics.update_or_create_post_metric_range(post, metric, low, high)


def test_update_or_create_post_metric_range_create(
        post_factory, tag_factory, metric_factory):
    post = post_factory()
    tag = tag_factory()
    post.tags = [tag]
    metric = metric_factory(tag)
    db.session.add(metric)
    db.session.flush()
    post_metric_range = metrics.update_or_create_post_metric_range(
        post, metric, 2, 3)
    assert post_metric_range.low == 2
    assert post_metric_range.high == 3


def test_update_or_create_post_metric_range_update(
        post_factory, tag_factory, metric_factory):
    post = post_factory()
    tag = tag_factory()
    post.tags = [tag]
    metric = metric_factory(tag)
    post_metric_range = model.PostMetricRange(
        post=post, metric=metric, low=2, high=3)
    db.session.add(post_metric_range)
    db.session.flush()

    metrics.update_or_create_post_metric_range(post, metric, 4, 5)
    db.session.flush()

    assert post_metric_range.low == 4
    assert post_metric_range.high == 5


def test_update_or_create_post_metric_ranges_missing_tag(
        post_factory, tag_factory, metric_factory):
    post = post_factory()
    tag = tag_factory(names=['tag1'])
    metric = metric_factory(tag)
    db.session.add(metric)
    db.session.flush()
    data = [{'tag_name': 'tag1', 'low': 2, 'high': 3}]
    with pytest.raises(metrics.PostMissingTagError):
        metrics.update_or_create_post_metric_ranges(post, data)


@pytest.mark.parametrize('params', [
    [{}],
    [{'tag_name': 'tag'}],
    [{'tag_name': 'tag', 'low': 2}],
    [{'low': 2, 'high': 3}],
])
def test_update_or_create_post_metric_ranges_with_missing_fields(
        params, post_factory, tag_factory):
    post = post_factory()
    tag = tag_factory(names=['tag'])
    post.tags = [tag]
    with pytest.raises(metrics.InvalidMetricError):
        metrics.update_or_create_post_metric_ranges(post, params)


def test_update_or_create_post_metric_ranges_with_invalid_tag(
        post_factory, tag_factory):
    post = post_factory()
    tag = tag_factory(names=['tag1'])
    post.tags = [tag]
    db.session.add(tag)
    db.session.flush()
    data = [{'tag_name': 'tag1', 'low': 2, 'high': 3}]
    with pytest.raises(metrics.MetricDoesNotExistsError):
        metrics.update_or_create_post_metric_ranges(post, data)


def test_update_or_create_post_metric_ranges_with_invalid_values(
        post_factory, tag_factory, metric_factory):
    post = post_factory()
    tag = tag_factory(names=['tag1'])
    post.tags = [tag]
    metric = metric_factory(tag=tag)
    db.session.add_all([metric, tag])
    db.session.flush()
    data = [
        {'tag_name': 'tag1', 'low': 4, 'high': 2},
    ]
    with pytest.raises(metrics.InvalidMetricError):
        metrics.update_or_create_post_metric_ranges(post, data)


def test_update_or_create_post_metric_ranges(
        post_factory, tag_factory, metric_factory):
    post = post_factory()
    tag1 = tag_factory(names=['tag1'])
    tag2 = tag_factory(names=['tag2'])
    post.tags = [tag1, tag2]
    metric1 = metric_factory(tag1)
    metric2 = metric_factory(tag2)
    db.session.add_all([metric1, metric2])
    db.session.flush()

    data = [
        {'tag_name': 'tag1', 'low': 2, 'high': 3},
        {'tag_name': 'tag2', 'low': 4, 'high': 5},
    ]
    metrics.update_or_create_post_metric_ranges(post, data)
    db.session.flush()

    assert len(post.metric_ranges) == 2
    assert post.metric_ranges[0].low == 2
    assert post.metric_ranges[0].high == 3
    assert post.metric_ranges[1].low == 4
    assert post.metric_ranges[1].high == 5
