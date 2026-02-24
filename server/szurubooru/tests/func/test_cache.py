from szurubooru.func import cache


def test_put_get_remove_roundtrip():
    key = ("cache-test", "roundtrip")
    value = {"x": 1, "y": [1, 2, 3]}

    cache.purge()
    cache.put(key, value, ttl_seconds=30)

    assert cache.has(key)
    assert cache.get(key) == value

    cache.remove(key)
    assert cache.get(key) is None


def test_put_with_zero_ttl_does_not_store():
    key = ("cache-test", "zero-ttl")

    cache.purge()
    cache.put(key, "value", ttl_seconds=0)

    assert cache.get(key) is None


def test_purge_invalidates_entries():
    key = ("cache-test", "purge")

    cache.purge()
    cache.put(key, "value", ttl_seconds=30)
    assert cache.get(key) == "value"

    cache.purge()
    assert cache.get(key) is None


def test_scoped_purge_does_not_invalidate_other_scopes():
    key = ("cache-test", "scopes")

    cache.purge(scope=cache.SCOPE_SEARCH)
    cache.purge(scope=cache.SCOPE_POST_RESPONSE)
    cache.put(
        key,
        "search-value",
        ttl_seconds=30,
        scope=cache.SCOPE_SEARCH,
    )
    cache.put(
        key,
        "post-value",
        ttl_seconds=30,
        scope=cache.SCOPE_POST_RESPONSE,
    )

    cache.purge(scope=cache.SCOPE_SEARCH)

    assert cache.get(key, scope=cache.SCOPE_SEARCH) is None
    assert cache.get(key, scope=cache.SCOPE_POST_RESPONSE) == "post-value"
