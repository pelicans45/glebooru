import redis

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


def _reset_cache_runtime_state(monkeypatch):
    monkeypatch.setattr(cache, "_CACHE_DEGRADED", False)
    monkeypatch.setattr(cache, "_CACHE_FAIL_OPEN_UNTIL", 0.0)
    monkeypatch.setattr(cache, "_CACHE_DOWN_LOGGED", False)
    monkeypatch.setattr(cache, "_RECOVERY_PURGE_PENDING", False)


class _DownRedis:
    def __init__(self):
        self.calls = 0

    def _fail(self):
        self.calls += 1
        raise redis.exceptions.ConnectionError("redis down")

    def ping(self):
        self._fail()

    def get(self, _key):
        self._fail()

    def set(self, _key, _value, nx=False):
        del nx
        self._fail()

    def exists(self, _key):
        self._fail()

    def delete(self, _key):
        self._fail()

    def setex(self, _key, _ttl, _payload):
        self._fail()

    def incr(self, _key):
        self._fail()


class _ToggleRedis:
    def __init__(self):
        self.available = False
        self.store = {}
        self.incr_calls = []

    @staticmethod
    def _to_bytes(value):
        if isinstance(value, bytes):
            return value
        return str(value).encode("utf-8")

    def _ensure_available(self):
        if not self.available:
            raise redis.exceptions.ConnectionError("redis down")

    def ping(self):
        self._ensure_available()

    def get(self, key):
        self._ensure_available()
        return self.store.get(key)

    def set(self, key, value, nx=False):
        self._ensure_available()
        if nx and key in self.store:
            return False
        self.store[key] = self._to_bytes(value)
        return True

    def exists(self, key):
        self._ensure_available()
        return 1 if key in self.store else 0

    def delete(self, key):
        self._ensure_available()
        if key in self.store:
            del self.store[key]
            return 1
        return 0

    def setex(self, key, _ttl, payload):
        self._ensure_available()
        self.store[key] = payload
        return True

    def incr(self, key):
        self._ensure_available()
        self.incr_calls.append(key)
        raw = self.store.get(key, b"0")
        value = int(raw.decode("utf-8")) + 1
        self.store[key] = str(value).encode("utf-8")
        return value

    def scan_iter(self, match):
        self._ensure_available()
        if match.endswith("*"):
            prefix = match[:-1]
            for key in self.store:
                if key.startswith(prefix):
                    yield key
            return
        if match in self.store:
            yield match


def test_redis_runtime_failure_enters_fail_open_mode(monkeypatch):
    _reset_cache_runtime_state(monkeypatch)
    fake_redis = _DownRedis()
    monkeypatch.setattr(cache, "_REDIS_CLIENT", fake_redis)

    key = ("cache-test", "redis-down")
    assert cache.get(key) is None
    assert fake_redis.calls == 1
    assert cache._CACHE_DEGRADED
    assert cache._RECOVERY_PURGE_PENDING

    # While in breaker window, calls should not hit Redis again.
    assert cache.get(key) is None
    assert fake_redis.calls == 1


def test_redis_recovery_purges_scopes_once(monkeypatch):
    _reset_cache_runtime_state(monkeypatch)
    fake_redis = _ToggleRedis()
    monkeypatch.setattr(cache, "_REDIS_CLIENT", fake_redis)

    key = ("cache-test", "redis-recovery")
    custom_scope = "response:user"
    custom_namespace_key = cache._redis_namespace_key(custom_scope)
    fake_redis.store[custom_namespace_key] = b"7"
    fake_redis.store[cache._redis_namespace_key(cache.SCOPE_SEARCH)] = b"2"

    stale_key = (
        f"{cache._REDIS_KEY_PREFIX}:{custom_scope}:7:"
        f"{cache._serialize_key(key)}"
    )
    fake_redis.store[stale_key] = cache._serialize("value")

    cache.put(key, "value", ttl_seconds=30, scope=custom_scope)
    assert cache._CACHE_DEGRADED
    assert cache._RECOVERY_PURGE_PENDING

    fake_redis.available = True
    monkeypatch.setattr(cache, "_CACHE_FAIL_OPEN_UNTIL", 0.0)
    assert cache.get(key, scope=custom_scope) is None
    assert not cache._CACHE_DEGRADED

    expected_purge_keys = {
        custom_namespace_key,
        cache._redis_namespace_key(cache.SCOPE_SEARCH),
    }
    assert expected_purge_keys.issubset(set(fake_redis.incr_calls))
    assert fake_redis.store[custom_namespace_key] == b"8"

    cache.put(key, "value", ttl_seconds=30, scope=custom_scope)
    assert cache.get(key, scope=custom_scope) == "value"
