# Performance Optimization Plan (Option A Only: Statistics Tables + Triggers)

Date: 2026-01-23
Scope: Maximize read performance (gallery + post view latency) with a comprehensive, trigger-maintained statistics system.
Assumptions: tens of thousands of posts, many posts with 12+ tags, single-node deployment, no Redis.

---

## 1) Current Performance Hotspots (based on latest code)

These are the specific code paths that remain expensive even after recent optimizations:

- **Correlated aggregates in ORM models**
  - `server/szurubooru/model/tag.py`: `Tag.post_count` uses a correlated subquery on `post_tag`.
  - `server/szurubooru/model/post.py`: `tag_count`, `comment_count`, `favorite_count`, `score`, etc. are correlated subqueries.
  - Sorting by these fields (search configs) executes heavy SQL per query.

- **Tag usage in serialization + sorting**
  - `server/szurubooru/func/posts.py` uses batch prefetch for tag counts, but still queries `post_tag` counts on every listing request.
  - `server/szurubooru/func/tags.py` uses `tag.post_count` for usage and for sort order (even when preloaded counts aren’t passed).

- **Search sorting/filtering on counts**
  - `server/szurubooru/search/configs/post_search_config.py` sorts by `model.Post.tag_count` / `comment_count` / `score`, which are correlated subqueries.
  - `server/szurubooru/search/configs/tag_search_config.py` filters/sorts by `Tag.post_count` (correlated subquery).

Recent improvements (already present) reduce N+1, but do not fix the underlying cost of per-row aggregates. The fastest read-path solution is to precompute these counts in the database.

---

## 2) Target Architecture (Option A)

### Core Principle
All frequently used counts and sort keys must be stored in dedicated statistics tables and kept in sync via database triggers. This eliminates correlated subqueries and makes sorting/filtering O(1) per row.

### Statistics Tables (Design)

**database_statistics** (single-row table)
- `id` BOOLEAN PRIMARY KEY (always true)
- `post_count` BIGINT
- `tag_count` BIGINT
- `pool_count` BIGINT
- `user_count` BIGINT
- `comment_count` BIGINT

**tag_statistics**
- `tag_id` BIGINT PRIMARY KEY REFERENCES `tag` ON DELETE CASCADE
- `usage_count` BIGINT
- `suggestion_count` BIGINT
- `implication_count` BIGINT

**post_statistics**
- `post_id` BIGINT PRIMARY KEY REFERENCES `post` ON DELETE CASCADE
- `tag_count` BIGINT
- `pool_count` BIGINT
- `note_count` BIGINT
- `comment_count` BIGINT
- `relation_count` BIGINT
- `score` BIGINT
- `favorite_count` BIGINT
- `feature_count` BIGINT
- `last_comment_time` TIMESTAMPTZ
- `last_favorite_time` TIMESTAMPTZ
- `last_feature_time` TIMESTAMPTZ

**pool_statistics**
- `pool_id` BIGINT PRIMARY KEY REFERENCES `pool` ON DELETE CASCADE
- `post_count` BIGINT

**user_statistics**
- `user_id` BIGINT PRIMARY KEY REFERENCES `user` ON DELETE CASCADE
- `upload_count` BIGINT
- `comment_count` BIGINT
- `favorite_count` BIGINT

**comment_statistics**
- `comment_id` BIGINT PRIMARY KEY REFERENCES `comment` ON DELETE CASCADE
- `score` BIGINT

**(Optional but recommended)** category statistics (for fast category usage lists)
- `tag_category_statistics(category_id, usage_count)`
- `pool_category_statistics(category_id, usage_count)`

### Trigger Strategy

Use **DEFERRABLE INITIALLY DEFERRED** constraint triggers to reduce lock time and deadlock risk. Triggers must handle INSERT, DELETE, and UPDATE where relevant (especially for merge operations that use UPDATE).

Critical trigger cases:

- **post_tag**: UPDATE must adjust counts for both old and new tag_id/post_id pairs.
- **pool_post**: UPDATE must adjust counts for both old and new pool_id/post_id pairs.
- **tag_suggestion / tag_implication**: INSERT/DELETE update counts.
- **post_score**: INSERT/UPDATE/DELETE update post score.
- **post_favorite**: INSERT/DELETE update post favorite count, user favorite count, last_favorite_time.
- **comment**: INSERT/DELETE update post comment count, user comment count, database comment count, last_comment_time.
- **post_note**: INSERT/DELETE update note count.
- **post_relation**: INSERT/DELETE update relation count.
- **post_feature**: INSERT/DELETE update feature count + last_feature_time.
- **tag**: INSERT/DELETE update database tag_count and tag_category usage counts.
- **pool**: INSERT/DELETE/UPDATE update database pool_count and pool_category usage counts.
- **post**: INSERT/DELETE/UPDATE update database post_count.
- **user**: INSERT/DELETE/UPDATE update database user_count.

### Indexes (Read-Path Optimized)

- Existing: `post_tag(tag_id, post_id)` and `lower(tag_name)` index are already in place.
- Add B-tree indexes for top sort keys:
  - `tag_statistics(usage_count)`
  - `post_statistics(tag_count)`
  - `post_statistics(comment_count)`
  - `post_statistics(favorite_count)`
  - `post_statistics(score)`
  - `post_statistics(last_comment_time)`
  - `post_statistics(last_favorite_time)`
- Optional if wildcard search is common: enable `pg_trgm` and add trigram indexes on `tag_name.name` / `pool_name.name`.

---

## 3) Application Code Changes (Required)

### ORM Models

Add SQLAlchemy models for statistics tables and change usage to reference them directly.

- Replace correlated subqueries in `Tag` and `Post` with joined statistics columns.
  - `Tag.post_count` becomes `tag_statistics.usage_count`.
  - `Post.score`, `Post.favorite_count`, `Post.comment_count`, etc. read from `post_statistics`.

### Tag Sorting + Serialization

- Update `tags.sort_tags` to read usage counts from `tag_statistics` (preloaded by join) and remove reliance on correlated subquery fallback.
- Update `TagSerializer.serialize_usages` to read from stats table.

### Post Serialization

- Update `PostSerializer` to pull `score`, `favorite_count`, `comment_count`, `tag_count`, etc. from stats table.
- Remove any query that aggregates `post_tag` on the fly for usage counts.

### Search Configs

- **Post search**: join `post_statistics` in base query, update sort/filter columns to use stats fields.
- **Tag search**: join `tag_statistics`, update usage-count filters/sorts.
- Where possible, use `database_statistics` for count queries without filters (fast total count).

---

## 4) Database Migration Plan (Single Comprehensive Migration)

1. **Upgrade PostgreSQL 16 → 18** (already planned).
2. **Create statistics tables**.
3. **Backfill statistics** using INSERT … SELECT with GROUP BY:
   - Tag usage counts from `post_tag`.
   - Post counts, comment counts, favorite counts, etc. from their tables.
   - Database counts from main tables.
4. **Install triggers** (DEFERRABLE INITIALLY DEFERRED).
5. **Deploy code changes** to use stats tables.
6. **Verification step:**
   - Spot-check counts vs live aggregates for a random sample of posts/tags.
   - Ensure tag merges update counts correctly (test explicitly).

---

## 5) Deadlock and Write-Cost Mitigation

- Use DEFERRABLE INITIALLY DEFERRED triggers to keep locks short-lived.
- Enforce consistent update ordering for tag updates in multi-tag operations.
- If deadlocks appear under bursty updates, introduce a mutex for tag/post update transactions (Oxibooru-style).

---

## 6) Benchmarking Plan (Before vs After)

We will benchmark both the **original system** and the **new statistics system** using the same dataset and hardware.

### Test Environments

- **Baseline system**: current codebase + current schema.
- **Optimized system**: new codebase + statistics tables.
- Use identical hardware and dataset sizes.
- If upgrading to PG18 is part of the real deployment, run baselines on PG18 as well (to isolate code vs DB gains).

### Workload Categories

#### A) Gallery Load (Listing)
Use the same fields the client requests (from `client/js/controllers/post_list_controller_class.js`).

Request:
```
GET /api/posts?query=&limit=42&fields=id,thumbnailUrl,contentUrl,creationTime,type,safety,score,favoriteCount,commentCount,tagsBasic,version
```

Variants:
- With tag filter (common case): `query=tagme` (or common tag)
- With safety filter: `query=-rating:unsafe`
- With sort tag-count: `query=sort:tag-count`
- With large offset: `query=-rating:unsafe&offset=20000`

Metrics:
- p50, p95, p99 latency
- throughput (req/s)
- DB query time distribution (from `pg_stat_statements`)

#### B) Post View (Single Post)
Use the same fields the client requests (from `client/js/controllers/post_main_controller.js`).

Request:
```
GET /api/post/{id}?fields=id,version,creationTime,lastEditTime,safety,source,type,mimeType,checksum,checksumMD5,fileSize,canvasWidth,canvasHeight,duration,contentUrl,thumbnailUrl,flags,tags,relations,user,score,ownScore,ownFavorite,favoriteCount,commentCount,notes,comments
```

Metrics:
- p50/p95/p99 latency
- total DB query count per request

#### C) Tag List and Autocomplete
Requests from `client/js/models/tag_list.js`:

```
GET /api/tags?query=&limit=50&fields=names,suggestions,implications,creationTime,usages,category
GET /api/tags?query=sort:usages&limit=50&fields=names,suggestions,implications,creationTime,usages,category
GET /api/tags?query=e* sort:usages&limit=15&fields=names,category,usages
```

Metrics:
- latency percentiles
- CPU utilization

#### D) Post Upload (Write Path)
Test both small and large files.

Workflow:
1. POST `/api/posts` with 100 small images (e.g., 100KB each)
2. POST `/api/posts` with 5 large images (e.g., 50MB each)

Metrics:
- Total upload time
- DB transaction duration
- Trigger overhead

#### E) Tag Creation + Tag Update

Workflow:
1. Create 100 new tags via `/api/tags`
2. Bulk edit posts to add tags (e.g., add 12+ tags to a post set)
3. Tag merge test (merge tag A into tag B)

Metrics:
- p50/p95 latency per operation
- Deadlock rate (should be zero)
- Trigger overhead

---

## 7) Benchmark Tooling

Use a combination of HTTP benchmarking and DB-level query profiling:

- **HTTP load testing:** `wrk` or `hey` for simple endpoints, `vegeta` for scripted workloads.
- **DB profiling:** `pg_stat_statements` and `auto_explain` to capture slow queries.
- **System telemetry:** CPU, I/O, memory (e.g., `pidstat`, `iostat`, `pg_stat_activity`).

Recommended test flow:
1. Warm-up run to populate caches.
2. Cold run after restart to measure cold-start latency.
3. Sustained run (5–10 minutes) to measure steady-state performance.

---

## 8) Success Criteria

- Gallery listing p95 latency reduced by at least 2–5x on tag-heavy datasets.
- Post view p95 latency reduced by at least 2x.
- Tag list/autocomplete p95 latency reduced by 5–20x.
- No regression in correctness (counts match aggregates).

---

This plan is intentionally focused on the most aggressive, read-optimized solution (Option A) with no phased or conservative alternatives.
