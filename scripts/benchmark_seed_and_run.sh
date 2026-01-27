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

WITH_FILES="${WITH_FILES:-1}"
FILE_VARIANTS="${FILE_VARIANTS:-64}"
IMAGE_WIDTH="${IMAGE_WIDTH:-640}"
IMAGE_HEIGHT="${IMAGE_HEIGHT:-360}"
THUMB_WIDTH="${THUMB_WIDTH:-300}"
THUMB_HEIGHT="${THUMB_HEIGHT:-300}"
SKEWED_TAGS="${SKEWED_TAGS:-1}"
ZIPF_ALPHA="${ZIPF_ALPHA:-1.1}"
EXCLUSION_TAG_RATE="${EXCLUSION_TAG_RATE:-0.10}"

ITERATIONS="${ITERATIONS:-30}"
CONCURRENCY="${CONCURRENCY:-5}"
TIMEOUT="${TIMEOUT:-20}"
WARMUP="${WARMUP:-3}"

mkdir -p "$(dirname "$OUTPUT")"

FILE_ARGS=()
if [[ "$WITH_FILES" == "1" ]]; then
    FILE_ARGS=(
        --with-files
        --file-variants "$FILE_VARIANTS"
        --image-width "$IMAGE_WIDTH"
        --image-height "$IMAGE_HEIGHT"
        --thumb-width "$THUMB_WIDTH"
        --thumb-height "$THUMB_HEIGHT"
    )
fi

TAG_ARGS=()
if [[ "$SKEWED_TAGS" == "1" ]]; then
    TAG_ARGS=(--skewed-tags --zipf-alpha "$ZIPF_ALPHA")
fi
if [[ -n "$EXCLUSION_TAG_RATE" ]]; then
    TAG_ARGS+=(--exclusion-tag-rate "$EXCLUSION_TAG_RATE")
fi

docker compose -f docker-compose.dev.yml stop server
docker compose -f docker-compose.dev.yml run --rm -w /opt/app server \
    python -m szurubooru.benchmark_seed_dataset \
    --posts "$POSTS" \
    --tagged-posts "$TAGGED_POSTS" \
    --min-tags "$MIN_TAGS" \
    --max-tags "$MAX_TAGS" \
    --tags "$TAGS" \
    --seed "$SEED" \
    "${FILE_ARGS[@]}" \
    "${TAG_ARGS[@]}"
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
