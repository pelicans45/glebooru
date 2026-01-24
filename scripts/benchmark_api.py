#!/usr/bin/env python3
"""
HTTP benchmark for Szurubooru API (gallery + post view).

Focus:
- Gallery listing latency
- Individual post latency (no tags / few tags / many tags)

Outputs a Markdown report.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple


def _request_json(url: str, timeout: float) -> Tuple[int, float, Optional[dict], Optional[str]]:
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            elapsed = time.perf_counter() - start
            status = resp.status
        try:
            data = json.loads(body.decode("utf-8"))
        except Exception:
            data = None
        return status, elapsed, data, None
    except urllib.error.HTTPError as err:
        elapsed = time.perf_counter() - start
        try:
            body = err.read().decode("utf-8")
        except Exception:
            body = None
        return err.code, elapsed, None, body
    except Exception as err:
        elapsed = time.perf_counter() - start
        return 0, elapsed, None, str(err)


def _format_percentiles(samples: List[float]) -> Dict[str, float]:
    if not samples:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "avg": 0.0}
    ordered = sorted(samples)

    def pct(p: float) -> float:
        if not ordered:
            return 0.0
        k = int(round((p / 100.0) * (len(ordered) - 1)))
        return ordered[max(0, min(len(ordered) - 1, k))]

    return {
        "p50": pct(50),
        "p95": pct(95),
        "p99": pct(99),
        "avg": statistics.mean(samples),
    }


def _benchmark_endpoint(
    name: str,
    url: str,
    iterations: int,
    concurrency: int,
    timeout: float,
    warmup: int,
) -> dict:
    # Warmup (serial)
    for _ in range(warmup):
        _request_json(url, timeout)

    timings: List[float] = []
    status_counts: Dict[int, int] = {}
    errors: List[str] = []

    def task() -> Tuple[int, float, Optional[str]]:
        status, elapsed, _data, err = _request_json(url, timeout)
        return status, elapsed, err

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(task) for _ in range(iterations)]
        for fut in as_completed(futures):
            status, elapsed, err = fut.result()
            timings.append(elapsed)
            status_counts[status] = status_counts.get(status, 0) + 1
            if err:
                errors.append(err)

    stats = _format_percentiles(timings)
    return {
        "name": name,
        "url": url,
        "iterations": iterations,
        "concurrency": concurrency,
        "status_counts": status_counts,
        "timings": stats,
        "error_samples": errors[:5],
    }


def _build_url(base: str, path: str, params: Optional[Dict[str, str]] = None) -> str:
    if base.endswith("/"):
        base = base[:-1]
    if not path.startswith("/"):
        path = "/" + path
    url = base + path
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    return url


def _find_post_samples(base_url: str, timeout: float, target: int = 5) -> dict:
    categories = {"no_tags": [], "few_tags": [], "many_tags": []}
    offset = 0
    page_size = 200
    max_offset = 2000

    while offset <= max_offset:
        url = _build_url(
            base_url,
            "/posts",
            {
                "offset": str(offset),
                "limit": str(page_size),
                "fields": "id,tags",
            },
        )
        status, _elapsed, data, _err = _request_json(url, timeout)
        if status != 200 or not data or "results" not in data:
            break
        results = data.get("results", [])
        if not results:
            break

        for post in results:
            tag_count = len(post.get("tags", []))
            if tag_count == 0 and len(categories["no_tags"]) < target:
                categories["no_tags"].append(post)
            elif 1 <= tag_count <= 3 and len(categories["few_tags"]) < target:
                categories["few_tags"].append(post)
            elif tag_count >= 12 and len(categories["many_tags"]) < target:
                categories["many_tags"].append(post)

        if all(len(categories[k]) >= target for k in categories):
            break

        if len(results) < page_size:
            break

        offset += page_size

    return categories


def _pick_common_tag(sample: dict) -> Optional[str]:
    for bucket in ("many_tags", "few_tags", "no_tags"):
        for post in sample.get(bucket, []):
            tags = post.get("tags", [])
            if tags:
                names = tags[0].get("names") or []
                if names:
                    return names[0]
    return None


def _markdown_report(
    title: str,
    base_url: str,
    samples: dict,
    results: List[dict],
    total_posts: Optional[int],
    warnings: List[str],
) -> str:
    lines: List[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"Base URL: `{base_url}`")
    if total_posts is not None:
        lines.append(f"Total posts (from API): `{total_posts}`")
    lines.append(f"Run time: `{time.strftime('%Y-%m-%d %H:%M:%S')}`")
    lines.append("")

    if warnings:
        lines.append("## Warnings")
        lines.append("")
        for warn in warnings:
            lines.append(f"- {warn}")
        lines.append("")

    def _fmt_samples(name: str) -> str:
        posts = samples.get(name, [])
        if not posts:
            return "(none found)"
        return ", ".join(str(p["id"]) for p in posts)

    lines.append("## Sampled Post IDs")
    lines.append("")
    lines.append(f"- No tags: {_fmt_samples('no_tags')}")
    lines.append(f"- Few tags (1-3): {_fmt_samples('few_tags')}")
    lines.append(f"- Many tags (>=12): {_fmt_samples('many_tags')}")
    lines.append("")

    lines.append("## Benchmarks")
    lines.append("")
    for item in results:
        timings = item["timings"]
        status_counts = ", ".join(
            f"{k}:{v}" for k, v in sorted(item["status_counts"].items())
        )
        lines.append(f"### {item['name']}")
        lines.append("")
        lines.append(f"- URL: `{item['url']}`")
        lines.append(f"- Iterations: `{item['iterations']}`")
        lines.append(f"- Concurrency: `{item['concurrency']}`")
        lines.append(
            "- Latency (seconds): "
            f"p50={timings['p50']:.4f}, "
            f"p95={timings['p95']:.4f}, "
            f"p99={timings['p99']:.4f}, "
            f"avg={timings['avg']:.4f}"
        )
        lines.append(f"- Status counts: `{status_counts}`")
        if item["error_samples"]:
            lines.append("- Error samples:")
            for err in item["error_samples"]:
                lines.append(f"  - `{err}`")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark Szurubooru API")
    parser.add_argument(
        "--base-url",
        default="http://localhost:4000/api",
        help="Base API URL (default: http://localhost:4000/api)",
    )
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--title",
        default="API Benchmark Results",
        help="Markdown report title",
    )
    args = parser.parse_args()

    warnings: List[str] = []

    # Preflight
    status, _elapsed, data, err = _request_json(
        _build_url(args.base_url, "/posts", {"limit": "1"}), args.timeout
    )
    if status != 200:
        print(f"Preflight failed: status={status} err={err}", file=sys.stderr)
        return 1

    total_posts = None
    if data and "total" in data:
        total_posts = data["total"]

    samples = _find_post_samples(args.base_url, args.timeout)
    common_tag = _pick_common_tag(samples)

    # Determine a large offset for pagination test
    large_offset = 0
    if isinstance(total_posts, int) and total_posts > 100:
        large_offset = min(20000, total_posts - 50)

    # Field sets
    gallery_fields_client = (
        "id,thumbnailUrl,contentUrl,creationTime,type,safety,score,"
        "favoriteCount,commentCount,tagsBasic,version"
    )
    gallery_fields_safe = (
        "id,thumbnailUrl,contentUrl,creationTime,type,safety,score,"
        "favoriteCount,commentCount,version,tags"
    )

    post_fields_client = (
        "id,version,creationTime,lastEditTime,safety,source,type,mimeType,"
        "checksum,checksumMD5,fileSize,canvasWidth,canvasHeight,duration,"
        "contentUrl,thumbnailUrl,flags,tags,relations,user,score,ownScore,"
        "ownFavorite,favoriteCount,commentCount,notes,comments"
    )
    post_fields_safe = (
        "id,version,creationTime,lastEditTime,safety,source,type,mimeType,"
        "checksum,checksumMD5,fileSize,canvasWidth,canvasHeight,"
        "contentUrl,thumbnailUrl,flags,tags,relations,user,score,ownScore,"
        "ownFavorite,favoriteCount,commentCount,notes,comments"
    )

    # Validate client fieldsets
    gallery_check_url = _build_url(
        args.base_url,
        "/posts",
        {"limit": "1", "fields": gallery_fields_client},
    )
    status, _elapsed, _data, _err = _request_json(gallery_check_url, args.timeout)
    if status != 200:
        warnings.append(
            "Gallery client fieldset (tagsBasic) returned non-200; using safe fieldset with tags."
        )

    post_check_url = _build_url(
        args.base_url,
        f"/post/{samples.get('few_tags', [{}])[0].get('id', 1)}",
        {"fields": post_fields_client},
    )
    status, _elapsed, _data, _err = _request_json(post_check_url, args.timeout)
    if status != 200:
        warnings.append(
            "Post client fieldset (includes duration) returned non-200; using safe fieldset without duration."
        )

    results: List[dict] = []

    # Gallery listing baseline
    gallery_fields = gallery_fields_safe if warnings else gallery_fields_client
    results.append(
        _benchmark_endpoint(
            "Gallery (default query)",
            _build_url(
                args.base_url,
                "/posts",
                {"limit": "42", "fields": gallery_fields, "query": ""},
            ),
            args.iterations,
            args.concurrency,
            args.timeout,
            args.warmup,
        )
    )

    # Gallery with tag filter
    if common_tag:
        results.append(
            _benchmark_endpoint(
                f"Gallery (tag filter: {common_tag})",
                _build_url(
                    args.base_url,
                    "/posts",
                    {
                        "limit": "42",
                        "fields": gallery_fields,
                        "query": common_tag,
                    },
                ),
                args.iterations,
                args.concurrency,
                args.timeout,
                args.warmup,
            )
        )

    # Gallery with sort:tag-count
    results.append(
        _benchmark_endpoint(
            "Gallery (sort:tag-count)",
            _build_url(
                args.base_url,
                "/posts",
                {
                    "limit": "42",
                    "fields": gallery_fields,
                    "query": "sort:tag-count",
                },
            ),
            args.iterations,
            args.concurrency,
            args.timeout,
            args.warmup,
        )
    )

    # Gallery with large offset
    if large_offset:
        results.append(
            _benchmark_endpoint(
                f"Gallery (large offset {large_offset})",
                _build_url(
                    args.base_url,
                    "/posts",
                    {
                        "limit": "42",
                        "fields": gallery_fields,
                        "query": "",
                        "offset": str(large_offset),
                    },
                ),
                args.iterations,
                args.concurrency,
                args.timeout,
                args.warmup,
            )
        )

    # Individual post loads
    post_fields = post_fields_safe if warnings else post_fields_client

    def add_post_benchmarks(label: str, posts: List[dict]):
        for post in posts:
            post_id = post.get("id")
            if not post_id:
                continue
            results.append(
                _benchmark_endpoint(
                    f"Post view ({label}) id={post_id}",
                    _build_url(
                        args.base_url,
                        f"/post/{post_id}",
                        {"fields": post_fields},
                    ),
                    args.iterations,
                    args.concurrency,
                    args.timeout,
                    args.warmup,
                )
            )

    add_post_benchmarks("no tags", samples.get("no_tags", []))
    add_post_benchmarks("few tags", samples.get("few_tags", []))
    add_post_benchmarks("many tags", samples.get("many_tags", []))

    report = _markdown_report(
        args.title,
        args.base_url,
        samples,
        results,
        total_posts,
        warnings,
    )
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(report)

    print(f"Wrote benchmark report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
