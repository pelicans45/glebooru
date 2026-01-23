#!/bin/bash
# Server Startup Script
# =====================
# Starts the szurubooru API server with the specified HTTP server.
#
# Environment variables:
#   PORT     - Server port (default: 6666)
#   THREADS  - Number of threads (default: 4)
#   WORKERS  - Number of workers for granian (default: 2)

set -e
cd /opt/app

# Run database migrations
alembic upgrade head

# Default values
PORT=${PORT:-6666}
THREADS=${THREADS:-4}
WORKERS=${WORKERS:-2}

echo "Starting szurubooru API on port ${PORT}"
echo "Server: granian, Threads: ${THREADS}, Workers: ${WORKERS}"
echo "Using Granian HTTP server (Rust-based, high performance)"
exec granian \
    --interface wsgi \
    --host 0.0.0.0 \
    --port ${PORT} \
    --workers ${WORKERS} \
    --blocking-threads ${THREADS} \
    --backpressure 64 \
    szurubooru.facade:app
