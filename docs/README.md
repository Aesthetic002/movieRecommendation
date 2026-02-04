# Movie Recommendation System - Documentation Index

## Overview

A movie recommendation system with a C-based collaborative filtering engine and Django web interface.

---

## Documentation Files

| # | Document | Description |
|---|----------|-------------|
| 01 | [Data Structures](./01_DATA_STRUCTURES.md) | Hash tables, bipartite graph, movie/user structures |
| 02 | [Recommendation Engine](./02_RECOMMENDATION_ENGINE.md) | Cosine similarity algorithm, weighted predictions |
| 03 | [Django Web Application](./03_DJANGO_WEB_APPLICATION.md) | Models, views, forms, URL routing, templates |
| 04 | [C-Django Integration](./04_C_DJANGO_INTEGRATION.md) | Subprocess calls, CSV sync, data flow |
| 05 | [File I/O System](./05_FILE_IO_SYSTEM.md) | CSV formats, C parsing, Django export |
| 06 | [User Authentication](./06_USER_AUTHENTICATION.md) | Registration, login, profile management |
| 07 | [Deployment Guide](./07_DEPLOYMENT_GUIDE.md) | Local setup, Render deployment, AWS S3 |
| 08 | [API Reference](./08_API_REFERENCE.md) | Endpoints, CLI commands, Python API |
| 09 | [Admin Panel](./09_ADMIN_PANEL.md) | Content management interface |

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Compile C engine
.\build_c.bat  # Windows
make c_interface  # Linux/Mac

# 3. Setup database
python manage.py migrate
python manage.py createsuperuser

# 4. Import data
python manage.py shell
>>> from movies.c_engine import CSVSync
>>> CSVSync.import_movies()

# 5. Run server
python manage.py runserver
```

---

## Architecture Summary

```
┌───────────────┐     ┌─────────────┐     ┌─────────────────┐
│  Web Browser  │────→│   Django    │────→│  C Engine       │
│  (Bootstrap)  │     │  (Python)   │     │  (Recommendation)│
└───────────────┘     └──────┬──────┘     └─────────────────┘
                             │
                        ┌────▼────┐
                        │   CSV   │
                        │  Files  │
                        └─────────┘
```

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Bootstrap 5, HTML/CSS |
| Backend | Django 5.0, Python 3.11 |
| Algorithm | C (GCC compiled) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Storage | Local / AWS S3 |
| Deployment | Render.com |

---

## Key Features

- **User Features**: Browse movies, rate (1-5 stars), get recommendations
- **Admin Features**: Add/edit movies, upload posters, view all data
- **Algorithm**: User-based collaborative filtering with cosine similarity
- **Integration**: Minimal changes to C code, CSV data bridge
