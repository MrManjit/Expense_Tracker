# #!/usr/bin/env bash
# set -e

# echo "Applying database migrations..."
# python manage.py migrate --noinput

# echo "Collecting static files..."
# python manage.py collectstatic --noinput

# echo "Ensuring superuser exists..."
# python manage.py ensure_superuser

# echo "Starting Gunicorn..."
# exec gunicorn Expense_Tracker.wsgi:application \
#   --bind 0.0.0.0:${PORT:-8000} \
#   --workers 2 \
#   --timeout 120 \
#   --access-logfile '-' \
#   --error-logfile '-'


#!/usr/bin/env bash
set -Eeuo pipefail

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Optional: only if you have this management command; keep if it’s working
echo "Ensuring superuser exists..."
python manage.py ensure_superuser || true

echo "Starting Gunicorn..."
exec gunicorn Expense_Tracker.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers ${WEB_CONCURRENCY:-2} \
  --threads ${GUNICORN_THREADS:-2} \
  --worker-class gthread \
  --timeout ${GUNICORN_TIMEOUT:-90} \
  --graceful-timeout ${GUNICORN_GRACEFUL_TIMEOUT:-30} \
  --keep-alive ${GUNICORN_KEEPALIVE:-5} \
  --access-logfile '-' \
  --error-logfile '-' \
  --log-level ${GUNICORN_LOG_LEVEL:-info}