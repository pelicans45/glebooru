#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:4000/api}"
DURATION="${DURATION:-20}"
MODE="${MODE:-posts}"
CONCURRENCY="${CONCURRENCY:-8}"
POST_ID="${POST_ID:-}"

TS=$(date +"%Y%m%d-%H%M%S")
OUT="/data/perf-profiles/pyspy-${MODE}-${TS}.svg"

PID=$(
  docker compose -f docker-compose.dev.yml exec -T server python - <<'PY'
import os

for pid in os.listdir("/proc"):
    if not pid.isdigit():
        continue
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as handle:
            cmdline = (
                handle.read()
                .replace(b"\x00", b" ")
                .decode("utf-8", errors="ignore")
            )
    except OSError:
        continue
    if "granian" in cmdline and "szurubooru.facade" in cmdline:
        print(pid)
        break
PY
)
if [[ -z "$PID" ]]; then
  echo "Unable to find granian PID" >&2
  exit 1
fi

echo "Profiling PID ${PID} for ${DURATION}s -> ${OUT}"

python scripts/load_api.py \
  --base-url "$BASE_URL" \
  --duration "$DURATION" \
  --concurrency "$CONCURRENCY" \
  --mode "$MODE" \
  ${POST_ID:+--post-id "$POST_ID"} \
  > /tmp/pyspy-load-${MODE}-${TS}.log &
LOAD_PID=$!

# Run py-spy inside the container (needs SYS_PTRACE)
docker compose -f docker-compose.dev.yml exec -T server sh -lc \
  "py-spy record --pid ${PID} --duration ${DURATION} --rate 100 --output ${OUT}"

wait "$LOAD_PID"

echo "Copying profile to doc/perf-profiles"
mkdir -p doc/perf-profiles
docker cp booru-server-1:${OUT} doc/perf-profiles/
