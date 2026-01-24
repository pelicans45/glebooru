#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:4000/api}"
DURATION="${DURATION:-20}"
MODE="${MODE:-posts}"
CONCURRENCY="${CONCURRENCY:-8}"
POST_ID="${POST_ID:-}"
INTERVAL_US="${INTERVAL_US:-1000}"
CHILDREN="${CHILDREN:-1}"
AUSTIN_BIN="${AUSTIN_BIN:-/opt/app/.local/bin/austin}"

TS=$(date +"%Y%m%d-%H%M%S")
OUT="/data/perf-profiles/austin-${MODE}-${TS}.mojo"
AUSTIN_FORMAT_OUT="${OUT%.mojo}.austin"
SPEEDSCOPE_OUT="${OUT%.mojo}.speedscope.json"
TOOLS_DIR="/opt/app/.local/bin"
MOJO2AUSTIN_BIN="${MOJO2AUSTIN_BIN:-}"
SPEEDSCOPE_BIN="${SPEEDSCOPE_BIN:-}"

if ! docker compose -f docker-compose.dev.yml exec -T server sh -lc "[ -x \"${AUSTIN_BIN}\" ]"; then
  if docker compose -f docker-compose.dev.yml exec -T server sh -lc "command -v austin" >/dev/null 2>&1; then
    AUSTIN_BIN="austin"
  else
    echo "Austin not found. Install inside the container with:" >&2
    echo "  docker compose -f docker-compose.dev.yml exec server pip install --user austin-dist" >&2
    exit 1
  fi
fi

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
  > /tmp/austin-load-${MODE}-${TS}.log &
LOAD_PID=$!

docker compose -f docker-compose.dev.yml exec -T server sh -lc "mkdir -p /data/perf-profiles"

AUSTIN_CMD="${AUSTIN_BIN} -i ${INTERVAL_US} -p ${PID} -o ${OUT} -x ${DURATION}"
if [[ "${CHILDREN}" != "0" ]]; then
  AUSTIN_CMD="${AUSTIN_BIN} -C -i ${INTERVAL_US} -p ${PID} -o ${OUT} -x ${DURATION}"
fi

set +e
docker compose -f docker-compose.dev.yml exec -T server sh -lc "${AUSTIN_CMD}"
AUSTIN_STATUS=$?
set -e
if [[ ${AUSTIN_STATUS} -ne 0 ]]; then
  echo "Austin exited with status ${AUSTIN_STATUS}; continuing to copy output."
fi

wait "$LOAD_PID"

if [[ -z "${MOJO2AUSTIN_BIN}" ]]; then
  if docker compose -f docker-compose.dev.yml exec -T server sh -lc "[ -x \"${TOOLS_DIR}/mojo2austin\" ]"; then
    MOJO2AUSTIN_BIN="${TOOLS_DIR}/mojo2austin"
  elif docker compose -f docker-compose.dev.yml exec -T server sh -lc "command -v mojo2austin" >/dev/null 2>&1; then
    MOJO2AUSTIN_BIN="mojo2austin"
  fi
fi
if [[ -n "${MOJO2AUSTIN_BIN}" ]]; then
  docker compose -f docker-compose.dev.yml exec -T server sh -lc \
    "\"${MOJO2AUSTIN_BIN}\" \"${OUT}\" \"${AUSTIN_FORMAT_OUT}\""
fi

if [[ -z "${SPEEDSCOPE_BIN}" ]]; then
  if docker compose -f docker-compose.dev.yml exec -T server sh -lc "[ -x \"${TOOLS_DIR}/austin2speedscope\" ]"; then
    SPEEDSCOPE_BIN="${TOOLS_DIR}/austin2speedscope"
  elif docker compose -f docker-compose.dev.yml exec -T server sh -lc "command -v austin2speedscope" >/dev/null 2>&1; then
    SPEEDSCOPE_BIN="austin2speedscope"
  fi
fi
if [[ -n "${SPEEDSCOPE_BIN}" ]]; then
  docker compose -f docker-compose.dev.yml exec -T server sh -lc \
    "\"${SPEEDSCOPE_BIN}\" \"${AUSTIN_FORMAT_OUT}\" \"${SPEEDSCOPE_OUT}\""
fi

echo "Copying profile to doc/perf-profiles"
mkdir -p doc/perf-profiles
docker cp booru-server-1:${OUT} doc/perf-profiles/
if docker compose -f docker-compose.dev.yml exec -T server sh -lc "[ -f \"${AUSTIN_FORMAT_OUT}\" ]"; then
  docker cp booru-server-1:${AUSTIN_FORMAT_OUT} doc/perf-profiles/
fi
if docker compose -f docker-compose.dev.yml exec -T server sh -lc "[ -f \"${SPEEDSCOPE_OUT}\" ]"; then
  docker cp booru-server-1:${SPEEDSCOPE_OUT} doc/perf-profiles/
fi
