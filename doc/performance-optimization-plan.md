# Performance Optimization Plan (Backend + DB)

Date: 2026-01-23
Scope: Reduce latency for gallery listings and individual post views, prioritizing DB query time and serialization overhead.
Assumptions: tens of thousands of posts, many posts with 12+ tags, single-node deployment, no Redis.
Goal: fastest possible reads even if it requires significant schema/code changes and a migration process.

## Executive Summary

The dominant latency drivers in the current codebase are correlated per-row aggregates (tag usage counts, post counts, score, favorite count, comment count) and filesystem disk-usage scanning at startup. The most comprehensive and fastest read-path solution is to introduce precomputed statistics tables maintained by database triggers (Oxibooru-style), then rewrite search/sort/serialization to read from those tables instead of correlated subqueries.

This approach trades a moderate increase in write cost for large reductions in read latency, and it scales far better for tag-heavy posts and usage-count sorts. Given your goal (fastest reads) and the willingness to accept heavier migrations, this is the recommended path.

## Research Notes

### Upstream issue rr-/szurubooru#608 ("Tag-post counting and storage counter causes slow page loading times")

Key observations:
- Tag usage counts are computed dynamically and can take several seconds per post on large datasets.
- A workaround that set usages to 0 in `posts.py` significantly improved load times.
- A trigger-based tag usage table worked well for reads but introduced correctness issues around tag merges.
- Disk usage calculation on `/api/info` is slow because it walks the filesystem and is not persistent across restarts.

### Oxibooru (Rust fork) optimizations relevant to us

Oxibooru’s most impactful optimizations are DB-side statistics tables maintained by triggers:
- `database_statistics` for global counts and disk usage
- `tag_statistics`, `post_statistics`, `pool_statistics`, `user_statistics`, `comment_statistics`
- DEFERRABLE INITIALLY DEFERRED triggers to reduce lock time
- Searches and sorts use the statistics tables directly
- Extra indexes for wildcard tag/pool name search and composite `post_tag(tag_id, post_id)`

This aligns directly with the performance problems seen in issue #608.

### Current state of our fork (not exhaustive)

Already in place:
- PostgreSQL 18 + SQLAlchemy 2.0 + Granian (see `PERFORMANCE_UPGRADE.md`)
- Batch post serialization with tag usage prefetch to reduce N+1 in listing responses
- Composite index `post_tag(tag_id, post_id)` and `lower(tag_name)` index
- Optimized random post path for tag-only queries

Still expensive:
- Tag usage count is a correlated subquery (`Tag.post_count`)
- Post stats (score, favorite_count, comment_count, tag_count) are correlated subqueries
- Sorting/filtering by those counts triggers heavy DB work
- `/api/info` disk usage still walks the filesystem

## Option Comparison (Answering the "Option C" question)

**Option A (statistics tables + triggers) vs Option C (materialized views / periodic refresh):**

- **Read speed:** Both can be very fast *if* the data is precomputed and indexed. Option A is always fresh; Option C is only as fresh as the last refresh.
- **Write cost:** Option C has lower per-write overhead (no triggers), but it shifts the cost to refresh time. If you refresh frequently enough to keep data fresh for UI sorts (tag usage, score), the refresh can be expensive and sometimes blocking. Option A pays a smaller cost on each write but avoids heavy refresh spikes.
- **Staleness:** Option C trades correctness for performance. Sorting by usage counts with stale data can lead to confusing results.
- **Operational impact:** Option C needs a scheduled refresh strategy and careful management of concurrent refreshes, plus extra disk space for MV indexes.

**Bottom line:** Option C can be fast for reads and cheaper per write, but only if you can tolerate staleness and expensive refresh operations. If you need fast *and* accurate sorts/filters (gallery, tag list, autocomplete), Option A is the fastest and most reliable approach long-term.

Given your goals, Option A is the best fit.

## Recommended Strategy (Fastest Full Solution)

Implement a full Oxibooru-style statistics system in one comprehensive migration, and refactor the API to read from it.

### Core Tables to Add

- `database_statistics` (disk_usage, post_count, tag_count, pool_count, user_count, comment_count)
- `tag_statistics` (usage_count, suggestion_count, implication_count)
- `post_statistics` (tag_count, comment_count, favorite_count, score, note_count, relation_count, feature_count, last_* timestamps)
- `pool_statistics` (post_count)
- `user_statistics` (upload_count, comment_count, favorite_count)
- `comment_statistics` (score)

### Triggers to Add (DEFERRABLE INITIALLY DEFERRED)

- `post_tag`: updates `post_statistics.tag_count` and `tag_statistics.usage_count`
- `post_score`: updates `post_statistics.score`
- `post_favorite`: updates `post_statistics.favorite_count`, `user_statistics.favorite_count`, and last_favorite_time
- `comment`: updates `post_statistics.comment_count`, `user_statistics.comment_count`, `database_statistics.comment_count` and last_comment_time
- `post_note`: updates `post_statistics.note_count`
- `post_relation`: updates `post_statistics.relation_count`
- `post_feature`: updates `post_statistics.feature_count` and last_feature_time
- `tag`: updates `database_statistics.tag_count`, `tag_category_statistics`
- `tag_suggestion`/`tag_implication`: update `tag_statistics`
- `pool`/`pool_post`: update `pool_statistics`, `post_statistics.pool_count`, `database_statistics.pool_count`
- `user`: updates `database_statistics.user_count`
- `post`: updates `database_statistics.post_count`, `database_statistics.disk_usage`

### Code Changes (Backend)

- Remove or bypass correlated subqueries in ORM models:
  - Tag: replace `Tag.post_count` with join to `tag_statistics`
  - Post: replace `score`, `favorite_count`, `comment_count`, `tag_count`, etc. with `post_statistics`
- Update search configs for tags and posts to use statistics columns for filtering and sorting
- Update serialization to use statistics values, not correlated subqueries
- Update `/api/info` to read disk usage and counts from `database_statistics`

### Write Cost Considerations

- Expect increased cost for updates that modify many tags or multiple statistics.
- Use DEFERRABLE INITIALLY DEFERRED triggers to shorten lock windows.
- Ensure tag/post update transactions always modify counts in a consistent order.
- If deadlocks appear under bursty updates, consider a per-post update mutex in application code (as Oxibooru does).

## Migration Plan (Single Comprehensive Migration)

1. **PostgreSQL 18 upgrade** (already planned).
2. **Add new statistics tables.**
3. **Backfill statistics** in a single migration:
   - Use INSERT ... SELECT with GROUP BY to compute initial counts.
   - Update `database_statistics` and disk_usage from `post.file_size` + thumbnails.
4. **Install triggers** (DEFERRABLE INITIALLY DEFERRED).
5. **Deploy code changes** to use stats tables.
6. **Run verification job**:
   - Compare precomputed counts vs live aggregates for a random sample.
7. **Add admin tasks**:
   - Recompute all statistics (full rebuild).
   - Recompute disk usage from data directory if needed.

## Additional Read-Path Optimizations (Safe, Still Comprehensive)

- Keep batch serialization for posts; extend it to always use stats tables.
- Add keyset pagination for gallery and tag lists to avoid large OFFSET costs.
- Add trigram indexes (`pg_trgm`) for wildcard tag/pool name search if queries use `%foo%` patterns.

## Risks and Mitigations

- **Deadlocks on tag updates:** Use deferred triggers and consistent update ordering; consider app-level mutex around multi-tag edits.
- **Drift in statistics:** Provide admin task to rebuild all stats and add periodic verification.
- **Migration time:** Backfills on large datasets will take time and can lock tables. Run during a maintenance window.

## Decision Summary

- Option A (full statistics + triggers) is the fastest and most consistent for read-heavy workloads and tag-heavy posts.
- Option C (materialized views) could reduce write overhead but introduces staleness and expensive refresh spikes. It is not ideal for fast, correct sorting/filtering in gallery and tag lists.

