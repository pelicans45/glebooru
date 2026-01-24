#!/usr/bin/env python3
"""Generate sustained load against /posts or /post/<id> for profiling."""
from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional, Tuple


def _request_json(url: str, timeout: float) -> Tuple[int, Optional[dict]]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return resp.status, json.loads(body.decode("utf-8"))
    except Exception:
        return 0, None


def _build_url(base: str, path: str, params: Optional[Dict[str, str]] = None) -> str:
    if base.endswith("/"):
        base = base[:-1]
    if not path.startswith("/"):
        path = "/" + path
    url = base + path
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    return url


def _pick_post_id(base_url: str, timeout: float) -> int:
    status, data = _request_json(
        _build_url(base_url, "/posts", {"limit": "1", "fields": "id"}),
        timeout,
    )
    if status == 200 and data and data.get("results"):
        return int(data["results"][0]["id"])
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate sustained API load")
    parser.add_argument("--base-url", default="http://localhost:4000/api")
    parser.add_argument("--duration", type=float, default=20.0)
    parser.add_argument("--concurrency", type=int, default=8)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--mode", choices=["posts", "post"], default="posts")
    parser.add_argument("--post-id", type=int, default=None)
    args = parser.parse_args()

    gallery_fields = (
        "id,thumbnailUrl,contentUrl,creationTime,type,safety,score,"
        "favoriteCount,commentCount,tagsBasic,version"
    )
    post_fields = (
        "id,version,creationTime,lastEditTime,safety,source,type,mimeType,"
        "checksum,checksumMD5,fileSize,canvasWidth,canvasHeight,duration,"
        "contentUrl,thumbnailUrl,flags,tags,relations,user,score,ownScore,"
        "ownFavorite,favoriteCount,commentCount,notes,comments"
    )

    if args.mode == "posts":
        url = _build_url(
            args.base_url,
            "/posts",
            {"limit": "42", "fields": gallery_fields, "query": ""},
        )
    else:
        post_id = args.post_id or _pick_post_id(args.base_url, args.timeout)
        url = _build_url(
            args.base_url,
            f"/post/{post_id}",
            {"fields": post_fields},
        )

    deadline = time.perf_counter() + args.duration
    success = 0
    errors = 0

    def worker() -> None:
        nonlocal success, errors
        while time.perf_counter() < deadline:
            status, _data = _request_json(url, args.timeout)
            if status == 200:
                success += 1
            else:
                errors += 1

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [executor.submit(worker) for _ in range(args.concurrency)]
        for future in futures:
            future.result()

    print(f"completed={success} errors={errors} url={url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
