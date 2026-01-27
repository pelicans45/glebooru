#!/usr/bin/env python3
"""
Upload a batch of generated PNG images through the Szurubooru API.

This script is meant to seed "real" image files for UI/Playwright testing
without requiring external image assets.
"""
from __future__ import annotations

import argparse
import base64
import json
import random
import struct
import sys
import time
import urllib.error
import urllib.request
import uuid
import zlib
from typing import Dict, List, Optional, Tuple


def _png_bytes(width: int, height: int, seed: int) -> bytes:
    rng = random.Random(seed)
    base_r = rng.randint(0, 255)
    base_g = rng.randint(0, 255)
    base_b = rng.randint(0, 255)
    step_rx = rng.randint(1, 9)
    step_ry = rng.randint(1, 9)
    step_gx = rng.randint(1, 9)
    step_gy = rng.randint(1, 9)
    step_bx = rng.randint(1, 9)
    step_by = rng.randint(1, 9)

    raw = bytearray()
    for y in range(height):
        row = bytearray(1 + width * 3)
        row[0] = 0
        for x in range(width):
            idx = 1 + x * 3
            row[idx] = (base_r + x * step_rx + y * step_ry) & 0xFF
            row[idx + 1] = (base_g + x * step_gx + y * step_gy) & 0xFF
            row[idx + 2] = (base_b + x * step_bx + y * step_by) & 0xFF
        raw.extend(row)

    compressed = zlib.compress(bytes(raw), level=6)

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


def _encode_multipart(
    fields: Dict[str, str],
    files: List[Tuple[str, str, str, bytes]],
) -> Tuple[bytes, str]:
    boundary = f"----szuru-upload-{uuid.uuid4().hex}"
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


def _request(
    url: str,
    data: Optional[bytes],
    headers: Dict[str, str],
    timeout: float,
    method: str,
) -> Tuple[int, float, Optional[str]]:
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read()
            elapsed = time.perf_counter() - start
            return resp.status, elapsed, None
    except urllib.error.HTTPError as err:
        elapsed = time.perf_counter() - start
        try:
            body = err.read().decode("utf-8")
        except Exception:
            body = None
        return err.code, elapsed, body
    except Exception as err:
        elapsed = time.perf_counter() - start
        return 0, elapsed, str(err)


def _pick_tags(rng: random.Random, pool_size: int, count: int) -> List[str]:
    if count <= 0:
        return []
    indexes = rng.sample(range(pool_size), count)
    return [f"tag_{idx:05d}" for idx in indexes]


def _upload_post(
    base_url: str,
    auth_header: str,
    tags: List[str],
    timeout: float,
    content: bytes,
    original_host: Optional[str],
) -> Tuple[int, float, Optional[str]]:
    metadata = {
        "anonymous": False,
        "safety": "safe",
        "tags": tags,
    }
    body, content_type = _encode_multipart(
        {"metadata": json.dumps(metadata)},
        [("content", "upload.png", "image/png", content)],
    )
    headers = {
        "Content-Type": content_type,
        "Accept": "application/json",
        "Authorization": auth_header,
    }
    if original_host:
        headers["X-Original-Host"] = original_host
    url = base_url.rstrip("/") + "/posts"
    return _request(url, body, headers, timeout, "POST")


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload generated images.")
    parser.add_argument("--base-url", default="http://localhost:4000/api")
    parser.add_argument("--user", default="benchmark_admin")
    parser.add_argument("--password", default="benchmark")
    parser.add_argument("--count", type=int, default=300)
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=360)
    parser.add_argument("--min-tags", type=int, default=1)
    parser.add_argument("--max-tags", type=int, default=8)
    parser.add_argument("--tag-pool", type=int, default=2000)
    parser.add_argument("--fixed-tag", default="")
    parser.add_argument("--seed", type=int, default=1447)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--original-host", default="")
    args = parser.parse_args()

    if args.min_tags < 0 or args.max_tags < args.min_tags:
        raise ValueError("Invalid min-tags/max-tags")

    token = f"{args.user}:{args.password}".encode("utf-8")
    auth_header = "Basic " + base64.b64encode(token).decode("ascii")
    rng = random.Random(args.seed)

    failures = 0
    for idx in range(args.count):
        if args.fixed_tag:
            tags = [args.fixed_tag]
        else:
            tag_count = rng.randint(args.min_tags, args.max_tags)
            tags = _pick_tags(rng, args.tag_pool, tag_count)
        content = _png_bytes(args.width, args.height, args.seed + idx)
        status, elapsed, err = _upload_post(
            args.base_url,
            auth_header,
            tags,
            args.timeout,
            content,
            args.original_host or None,
        )
        if status != 200:
            failures += 1
            print(
                f"[{idx + 1}/{args.count}] upload failed: {status} {err}",
                file=sys.stderr,
            )
        elif (idx + 1) % 25 == 0:
            print(
                f"[{idx + 1}/{args.count}] ok ({elapsed:.2f}s)",
                file=sys.stderr,
            )

    print(
        f"Uploaded {args.count - failures}/{args.count} images "
        f"(failures={failures})."
    )
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
