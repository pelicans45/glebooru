#!/usr/bin/env python3
"""
Benchmark script to compare old vs new post listing serialization.

This script measures the performance difference between:
1. Old method: Individual serialization with N+1 queries
2. New method: Batch serialization with pre-fetched data

Run with: python -m szurubooru.benchmark_post_listings
"""

import gc
import statistics
import time
from typing import List, Tuple
import sys
import os

# Ensure the parent module is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlalchemy as sa
from sqlalchemy import event

from szurubooru import config, db, model
from szurubooru.func import posts, scores, serialization


class MockUser:
    """Mock user for serialization."""
    user_id = 1
    name = "benchmark_user"
    rank = "regular"


class MockContext:
    """Mock context for API testing."""
    def __init__(self, user):
        self.user = user

    def get_param_as_list(self, name, default=None):
        return default


def old_serialize_posts(post_list: List[model.Post], auth_user) -> List[dict]:
    """Old method: Individual serialization (N+1 queries per post)."""
    return [
        posts.serialize_post(post, auth_user, options=[])
        for post in post_list
    ]


def new_serialize_posts_batch(post_list: List[model.Post], auth_user) -> List[dict]:
    """New method: Batch serialization with pre-fetched data."""
    return posts.serialize_posts_batch(post_list, auth_user, options=[])


def get_listing_posts(limit: int = 100) -> List[model.Post]:
    """Fetch posts as the listing endpoint would."""
    return (
        db.session.query(model.Post)
        .options(
            sa.orm.lazyload("*"),
            sa.orm.joinedload(model.Post.statistics),
        )
        .order_by(model.Post.post_id.desc())
        .limit(limit)
        .all()
    )


def count_queries_for_serialization(serialize_func, post_list: List[model.Post], auth_user) -> Tuple[int, float]:
    """Count SQL queries and measure time for a serialization function."""
    query_count = [0]
    engine = db.get_engine()

    def count_query(conn, cursor, statement, parameters, context, executemany):
        query_count[0] += 1

    event.listen(engine, "before_cursor_execute", count_query)

    try:
        db.session.expire_all()
        gc.collect()

        start = time.perf_counter()
        _ = serialize_func(post_list, auth_user)
        end = time.perf_counter()

    finally:
        event.remove(engine, "before_cursor_execute", count_query)
        db.session.rollback()

    return query_count[0], end - start


def benchmark_serialization(
    serialize_func, post_list: List[model.Post], auth_user, iterations: int = 10
) -> Tuple[float, float, List[float], int]:
    """Benchmark serialization function with query counting."""
    times = []
    total_queries = 0

    for i in range(iterations):
        gc.collect()
        db.session.expire_all()

        queries, elapsed = count_queries_for_serialization(serialize_func, post_list, auth_user)
        times.append(elapsed)
        if i == 0:
            total_queries = queries

    return (
        statistics.mean(times),
        statistics.stdev(times) if len(times) > 1 else 0,
        times,
        total_queries,
    )


def create_test_data(num_posts: int = 50):
    """Create test posts with relationships for benchmarking."""
    from datetime import datetime, timezone
    import random

    now = datetime.now(timezone.utc)
    print(f"Creating {num_posts} test posts for benchmarking...")

    # Create a test user
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

    # Create a tag category
    test_category = db.session.query(model.TagCategory).first()
    if not test_category:
        test_category = model.TagCategory()
        test_category.name = "default"
        test_category.color = "default"
        test_category.version = 1
        test_category.default = True
        db.session.add(test_category)
        db.session.flush()

    # Create tags
    test_tags = []
    existing_tags = db.session.query(model.Tag).limit(10).all()
    if len(existing_tags) >= 5:
        test_tags = existing_tags[:5]
    else:
        for i in range(5):
            tag = model.Tag()
            tag.category_id = test_category.tag_category_id
            tag.version = 1
            tag.creation_time = now
            db.session.add(tag)
            db.session.flush()
            tag_name = model.TagName(f"benchmark_tag_{i}", i)
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
        post.checksum = f"benchmark_listing_checksum_{i:08d}_{now.timestamp()}"
        post.mime_type = "image/png"
        post.canvas_width = 100
        post.canvas_height = 100
        post.file_size = 1000
        db.session.add(post)
        db.session.flush()

        # Add tags to each post
        for tag in random.sample(test_tags, min(3, len(test_tags))):
            post.tags.append(tag)

        # Add some scores and favorites for some posts
        if i % 3 == 0:
            score = model.PostScore()
            score.post_id = post.post_id
            score.user_id = test_user.user_id
            score.score = random.choice([-1, 1])
            score.time = now
            db.session.add(score)

        if i % 4 == 0:
            fav = model.PostFavorite()
            fav.post_id = post.post_id
            fav.user_id = test_user.user_id
            fav.time = now
            db.session.add(fav)

    db.session.commit()
    print(f"Created {num_posts} test posts with tags, scores, and favorites.")


def run_benchmark():
    """Run the full listing benchmark suite."""
    print("=" * 70)
    print("POST LISTING BENCHMARK")
    print("=" * 70)

    # Get posts for testing
    post_list = get_listing_posts(100)

    if len(post_list) < 20:
        print(f"Only {len(post_list)} posts found. Creating test data...")
        create_test_data(50)
        post_list = get_listing_posts(100)

    if not post_list:
        print("ERROR: Could not get posts for benchmark.")
        return

    print(f"\nTesting with {len(post_list)} posts")

    mock_user = MockUser()
    iterations = 10

    print("\n" + "-" * 70)
    print(f"SERIALIZATION BENCHMARK ({iterations} iterations)")
    print("-" * 70)

    # Benchmark old method
    old_mean, old_std, old_times, old_queries = benchmark_serialization(
        old_serialize_posts, post_list, mock_user, iterations
    )

    # Benchmark new method
    new_mean, new_std, new_times, new_queries = benchmark_serialization(
        new_serialize_posts_batch, post_list, mock_user, iterations
    )

    print(f"\nOld method (individual serialization):")
    print(f"  Queries:  {old_queries}")
    print(f"  Mean:     {old_mean*1000:.2f}ms +/- {old_std*1000:.2f}ms")
    print(f"  Min:      {min(old_times)*1000:.2f}ms")
    print(f"  Max:      {max(old_times)*1000:.2f}ms")

    print(f"\nNew method (batch serialization):")
    print(f"  Queries:  {new_queries}")
    print(f"  Mean:     {new_mean*1000:.2f}ms +/- {new_std*1000:.2f}ms")
    print(f"  Min:      {min(new_times)*1000:.2f}ms")
    print(f"  Max:      {max(new_times)*1000:.2f}ms")

    # Calculate improvements
    query_reduction = old_queries - new_queries
    query_reduction_pct = (query_reduction / old_queries * 100) if old_queries > 0 else 0

    time_improvement_pct = ((old_mean - new_mean) / old_mean * 100) if old_mean > 0 else 0
    speedup = old_mean / new_mean if new_mean > 0 else float('inf')

    print("\n" + "-" * 70)
    print("IMPROVEMENT SUMMARY")
    print("-" * 70)
    print(f"Query reduction:    {query_reduction} queries ({query_reduction_pct:.1f}% fewer)")
    print(f"Time improvement:   {time_improvement_pct:.1f}% faster ({speedup:.2f}x speedup)")

    # Test different batch sizes
    print("\n" + "-" * 70)
    print("BATCH SIZE SCALING TEST")
    print("-" * 70)

    for batch_size in [10, 25, 50, 100]:
        batch_posts = post_list[:batch_size]
        if len(batch_posts) < batch_size:
            continue

        old_queries_batch, _ = count_queries_for_serialization(old_serialize_posts, batch_posts, mock_user)
        new_queries_batch, _ = count_queries_for_serialization(new_serialize_posts_batch, batch_posts, mock_user)

        print(f"\nBatch size: {batch_size}")
        print(f"  Old queries: {old_queries_batch}")
        print(f"  New queries: {new_queries_batch}")
        print(f"  Reduction:   {old_queries_batch - new_queries_batch}")

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    run_benchmark()
