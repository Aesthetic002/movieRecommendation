# Deployment Guide

## Overview

The application is configured for deployment on Render.com with PostgreSQL database and optional AWS S3 for media storage.

---

## Local Development Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Compile C Engine
```bash
# Windows
.\build_c.bat

# Linux/Mac
make c_interface
```

### 3. Setup Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Import Data
```bash
python manage.py shell
>>> from movies.c_engine import CSVSync
>>> CSVSync.import_movies()
>>> exit()
```

### 6. Run Server
```bash
python manage.py runserver
# Visit http://localhost:8000
```

---

## Production Deployment (Render)

### Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `False` for production |
| `ALLOWED_HOSTS` | Your domain |
| `DATABASE_URL` | PostgreSQL URL (auto) |
| `USE_S3` | `True` to use S3 |
| `AWS_ACCESS_KEY_ID` | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket name |

### Build Command
```bash
./build.sh
```

### Start Command
```bash
gunicorn movie_site.wsgi:application
```

---

## AWS S3 Setup

1. Create S3 bucket
2. Set bucket policy for public read
3. Create IAM user with S3 permissions
4. Add credentials to environment variables

---

## Database

### Development
SQLite - automatic, no configuration needed.

### Production
PostgreSQL via `DATABASE_URL` environment variable:
```python
if os.environ.get('DATABASE_URL'):
    import dj_database_url
    DATABASES = {'default': dj_database_url.config()}
```

---

## Static Files

Served via WhiteNoise:
```python
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

Collect static files:
```bash
python manage.py collectstatic
```
