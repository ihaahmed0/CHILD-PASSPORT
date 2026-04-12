#!/bin/bash
set -e

echo "=========================================="
echo " App Startup — $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "=========================================="

cd /home/site/wwwroot

# Activate the virtual environment created by Oryx during deployment.
# This must exist — if it doesn't, the deployment itself failed.
if [ -f "antenv/bin/activate" ]; then
    echo "[startup] Activating antenv..."
    source antenv/bin/activate
else
    echo "[startup] ERROR: antenv not found. Was Oryx build enabled during deployment?"
    exit 1
fi

echo "[startup] Python: $(python --version)"
echo "[startup] Gunicorn: $(gunicorn --version)"

# Run database migrations (idempotent — safe to run on every boot)
echo "[startup] Running database migrations..."
python manage.py migrate --noinput

# Seed static/reference data
echo "[startup] Seeding assessment categories..."
python manage.py seed_assessment_categories 2>/dev/null || echo "[startup] Already seeded, skipping."

echo "[startup] Starting Gunicorn on port 8000..."
exec gunicorn childpassport.wsgi \
    --bind=0.0.0.0:8000 \
    --workers=2 \
    --timeout=120 \
    --preload \
    --access-logfile='-' \
    --error-logfile='-' \
    --log-level=info
