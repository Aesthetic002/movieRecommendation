#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Compiling C recommendation engine..."
make c_interface

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

echo "Creating initial data..."
python manage.py shell << END
from movies.c_engine import CSVSync
from movies.models import Movie
import os

# Import movies from CSV if they exist
if os.path.exists('movies.csv'):
    CSVSync.import_movies()
    print("Movies imported from CSV")
else:
    print("No movies.csv found")
END

echo "Build complete!"
