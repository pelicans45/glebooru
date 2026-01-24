"""Rebuild all post signatures using current image hash backend."""

from __future__ import annotations

import argparse

import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from szurubooru import db, model
from szurubooru.func import files, posts


def _build_path_index() -> dict[int, str]:
    index: dict[int, str] = {}
    for entry in files.scan("posts"):
        name = entry.name
        if "_" in name:
            prefix = name.split("_", 1)[0]
        else:
            prefix = name.split(".", 1)[0]
        if not prefix.isdigit():
            continue
        post_id = int(prefix)
        path = f"posts/{name}"
        if "_" in name or post_id not in index:
            index[post_id] = path
    return index


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rebuild post signatures for all image/animation posts."
    )
    parser.add_argument("--batch-size", type=int, default=200)
    parser.add_argument("--start-id", type=int, default=1)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    base_query = db.session.query(model.Post).filter(
        (model.Post.type == model.Post.TYPE_IMAGE)
        | (model.Post.type == model.Post.TYPE_ANIMATION)
    )

    remaining = args.limit if args.limit > 0 else None
    last_id = args.start_id - 1
    path_index = _build_path_index()
    processed = 0
    skipped = 0

    while True:
        query = (
            base_query.filter(model.Post.post_id > last_id)
            .order_by(model.Post.post_id.asc())
            .limit(args.batch_size)
        )
        if remaining is not None:
            query = query.limit(min(args.batch_size, remaining))
        batch = query.all()
        if not batch:
            break

        for post in batch:
            content = files.get(posts.get_post_content_path(post))
            if not content:
                fallback = path_index.get(post.post_id)
                if fallback:
                    content = files.get(fallback)
            if not content:
                posts.purge_post_signature(post)
                skipped += 1
                last_id = post.post_id
                continue
            posts.purge_post_signature(post)
            posts.generate_post_signature(post, content)
            processed += 1
            last_id = post.post_id
        db.session.commit()
        if remaining is not None:
            remaining -= len(batch)
            if remaining <= 0:
                break
        print(f"processed={processed} skipped={skipped}")

    print(f"done processed={processed} skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
