#!/usr/bin/env python3
"""
Seed a deterministic benchmark dataset for Szurubooru.

This script clears the database, inserts a large post + tag dataset, and
optionally runs ANALYZE so the planner has accurate stats.

Run with:
    python -m szurubooru.benchmark_seed_dataset --posts 50000 \
        --tagged-posts 40000 --min-tags 1 --max-tags 20
"""
from __future__ import annotations

import argparse
import hashlib
import os
import random
import shutil
import sys
import time
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Dict, List, Tuple

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql  # Ensure dialect is loaded

from PIL import Image, ImageDraw

from szurubooru import db, model
from szurubooru.func import files, mime, posts


def _log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def _reset_database() -> None:
    tables = [table.name for table in model.Base.metadata.sorted_tables]
    if not tables:
        return
    quoted = ", ".join(f'"{name}"' for name in tables)
    db.session.execute(
        sa.text(f"TRUNCATE {quoted} RESTART IDENTITY CASCADE")
    )
    db.session.commit()


def _reset_data_dir() -> None:
    data_dir = os.path.abspath("/data")
    for subdir in ("posts", "generated-thumbnails"):
        path = os.path.join(data_dir, subdir)
        if os.path.exists(path):
            shutil.rmtree(path)


def _create_user(now: datetime) -> int:
    user = model.User()
    user.name = "benchmark_admin"
    user.password_hash = "x" * 128
    user.password_salt = "x" * 32
    user.rank = model.User.RANK_ADMINISTRATOR
    user.creation_time = now
    db.session.add(user)
    db.session.flush()
    return user.user_id


def _create_tag_category(now: datetime) -> int:
    category = model.TagCategory()
    category.name = "default"
    category.color = "default"
    category.default = True
    category.order = 1
    category.version = 1
    db.session.add(category)
    db.session.flush()
    return category.tag_category_id


def _create_tags(category_id: int, now: datetime, count: int) -> List[int]:
    tags = []
    for i in range(count):
        tag = model.Tag()
        tag.category_id = category_id
        tag.version = 1
        tag.creation_time = now
        tag.names = [model.TagName(f"tag_{i:05d}", 0)]
        tags.append(tag)
    db.session.add_all(tags)
    db.session.flush()
    tag_ids = [tag.tag_id for tag in tags]
    db.session.commit()
    return tag_ids


def _build_tag_counts(
    total_posts: int,
    tagged_posts: int,
    min_tags: int,
    max_tags: int,
    rng: random.Random,
) -> List[int]:
    if tagged_posts > total_posts:
        raise ValueError("tagged-posts cannot exceed total posts")
    untagged = total_posts - tagged_posts
    counts = [0] * untagged
    counts.extend(rng.randint(min_tags, max_tags) for _ in range(tagged_posts))
    rng.shuffle(counts)
    return counts


def _checksum(seed: int, post_id: int) -> str:
    payload = f"benchmark-{seed}-{post_id}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _checksum_md5(seed: int, post_id: int) -> str:
    payload = f"benchmark-{seed}-{post_id}".encode("utf-8")
    return hashlib.md5(payload).hexdigest()


def _insert_posts(
    user_id: int,
    total_posts: int,
    seed: int,
    now: datetime,
    batch_size: int,
    file_sizes: List[int],
    image_width: int,
    image_height: int,
    mime_type: str,
) -> None:
    post_rows: List[dict] = []
    variant_count = max(1, len(file_sizes))

    for idx in range(total_posts):
        post_id = idx + 1
        creation_time = now - timedelta(seconds=(total_posts - post_id))
        variant = (post_id - 1) % variant_count
        post_rows.append(
            {
                "id": post_id,
                "user_id": user_id,
                "version": 1,
                "creation_time": creation_time,
                "safety": model.Post.SAFETY_SAFE,
                "type": model.Post.TYPE_IMAGE,
                "checksum": _checksum(seed, post_id),
                "checksum_md5": _checksum_md5(seed, post_id),
                "file_size": file_sizes[variant],
                "image_width": image_width,
                "image_height": image_height,
                "mime-type": mime_type,
                "flags": "",
            }
        )

        if len(post_rows) >= batch_size:
            db.session.execute(model.Post.__table__.insert(), post_rows)
            post_rows.clear()

        if post_id % (batch_size * 5) == 0:
            _log(f"Inserted {post_id:,} posts...")

    if post_rows:
        db.session.execute(model.Post.__table__.insert(), post_rows)

    db.session.commit()
    db.session.execute(
        sa.text(
            "SELECT setval("
            "pg_get_serial_sequence('post', 'id'), "
            "(SELECT COALESCE(MAX(id), 1) FROM post)"
            ")"
        )
    )
    db.session.commit()


def _weighted_unique_sample(
    rng: random.Random,
    tag_ids: List[int],
    weights: List[float],
    count: int,
) -> List[int]:
    if count <= 0:
        return []
    chosen: set[int] = set()
    while len(chosen) < count:
        picked = rng.choices(tag_ids, weights=weights, k=1)[0]
        chosen.add(picked)
    return list(chosen)


def _select_forced_posts(
    tag_counts: List[int],
    target_count: int,
    rng: random.Random,
) -> set[int]:
    candidates = [idx + 1 for idx, count in enumerate(tag_counts) if count > 0]
    if not candidates or target_count <= 0:
        return set()
    target_count = min(target_count, len(candidates))
    return set(rng.sample(candidates, target_count))


def _insert_post_tags(
    tag_ids: List[int],
    tag_counts: List[int],
    seed: int,
    batch_size: int,
    skewed: bool,
    zipf_alpha: float,
    forced_tag_id: int | None,
    forced_post_ids: set[int],
) -> None:
    rng = random.Random(seed)
    post_ids_batch: List[int] = []
    tag_ids_batch: List[int] = []

    pool_tag_ids = (
        [tag_id for tag_id in tag_ids if tag_id != forced_tag_id]
        if forced_tag_id is not None
        else list(tag_ids)
    )

    weights: List[float] | None = None
    if skewed and pool_tag_ids:
        weights = [
            1.0 / pow(rank + 1, zipf_alpha)
            for rank in range(len(pool_tag_ids))
        ]

    for idx, tag_count in enumerate(tag_counts):
        if tag_count <= 0:
            continue
        post_id = idx + 1
        chosen: List[int] = []
        if forced_tag_id is not None and post_id in forced_post_ids:
            chosen.append(forced_tag_id)
            tag_count -= 1
        if tag_count > 0:
            if weights is None:
                chosen.extend(rng.sample(pool_tag_ids, tag_count))
            else:
                chosen.extend(
                    _weighted_unique_sample(
                        rng, pool_tag_ids, weights, tag_count
                    )
                )

        for tag_id in chosen:
            post_ids_batch.append(post_id)
            tag_ids_batch.append(tag_id)
        if len(post_ids_batch) >= batch_size:
            db.session.execute(
                sa.text(
                    "INSERT INTO post_tag (post_id, tag_id) "
                    "SELECT * FROM unnest("
                    "CAST(:post_ids AS int[]), "
                    "CAST(:tag_ids AS int[])"
                    ")"
                ),
                {
                    "post_ids": post_ids_batch,
                    "tag_ids": tag_ids_batch,
                },
            )
            post_ids_batch.clear()
            tag_ids_batch.clear()

        if post_id % 5000 == 0:
            _log(f"Tagged {post_id:,} posts...")

    if post_ids_batch:
        db.session.execute(
            sa.text(
                "INSERT INTO post_tag (post_id, tag_id) "
                "SELECT * FROM unnest("
                "CAST(:post_ids AS int[]), "
                "CAST(:tag_ids AS int[])"
                ")"
            ),
            {"post_ids": post_ids_batch, "tag_ids": tag_ids_batch},
        )

    db.session.commit()


def _generate_image_variants(
    variants: int,
    width: int,
    height: int,
    thumb_size: Tuple[int, int],
    seed: int,
) -> List[Dict[str, bytes]]:
    rng = random.Random(seed)
    images: List[Dict[str, bytes]] = []

    for idx in range(max(1, variants)):
        base_color = (
            rng.randint(0, 255),
            rng.randint(0, 255),
            rng.randint(0, 255),
        )
        img = Image.new("RGB", (width, height), base_color)
        draw = ImageDraw.Draw(img)
        for _ in range(6):
            x0 = rng.randint(0, width - 1)
            y0 = rng.randint(0, height - 1)
            x1 = rng.randint(x0, width - 1)
            y1 = rng.randint(y0, height - 1)
            color = (
                rng.randint(0, 255),
                rng.randint(0, 255),
                rng.randint(0, 255),
            )
            draw.rectangle([x0, y0, x1, y1], outline=color)

        content_buf = BytesIO()
        img.save(content_buf, format="PNG", optimize=True)
        content_bytes = content_buf.getvalue()

        thumb = img.copy()
        thumb.thumbnail(thumb_size)
        thumb_buf = BytesIO()
        thumb.save(thumb_buf, format="JPEG", quality=85, optimize=True)
        thumb_bytes = thumb_buf.getvalue()

        images.append({"content": content_bytes, "thumb": thumb_bytes})
    return images


def _write_post_files(
    total_posts: int,
    variants: List[Dict[str, bytes]],
    mime_type: str,
) -> None:
    if not variants:
        return
    content_ext = mime.get_extension(mime_type) or "dat"
    variant_count = len(variants)
    for post_id in range(1, total_posts + 1):
        variant = variants[(post_id - 1) % variant_count]
        security_hash = posts.get_post_security_hash(post_id)
        content_path = (
            f"posts/{post_id}_{security_hash}.{content_ext}"
        )
        thumb_path = (
            f"generated-thumbnails/{post_id}_{security_hash}.jpg"
        )
        files.save(content_path, variant["content"])
        files.save(thumb_path, variant["thumb"])
        if post_id % 5000 == 0:
            _log(f"Wrote files for {post_id:,} posts...")


def _analyze() -> None:
    db.session.execute(sa.text("ANALYZE"))
    db.session.commit()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seed a deterministic benchmark dataset."
    )
    parser.add_argument("--posts", type=int, default=50000)
    parser.add_argument("--tagged-posts", type=int, default=40000)
    parser.add_argument("--min-tags", type=int, default=1)
    parser.add_argument("--max-tags", type=int, default=20)
    parser.add_argument("--tags", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--post-batch", type=int, default=2000)
    parser.add_argument("--tag-batch", type=int, default=20000)
    parser.add_argument("--no-analyze", action="store_true")
    parser.add_argument("--with-files", action="store_true")
    parser.add_argument("--file-variants", type=int, default=64)
    parser.add_argument("--image-width", type=int, default=640)
    parser.add_argument("--image-height", type=int, default=360)
    parser.add_argument("--thumb-width", type=int, default=300)
    parser.add_argument("--thumb-height", type=int, default=300)
    parser.add_argument(
        "--skewed-tags",
        action="store_true",
        help="Use a Zipf-like distribution for tag selection.",
    )
    parser.add_argument(
        "--zipf-alpha",
        type=float,
        default=1.1,
        help="Zipf alpha for skewed tag distribution.",
    )
    parser.add_argument(
        "--exclusion-tag-rate",
        type=float,
        default=0.10,
        help="Force tag_00000 onto this fraction of posts.",
    )
    parser.add_argument(
        "--skip-reset",
        action="store_true",
        help="Skip TRUNCATE/RESET (dangerous if data exists)",
    )
    args = parser.parse_args()

    if args.min_tags < 0 or args.max_tags < args.min_tags:
        raise ValueError("Invalid min-tags/max-tags")
    if args.tags < args.max_tags:
        raise ValueError("--tags must be >= max-tags")

    start_time = time.perf_counter()
    now = datetime.now(timezone.utc)

    _log("Starting benchmark dataset seed...")
    _log(
        f"Posts={args.posts} "
        f"(tagged={args.tagged_posts}, untagged={args.posts - args.tagged_posts}), "
        f"tags={args.tags}, tags/post={args.min_tags}-{args.max_tags}, "
        f"seed={args.seed}"
    )

    if not args.skip_reset:
        _log("Clearing database...")
        _reset_database()
        if args.with_files:
            _log("Clearing data directory...")
            _reset_data_dir()

    _log("Creating user and tag category...")
    user_id = _create_user(now)
    category_id = _create_tag_category(now)
    db.session.commit()

    _log("Creating tags...")
    tag_ids = _create_tags(category_id, now, args.tags)
    _log(f"Created {len(tag_ids):,} tags.")

    variants: List[Dict[str, bytes]] = []
    if args.with_files:
        _log("Generating image variants...")
        variants = _generate_image_variants(
            args.file_variants,
            args.image_width,
            args.image_height,
            (args.thumb_width, args.thumb_height),
            args.seed,
        )
        _log(f"Generated {len(variants):,} image variants.")

    _log("Preparing tag distributions...")
    rng_counts = random.Random(args.seed)
    tag_counts = _build_tag_counts(
        args.posts,
        args.tagged_posts,
        args.min_tags,
        args.max_tags,
        rng_counts,
    )

    forced_tag_id = None
    forced_post_ids: set[int] = set()
    if args.exclusion_tag_rate > 0 and tag_ids:
        forced_tag_id = tag_ids[0]
        forced_target = int(round(args.posts * args.exclusion_tag_rate))
        forced_rng = random.Random(args.seed + 99)
        forced_post_ids = _select_forced_posts(
            tag_counts, forced_target, forced_rng
        )
        _log(
            "Forcing tag_00000 onto "
            f"{len(forced_post_ids):,} posts "
            f"({len(forced_post_ids) / args.posts:.1%})."
        )

    _log("Inserting posts...")
    file_sizes = (
        [len(variant["content"]) for variant in variants]
        if variants
        else [150000]
    )
    _insert_posts(
        user_id=user_id,
        total_posts=args.posts,
        seed=args.seed,
        now=now,
        batch_size=args.post_batch,
        file_sizes=file_sizes,
        image_width=args.image_width,
        image_height=args.image_height,
        mime_type="image/png",
    )

    if args.with_files:
        _log("Writing post files...")
        _write_post_files(
            args.posts,
            variants,
            "image/png",
        )

    _log("Inserting post tags...")
    _insert_post_tags(
        tag_ids=tag_ids,
        tag_counts=tag_counts,
        seed=args.seed + 1,
        batch_size=args.tag_batch,
        skewed=args.skewed_tags,
        zipf_alpha=args.zipf_alpha,
        forced_tag_id=forced_tag_id,
        forced_post_ids=forced_post_ids,
    )

    if not args.no_analyze:
        _log("Running ANALYZE...")
        _analyze()

    elapsed = time.perf_counter() - start_time
    _log(f"Dataset ready in {elapsed:.2f}s.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
