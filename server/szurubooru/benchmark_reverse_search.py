#!/usr/bin/env python3
"""
Simple benchmark for reverse-search (signature) and similar-by-tags.

Compares the current optimized code path with the legacy SQL approach
for signature search and the previous tag-overlap query pattern.
"""
from __future__ import annotations

import argparse
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import sqlalchemy as sa

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from szurubooru import db, model
from szurubooru.func import image_hash, posts, similar, tags


def _format_stats(samples: List[float]) -> Dict[str, float]:
    if not samples:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "avg": 0.0}
    ordered = sorted(samples)

    def pct(p: float) -> float:
        k = int(round((p / 100.0) * (len(ordered) - 1)))
        return ordered[max(0, min(len(ordered) - 1, k))]

    return {
        "p50": pct(50),
        "p95": pct(95),
        "p99": pct(99),
        "avg": statistics.mean(samples),
    }


def _old_search_by_signature(
    signature: image_hash.NpMatrix,
    limit: int,
    distance_cutoff: float,
    query: str | None,
) -> List[Tuple[float, model.Post]]:
    query_words = image_hash.generate_words(signature)

    dbquery = """
    SELECT s.post_id, s.signature, count(a.query) AS score
    FROM post_signature AS s
    CROSS JOIN LATERAL unnest(s.words, CAST(:q AS integer[])) AS a(word, query)
    {join_clause}
    WHERE a.word = a.query {where_clause}
    GROUP BY s.post_id
    ORDER BY score DESC LIMIT :limit;
    """

    join_clause = ""
    where_clause = ""
    params = {"q": query_words, "limit": limit}

    if query:
        join_clause = """
        JOIN post_tag pt ON s.post_id = pt.post_id
        JOIN tag t ON pt.tag_id = t.id
        JOIN tag_name tn ON t.id = tn.tag_id
        """
        where_clause = "AND tn.name = :query"
        params["query"] = query.lower()

    dbquery = dbquery.format(join_clause=join_clause, where_clause=where_clause)
    candidates = db.session.execute(sa.text(dbquery), params)
    data = tuple(
        zip(
            *[
                (post_id, image_hash.unpack_signature(packedsig))
                for post_id, packedsig, _score in candidates
            ]
        )
    )
    if not data:
        return []

    candidate_post_ids, sigarray = data
    distances = image_hash.normalized_distance(sigarray, signature)

    matching = [
        (pid, dist)
        for pid, dist in zip(candidate_post_ids, distances)
        if dist < distance_cutoff
    ]
    if not matching:
        return []

    post_ids = [pid for pid, _ in matching]
    posts_map = {p.post_id: p for p in posts.get_posts_by_ids(post_ids)}
    return [
        (dist, posts_map.get(pid))
        for pid, dist in matching
        if posts_map.get(pid) is not None
    ]


def _old_similar_by_tags(
    source_post: model.Post, limit: int
) -> List[model.Post]:
    db.session.expire(source_post, ["tags"])
    post_alias = sa.orm.aliased(model.Post)
    pt_alias = sa.orm.aliased(model.PostTag)
    result = (
        db.session.query(post_alias)
        .join(pt_alias, pt_alias.post_id == post_alias.post_id)
        .filter(pt_alias.tag_id.in_([tag.tag_id for tag in source_post.tags]))
        .filter(pt_alias.post_id != source_post.post_id)
        .group_by(post_alias.post_id)
        .order_by(sa.func.count(pt_alias.tag_id).desc())
        .order_by(post_alias.post_id.desc())
        .limit(limit)
        .all()
    )
    return result


def _benchmark(
    label: str,
    func: Callable[[], object],
    iterations: int,
) -> Dict[str, float]:
    times: List[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        _ = func()
        times.append(time.perf_counter() - start)
    stats = _format_stats(times)
    print(
        f"{label}: p50={stats['p50']:.4f}s "
        f"p95={stats['p95']:.4f}s "
        f"p99={stats['p99']:.4f}s avg={stats['avg']:.4f}s"
    )
    return stats


def _pick_source_post_id(min_tags: int) -> int:
    row = (
        db.session.query(model.PostStatistics.post_id)
        .filter(model.PostStatistics.tag_count >= min_tags)
        .limit(1)
        .one_or_none()
    )
    if row:
        return int(row[0])
    post = db.session.query(model.Post).limit(1).one()
    return int(post.post_id)


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark reverse search paths")
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--image", default="")
    parser.add_argument("--tag-query", default="")
    parser.add_argument("--min-tags", type=int, default=3)
    parser.add_argument("--output", default="doc/benchmark-reverse-search.md")
    args = parser.parse_args()

    sig_count = db.session.query(sa.func.count(model.PostSignature.post_id)).scalar() or 0
    signature_source = ""
    if args.image:
        content = Path(args.image).read_bytes()
        signature = image_hash.generate_signature(content)
        signature_source = f"image:{args.image}"
    else:
        sig_row = db.session.query(model.PostSignature).limit(1).first()
        if sig_row:
            signature = image_hash.unpack_signature(sig_row.signature)
            signature_source = "post_signature"
        else:
            default_image = Path("szurubooru/tests/assets/jpeg.jpg")
            if not default_image.exists():
                raise RuntimeError(
                    "No post signatures found and default test image missing."
                )
            content = default_image.read_bytes()
            signature = image_hash.generate_signature(content)
            signature_source = f"image:{default_image}"

    tag_query = args.tag_query.strip() or None

    print("Benchmarking reverse-search (signature)...")
    stats_old = _benchmark(
        "search_by_signature (legacy SQL)",
        lambda: _old_search_by_signature(
            signature, args.limit, image_hash.DISTANCE_CUTOFF, tag_query
        ),
        args.iterations,
    )
    stats_new = _benchmark(
        "search_by_signature (optimized)",
        lambda: posts.search_by_signature(
            signature, args.limit, image_hash.DISTANCE_CUTOFF, tag_query
        ),
        args.iterations,
    )

    print("Benchmarking similar-by-tags...")
    source_post_id = _pick_source_post_id(args.min_tags)
    source_post = posts.get_post_by_id(source_post_id)

    stats_similar_old = _benchmark(
        "similar_by_tags (legacy)",
        lambda: _old_similar_by_tags(source_post, args.limit),
        args.iterations,
    )
    stats_similar_new = _benchmark(
        "similar_by_tags (optimized)",
        lambda: similar.find_similar_posts(source_post, args.limit),
        args.iterations,
    )

    lines: List[str] = []
    lines.append("# Reverse Search / Similarity Benchmark")
    lines.append("")
    lines.append(f"Iterations: `{args.iterations}`")
    lines.append(f"Limit: `{args.limit}`")
    lines.append(f"Signature source: `{signature_source}`")
    lines.append(f"Signature rows: `{sig_count}`")
    if tag_query:
        lines.append(f"Tag query: `{tag_query}`")
    lines.append("")
    lines.append("## search_by_signature")
    lines.append("")
    lines.append("| Variant | p50 | p95 | p99 | avg |")
    lines.append("|---|---:|---:|---:|---:|")
    lines.append(
        f"| legacy SQL | {stats_old['p50']:.4f} | {stats_old['p95']:.4f} | "
        f"{stats_old['p99']:.4f} | {stats_old['avg']:.4f} |"
    )
    lines.append(
        f"| optimized | {stats_new['p50']:.4f} | {stats_new['p95']:.4f} | "
        f"{stats_new['p99']:.4f} | {stats_new['avg']:.4f} |"
    )
    lines.append("")
    lines.append("## similar_by_tags")
    lines.append("")
    lines.append(f"Source post: `{source_post_id}`")
    lines.append("")
    lines.append("| Variant | p50 | p95 | p99 | avg |")
    lines.append("|---|---:|---:|---:|---:|")
    lines.append(
        f"| legacy | {stats_similar_old['p50']:.4f} | {stats_similar_old['p95']:.4f} | "
        f"{stats_similar_old['p99']:.4f} | {stats_similar_old['avg']:.4f} |"
    )
    lines.append(
        f"| optimized | {stats_similar_new['p50']:.4f} | {stats_similar_new['p95']:.4f} | "
        f"{stats_similar_new['p99']:.4f} | {stats_similar_new['avg']:.4f} |"
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n")
    print(f"Wrote benchmark report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
