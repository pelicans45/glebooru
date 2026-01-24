#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:4000/api}"
OUTPUT="${OUTPUT:-doc/benchmark-results-pre-implementation-50k.md}"
SEED="${SEED:-1337}"
TITLE="${TITLE:-Pre-Implementation Benchmark (50k posts, seed ${SEED})}"

POSTS="${POSTS:-50000}"
TAGGED_POSTS="${TAGGED_POSTS:-40000}"
MIN_TAGS="${MIN_TAGS:-1}"
MAX_TAGS="${MAX_TAGS:-20}"
TAGS="${TAGS:-2000}"

ITERATIONS="${ITERATIONS:-30}"
CONCURRENCY="${CONCURRENCY:-5}"
TIMEOUT="${TIMEOUT:-20}"
WARMUP="${WARMUP:-3}"

mkdir -p "$(dirname "$OUTPUT")"

docker compose -f docker-compose.dev.yml stop server
docker compose -f docker-compose.dev.yml run --rm -w /opt/app server \
    python -m szurubooru.benchmark_seed_dataset \
    --posts "$POSTS" \
    --tagged-posts "$TAGGED_POSTS" \
    --min-tags "$MIN_TAGS" \
    --max-tags "$MAX_TAGS" \
    --tags "$TAGS" \
    --seed "$SEED"
docker compose -f docker-compose.dev.yml up -d server

python - <<'PY'
import os
import time
import urllib.error
import urllib.request

base_url = os.environ.get("BASE_URL", "http://localhost:4000/api").rstrip("/")
url = f"{base_url}/posts?limit=1&fields=id"
deadline = time.time() + 60

while True:
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            if resp.status == 200:
                break
    except Exception:
        pass
    if time.time() >= deadline:
        raise SystemExit("API did not become ready within 60s")
    time.sleep(1)
PY

python scripts/benchmark_api.py \
    --base-url "$BASE_URL" \
    --iterations "$ITERATIONS" \
    --concurrency "$CONCURRENCY" \
    --timeout "$TIMEOUT" \
    --warmup "$WARMUP" \
    --output "$OUTPUT" \
    --title "$TITLE"
