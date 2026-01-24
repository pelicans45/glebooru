#!/usr/bin/env python3
"""
Trigger server-side request profiling for /posts and /post/<id>.

Uses the same field sets as the benchmark to keep work realistic.
Set _profile=1 to capture profiles on the server.
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Tuple


def _request_json(url: str, timeout: float) -> Tuple[int, Optional[dict]]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
        return resp.status, json.loads(body.decode("utf-8"))


def _build_url(base: str, path: str, params: Optional[Dict[str, str]] = None) -> str:
    if base.endswith("/"):
        base = base[:-1]
    if not path.startswith("/"):
        path = "/" + path
    url = base + path
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    return url


def _find_post_samples(base_url: str, timeout: float, target: int = 3) -> dict:
    categories = {"no_tags": [], "few_tags": [], "many_tags": []}
    offset = 0
    page_size = 200
    max_offset = 2000

    while offset <= max_offset:
        url = _build_url(
            base_url,
            "/posts",
            {"offset": str(offset), "limit": str(page_size), "fields": "id,tags"},
        )
        status, data = _request_json(url, timeout)
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


def _hit(url: str, timeout: float) -> None:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        resp.read()


def main() -> int:
    parser = argparse.ArgumentParser(description="Trigger request profiling")
    parser.add_argument("--base-url", default="http://localhost:4000/api")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--repeat", type=int, default=1)
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

    samples = _find_post_samples(args.base_url, args.timeout)
    common_tag = _pick_common_tag(samples)

    urls: List[str] = []
    urls.append(
        _build_url(
            args.base_url,
            "/posts",
            {"limit": "42", "fields": gallery_fields, "query": "", "_profile": "1"},
        )
    )
    if common_tag:
        urls.append(
            _build_url(
                args.base_url,
                "/posts",
                {
                    "limit": "42",
                    "fields": gallery_fields,
                    "query": common_tag,
                    "_profile": "1",
                },
            )
        )

    for bucket in ("no_tags", "few_tags", "many_tags"):
        for post in samples.get(bucket, [])[:1]:
            urls.append(
                _build_url(
                    args.base_url,
                    f"/post/{post['id']}",
                    {"fields": post_fields, "_profile": "1"},
                )
            )

    for _ in range(args.repeat):
        for url in urls:
            _hit(url, args.timeout)
            time.sleep(0.2)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
