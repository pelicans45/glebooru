"""Request timing and query profiling for posts endpoints."""

import contextvars
import logging
import re
import time
from dataclasses import dataclass

import sqlalchemy as sa

from szurubooru import db, rest
from szurubooru.rest import middleware

_POSTS_PATHS = {"/posts", "/api/posts"}
_POST_PATH_RE = re.compile(r"^/(?:api/)?post/\d+/?$")
_perf_logger = logging.getLogger("glebooru.perf")
if not _perf_logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
    )
    _perf_logger.addHandler(handler)
    _perf_logger.setLevel(logging.INFO)
    _perf_logger.propagate = False


@dataclass
class _RequestStats:
    query_count: int = 0
    query_time: float = 0.0


_request_stats = contextvars.ContextVar("request_stats", default=None)


@sa.event.listens_for(db.get_engine(), "before_cursor_execute")
def _before_cursor_execute(
    conn, cursor, statement, parameters, context, executemany
) -> None:
    stats = _request_stats.get()
    if stats is None:
        return
    conn.info.setdefault("_query_start_time", []).append(time.perf_counter())


@sa.event.listens_for(db.get_engine(), "after_cursor_execute")
def _after_cursor_execute(
    conn, cursor, statement, parameters, context, executemany
) -> None:
    stats = _request_stats.get()
    if stats is None:
        return
    start = conn.info.get("_query_start_time", []).pop()
    stats.query_count += 1
    stats.query_time += time.perf_counter() - start


def _should_profile(ctx: rest.Context) -> bool:
    if ctx.url.rstrip("/") in _POSTS_PATHS:
        return True
    return _POST_PATH_RE.match(ctx.url) is not None


@middleware.pre_hook
def _start_timing(ctx: rest.Context) -> None:
    if not _should_profile(ctx):
        return
    ctx._perf_start = time.perf_counter()
    stats = _RequestStats()
    ctx._perf_token = _request_stats.set(stats)
    ctx._perf_stats = stats


@middleware.post_hook
def _end_timing(ctx: rest.Context) -> None:
    if not hasattr(ctx, "_perf_start"):
        return
    total = time.perf_counter() - ctx._perf_start
    stats = getattr(ctx, "_perf_stats", None)
    token = getattr(ctx, "_perf_token", None)
    if token is not None:
        _request_stats.reset(token)
    if stats is None:
        return
    _perf_logger.info(
        "perf %s %s user=%s total=%.4fs db=%.4fs queries=%d",
        ctx.method,
        ctx.url,
        ctx.user.name,
        total,
        stats.query_time,
        stats.query_count,
    )
