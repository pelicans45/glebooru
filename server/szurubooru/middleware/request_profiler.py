"""Optional request profiler for /posts and /post/<id>."""

import cProfile
import io
import logging
import os
import re
import time
from pathlib import Path

from szurubooru import rest
from szurubooru.rest import middleware

try:
    from pyinstrument import Profiler  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Profiler = None

_POSTS_PATHS = {"/posts", "/api/posts"}
_POST_PATH_RE = re.compile(r"^/(?:api/)?post/\d+/?$")
_PROFILE_ENV = os.getenv("GLEBOORU_PROFILE_REQUESTS", "").lower() in {
    "1",
    "true",
    "yes",
}
_PROFILE_TOOL = os.getenv("GLEBOORU_PROFILE_TOOL", "pyinstrument")
_PROFILE_DIR = os.getenv("GLEBOORU_PROFILE_DIR", "/data/perf-profiles")

_prof_logger = logging.getLogger("glebooru.profile")
if not _prof_logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
    )
    _prof_logger.addHandler(handler)
    _prof_logger.setLevel(logging.INFO)
    _prof_logger.propagate = False


def _should_profile(ctx: rest.Context) -> bool:
    if ctx.url.rstrip("/") in _POSTS_PATHS:
        return True
    return _POST_PATH_RE.match(ctx.url) is not None


def _is_enabled(ctx: rest.Context) -> bool:
    if not _should_profile(ctx):
        return False
    if _PROFILE_ENV:
        return True
    return ctx.has_param("_profile")


def _profile_label(ctx: rest.Context) -> str:
    path = ctx.url.strip("/") or "root"
    return path.replace("/", "_")


@middleware.pre_hook
def _start_profile(ctx: rest.Context) -> None:
    if not _is_enabled(ctx):
        return
    ctx._profile_start = time.perf_counter()
    tool = _PROFILE_TOOL
    if tool == "pyinstrument" and Profiler is not None:
        profiler = Profiler(interval=0.001, async_mode="disabled")
        profiler.start()
        ctx._profile_state = ("pyinstrument", profiler)
    else:
        profiler = cProfile.Profile()
        profiler.enable()
        ctx._profile_state = ("cprofile", profiler)


@middleware.post_hook
def _end_profile(ctx: rest.Context) -> None:
    if not hasattr(ctx, "_profile_state"):
        return
    tool, profiler = ctx._profile_state
    elapsed = time.perf_counter() - getattr(ctx, "_profile_start", 0.0)

    Path(_PROFILE_DIR).mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    label = _profile_label(ctx)

    if tool == "pyinstrument":
        profiler.stop()
        html_path = os.path.join(_PROFILE_DIR, f"{label}-{stamp}.html")
        text_path = os.path.join(_PROFILE_DIR, f"{label}-{stamp}.txt")
        with open(html_path, "w", encoding="utf-8") as handle:
            handle.write(profiler.output_html())
        with open(text_path, "w", encoding="utf-8") as handle:
            handle.write(profiler.output_text(unicode=True, color=False))
        _prof_logger.info(
            "profiled %s %s tool=pyinstrument total=%.4fs html=%s",
            ctx.method,
            ctx.url,
            elapsed,
            html_path,
        )
        return

    profiler.disable()
    raw_path = os.path.join(_PROFILE_DIR, f"{label}-{stamp}.prof")
    profiler.dump_stats(raw_path)
    stats = io.StringIO()
    import pstats

    pstats.Stats(raw_path, stream=stats).strip_dirs().sort_stats("cumtime").print_stats(40)
    text_path = os.path.join(_PROFILE_DIR, f"{label}-{stamp}.txt")
    with open(text_path, "w", encoding="utf-8") as handle:
        handle.write(stats.getvalue())
    _prof_logger.info(
        "profiled %s %s tool=cprofile total=%.4fs stats=%s",
        ctx.method,
        ctx.url,
        elapsed,
        raw_path,
    )
