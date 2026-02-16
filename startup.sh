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

# Run migrations
python /home/site/wwwroot/manage.py migrate --noinput

# Start Gunicorn
gunicorn --bind=0.0.0.0 --timeout 600 --chdir /home/site/wwwroot childpassport.wsgi
