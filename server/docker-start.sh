#!/bin/bash
set -e
cd /opt/app

alembic upgrade head

#echo "Starting szurubooru API on port ${PORT} - Running on ${THREADS} threads"
exec waitress-serve --port ${PORT} --threads ${THREADS} szurubooru.facade:app
