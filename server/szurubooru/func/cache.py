import base64
import hashlib
import logging
import os
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import orjson
import redis

from szurubooru import config


_DEFAULT_TTL_SECONDS = 600
_CIRCUIT_BREAKER_SECONDS = 30.0
_REDIS_KEY_PREFIX = "szurubooru:cache"
_REDIS_NAMESPACE_KEY = "szurubooru:cache:namespace"
_TYPE_KEY = "__cache_type__"

SCOPE_GLOBAL = "global"
SCOPE_SEARCH = "search"
SCOPE_POST_RESPONSE = "response:post"
SCOPE_TAG_RESPONSE = "response:tag"

_STATE_LOCK = threading.Lock()
_CACHE_DEGRADED = False
_CACHE_FAIL_OPEN_UNTIL = 0.0
_CACHE_DOWN_LOGGED = False
_RECOVERY_PURGE_PENDING = False


def _build_redis_url() -> Optional[str]:
    cfg = getattr(config, "config", {})
    if isinstance(cfg, dict):
        url = cfg.get("redis_url")
        if url:
            return str(url)

    env_url = os.getenv("REDIS_URL")
    if env_url:
        return env_url

    host = os.getenv("REDIS_HOST")
    if host:
        port = int(os.getenv("REDIS_PORT", "6379"))
        db = int(os.getenv("REDIS_DB", "0"))
        password = os.getenv("REDIS_PASSWORD")
        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        return f"redis://{host}:{port}/{db}"
    return None


def _on_redis_runtime_error(action: str, ex: Exception) -> None:
    global _CACHE_DEGRADED
    global _CACHE_FAIL_OPEN_UNTIL
    global _CACHE_DOWN_LOGGED
    global _RECOVERY_PURGE_PENDING

    now = time.monotonic()
    with _STATE_LOCK:
        _CACHE_DEGRADED = True
        _CACHE_FAIL_OPEN_UNTIL = now + _CIRCUIT_BREAKER_SECONDS
        _RECOVERY_PURGE_PENDING = True
        should_log = not _CACHE_DOWN_LOGGED
        if should_log:
            _CACHE_DOWN_LOGGED = True
    if should_log:
        logging.error(
            "Redis cache %s failed; entering fail-open mode for %.0f seconds.",
            action,
            _CIRCUIT_BREAKER_SECONDS,
            exc_info=True,
        )


def _recover_if_needed() -> bool:
    global _CACHE_DEGRADED
    global _CACHE_FAIL_OPEN_UNTIL
    global _CACHE_DOWN_LOGGED
    global _RECOVERY_PURGE_PENDING

    now = time.monotonic()
    with _STATE_LOCK:
        degraded = _CACHE_DEGRADED
        fail_open_until = _CACHE_FAIL_OPEN_UNTIL
        recovery_purge_pending = _RECOVERY_PURGE_PENDING
        if not degraded:
            return True
        if now < fail_open_until:
            return False
        # Keep other threads in fail-open mode while this thread probes Redis.
        _CACHE_FAIL_OPEN_UNTIL = now + _CIRCUIT_BREAKER_SECONDS

    try:
        _REDIS_CLIENT.ping()
        if recovery_purge_pending:
            namespace_pattern = f"{_REDIS_NAMESPACE_KEY}:*"
            for namespace_key in _REDIS_CLIENT.scan_iter(
                match=namespace_pattern
            ):
                _REDIS_CLIENT.incr(namespace_key)
    except redis.exceptions.RedisError as ex:
        _on_redis_runtime_error("recovery", ex)
        return False

    with _STATE_LOCK:
        was_logged_down = _CACHE_DOWN_LOGGED
        _CACHE_DEGRADED = False
        _CACHE_FAIL_OPEN_UNTIL = 0.0
        _CACHE_DOWN_LOGGED = False
        _RECOVERY_PURGE_PENDING = False
    if was_logged_down:
        logging.info(
            "Redis cache recovered; fail-open mode disabled and scopes purged."
        )
    return True


def _init_redis_client() -> redis.Redis:
    url = _build_redis_url()
    if not url:
        raise RuntimeError(
            "Redis URL is not configured. Set redis_url, REDIS_URL, or "
            "REDIS_HOST/REDIS_PORT/REDIS_DB."
        )
    client = redis.Redis.from_url(
        url,
        decode_responses=False,
        socket_connect_timeout=0.5,
        socket_timeout=0.5,
    )
    client.ping()
    return client


def _encode(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, datetime):
        return {
            _TYPE_KEY: "datetime",
            "value": value.isoformat(),
        }
    if isinstance(value, bytes):
        return {
            _TYPE_KEY: "bytes",
            "value": base64.b64encode(value).decode("ascii"),
        }
    if isinstance(value, tuple):
        return {
            _TYPE_KEY: "tuple",
            "items": [_encode(item) for item in value],
        }
    if isinstance(value, list):
        return [_encode(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _encode(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset)):
        normalized = [_encode(item) for item in value]
        normalized.sort(key=lambda item: orjson.dumps(item).decode("utf-8"))
        return {_TYPE_KEY: "set", "items": normalized}
    raise TypeError(f"Unsupported cache value type: {type(value).__name__}")


def _decode(value: Any) -> Any:
    if isinstance(value, list):
        return [_decode(item) for item in value]
    if isinstance(value, dict):
        value_type = value.get(_TYPE_KEY)
        if value_type == "datetime":
            return datetime.fromisoformat(value["value"])
        if value_type == "bytes":
            return base64.b64decode(value["value"].encode("ascii"))
        if value_type == "tuple":
            return tuple(_decode(item) for item in value["items"])
        if value_type == "set":
            return set(_decode(item) for item in value["items"])
        return {key: _decode(item) for key, item in value.items()}
    return value


def _serialize(value: Any) -> bytes:
    return orjson.dumps(_encode(value))


def _deserialize(payload: bytes) -> Any:
    return _decode(orjson.loads(payload))


def _serialize_key(key: object) -> str:
    digest = hashlib.sha256(_serialize(key))
    return digest.hexdigest()


def _normalize_scope(scope: Optional[str]) -> str:
    if not scope:
        return SCOPE_GLOBAL
    return str(scope)


def _redis_namespace_key(scope: Optional[str]) -> str:
    normalized_scope = _normalize_scope(scope)
    return f"{_REDIS_NAMESPACE_KEY}:{normalized_scope}"


def _get_namespace(scope: Optional[str]) -> str:
    namespace_key = _redis_namespace_key(scope)
    namespace = _REDIS_CLIENT.get(namespace_key)
    if namespace is None:
        _REDIS_CLIENT.set(namespace_key, "1", nx=True)
        namespace = _REDIS_CLIENT.get(namespace_key)

    if namespace is None:
        return "1"
    if isinstance(namespace, bytes):
        return namespace.decode("utf-8")
    return str(namespace)


def _redis_key(key: object, scope: Optional[str]) -> str:
    normalized_scope = _normalize_scope(scope)
    namespace = _get_namespace(normalized_scope)
    key_hash = _serialize_key(key)
    return f"{_REDIS_KEY_PREFIX}:{normalized_scope}:{namespace}:{key_hash}"


def _effective_ttl(ttl_seconds: Optional[int]) -> int:
    if ttl_seconds is None:
        return _DEFAULT_TTL_SECONDS
    return int(ttl_seconds)


_REDIS_CLIENT = _init_redis_client()


def purge(scope: Optional[str] = None) -> None:
    if not _recover_if_needed():
        return
    namespace_key = _redis_namespace_key(scope)
    try:
        _REDIS_CLIENT.incr(namespace_key)
    except redis.exceptions.RedisError as ex:
        _on_redis_runtime_error("purge", ex)


def has(key: object, scope: Optional[str] = None) -> bool:
    if not _recover_if_needed():
        return False
    try:
        return bool(_REDIS_CLIENT.exists(_redis_key(key, scope)))
    except redis.exceptions.RedisError as ex:
        _on_redis_runtime_error("exists", ex)
        return False


def get(key: object, scope: Optional[str] = None) -> Any:
    if not _recover_if_needed():
        return None
    try:
        payload = _REDIS_CLIENT.get(_redis_key(key, scope))
    except redis.exceptions.RedisError as ex:
        _on_redis_runtime_error("get", ex)
        return None

    if payload is None:
        return None
    return _deserialize(payload)


def remove(key: object, scope: Optional[str] = None) -> None:
    if not _recover_if_needed():
        return
    try:
        _REDIS_CLIENT.delete(_redis_key(key, scope))
    except redis.exceptions.RedisError as ex:
        _on_redis_runtime_error("delete", ex)


def put(
    key: object,
    value: Any,
    ttl_seconds: Optional[int] = None,
    scope: Optional[str] = None,
) -> None:
    if not _recover_if_needed():
        return
    ttl = _effective_ttl(ttl_seconds)
    if ttl <= 0:
        remove(key, scope=scope)
        return
    payload = _serialize(value)
    try:
        _REDIS_CLIENT.setex(_redis_key(key, scope), ttl, payload)
    except redis.exceptions.RedisError as ex:
        _on_redis_runtime_error("setex", ex)
