#!/usr/bin/env python3
"""
Generate real image files, signatures, and realistic tag distributions
for a subset of posts (default 30k).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import os
import sys
from datetime import UTC, datetime
from typing import Dict, Iterable, List, Tuple

import numpy as np
from PIL import Image, ImageDraw

import sqlalchemy as sa

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from szurubooru import db, model
from szurubooru.func import files, posts


def _generate_image(post_id: int, size: int) -> Tuple[bytes, int, int]:
    rng = np.random.default_rng(post_id)
    base = rng.integers(0, 255, size=(size, size, 3), dtype=np.uint8)
    img = Image.fromarray(base, "RGB")
    draw = ImageDraw.Draw(img)
    # Add a deterministic pattern for a bit more structure.
    color = (
        int(post_id * 17 % 255),
        int(post_id * 29 % 255),
        int(post_id * 43 % 255),
    )
    draw.rectangle(
        (size // 4, size // 4, size * 3 // 4, size * 3 // 4),
        outline=color,
        width=2,
    )
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    return buf.getvalue(), size, size


def _hashes(content: bytes) -> Tuple[str, str]:
    sha1 = hashlib.sha1(content).hexdigest()
    md5 = hashlib.md5(content).hexdigest()
    return sha1, md5


def _iter_posts(count: int) -> List[model.Post]:
    return (
        db.session.query(model.Post)
        .order_by(model.Post.post_id.asc())
        .limit(count)
        .all()
    )


def _get_or_create_tags(tag_count: int, prefix: str) -> List[model.Tag]:
    names = [f"{prefix}{i:04d}" for i in range(tag_count)]
    existing_rows = (
        db.session.query(model.TagName.name, model.Tag)
        .join(model.Tag, model.TagName.tag_id == model.Tag.tag_id)
        .filter(model.TagName.name.in_(names))
        .all()
    )
    existing = {name: tag for name, tag in existing_rows}
    tags_out: List[model.Tag] = []
    now = datetime.now(UTC).replace(tzinfo=None)
    category = (
        db.session.query(model.TagCategory)
        .filter(model.TagCategory.default == True)  # noqa: E712
        .one()
    )
    for name in names:
        tag = existing.get(name)
        if tag is not None:
            tags_out.append(tag)
            continue
        tag = model.Tag()
        tag.creation_time = now
        tag.category = category
        tag.names = [model.TagName(name=name, order=0)]
        tags_out.append(tag)
    new_tags = [tag for tag in tags_out if tag.tag_id is None]
    if new_tags:
        db.session.add_all(new_tags)
        db.session.commit()
    return tags_out


def _build_tag_distribution() -> List[int]:
    # (num_tags, usage_per_tag)
    buckets = [
        (50, 300),
        (100, 500),
        (200, 200),
        (300, 50),
        (500, 20),
        (1000, 5),
        (1000, 1),
    ]
    counts: List[int] = []
    for num, usage in buckets:
        counts.extend([usage] * num)
    return counts


def _clear_post_tags(post_ids: List[int], batch_size: int) -> None:
    for i in range(0, len(post_ids), batch_size):
        chunk = post_ids[i : i + batch_size]
        if not chunk:
            continue
        db.session.execute(
            sa.delete(model.PostTag).where(model.PostTag.post_id.in_(chunk))
        )
        db.session.commit()


def _assign_tags_to_posts(
    posts_list: List[model.Post],
    tags_list: List[model.Tag],
    usage_counts: List[int],
    seed: int,
    batch_size: int,
) -> None:
    rng = np.random.default_rng(seed)
    post_ids = np.array([post.post_id for post in posts_list], dtype=np.int64)
    total = 0

    for tag, usage in zip(tags_list, usage_counts):
        if usage <= 0:
            continue
        usage = min(usage, len(post_ids))
        chosen = rng.choice(post_ids, size=usage, replace=False)
        mappings = [
            {"post_id": int(pid), "tag_id": tag.tag_id} for pid in chosen
        ]
        db.session.bulk_insert_mappings(model.PostTag, mappings)
        total += len(mappings)
        if total % batch_size == 0:
            db.session.commit()
    db.session.commit()
    print(f"tag assignments created={total}")


def _build_existing_file_index() -> Dict[int, List[str]]:
    index: Dict[int, List[str]] = {}
    for entry in files.scan("posts"):
        name = entry.name
        if "_" in name:
            prefix = name.split("_", 1)[0]
        else:
            prefix = name.split(".", 1)[0]
        if not prefix.isdigit():
            continue
        post_id = int(prefix)
        index.setdefault(post_id, []).append(f"posts/{name}")
    return index


def _write_files_and_signatures(
    posts_list: List[model.Post],
    size: int,
    batch_size: int,
    remove_existing: bool,
) -> None:
    processed = 0
    existing_files = _build_existing_file_index() if remove_existing else {}
    for post in posts_list:
        if remove_existing:
            for path in existing_files.get(post.post_id, []):
                files.delete(path)
        content, width, height = _generate_image(post.post_id, size)
        post.mime_type = "image/jpeg"
        post.type = model.Post.TYPE_IMAGE
        path = posts.get_post_content_path(post)
        files.save(path, content)

        sha1, md5 = _hashes(content)
        post.checksum = sha1
        post.checksum_md5 = md5
        post.file_size = len(content)
        post.canvas_width = width
        post.canvas_height = height

        posts.purge_post_signature(post)
        posts.generate_post_signature(post, content)
        processed += 1
        if processed % batch_size == 0:
            db.session.commit()
            print(f"files/signatures processed={processed}")
    db.session.commit()
    print(f"files/signatures done processed={processed}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seed real files, signatures, and tags for benchmarking."
    )
    parser.add_argument("--count", type=int, default=30000)
    parser.add_argument("--image-size", type=int, default=96)
    parser.add_argument("--tag-prefix", default="real_tag_")
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--batch-size", type=int, default=200)
    parser.add_argument("--reset-tags", action="store_true", default=True)
    parser.add_argument("--no-reset-tags", action="store_false", dest="reset_tags")
    parser.add_argument("--reset-files", action="store_true", default=True)
    parser.add_argument("--no-reset-files", action="store_false", dest="reset_files")
    args = parser.parse_args()

    posts_list = _iter_posts(args.count)
    if not posts_list:
        print("No posts found to seed.")
        return 1
    print(f"seeding posts={len(posts_list)}")

    # Files + signatures
    _write_files_and_signatures(
        posts_list,
        args.image_size,
        args.batch_size,
        args.reset_files,
    )

    # Tags
    usage_counts = _build_tag_distribution()
    tags_needed = len(usage_counts)
    tags_list = _get_or_create_tags(tags_needed, args.tag_prefix)
    if len(tags_list) < tags_needed:
        usage_counts = usage_counts[: len(tags_list)]

    if args.reset_tags:
        _clear_post_tags(
            [post.post_id for post in posts_list], args.batch_size
        )
    _assign_tags_to_posts(
        posts_list, tags_list, usage_counts, args.seed, args.batch_size
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
