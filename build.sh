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

echo "Build complete!"
