# Quick Start Guide

## Prerequisites
- Python 3.11+
- GCC compiler (MinGW on Windows, gcc on Linux/Mac)
- Git (for deployment)

## Local Development Setup (Windows)

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Compile C Engine
```powershell
# Windows
.\build_c.bat

# Linux/Mac
make c_interface
```

### 3. Setup Environment
```powershell
# Copy example env file
copy .env.example .env
# Edit .env if needed (default values work for local dev)
```

### 4. Initialize Database
```powershell
python manage.py migrate
python manage.py createsuperuser
```

### 5. Import Initial Movie Data
```powershell
python manage.py shell
```
Then in Python shell:
```python
from movies.c_engine import CSVSync
CSVSync.import_movies()
exit()
```

### 6. Run Development Server
```powershell
python manage.py runserver
```

Visit: http://localhost:8000

## First Steps

1. **Login to Admin**: http://localhost:8000/admin
   - Add movies with posters
   - View users and ratings

2. **Register a User Account**
   - Go to http://localhost:8000/register
   - Create account with age

3. **Rate Some Movies**
   - Browse movies
   - Rate at least 3-5 movies

4. **Get Recommendations**
   - Visit "Recommendations" in navbar
   - See personalized suggestions from C engine

## Adding Sample Data via Admin

1. Login to admin panel
2. Add movies manually:
   - Movie ID: 501 (use numbers > 500 to avoid conflicts)
   - Title: Your Movie Title
   - Genre: Action/Drama/Comedy/etc
   - Year: 2024
   - Upload poster image (optional, stored locally in dev)

## Testing the C Engine Directly

```powershell
# Test recommendations for user 101
.\c_interface.exe recommend 101 5

# Add a rating
.\c_interface.exe add_rating 101 1 5.0
```

## Common Issues

### C Engine Not Compiling
- Install MinGW on Windows: https://www.mingw-w64.org/
- Add gcc to PATH
- Alternative: Use WSL (Windows Subsystem for Linux)

### Recommendations Empty
- Ensure user has rated some movies
- Run: `python manage.py sync_csv` to sync data
- Check that CSV files exist and have data

### Import Errors
- Run `pip install -r requirements.txt` again
- Check Python version: `python --version` (should be 3.11+)

## Production Deployment

See README.md for full deployment instructions to Render.

## Project Structure Quick Reference

```
DSA EL/
├── c_interface.exe        # Compiled C engine (Windows)
├── *.csv                  # Data files for C engine
├── manage.py              # Django management
├── movies/                # Main Django app
│   ├── views.py          # Web views
│   ├── models.py         # Database models
│   ├── c_engine.py       # Python wrapper for C
│   └── templates/        # HTML templates
└── movie_site/           # Django settings
    └── settings.py
```

## Development Workflow

1. Make changes to Django code
2. Run server: `python manage.py runserver`
3. Test changes at http://localhost:8000
4. Sync data: `python manage.py sync_csv`
5. Test C engine: `.\c_interface.exe recommend <user_id> 10`

## Next Steps

- Configure AWS S3 for poster storage (see README.md)
- Deploy to Render (see README.md)
- Add more movies via admin panel
- Customize templates in `movies/templates/`
