#!/bin/bash
echo "=========================================="
echo " App Startup — $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "=========================================="

cd /home/site/wwwroot

# ── Activate virtual environment ─────────────────────
# Oryx creates 'antenv' during deployment when
# SCM_DO_BUILD_DURING_DEPLOYMENT=true.
# If it doesn't exist yet (e.g. first deploy after
# switching to Oryx), fall through to system Python —
# Azure's runtime already has Django in PATH.
if [ -f "antenv/bin/activate" ]; then
    echo "[startup] Activating Oryx antenv..."
    source antenv/bin/activate
else
    echo "[startup] antenv not found — using system Python."
    echo "[startup] Tip: ensure SCM_DO_BUILD_DURING_DEPLOYMENT=true in App Settings."
fi

echo "[startup] Python  : $(python --version 2>&1)"
echo "[startup] Gunicorn: $(gunicorn --version 2>&1)"
echo "[startup] WorkDir : $(pwd)"

# ── Database migrations ───────────────────────────────
# Run on every boot so code and schema stay in sync.
# Non-fatal: a migration failure should not prevent the
# app from starting — existing routes still work.
echo "[startup] Running database migrations..."
python manage.py migrate --noinput || echo "[startup] WARNING: migrate failed — check DB env vars."

# ── Seed reference data ───────────────────────────────
echo "[startup] Seeding assessment categories..."
python manage.py seed_assessment_categories 2>/dev/null || true

# ── Start Gunicorn ────────────────────────────────────
echo "[startup] Starting Gunicorn on 0.0.0.0:8000 ..."
exec gunicorn childpassport.wsgi \
    --bind=0.0.0.0:8000 \
    --workers=2 \
    --timeout=120 \
    --preload \
    --access-logfile='-' \
    --error-logfile='-' \
    --log-level=info
