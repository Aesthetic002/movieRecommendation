#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Compiling C recommendation engine..."
# Check if gcc is available
if command -v gcc &> /dev/null; then
    echo "GCC found, compiling C interface..."
    make clean || true
    make c_interface
else
    echo "WARNING: GCC not found, skipping C compilation"
    echo "The recommendation engine may not work properly"
fi

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

echo "Importing initial data..."
python manage.py shell << END
from movies.c_engine import CSVSync
from movies.models import Movie, UserProfile
import os

# Import movies from CSV if they exist
if os.path.exists('movies.csv') and Movie.objects.count() == 0:
    CSVSync.import_movies()
    print(f"Imported {Movie.objects.count()} movies")
else:
    print(f"Movies already imported: {Movie.objects.count()}")
END

echo "Build complete!"
