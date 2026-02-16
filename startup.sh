#!/bin/bash

# Install dependencies if not already installed
if [ ! -d "/home/site/wwwroot/antenv" ]; then
    echo "Creating virtual environment and installing dependencies..."
    python -m venv /home/site/wwwroot/antenv
    source /home/site/wwwroot/antenv/bin/activate
    pip install --upgrade pip
    pip install -r /home/site/wwwroot/requirements.txt
else
    echo "Virtual environment exists, activating..."
    source /home/site/wwwroot/antenv/bin/activate
fi

cd /home/site/wwwroot

echo "Running migrations..."
python manage.py migrate --noinput

echo "Seeding assessment categories..."
python manage.py seed_assessment_categories || true

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Starting Gunicorn..."
gunicorn --bind=0.0.0.0 --timeout 600 childpassport.wsgi

