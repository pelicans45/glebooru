#!/bin/bash
# Server Startup Script
# =====================
# Starts the szurubooru API server using Granian (Rust-based HTTP server).
#
# Environment variables:
#   PORT        - Server port (default: 6666)
#   THREADS     - Blocking threads per worker (default: 4)
#   WORKERS     - Number of worker processes (default: 2)
#   BACKPRESSURE - Max concurrent requests per worker (default: 16)
#
# Tuning guidelines (for 2 vCPU / 2GB RAM server):
#   - WORKERS: Set to CPU core count (2)
#   - THREADS: Set to 2× WORKERS (4) - limited by GIL contention
#   - BACKPRESSURE: Keep low (16) to limit memory pressure
#   - Higher values increase throughput but use more memory

set -e
cd /opt/app

# Run database migrations
alembic upgrade head

# Default values tuned for 2 vCPU / 2GB RAM production server
PORT=${PORT:-6666}
WORKERS=${WORKERS:-2}
THREADS=${THREADS:-4}
BACKPRESSURE=${BACKPRESSURE:-16}

echo "Starting szurubooru API on port ${PORT}"
echo "Server: granian, Workers: ${WORKERS}, Threads: ${THREADS}, Backpressure: ${BACKPRESSURE}"
exec granian \
    --interface wsgi \
    --host 0.0.0.0 \
    --port ${PORT} \
    --workers ${WORKERS} \
    --blocking-threads ${THREADS} \
    --backpressure ${BACKPRESSURE} \
    --http1-keep-alive \
    szurubooru.facade:app
