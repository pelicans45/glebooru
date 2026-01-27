#!/usr/bin/env python3
"""
Benchmark tag exclusion performance for gallery and tag searches.

Scenarios:
- Gallery with only an exclusion tag (~10% usage).
- Tag filter + exclusion tag.
"""
from __future__ import annotations

import argparse
import json
import statistics
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


def _pick_tags(
    base_url: str,
    timeout: float,
    force_exclude: str,
    force_include: str,
) -> Tuple[Optional[dict], Optional[dict], Optional[int]]:
    status, _elapsed, data, _err = _request_json(
        _build_url(base_url, "/posts", {"limit": "1"}), timeout
    )
    total_posts = data.get("total") if status == 200 and data else None

    tag_params = {
        "query": "sort:usages",
        "limit": "5000",
        "fields": "names,usages",
    }
    status, _elapsed, tag_data, _err = _request_json(
        _build_url(base_url, "/tags", tag_params), timeout
    )
    if status != 200 or not tag_data:
        return None, None, total_posts
    tags = tag_data.get("results", [])
    if not tags:
        return None, None, total_posts

    target = None
    if isinstance(total_posts, int) and total_posts > 0:
        target = int(round(total_posts * 0.10))

    exclude = None
    include = None

    if force_exclude:
        exclude = next(
            (tag for tag in tags if _name_of(tag) == force_exclude),
            None,
        )
    if force_include:
        include = next(
            (tag for tag in tags if _name_of(tag) == force_include),
            None,
        )

    if exclude is None:
        if target is not None:
            exclude = min(
                tags, key=lambda t: abs((t.get("usages") or 0) - target)
            )
        if not exclude:
            exclude = tags[0]

    if include is None:
        for tag in tags:
            if tag is not exclude:
                include = tag
                break
        if not include:
            include = exclude
    return exclude, include, total_posts


def _name_of(tag: dict) -> str:
    names = tag.get("names") or []
    if names:
        return names[0]
    return ""


def _markdown_report(
    title: str,
    base_url: str,
    exclude_tag: dict,
    include_tag: dict,
    total_posts: Optional[int],
    results: List[dict],
) -> str:
    lines: List[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"Base URL: `{base_url}`")
    if total_posts is not None:
        lines.append(f"Total posts (from API): `{total_posts}`")
    lines.append(f"Run time: `{time.strftime('%Y-%m-%d %H:%M:%S')}`")
    lines.append("")
    lines.append("## Selected tags")
    lines.append("")
    lines.append(
        f"- Exclusion tag: `{_name_of(exclude_tag)}` (usages={exclude_tag.get('usages')})"
    )
    lines.append(
        f"- Inclusion tag: `{_name_of(include_tag)}` (usages={include_tag.get('usages')})"
    )
    lines.append("")
    lines.append("## Benchmarks")
    lines.append("")
    for result in results:
        lines.append(f"### {result['name']}")
        lines.append("")
        lines.append(f"- URL: `{result['url']}`")
        lines.append(f"- Iterations: `{result['iterations']}`")
        lines.append(f"- Concurrency: `{result['concurrency']}`")
        timings = result["timings"]
        lines.append(
            "- Latency (seconds): "
            f"p50={timings['p50']:.4f}, "
            f"p95={timings['p95']:.4f}, "
            f"p99={timings['p99']:.4f}, "
            f"avg={timings['avg']:.4f}"
        )
        status_counts = ", ".join(
            f"{code}:{count}"
            for code, count in sorted(result["status_counts"].items())
        )
        lines.append(f"- Status counts: `{status_counts}`")
        if result["error_samples"]:
            lines.append("- Error samples:")
            for err in result["error_samples"]:
                lines.append(f"  - `{err}`")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark tag exclusion performance"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:4000/api",
        help="Base API URL (default: http://localhost:4000/api)",
    )
    parser.add_argument("--iterations", type=int, default=50)
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--title",
        default="Tag Exclusion Benchmark",
        help="Markdown report title",
    )
    parser.add_argument(
        "--exclude-tag",
        default="",
        help="Force exclusion tag name (e.g., tag_00000).",
    )
    parser.add_argument(
        "--include-tag",
        default="",
        help="Force inclusion tag name (e.g., tag_00001).",
    )
    args = parser.parse_args()

    exclude_tag, include_tag, total_posts = _pick_tags(
        args.base_url, args.timeout, args.exclude_tag, args.include_tag
    )
    if not exclude_tag or not include_tag:
        raise SystemExit("Failed to select tags; ensure /tags endpoint works.")

    exclude_name = _name_of(exclude_tag)
    include_name = _name_of(include_tag)

    gallery_fields = (
        "id,thumbnailUrl,contentUrl,creationTime,type,safety,score,"
        "favoriteCount,commentCount,tagsBasic,version"
    )

    results: List[dict] = []
    q_exclude = f"-tag:{exclude_name}"
    q_include_exclude = f"tag:{include_name} -tag:{exclude_name}"

    results.append(
        _benchmark_endpoint(
            f"Gallery (exclude tag {exclude_name})",
            _build_url(
                args.base_url,
                "/posts",
                {"limit": "42", "fields": gallery_fields, "query": q_exclude},
            ),
            args.iterations,
            args.concurrency,
            args.timeout,
            args.warmup,
        )
    )
    results.append(
        _benchmark_endpoint(
            f"Gallery (tag {include_name} with exclude {exclude_name})",
            _build_url(
                args.base_url,
                "/posts",
                {
                    "limit": "42",
                    "fields": gallery_fields,
                    "query": q_include_exclude,
                },
            ),
            args.iterations,
            args.concurrency,
            args.timeout,
            args.warmup,
        )
    )

    report = _markdown_report(
        args.title,
        args.base_url,
        exclude_tag,
        include_tag,
        total_posts,
        results,
    )
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
