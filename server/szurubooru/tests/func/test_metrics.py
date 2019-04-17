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


def test_create_metric(tag_factory):
    tag = tag_factory()
    db.session.add(tag)
    new_metric = metrics.create_metric(tag, 1, 2)
    assert new_metric is not None
    db.session.flush()
    db.session.refresh(tag)
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
    db.session.refresh(tag)
    assert tag.metric is not None
    assert tag.metric.min == 1
    assert tag.metric.max == 2

    new_metric = metrics.update_or_create_metric(tag, {'min': 3, 'max': 4})
    assert new_metric is None
    db.session.flush()
    db.session.refresh(tag)
    assert tag.metric.min == 3
    assert tag.metric.max == 4


@pytest.mark.parametrize('params', [
    {'min': 1}, {'max': 2}, {'min': 2, 'max': 1}
])
def test_update_or_create_metric_with_invalid_params(tag_factory, params):
    tag = tag_factory()
    with pytest.raises(metrics.InvalidMetricError):
        metrics.update_or_create_metric(tag, params)
