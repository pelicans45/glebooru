#!/usr/bin/env python3
"""
Benchmark small uploads and tag updates via the Szurubooru API.

Measures:
- Upload with 0 tags
- Upload with few tags
- Upload with many tags
- Update tags on existing posts (0->few, few->many, many->few)
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zlib
import struct
from typing import Dict, List, Optional, Tuple


def _png_bytes(width: int, height: int, color: Tuple[int, int, int]) -> bytes:
    r, g, b = color
    row = bytes([0] + [r, g, b] * width)
    raw = row * height
    compressed = zlib.compress(raw)

    def _chunk(tag: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    header = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        header
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", compressed)
        + _chunk(b"IEND", b"")
    )


def _request(
    url: str,
    data: Optional[bytes],
    headers: Dict[str, str],
    timeout: float,
    method: str,
) -> Tuple[int, float, Optional[dict], Optional[str]]:
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            elapsed = time.perf_counter() - start
            status = resp.status
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            payload = None
        return status, elapsed, payload, None
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


def _encode_multipart(
    fields: Dict[str, str],
    files: List[Tuple[str, str, str, bytes]],
) -> Tuple[bytes, str]:
    boundary = f"----szuru-bench-{uuid.uuid4().hex}"
    parts: List[bytes] = []

    for name, value in fields.items():
        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        parts.append(
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(
                "utf-8"
            )
        )
        parts.append(value.encode("utf-8"))
        parts.append(b"\r\n")

    for name, filename, content_type, data in files:
        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        parts.append(
            (
                f'Content-Disposition: form-data; name="{name}"; '
                f'filename="{filename}"\r\n'
            ).encode("utf-8")
        )
        parts.append(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
        parts.append(data)
        parts.append(b"\r\n")

    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)
    return body, f"multipart/form-data; boundary={boundary}"


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


def _upload_post(
    base_url: str,
    tags: List[str],
    timeout: float,
    original_host: str,
    content: bytes,
) -> Tuple[int, float, Optional[dict], Optional[str]]:
    metadata = {
        "anonymous": True,
        "safety": "safe",
        "tags": tags,
    }
    fields = {
        "metadata": json.dumps(metadata),
    }
    body, content_type = _encode_multipart(
        fields,
        [
            ("content", "bench.png", "image/png", content),
        ],
    )
    url = base_url.rstrip("/") + "/posts"
    headers = {
        "Content-Type": content_type,
        "Accept": "application/json",
    }
    if original_host:
        headers["Host"] = original_host
    return _request(
        url,
        body,
        headers,
        timeout,
        "POST",
    )


def _update_post(
    base_url: str,
    post_id: int,
    version: int,
    tags: List[str],
    timeout: float,
) -> Tuple[int, float, Optional[dict], Optional[str]]:
    query = urllib.parse.urlencode(
        {
            "tags": ",".join(tags) if tags else "",
            "version": str(version),
        }
    )
    url = base_url.rstrip("/") + f"/post/{post_id}?{query}"
    return _request(
        url,
        None,
        {"Accept": "application/json"},
        timeout,
        "PUT",
    )


def _pick_tags(rng: random.Random, pool_size: int, count: int) -> List[str]:
    if count <= 0:
        return []
    indexes = rng.sample(range(pool_size), count)
    return [f"tag_{idx:05d}" for idx in indexes]


def _run_scenario(
    name: str,
    fn,
    iterations: int,
    warmup: int,
) -> Tuple[dict, List[dict]]:
    for _ in range(warmup):
        fn()

    timings: List[float] = []
    status_counts: Dict[int, int] = {}
    errors: List[str] = []
    payloads: List[dict] = []

    for _ in range(iterations):
        status, elapsed, data, err = fn()
        timings.append(elapsed)
        status_counts[status] = status_counts.get(status, 0) + 1
        if err:
            errors.append(err)
        if isinstance(data, dict):
            payloads.append(data)

    stats = _format_percentiles(timings)
    result = {
        "name": name,
        "iterations": iterations,
        "status_counts": status_counts,
        "timings": stats,
        "error_samples": errors[:5],
    }
    return result, payloads


def _markdown_report(
    title: str,
    base_url: str,
    results: List[dict],
    warnings: List[str],
) -> str:
    lines: List[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"Base URL: `{base_url}`")
    lines.append(f"Run time: `{time.strftime('%Y-%m-%d %H:%M:%S')}`")
    lines.append("")

    if warnings:
        lines.append("## Warnings")
        lines.append("")
        for warn in warnings:
            lines.append(f"- {warn}")
        lines.append("")

    lines.append("## Results")
    lines.append("")
    lines.append("| Benchmark | p50 | p95 | p99 | avg | status |")
    lines.append("|---|---:|---:|---:|---:|---|")
    for result in results:
        status = ", ".join(
            f"{code}:{count}"
            for code, count in sorted(result["status_counts"].items())
        )
        timings = result["timings"]
        lines.append(
            "| {name} | {p50:.4f} | {p95:.4f} | {p99:.4f} | {avg:.4f} | {status} |".format(
                name=result["name"],
                p50=timings["p50"],
                p95=timings["p95"],
                p99=timings["p99"],
                avg=timings["avg"],
                status=status or "-",
            )
        )

    for result in results:
        errors = result.get("error_samples") or []
        if errors:
            lines.append("")
            lines.append(f"### Errors: {result['name']}")
            lines.append("")
            for err in errors:
                lines.append(f"- {err}")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark small uploads and tag updates."
    )
    parser.add_argument(
        "--base-url", default="http://localhost:4000/api"
    )
    parser.add_argument("--iterations", type=int, default=15)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--tag-pool", type=int, default=2000)
    parser.add_argument("--few-tags", type=int, default=5)
    parser.add_argument("--many-tags", type=int, default=20)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--original-host", default="booru")
    parser.add_argument(
        "--output",
        default="doc/benchmark-results-upload-benchmark.md",
    )
    parser.add_argument(
        "--title",
        default="Upload/Tag Update Benchmark",
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    few_tags = args.few_tags
    many_tags = args.many_tags

    results: List[dict] = []
    warnings: List[str] = []

    created_zero: List[Tuple[int, int]] = []
    created_few: List[Tuple[int, int]] = []
    created_many: List[Tuple[int, int]] = []

    upload_counter = 0
    content_rng = random.Random(args.seed ^ int(time.time()))

    def _next_content() -> bytes:
        nonlocal upload_counter
        upload_counter += 1
        color = (
            content_rng.randrange(256),
            content_rng.randrange(256),
            content_rng.randrange(256),
        )
        return _png_bytes(64, 64, color)

    def _upload_zero():
        return _upload_post(
            args.base_url,
            [],
            args.timeout,
            args.original_host,
            _next_content(),
        )

    def _upload_few():
        tags = _pick_tags(rng, args.tag_pool, few_tags)
        return _upload_post(
            args.base_url,
            tags,
            args.timeout,
            args.original_host,
            _next_content(),
        )

    def _upload_many():
        tags = _pick_tags(rng, args.tag_pool, many_tags)
        return _upload_post(
            args.base_url,
            tags,
            args.timeout,
            args.original_host,
            _next_content(),
        )

    res, payloads = _run_scenario(
        f"Upload (0 tags)", _upload_zero, args.iterations, args.warmup
    )
    results.append(res)
    for payload in payloads:
        if "id" in payload and "version" in payload:
            created_zero.append((payload["id"], payload["version"]))

    res, payloads = _run_scenario(
        f"Upload ({few_tags} tags)", _upload_few, args.iterations, args.warmup
    )
    results.append(res)
    for payload in payloads:
        if "id" in payload and "version" in payload:
            created_few.append((payload["id"], payload["version"]))

    res, payloads = _run_scenario(
        f"Upload ({many_tags} tags)", _upload_many, args.iterations, args.warmup
    )
    results.append(res)
    for payload in payloads:
        if "id" in payload and "version" in payload:
            created_many.append((payload["id"], payload["version"]))

    if not created_zero:
        warnings.append("No successful uploads for 0-tag scenario.")
    if not created_few:
        warnings.append("No successful uploads for few-tag scenario.")
    if not created_many:
        warnings.append("No successful uploads for many-tag scenario.")

    update_tags_few = _pick_tags(rng, args.tag_pool, few_tags)
    update_tags_many = _pick_tags(rng, args.tag_pool, many_tags)

    def _update_from_zero():
        post_id, version = created_zero.pop(0)
        return _update_post(args.base_url, post_id, version, update_tags_few, args.timeout)

    def _update_from_few():
        post_id, version = created_few.pop(0)
        return _update_post(args.base_url, post_id, version, update_tags_many, args.timeout)

    def _update_from_many():
        post_id, version = created_many.pop(0)
        return _update_post(args.base_url, post_id, version, update_tags_few, args.timeout)

    if created_zero:
        res, _payloads = _run_scenario(
            f"Update tags (0 -> {few_tags})",
            _update_from_zero,
            min(args.iterations, len(created_zero)),
            0,
        )
        results.append(res)
    if created_few:
        res, _payloads = _run_scenario(
            f"Update tags ({few_tags} -> {many_tags})",
            _update_from_few,
            min(args.iterations, len(created_few)),
            0,
        )
        results.append(res)
    if created_many:
        res, _payloads = _run_scenario(
            f"Update tags ({many_tags} -> {few_tags})",
            _update_from_many,
            min(args.iterations, len(created_many)),
            0,
        )
        results.append(res)

    report = _markdown_report(args.title, args.base_url, results, warnings)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(report)

    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
