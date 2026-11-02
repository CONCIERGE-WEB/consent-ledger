#!/bin/sh
set -eu

mkdir -p /data /app/staticfiles
chown app:app /data /app/staticfiles

gosu app python manage.py migrate --noinput
gosu app python manage.py collectstatic --noinput

exec gosu app gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --access-logfile - \
    --error-logfile -
