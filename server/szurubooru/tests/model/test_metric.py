from szurubooru import db, model


def test_saving_metric(post_factory, tag_factory):
    post = post_factory()
    tag = tag_factory()
    metric = model.Metric(tag=tag, min=1., max=10.)
    post_metric = model.PostMetric(metric=metric, post=post, value=5.5)
    post_metric_range = model.PostMetricRange(metric=metric, post=post, low=2., high=8.)
    db.session.add_all([post, tag, metric, post_metric, post_metric_range])
    db.session.commit()

    assert metric.tag_id is not None
    assert post_metric.tag_id is not None
    assert post_metric.post_id is not None
    assert post_metric_range.tag_id is not None
    assert post_metric_range.post_id is not None

    metric = (
        db.session
        .query(model.Metric)
        .filter(model.Metric.tag_id == tag.tag_id)
        .one())
    assert metric.min == 1.
    assert metric.max == 10.

    post_metric = (
        db.session
        .query(model.PostMetric)
        .filter(model.PostMetric.tag_id == tag.tag_id and
                model.PostMetric.post_id == post.post_id)
        .one())
    assert post_metric.value == 5.5

    post_metric_range = (
        db.session
        .query(model.PostMetricRange)
        .filter(model.PostMetricRange.tag_id == tag.tag_id and
                model.PostMetricRange.post_id == post.post_id)
        .one())
    assert post_metric_range.low == 2.
    assert post_metric_range.high == 8.


def test_cascade_delete_metric():
    pass


def test_cascade_delete_tag():
    pass


def test_cascade_delete_post():
    pass


def test_tag_without_metric():
    pass


def test_post_tag_without_metric():
    pass


def test_metric_counts():
    pass
