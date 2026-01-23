# Performance Upgrade Guide

This document describes the database and HTTP server performance optimizations implemented for glebooru.

## Summary of Changes

### 1. PostgreSQL 16 → 18.1 Upgrade

PostgreSQL 18 introduces Asynchronous I/O (AIO) which can provide **2-3x faster** read operations.

**Files Changed:**
- `docker-compose.yml` - Updated postgres image to 18.1
- `docker-compose.dev.yml` - Updated postgres image to 18.1
- `server/postgres/postgresql.conf` - New optimized configuration

**Key Features:**
- Asynchronous I/O with `io_method` setting (worker/io_uring)
- Optimized memory settings for 2GB RAM server
- Better autovacuum configuration
- JIT compilation enabled

**Volume Path Change:**
PostgreSQL 18 changed the data directory from `/var/lib/postgresql/data` to `/var/lib/postgresql/18/docker`. The docker-compose files have been updated to mount at `/var/lib/postgresql` for compatibility.

### 2. SQLAlchemy 1.4.46 → 2.0 Upgrade

SQLAlchemy 2.0 provides better performance through Cython extensions and improved ORM operations.

**Files Changed:**
- `server/requirements.txt` - Updated SQLAlchemy and related packages
- `server/szurubooru/model/base.py` - Fixed deprecated import
- `server/szurubooru/db.py` - Added connection pooling optimizations

**Performance Improvements:**
- 500% faster ORM inserts with "insertmanyvalues"
- Cython-based core for faster execution
- Better connection pooling with `pool_pre_ping`
- psycopg3 support for improved async capabilities

**Migration Notes:**
The legacy `.query()` method is deprecated but still works. For maximum performance, gradually migrate to the new `select()` syntax:

```python
# Old (deprecated but works)
posts = db.session.query(model.Post).filter(...).all()

# New (recommended)
from sqlalchemy import select
stmt = select(model.Post).where(...)
posts = db.session.execute(stmt).scalars().all()
```

### 3. HTTP Server (Granian)

Granian, a Rust-based HTTP server, is now the **only** supported HTTP server.
Waitress support has been removed to simplify deployment and improve throughput.

**Files Changed:**
- `server/requirements.txt` - Added granian, removed waitress
- `server/docker-start.sh` - Granian-only startup

**Usage:**
```bash
./d
```

**Granian Advantages:**
- High throughput for I/O-bound workloads
- Lower memory usage per worker
- Built on Rust's Tokio and Hyper for maximum efficiency

## Migration Procedure

### Development Environment

1. **Stop current containers:**
   ```bash
   docker compose -f docker-compose.dev.yml down
   ```

2. **Remove old PostgreSQL volume (data will be lost!):**
   ```bash
   docker volume rm szurubooru_db
   ```

3. **Start with new configuration:**
   ```bash
   ./d
   ```

### Production Environment

Use the migration script: `scripts/migrate-postgres-16-to-18.sh`

1. **Create backup only (safe to run anytime):**
   ```bash
   ./scripts/migrate-postgres-16-to-18.sh --backup-only
   ```

2. **Full migration (requires downtime):**
   ```bash
   ./scripts/migrate-postgres-16-to-18.sh
   ```

3. **Restore from backup if needed:**
   ```bash
   ./scripts/migrate-postgres-16-to-18.sh --restore-only /opt/backup/backup_file.sql.gz
   ```

## Benchmarking

### PostgreSQL AIO Modes

Benchmark different AIO modes to find the best for your storage:

```bash
# Quick benchmark with current settings
./scripts/benchmark-postgres-aio.sh --quick

# Full comparison of all modes
./scripts/benchmark-postgres-aio.sh --full

# Test specific mode
./scripts/benchmark-postgres-aio.sh --mode io_uring
```

**Recommendations:**
- **Network-attached storage (DigitalOcean, AWS EBS):** Use `io_method = worker`
- **Local NVMe/SSD:** Use `io_method = io_uring`

### HTTP Server Benchmarking

```bash
# Benchmark current server
./scripts/benchmark-http-servers.sh --quick

# Full benchmarking workflow
./scripts/benchmark-http-servers.sh --full
```

## Configuration Reference

### PostgreSQL Settings (postgresql.conf)

| Setting | Value | Description |
|---------|-------|-------------|
| `shared_buffers` | 384MB | ~25% of 2GB RAM |
| `effective_cache_size` | 1536MB | ~75% of RAM |
| `work_mem` | 16MB | Per-connection query memory |
| `io_method` | worker | AIO mode (worker/io_uring/sync) |
| `io_workers` | 4 | Background I/O workers |
| `random_page_cost` | 1.1 | Optimized for SSD |
| `effective_io_concurrency` | 200 | Concurrent I/O requests |

### SQLAlchemy Connection Pool

| Setting | Value | Description |
|---------|-------|-------------|
| `pool_size` | 10 | Base connections |
| `max_overflow` | 20 | Additional under load |
| `pool_pre_ping` | True | Validate connections |
| `pool_recycle` | 1800 | Recycle after 30 min |

### HTTP Server Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 6666 | Server port |
| `THREADS` | 4 | Blocking threads per worker |
| `WORKERS` | 2 | Worker processes (granian) |

## Rollback Procedure

### PostgreSQL Rollback

1. Stop services
2. Edit docker-compose.yml: change `postgres:18.1` back to `postgres:16`
3. Remove new volume
4. Restore from backup
5. Restart services

### SQLAlchemy Rollback

1. Edit `requirements.txt`: change `SQLAlchemy>=2.0.0` to `SQLAlchemy==1.4.46`
2. Revert `model/base.py` import
3. Rebuild Docker image

### HTTP Server Rollback

No rollback path for the HTTP server is documented; Granian is the only supported server.

## Performance Expectations

Based on benchmarks and documentation:

| Component | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Sequential scans | Baseline | 2-3x faster | PostgreSQL 18 AIO |
| Cold cache reads | Baseline | 2-3x faster | PostgreSQL 18 AIO |
| ORM inserts | Baseline | 5x faster | SQLAlchemy 2.0 |
| HTTP requests | Baseline | Higher | Granian |
| Memory usage | Baseline | Lower | Granian workers |

**Note:** Actual improvements depend on workload and hardware. Always benchmark in your environment.

## Monitoring

After upgrade, monitor these PostgreSQL metrics:

```sql
-- Check current io_method
SHOW io_method;

-- Monitor active connections
SELECT count(*) FROM pg_stat_activity;

-- Check slow queries
SELECT query, calls, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check cache hit ratio (should be >99%)
SELECT
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) AS ratio
FROM pg_statio_user_tables;
```

## Troubleshooting

### PostgreSQL 18 Won't Start

Check if the volume path is correct. PostgreSQL 18 uses `/var/lib/postgresql/18/docker` internally.

### io_uring Not Available

Requires Linux kernel 5.1+ and Postgres built with `--with-liburing`. The official Docker image includes io_uring support.

### Granian Module Not Found

Rebuild the Docker image to install granian:
```bash
docker compose build --no-cache server
```

### SQLAlchemy Deprecation Warnings

These are expected. The legacy `.query()` API still works. Set `SQLALCHEMY_WARN_20=1` to see all deprecation warnings if you want to migrate queries incrementally.
