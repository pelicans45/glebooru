import pytest
from szurubooru import db
from szurubooru.func import similar


@pytest.fixture
def verify_posts():
    def verify(actual_posts, expected_posts):
        actual_post_ids = list([p.post_id for p in actual_posts])
        expected_post_ids = list([p.post_id for p in expected_posts])
        assert actual_post_ids == expected_post_ids
    return verify


def test_find_similar_posts(post_factory, tag_factory, verify_posts):
    tagA = tag_factory(names=["a"])
    tagB = tag_factory(names=["b"])
    tagC = tag_factory(names=["c"])
    postA = post_factory(id=1, tags=[tagA])
    postAB = post_factory(id=2, tags=[tagA, tagB])
    postAC = post_factory(id=3, tags=[tagA, tagC])
    postABC = post_factory(id=4, tags=[tagA, tagB, tagC])
    postBC = post_factory(id=5, tags=[tagB, tagC])
    db.session.add_all([tagA, tagB, tagC, postA, postAB, postAC, postABC, postBC])
    db.session.flush()

    results = similar.find_similar_posts(postBC, 10)
    verify_posts(results, [postABC, postAC, postAB])

    results = similar.find_similar_posts(postBC, 2)
    verify_posts(results, [postABC, postAC])

    results = similar.find_similar_posts(postABC, 10)
    verify_posts(results, [postBC, postAC, postAB, postA])

    results = similar.find_similar_posts(postA, 10)
    verify_posts(results, [postABC, postAC, postAB])  # sorted by id

    results = similar.find_similar_posts(postAB, 10)
    verify_posts(results, [postABC, postBC, postAC, postA])

    results = similar.find_similar_posts(postAC, 10)
    verify_posts(results, [postABC, postBC, postAB, postA])
