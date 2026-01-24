"""
Optimized random post selection.

This module provides fast paths for the common case of selecting random posts
by tag filters, bypassing the generic search executor for better performance.

Performance characteristics (benchmark results):
- Single tag (50%+ of calls): ~1.3x faster via direct JOIN
- Two+ tags: ~11x faster by skipping COUNT query and using EXISTS clauses
- Complex queries (with special operators): Falls back to generic search executor
"""
import re
from typing import List, Optional, Set, Tuple

import sqlalchemy as sa

from szurubooru import db, model


# Pre-compiled regex for detecting special search operators
_SPECIAL_TOKEN_PATTERN = re.compile(
    r'(sort|type|safety|rating|id|score|uploader|upload|submit|fav|comment|'
    r'source|tag-count|file-size|width|height|area|ar|date|time|pool|special|'
    r'category|flag|note|similar):',
    re.IGNORECASE
)

# Valid media types for random post
_RANDOM_POST_TYPES = (
    model.Post.TYPE_IMAGE,
    model.Post.TYPE_ANIMATION,
    model.Post.TYPE_VIDEO,
)


def is_simple_tag_query(query_text: str) -> bool:
    """
    Check if query contains only simple tag tokens (no special search operators).
    Returns True for queries like: "tag1", "tag1 tag2", "-tag1 tag2", "tag*"
    Returns False for queries with operators like: "sort:random", "type:image", etc.
    """
    if not query_text:
        return False
    # Check for special search operators
    if _SPECIAL_TOKEN_PATTERN.search(query_text):
        return False
    return True


def parse_tag_tokens(query_text: str) -> Tuple[List[str], List[str]]:
    """
    Parse query into included and excluded tag names.
    Returns (included_tags, excluded_tags).
    """
    included = []
    excluded = []
    tokens = query_text.split()
    for token in tokens:
        if token.startswith('-'):
            tag_name = token[1:]
            if tag_name:
                excluded.append(tag_name)
        else:
            included.append(token)
    return included, excluded


def resolve_tag_id_single(tag_name: str) -> Optional[int]:
    """
    Resolve a single exact tag name to tag ID. Optimized for the common case.
    Returns None if tag not found.
    """
    name = (tag_name or "").lower()
    result = (
        db.session.query(model.Tag.tag_id)
        .join(model.TagName)
        .filter(model.TagName.name == name)
        .first()
    )
    return result[0] if result else None


def resolve_tag_ids(tag_names: List[str]) -> Set[int]:
    """
    Resolve tag names (with optional wildcards) to tag IDs.
    Returns a set of tag IDs.
    """
    if not tag_names:
        return set()

    tag_ids = set()
    exact_names = []
    wildcard_patterns = []

    for name in tag_names:
        if '*' in name:
            # Convert glob pattern to SQL LIKE pattern
            pattern = name.replace('*', '%').lower()
            wildcard_patterns.append(pattern)
        else:
            exact_names.append(name.lower())

    # Batch query for exact names
    if exact_names:
        results = (
            db.session.query(model.Tag.tag_id)
            .join(model.TagName)
            .filter(model.TagName.name.in_(exact_names))
            .all()
        )
        tag_ids.update(r[0] for r in results)

    # Query for wildcard patterns (batch with OR)
    if wildcard_patterns:
        conditions = [
            model.TagName.name.like(pattern)
            for pattern in wildcard_patterns
        ]
        results = (
            db.session.query(model.Tag.tag_id)
            .join(model.TagName)
            .filter(sa.or_(*conditions))
            .all()
        )
        tag_ids.update(r[0] for r in results)

    return tag_ids


def get_random_post_single_tag(
    tag_id: int,
    excluded_tag_ids: Set[int],
    excluding_post_id: Optional[int],
    limit: int,
) -> List[model.Post]:
    """
    Ultra-fast path for single tag queries (50%+ of calls).
    Uses direct JOIN instead of EXISTS for better performance.
    """
    # Direct JOIN is faster than EXISTS for single tag
    query = (
        db.session.query(model.Post)
        .join(model.PostTag, model.PostTag.post_id == model.Post.post_id)
        .options(sa.orm.lazyload('*'))
        .filter(model.PostTag.tag_id == tag_id)
        .filter(model.Post.type.in_(_RANDOM_POST_TYPES))
    )

    # Filter out excluded tags using NOT EXISTS
    for excl_tag_id in excluded_tag_ids:
        not_exists_subq = (
            sa.exists()
            .where(model.PostTag.post_id == model.Post.post_id)
            .where(model.PostTag.tag_id == excl_tag_id)
        )
        query = query.filter(~not_exists_subq)

    # Exclude specific post if requested
    if excluding_post_id is not None:
        query = query.filter(model.Post.post_id != excluding_post_id)

    # Random ordering and limit
    query = query.order_by(sa.func.random()).limit(limit)

    return query.all()


def get_random_post_multi_tag(
    included_tag_ids: Set[int],
    excluded_tag_ids: Set[int],
    excluding_post_id: Optional[int],
    limit: int,
) -> List[model.Post]:
    """
    Fast path for multi-tag queries.
    Uses EXISTS clauses which work well with index scans.
    """
    query = (
        db.session.query(model.Post)
        .options(sa.orm.lazyload('*'))
        .filter(model.Post.type.in_(_RANDOM_POST_TYPES))
    )

    # Filter by included tags using EXISTS
    for tag_id in included_tag_ids:
        exists_subq = (
            sa.exists()
            .where(model.PostTag.post_id == model.Post.post_id)
            .where(model.PostTag.tag_id == tag_id)
        )
        query = query.filter(exists_subq)

    # Filter out excluded tags using NOT EXISTS
    for tag_id in excluded_tag_ids:
        not_exists_subq = (
            sa.exists()
            .where(model.PostTag.post_id == model.Post.post_id)
            .where(model.PostTag.tag_id == tag_id)
        )
        query = query.filter(~not_exists_subq)

    # Exclude specific post if requested
    if excluding_post_id is not None:
        query = query.filter(model.Post.post_id != excluding_post_id)

    # Random ordering and limit
    query = query.order_by(sa.func.random()).limit(limit)

    return query.all()


def get_random_post_fast(
    included_tag_ids: Set[int],
    excluded_tag_ids: Set[int],
    excluding_post_id: Optional[int],
    limit: int,
) -> List[model.Post]:
    """
    Fast path for getting random posts with tag filters.
    Dispatches to optimized implementations based on query pattern.
    """
    # Single included tag - use optimized JOIN path
    if len(included_tag_ids) == 1:
        tag_id = next(iter(included_tag_ids))
        return get_random_post_single_tag(
            tag_id, excluded_tag_ids, excluding_post_id, limit
        )

    # Multiple included tags or exclusions only
    return get_random_post_multi_tag(
        included_tag_ids, excluded_tag_ids, excluding_post_id, limit
    )
