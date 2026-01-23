#!/bin/bash
# Granian HTTP Server Startup Script
# ===================================
# Granian startup helper (Rust-based HTTP server).
# Note: docker-start.sh already launches Granian in normal usage.

set -e
cd /opt/app

# Run database migrations
alembic upgrade head

# Granian configuration
# - interface: wsgi (for our current WSGI app)
# - workers: number of worker processes (usually 1-2 per CPU core)
# - blocking-threads: threads per worker (for WSGI mode)
# - backpressure: prevents overloading the Python interpreter
#
# Note: For even better performance, convert to ASGI and use interface=asgi

WORKERS=${WORKERS:-2}
THREADS=${THREADS:-4}

echo "Starting szurubooru with Granian on port ${PORT}"
echo "Workers: ${WORKERS}, Threads per worker: ${THREADS}"

exec granian \
    --interface wsgi \
    --host 0.0.0.0 \
    --port ${PORT} \
    --workers ${WORKERS} \
    --blocking-threads ${THREADS} \
    --backpressure 64 \
    --log-level info \
    szurubooru.facade:app
