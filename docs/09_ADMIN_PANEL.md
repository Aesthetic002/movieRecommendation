# Admin Panel Documentation

## Overview

The Django Admin panel provides a complete interface for content management without requiring code changes.

---

## Access

**URL**: `/admin/`

**Login**: Use superuser credentials created with:
```bash
python manage.py createsuperuser
```

---

## Movie Management

### List View
- Display columns: ID, Title, Genre, Year, Avg Rating, Rating Count, Poster Preview
- Filters: Genre, Year
- Search: Title, Genre
- Ordering: Alphabetical

### Add/Edit Movie
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `movie_id` | Integer | Yes | Unique ID for C engine |
| `title` | Text | Yes | Movie title |
| `genre` | Text | Yes | Genre category |
| `year` | Integer | Yes | Release year |
| `poster` | Image | No | Upload poster (S3/local) |
| `avg_rating` | Float | Auto | Computed from ratings |
| `rating_count` | Integer | Auto | Number of ratings |

---

## User Profile Management

### List View
- Display: C User ID, Username, Age, Ratings Count, Avg Rating Given
- Search: Username, Email

### Fields
| Field | Type | Description |
|-------|------|-------------|
| `user` | FK | Link to Django User |
| `c_user_id` | Integer | ID for C engine (auto-generated) |
| `age` | Integer | User's age |

---

## Rating Management

### List View
- Display: User, Movie, Rating, Created At
- Filters: Rating value, Date
- Search: Username, Movie title
- Ordering: Most recent first

### Fields
| Field | Type | Description |
|-------|------|-------------|
| `user` | FK | Who rated |
| `movie` | FK | Movie rated |
| `rating` | Float | 1.0 - 5.0 |
| `created_at` | DateTime | Auto |
| `updated_at` | DateTime | Auto |

---

## Admin Configuration

```python
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('movie_id', 'title', 'genre', 'year', 
                    'avg_rating', 'rating_count', 'poster_preview')
    list_filter = ('genre', 'year')
    search_fields = ('title', 'genre')
```
