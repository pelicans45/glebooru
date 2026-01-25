"""Merge near-duplicate image posts into the highest-quality post."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, Iterable, List, Optional, Set, Tuple

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from szurubooru import db, model
from szurubooru.func import image_hash, posts

IMAGE_TYPES = {model.Post.TYPE_IMAGE, model.Post.TYPE_ANIMATION}


def _quality_score(post: model.Post) -> Tuple[int, int, int]:
    width = post.canvas_width or 0
    height = post.canvas_height or 0
    pixels = width * height
    file_size = post.file_size or 0
    # Prefer higher resolution, then larger file size, then lowest id.
    return (pixels, file_size, -post.post_id)


def _iter_posts(
    base_query, start_id: int, limit: int, batch_size: int
) -> Iterable[model.Post]:
    remaining = limit if limit > 0 else None
    last_id = start_id - 1

    while True:
        query = (
            base_query.filter(model.Post.post_id > last_id)
            .order_by(model.Post.post_id.asc())
            .limit(batch_size)
        )
        if remaining is not None:
            query = query.limit(min(batch_size, remaining))
        batch = query.all()
        if not batch:
            break
        for post in batch:
            yield post
        last_id = batch[-1].post_id
        if remaining is not None:
            remaining -= len(batch)
            if remaining <= 0:
                break


def _unpack_signature(post: model.Post) -> Optional[image_hash.NpMatrix]:
    if not post.signature:
        return None
    packed = post.signature.signature
    if not packed:
        return None
    return image_hash.unpack_signature(packed)


def _expand_group(
    seed: model.Post,
    distance_cutoff: float,
    similar_limit: int,
) -> Dict[int, model.Post]:
    group: Dict[int, model.Post] = {}
    queue: List[model.Post] = [seed]

    while queue:
        post = queue.pop()
        if post.post_id in group:
            continue
        if post.type not in IMAGE_TYPES:
            continue
        group[post.post_id] = post
        signature = _unpack_signature(post)
        if signature is None:
            continue
        matches = posts.search_by_signature(
            signature,
            limit=similar_limit,
            distance_cutoff=distance_cutoff,
        )
        for _dist, match in matches:
            if not match:
                continue
            if match.post_id in group:
                continue
            if match.type not in IMAGE_TYPES:
                continue
            queue.append(match)

    return group


def _describe(post: model.Post) -> str:
    width = post.canvas_width or 0
    height = post.canvas_height or 0
    file_size = post.file_size or 0
    return f"id={post.post_id} {width}x{height} size={file_size}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Merge near-duplicate image posts into the highest-quality post."
        )
    )
    parser.add_argument("--start-id", type=int, default=1)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=200)
    parser.add_argument(
        "--distance-cutoff",
        type=float,
        default=image_hash.DISTANCE_CUTOFF,
    )
    parser.add_argument("--similar-limit", type=int, default=100)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    base_query = db.session.query(model.Post).filter(
        model.Post.type.in_(IMAGE_TYPES)
    )
    base_query = base_query.join(model.PostSignature)

    processed: Set[int] = set()
    group_count = 0
    merged_posts = 0

    for post in _iter_posts(
        base_query, args.start_id, args.limit, args.batch_size
    ):
        if post.post_id in processed:
            continue

        group = _expand_group(
            post,
            args.distance_cutoff,
            args.similar_limit,
        )
        if len(group) < 2:
            processed.add(post.post_id)
            continue

        group_posts = list(group.values())
        target = max(group_posts, key=_quality_score)
        sources = [p for p in group_posts if p.post_id != target.post_id]

        print(
            "group",
            ",".join(str(p.post_id) for p in group_posts),
            "->",
            _describe(target),
        )
        if args.dry_run:
            for source in sources:
                print("  would-merge", _describe(source))
        else:
            for source in sources:
                posts.merge_posts(source, target)
                merged_posts += 1
            db.session.commit()

        processed.update(group.keys())
        group_count += 1

    print(
        f"done groups={group_count} merged_posts={merged_posts} "
        f"dry_run={args.dry_run}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
