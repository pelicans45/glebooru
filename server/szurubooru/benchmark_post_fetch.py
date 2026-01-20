#!/usr/bin/env python3
"""
Benchmark script to compare old vs new post fetching functions.

This script measures the performance difference between:
1. Old method: Raw SQL with lazy loading (N+1 queries)
2. New method: SQLAlchemy ORM with eager loading (minimal queries)

Run with: python -m szurubooru.benchmark_post_fetch
"""

import gc
import statistics
import time
from typing import List, Optional, Tuple
import sys
import os

# Ensure the parent module is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlalchemy as sa
from sqlalchemy.orm import joinedload, selectinload

from szurubooru import config, db, model
from szurubooru.func import posts, serialization


def old_try_get_post_by_id(post_id: int) -> Optional[model.Post]:
    """Old method: Raw SQL that bypasses ORM eager loading."""
    return (
        db.session.query(model.Post)
        .from_statement(sa.text("select * from post where id = :id"))
        .params(id=post_id)
        .first()
    )


def old_try_get_post_by_id_orm(post_id: int) -> Optional[model.Post]:
    """Old method variant: Simple ORM query without eager loading."""
    return (
        db.session.query(model.Post)
        .filter(model.Post.post_id == post_id)
        .one_or_none()
    )


def new_get_post_by_id_optimized(post_id: int) -> Optional[model.Post]:
    """New method: SQLAlchemy ORM with eager loading for all relationships."""
    return (
        db.session.query(model.Post)
        .options(
            # Tags with their names and categories
            selectinload(model.Post.tags)
            .joinedload(model.Tag.names),
            selectinload(model.Post.tags)
            .joinedload(model.Tag.category),
            # User who created the post
            joinedload(model.Post.user),
            # Favorites with user info
            selectinload(model.Post.favorited_by)
            .joinedload(model.PostFavorite.user),
            # Notes
            selectinload(model.Post.notes),
            # Scores
            selectinload(model.Post.scores),
            # Comments with their users
            selectinload(model.Post.comments)
            .joinedload(model.Comment.user),
            # Pools
            selectinload(model.Post._pools)
            .joinedload(model.PoolPost.pool)
            .joinedload(model.Pool.names),
            selectinload(model.Post._pools)
            .joinedload(model.PoolPost.pool)
            .joinedload(model.Pool.category),
            # Post signature
            joinedload(model.Post.signature),
        )
        .filter(model.Post.post_id == post_id)
        .one_or_none()
    )


class MockUser:
    """Mock user for serialization."""
    user_id = 0
    name = "benchmark_user"
    rank = "anonymous"


def serialize_post_full(post: model.Post) -> dict:
    """Full serialization - what happens when viewing a post."""
    if not post:
        return None
    return posts.PostSerializer(post, MockUser()).serialize([])


def benchmark_fetch_only(
    fetch_func, post_ids: List[int], iterations: int = 10
) -> Tuple[float, float, List[float]]:
    """Benchmark just the fetch operation (no serialization)."""
    times = []

    for _ in range(iterations):
        gc.collect()
        db.session.expire_all()  # Clear ORM cache to simulate cold fetch

        start = time.perf_counter()
        for post_id in post_ids:
            post = fetch_func(post_id)
        end = time.perf_counter()

        times.append(end - start)
        db.session.rollback()  # Clean up session

    return statistics.mean(times), statistics.stdev(times) if len(times) > 1 else 0, times


def benchmark_fetch_and_serialize(
    fetch_func, post_ids: List[int], iterations: int = 10
) -> Tuple[float, float, List[float]]:
    """Benchmark fetch + full serialization (the real-world scenario)."""
    times = []

    for _ in range(iterations):
        gc.collect()
        db.session.expire_all()  # Clear ORM cache to simulate cold fetch

        start = time.perf_counter()
        for post_id in post_ids:
            post = fetch_func(post_id)
            if post:
                _ = serialize_post_full(post)
        end = time.perf_counter()

        times.append(end - start)
        db.session.rollback()  # Clean up session

    return statistics.mean(times), statistics.stdev(times) if len(times) > 1 else 0, times


def count_queries(func, post_id: int) -> int:
    """Count the number of SQL queries executed by a function."""
    from sqlalchemy import event

    query_count = [0]
    engine = db.get_engine()

    def count_query(conn, cursor, statement, parameters, context, executemany):
        query_count[0] += 1

    event.listen(engine, "before_cursor_execute", count_query)

    try:
        db.session.expire_all()
        post = func(post_id)
        if post:
            _ = serialize_post_full(post)
    finally:
        event.remove(engine, "before_cursor_execute", count_query)
        db.session.rollback()

    return query_count[0]


def create_test_data(num_posts: int = 20):
    """Create test posts and related data for benchmarking."""
    from datetime import datetime, timezone
    import random

    now = datetime.now(timezone.utc)
    print(f"Creating {num_posts} test posts for benchmarking...")

    # Create a test user if none exists
    test_user = db.session.query(model.User).first()
    if not test_user:
        test_user = model.User()
        test_user.name = "benchmark_test_user"
        test_user.password_hash = "x" * 64
        test_user.password_salt = "x" * 16
        test_user.email = "test@test.com"
        test_user.rank = "administrator"
        test_user.creation_time = now
        db.session.add(test_user)
        db.session.flush()

    # Create a test tag category if none exists
    test_category = db.session.query(model.TagCategory).first()
    if not test_category:
        test_category = model.TagCategory()
        test_category.name = "default"
        test_category.color = "default"
        test_category.version = 1
        test_category.default = True
        db.session.add(test_category)
        db.session.flush()

    # Create some test tags
    test_tags = []
    for i in range(5):
        tag = model.Tag()
        tag.category_id = test_category.tag_category_id
        tag.version = 1
        tag.creation_time = now
        db.session.add(tag)
        db.session.flush()
        tag_name = model.TagName(f"test_tag_{i}", i)
        tag_name.tag_id = tag.tag_id
        db.session.add(tag_name)
        test_tags.append(tag)
    db.session.flush()

    # Create test posts
    for i in range(num_posts):
        post = model.Post()
        post.user_id = test_user.user_id
        post.version = 1
        post.creation_time = now
        post.safety = "safe"
        post.type = "image"
        post.checksum = f"benchmark_checksum_{i:08d}"
        post.mime_type = "image/png"
        post.canvas_width = 100
        post.canvas_height = 100
        post.file_size = 1000
        db.session.add(post)
        db.session.flush()

        # Add some tags to each post
        for tag in random.sample(test_tags, min(3, len(test_tags))):
            post.tags.append(tag)

    db.session.commit()
    print(f"Created {num_posts} test posts.")


def run_benchmark():
    """Run the full benchmark suite."""
    print("=" * 70)
    print("POST FETCH BENCHMARK")
    print("=" * 70)

    # Get some post IDs to test with
    post_ids = [
        row[0] for row in
        db.session.query(model.Post.post_id)
        .order_by(model.Post.post_id.desc())
        .limit(20)
        .all()
    ]

    if not post_ids:
        print("No posts found. Creating test data...")
        create_test_data(20)
        post_ids = [
            row[0] for row in
            db.session.query(model.Post.post_id)
            .order_by(model.Post.post_id.desc())
            .limit(20)
            .all()
        ]

    if not post_ids:
        print("ERROR: Could not create test data. Cannot run benchmark.")
        return

    print(f"\nTesting with {len(post_ids)} posts: {post_ids[:5]}...")

    # Single post test
    test_post_id = post_ids[0]

    print("\n" + "-" * 70)
    print("QUERY COUNT ANALYSIS (single post)")
    print("-" * 70)

    old_raw_queries = count_queries(old_try_get_post_by_id, test_post_id)
    old_orm_queries = count_queries(old_try_get_post_by_id_orm, test_post_id)
    new_queries = count_queries(new_get_post_by_id_optimized, test_post_id)

    print(f"Old method (raw SQL):        {old_raw_queries:3d} queries")
    print(f"Old method (ORM no eager):   {old_orm_queries:3d} queries")
    print(f"New method (eager loading):  {new_queries:3d} queries")
    print(f"Query reduction:             {old_orm_queries - new_queries} fewer queries")

    # Benchmark parameters
    iterations = 15

    print("\n" + "-" * 70)
    print(f"FETCH ONLY BENCHMARK ({iterations} iterations, {len(post_ids)} posts each)")
    print("-" * 70)

    old_raw_mean, old_raw_std, _ = benchmark_fetch_only(
        old_try_get_post_by_id, post_ids, iterations
    )
    old_orm_mean, old_orm_std, _ = benchmark_fetch_only(
        old_try_get_post_by_id_orm, post_ids, iterations
    )
    new_mean, new_std, _ = benchmark_fetch_only(
        new_get_post_by_id_optimized, post_ids, iterations
    )

    print(f"Old method (raw SQL):        {old_raw_mean*1000:8.2f}ms +/- {old_raw_std*1000:.2f}ms")
    print(f"Old method (ORM no eager):   {old_orm_mean*1000:8.2f}ms +/- {old_orm_std*1000:.2f}ms")
    print(f"New method (eager loading):  {new_mean*1000:8.2f}ms +/- {new_std*1000:.2f}ms")

    print("\n" + "-" * 70)
    print(f"FETCH + SERIALIZE BENCHMARK ({iterations} iterations, {len(post_ids)} posts each)")
    print("-" * 70)

    old_raw_mean, old_raw_std, _ = benchmark_fetch_and_serialize(
        old_try_get_post_by_id, post_ids, iterations
    )
    old_orm_mean, old_orm_std, _ = benchmark_fetch_and_serialize(
        old_try_get_post_by_id_orm, post_ids, iterations
    )
    new_mean, new_std, _ = benchmark_fetch_and_serialize(
        new_get_post_by_id_optimized, post_ids, iterations
    )

    print(f"Old method (raw SQL):        {old_raw_mean*1000:8.2f}ms +/- {old_raw_std*1000:.2f}ms")
    print(f"Old method (ORM no eager):   {old_orm_mean*1000:8.2f}ms +/- {old_orm_std*1000:.2f}ms")
    print(f"New method (eager loading):  {new_mean*1000:8.2f}ms +/- {new_std*1000:.2f}ms")

    # Calculate improvement
    if old_orm_mean > 0:
        improvement_pct = ((old_orm_mean - new_mean) / old_orm_mean) * 100
        speedup = old_orm_mean / new_mean if new_mean > 0 else float('inf')
        print(f"\nImprovement: {improvement_pct:.1f}% faster ({speedup:.2f}x speedup)")

    print("\n" + "-" * 70)
    print("SINGLE POST LATENCY TEST (100 iterations)")
    print("-" * 70)

    single_iterations = 100

    _, _, old_times = benchmark_fetch_and_serialize(
        old_try_get_post_by_id_orm, [test_post_id], single_iterations
    )
    _, _, new_times = benchmark_fetch_and_serialize(
        new_get_post_by_id_optimized, [test_post_id], single_iterations
    )

    print(f"Old method:")
    print(f"  Mean:   {statistics.mean(old_times)*1000:.2f}ms")
    print(f"  Median: {statistics.median(old_times)*1000:.2f}ms")
    print(f"  Min:    {min(old_times)*1000:.2f}ms")
    print(f"  Max:    {max(old_times)*1000:.2f}ms")
    print(f"  P95:    {sorted(old_times)[int(len(old_times)*0.95)]*1000:.2f}ms")

    print(f"\nNew method:")
    print(f"  Mean:   {statistics.mean(new_times)*1000:.2f}ms")
    print(f"  Median: {statistics.median(new_times)*1000:.2f}ms")
    print(f"  Min:    {min(new_times)*1000:.2f}ms")
    print(f"  Max:    {max(new_times)*1000:.2f}ms")
    print(f"  P95:    {sorted(new_times)[int(len(new_times)*0.95)]*1000:.2f}ms")

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    run_benchmark()
