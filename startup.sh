set -e

echo "=== Custom Startup Script ==="

# Navigate to app directory
cd /home/site/wwwroot

# Install dependencies if not already installed
if [ ! -d "/home/site/wwwroot/antenv" ]; then
    echo "Installing dependencies..."
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
else
    echo "Dependencies already installed"
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput || echo "Migrations failed or already applied"

# Seed categories
echo "Seeding assessment categories..."
python manage.py seed_assessment_categories || echo "Categories already seeded"

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn --bind=0.0.0.0 --timeout 600 childpassport.wsgi