#!/usr/bin/env bash

set -o errexit
set -o pipefail

# the number of CPUs + 1
WORKERS=$(( $(cat /proc/cpuinfo | grep -c processor) + 1 ))

echo "${WORKERS} workers will be used."

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Migrating Database"
python manage.py migrate

echo "Starting server..."
gunicorn core.asgi:application \
    -w "${WORKERS}" \
    -b 0.0.0.0:8000 \
    -k uvicorn.workers.UvicornWorker \
