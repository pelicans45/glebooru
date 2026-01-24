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
import random
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import List

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql  # Ensure dialect is loaded

from szurubooru import db, model


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
) -> None:
    post_rows: List[dict] = []

    for idx in range(total_posts):
        post_id = idx + 1
        creation_time = now - timedelta(seconds=(total_posts - post_id))
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
                "file_size": 150000,
                "image_width": 1280,
                "image_height": 720,
                "mime-type": "image/png",
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


def _insert_post_tags(
    tag_ids: List[int],
    tag_counts: List[int],
    seed: int,
    batch_size: int,
) -> None:
    rng = random.Random(seed)
    post_ids_batch: List[int] = []
    tag_ids_batch: List[int] = []
    total_posts = len(tag_counts)

    for idx, tag_count in enumerate(tag_counts):
        if tag_count <= 0:
            continue
        post_id = idx + 1
        chosen = rng.sample(tag_ids, tag_count)
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

    _log("Creating user and tag category...")
    user_id = _create_user(now)
    category_id = _create_tag_category(now)
    db.session.commit()

    _log("Creating tags...")
    tag_ids = _create_tags(category_id, now, args.tags)
    _log(f"Created {len(tag_ids):,} tags.")

    _log("Preparing tag distributions...")
    rng_counts = random.Random(args.seed)
    tag_counts = _build_tag_counts(
        args.posts,
        args.tagged_posts,
        args.min_tags,
        args.max_tags,
        rng_counts,
    )

    _log("Inserting posts...")
    _insert_posts(
        user_id=user_id,
        total_posts=args.posts,
        seed=args.seed,
        now=now,
        batch_size=args.post_batch,
    )

    _log("Inserting post tags...")
    _insert_post_tags(
        tag_ids=tag_ids,
        tag_counts=tag_counts,
        seed=args.seed + 1,
        batch_size=args.tag_batch,
    )

    if not args.no_analyze:
        _log("Running ANALYZE...")
        _analyze()

    elapsed = time.perf_counter() - start_time
    _log(f"Dataset ready in {elapsed:.2f}s.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
