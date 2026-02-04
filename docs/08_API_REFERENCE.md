# API Reference

## Web Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | No | Home page with featured movies |
| `/movies/` | GET | No | Movie list with search/filter |
| `/movies/<id>/` | GET/POST | No/Yes | Movie detail + rating form |
| `/recommendations/` | GET | Yes | Personalized recommendations |
| `/my-ratings/` | GET | Yes | User's rating history |
| `/register/` | GET/POST | No | User registration |
| `/accounts/login/` | GET/POST | No | Login |
| `/accounts/logout/` | POST | Yes | Logout |
| `/admin/` | GET | Admin | Django admin panel |

---

## Query Parameters

### Movie List (`/movies/`)
| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Search query (title/genre) |
| `genre` | string | Filter by genre |

Example: `/movies/?q=matrix&genre=Sci-Fi`

---

## C Engine CLI

### Get Recommendations
```bash
./c_interface recommend <user_id> <count>
```
**Response**: JSON array of recommendations

### Add Rating
```bash
./c_interface add_rating <user_id> <movie_id> <rating>
```
**Response**: `{"status":"success"}`

---

## Django Management Commands

```bash
# Sync Django data to CSV files
python manage.py sync_csv

# Import movies from CSV
python manage.py import_movies

# Create test user with ratings
python manage.py create_test_user

# Standard Django commands
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

---

## Python API

### CRecommendationEngine

```python
from movies.c_engine import CRecommendationEngine

engine = CRecommendationEngine()

# Get recommendations
recs = engine.get_recommendations(user_id=101, count=10)

# Add rating
success = engine.add_rating(user_id=101, movie_id=5, rating=4.5)
```

### CSVSync

```python
from movies.c_engine import CSVSync

# Export all to CSV
CSVSync.sync_all()

# Individual exports
CSVSync.export_movies()
CSVSync.export_users()
CSVSync.export_ratings()

# Import from CSV
CSVSync.import_movies()
```
