#!/usr/bin/env bash
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser if not exists....."
python manage.py createsuperuser --noinput || true

echo "Starting Gunicorn..."
exec gunicorn Expense_Tracker.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 2 \
  --timeout 120 \
  --access-logfile '-' \
  --error-logfile '-'