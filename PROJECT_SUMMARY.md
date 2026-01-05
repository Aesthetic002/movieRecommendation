# 🎬 Movie Recommendation Website - Project Summary

## What Was Built

A complete movie recommendation website that wraps your existing C recommendation engine with a Django web interface. The project follows the principle of **minimal changes** - treating the C code as a black box and adding only a thin integration layer.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                         │
│                     (Bootstrap UI)                          │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP Requests
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                     Django Web Layer                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Views: Authentication, Movie Display, Rating Forms  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Models: Movie, UserProfile, Rating (PostgreSQL)     │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────────┘
                   │ CSV Sync
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              CSV Files (Data Bridge)                        │
│          movies.csv, users.csv, ratings.csv                 │
└──────────────────┬──────────────────────────────────────────┘
                   │ File I/O
                   ▼
┌─────────────────────────────────────────────────────────────┐
│            C Recommendation Engine                          │
│         (Original Code - Unchanged)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ c_interface.c: CLI wrapper (subprocess calls)        │   │
│  │ recommendation.c: Collaborative filtering algorithm  │   │
│  │ graph.c, hash_table.c: Data structures             │   │
│  └──────────────────────────────────────────────────────┘   │
│                  Output: JSON                               │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. **C Integration Layer** (Minimal Changes)
- **c_interface.c**: New CLI wrapper that accepts commands via subprocess
  - `recommend <user_id> <count>`: Get recommendations
  - `add_rating <user_id> <movie_id> <rating>`: Add rating
- **Output**: JSON format for easy parsing by Django
- **Original C code**: Completely untouched, works as-is

### 2. **Django Application**
- **movies/models.py**: Database models (Movie, UserProfile, Rating)
- **movies/views.py**: Web views for all features
- **movies/c_engine.py**: Python wrapper that calls C executable via subprocess
- **movies/admin.py**: Admin interface for content management
- **movies/templates/**: Bootstrap-based HTML templates

### 3. **Data Sync System**
- **CSVSync class**: Bidirectional sync between Django DB and CSV files
- Django → CSV: Before calling C engine
- CSV → Django: For importing initial data

### 4. **Deployment Configuration**
- **Render**: Web hosting with automatic PostgreSQL
- **AWS S3**: Movie poster storage
- **Gunicorn**: Production WSGI server
- **WhiteNoise**: Static file serving

## Features Implemented

### User-Facing Features
✅ User registration & authentication  
✅ Browse movies with search & filters  
✅ Movie detail pages  
✅ Rate movies (1-5 stars)  
✅ View personal rating history  
✅ **Get personalized recommendations** (powered by C algorithm)  
✅ Responsive Bootstrap UI  

### Admin Features (Django Admin)
✅ Add/edit/delete movies  
✅ Upload movie posters (S3 storage)  
✅ View all users  
✅ View all ratings  
✅ Manage database content  

## File Structure

```
DSA EL/
├── C Engine (Existing + Minimal Additions)
│   ├── main.c                    # Original interactive program
│   ├── c_interface.c             # NEW: CLI wrapper for Django
│   ├── recommendation.c/h        # Unchanged
│   ├── file_io.c/h               # Unchanged
│   ├── graph.c/h                 # Unchanged
│   ├── hash_table.c/h            # Unchanged
│   ├── movie.c/h                 # Unchanged
│   └── user.c/h                  # Unchanged
│
├── Django Project
│   ├── movie_site/               # Project settings
│   │   ├── settings.py           # Database, S3, middleware config
│   │   ├── urls.py               # URL routing
│   │   └── wsgi.py               # WSGI application
│   │
│   └── movies/                   # Main app
│       ├── models.py             # Movie, UserProfile, Rating
│       ├── views.py              # All web views
│       ├── c_engine.py           # C integration wrapper
│       ├── admin.py              # Admin configuration
│       ├── forms.py              # Rating form
│       ├── urls.py               # App URL patterns
│       ├── templates/            # HTML templates
│       │   ├── movies/
│       │   │   ├── base.html
│       │   │   ├── home.html
│       │   │   ├── movie_list.html
│       │   │   ├── movie_detail.html
│       │   │   ├── recommendations.html
│       │   │   └── my_ratings.html
│       │   └── registration/
│       │       ├── login.html
│       │       └── register.html
│       └── management/commands/
│           ├── sync_csv.py       # Sync Django to CSV
│           ├── import_movies.py  # Import from CSV
│           └── create_test_user.py
│
├── Data Files
│   ├── movies.csv                # Synced with Django
│   ├── users.csv                 # Synced with Django
│   └── ratings.csv               # Synced with Django
│
├── Deployment
│   ├── build.sh                  # Render build script
│   ├── build_c.bat               # Windows C compilation
│   ├── Makefile                  # Linux/Mac C compilation
│   ├── render.yaml               # Render configuration
│   ├── requirements.txt          # Python dependencies
│   ├── Procfile                  # Process configuration
│   └── runtime.txt               # Python version
│
└── Documentation
    ├── README.md                 # Full documentation
    ├── QUICKSTART.md             # Getting started guide
    ├── DEPLOYMENT.md             # Deployment checklist
    └── .env.example              # Environment variables template
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Bootstrap 5, HTML, CSS |
| Backend | Django 5.0, Python 3.11 |
| Core Algorithm | C (GCC compiled) |
| Database (Dev) | SQLite |
| Database (Prod) | PostgreSQL |
| File Storage | Local / AWS S3 |
| Web Server | Gunicorn |
| Static Files | WhiteNoise |
| Deployment | Render.com |

## How It Works

### User Flow Example:

1. **User registers** → Django creates User + UserProfile with unique `c_user_id`
2. **User rates movies** → Ratings stored in Django DB
3. **User clicks "Recommendations"** →
   - Django calls `CSVSync.sync_all()` (exports to CSV)
   - Django executes: `./c_interface recommend <user_id> 10`
   - C engine reads CSVs, runs collaborative filtering
   - C engine outputs JSON recommendations
   - Django parses JSON, enriches with database data
   - Django renders recommendations page

### Data Flow:

```
User Action → Django View → Database Write → CSV Export → 
C Engine Read → Algorithm → JSON Output → Django Parse → 
HTML Template → User Browser
```

## What Was NOT Changed

✅ Original recommendation algorithm (recommendation.c)  
✅ Graph and hash table implementations  
✅ Collaborative filtering logic  
✅ Movie and user data structures  
✅ File I/O operations  
✅ Original main.c (still works standalone)  

## What WAS Added

✅ c_interface.c (thin CLI wrapper)  
✅ JSON output formatting  
✅ Django web application  
✅ Python subprocess integration  
✅ CSV sync utilities  
✅ Web templates  
✅ Deployment configuration  

## Commands Reference

### Development
```bash
# Setup
pip install -r requirements.txt
make c_interface  # or .\build_c.bat on Windows
python manage.py migrate
python manage.py createsuperuser

# Run
python manage.py runserver

# Utilities
python manage.py sync_csv
python manage.py import_movies
python manage.py create_test_user
```

### Production
```bash
# Deploy
git push origin main  # Auto-deploys to Render

# Post-deploy
python manage.py createsuperuser
python manage.py import_movies
```

## Success Criteria Met

✅ **Minimal changes to C code**: Only added c_interface.c wrapper  
✅ **C code as black box**: Algorithm untouched  
✅ **Simple integration**: subprocess + CSV files  
✅ **Django web app**: Full-featured movie website  
✅ **User authentication**: Django built-in auth  
✅ **Admin panel**: Django Admin (no custom code)  
✅ **S3 integration**: django-storages + boto3  
✅ **Render deployment**: Ready to deploy  
✅ **PostgreSQL support**: Environment-based switching  
✅ **No algorithm changes**: Original logic preserved  

## Next Steps

### Immediate (to test locally):
1. Compile C code: `.\build_c.bat`
2. Import movies: `python manage.py import_movies`
3. Create admin: `python manage.py createsuperuser`
4. Run server: `python manage.py runserver`
5. Visit http://localhost:8000

### For Production:
1. Setup AWS S3 bucket (optional)
2. Create Render account
3. Push to GitHub
4. Deploy to Render (see DEPLOYMENT.md)
5. Add content via admin panel

## Support

- **Setup Issues**: See QUICKSTART.md
- **Deployment**: See DEPLOYMENT.md
- **Full Docs**: See README.md
- **C Engine**: Works unchanged from original

## Project Philosophy

This project demonstrates **wrapper pattern integration**:
- Existing complex system (C recommendation engine)
- Minimal-change integration layer (c_interface.c)
- Modern web interface (Django)
- No rewrites or refactoring
- Maximum code reuse

Perfect for situations where you have working legacy/low-level code and need to add a modern interface without touching the core logic.
