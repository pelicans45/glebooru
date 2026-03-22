import unittest.mock

import pytest

from szurubooru import search
from szurubooru.func import cache


def test_retrieving_from_cache():
    config = unittest.mock.MagicMock()
    with unittest.mock.patch("szurubooru.func.cache.get"):
        cache.get.return_value = {
            "_type": "cached_search_result",
            "model_path": None,
            "ids": [],
            "count": 123,
            "has_more": False,
        }
        executor = search.Executor(config)
        result = executor.execute("test:whatever", 1, 10)
        assert cache.get.called
        assert result == (123, [])
        assert not config.create_filter_query.called


def test_putting_equivalent_queries_into_cache():
    config = search.configs.PostSearchConfig()
    with unittest.mock.patch("szurubooru.func.cache.get"), unittest.mock.patch(
        "szurubooru.func.cache.put"
    ):
        hashes = []

        def appender(key, _value, **_kwargs):
            hashes.append(key)

        cache.get.return_value = None
        cache.put.side_effect = appender
        executor = search.Executor(config)
        executor.execute("safety:safe test", 1, 10)
        executor.execute("safety:safe  test", 1, 10)
        executor.execute("safety:safe test ", 1, 10)
        executor.execute(" safety:safe test", 1, 10)
        executor.execute(" SAFETY:safe test", 1, 10)
        executor.execute("test safety:safe", 1, 10)
        assert len(hashes) == 6
        assert len(set(hashes)) == 1


def test_putting_non_equivalent_queries_into_cache():
    config = search.configs.PostSearchConfig()
    with unittest.mock.patch("szurubooru.func.cache.get"), unittest.mock.patch(
        "szurubooru.func.cache.put"
    ):
        hashes = []

        def appender(key, _value, **_kwargs):
            hashes.append(key)

        cache.get.return_value = None
        cache.put.side_effect = appender
        executor = search.Executor(config)
        args = [
            ("", 1, 10),
            ("creation-time:2016", 1, 10),
            ("creation-time:2015", 1, 10),
            ("creation-time:2016-01", 1, 10),
            ("creation-time:2016-02", 1, 10),
            ("creation-time:2016-01-01", 1, 10),
            ("creation-time:2016-01-02", 1, 10),
            ("tag-count:1,3", 1, 10),
            ("tag-count:1,2", 1, 10),
            ("tag-count:1", 1, 10),
            ("tag-count:1..3", 1, 10),
            ("tag-count:1..4", 1, 10),
            ("tag-count:2..3", 1, 10),
            ("tag-count:1..", 1, 10),
            ("tag-count:2..", 1, 10),
            ("tag-count:..3", 1, 10),
            ("tag-count:..4", 1, 10),
            ("-tag-count:1..3", 1, 10),
            ("-tag-count:1..4", 1, 10),
            ("-tag-count:2..3", 1, 10),
            ("-tag-count:1..", 1, 10),
            ("-tag-count:2..", 1, 10),
            ("-tag-count:..3", 1, 10),
            ("-tag-count:..4", 1, 10),
            ("safety:safe", 1, 10),
            ("safety:safe", 1, 20),
            ("safety:safe", 2, 10),
            ("safety:sketchy", 1, 10),
            ("safety:safe test", 1, 10),
            ("-safety:safe", 1, 10),
            ("-safety:safe", 1, 20),
            ("-safety:safe", 2, 10),
            ("-safety:sketchy", 1, 10),
            ("-safety:safe test", 1, 10),
            ("safety:safe -test", 1, 10),
            ("-test", 1, 10),
        ]
        for arg in args:
            executor.execute(*arg)
        assert len(hashes) == len(args)
        assert len(set(hashes)) == len(args)


def test_invalid_cached_payload_is_treated_as_cache_miss():
    config = search.configs.PostSearchConfig()
    with unittest.mock.patch("szurubooru.func.cache.get"), unittest.mock.patch(
        "szurubooru.func.cache.put"
    ):
        cache.get.return_value = {"_type": "unexpected"}
        executor = search.Executor(config)
        executor.execute("safety:safe", 1, 10)
        assert cache.put.called


def test_invalid_cached_model_path_is_treated_as_cache_miss():
    config = search.configs.PostSearchConfig()
    with unittest.mock.patch("szurubooru.func.cache.get"), unittest.mock.patch(
        "szurubooru.func.cache.put"
    ):
        cache.get.return_value = {
            "_type": "cached_search_result",
            "model_path": "not.a.real.module:Nope",
            "ids": [],
            "count": 1,
            "has_more": False,
        }
        executor = search.Executor(config)
        executor.execute("safety:safe", 1, 10)
        assert cache.put.called


def test_cache_keys_are_stable_across_executor_instances():
    cached_keys = []
    cached_response = {
        "_type": "cached_search_result",
        "model_path": None,
        "ids": [],
        "count": 0,
        "has_more": False,
    }

    def _cache_get(key, **_kwargs):
        cached_keys.append(key)
        return cached_response

    with unittest.mock.patch("szurubooru.func.cache.get"):
        cache.get.side_effect = _cache_get
        first = search.Executor(search.configs.PostSearchConfig())
        second = search.Executor(search.configs.PostSearchConfig())

        first.execute("safety:safe test", 1, 10)
        second.execute("safety:safe test", 1, 10)

    assert len(cached_keys) == 2
    assert cached_keys[0] == cached_keys[1]


@pytest.mark.parametrize(
    "input",
    [
        "special:fav",
        "special:liked",
        "special:disliked",
        "-special:fav",
        "-special:liked",
        "-special:disliked",
    ],
)
def test_putting_auth_dependent_queries_into_cache(user_factory, input):
    config = search.configs.PostSearchConfig()
    with unittest.mock.patch("szurubooru.func.cache.get"), unittest.mock.patch(
        "szurubooru.func.cache.put"
    ):
        hashes = []

        def appender(key, _value, **_kwargs):
            hashes.append(key)

        cache.get.return_value = None
        cache.put.side_effect = appender
        executor = search.Executor(config)

        executor.config.user = user_factory()
        executor.execute(input, 1, 1)
        assert len(set(hashes)) == 1

        executor.config.user = user_factory()
        executor.execute(input, 1, 1)
        assert len(set(hashes)) == 2

        executor.execute(input, 1, 1)
        assert len(set(hashes)) == 2
