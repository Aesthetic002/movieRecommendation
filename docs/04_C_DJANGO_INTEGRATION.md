# C-Django Integration Documentation

## Overview

The integration between Django and C uses subprocess calls with CSV files as the data bridge.

---

## CRecommendationEngine Class

**Source File**: `movies/c_engine.py`

```python
class CRecommendationEngine:
    def __init__(self):
        self.base_dir = Path(settings.BASE_DIR)
        self.executable = self.base_dir / 'c_interface'
        if os.name == 'nt':  # Windows
            self.executable = self.base_dir / 'c_interface.exe'
    
    def get_recommendations(self, user_id, count=10):
        result = subprocess.run(
            [str(self.executable), 'recommend', str(user_id), str(count)],
            cwd=str(self.base_dir),
            capture_output=True, text=True, timeout=30
        )
        return json.loads(result.stdout)
    
    def add_rating(self, user_id, movie_id, rating):
        result = subprocess.run(
            [str(self.executable), 'add_rating', 
             str(user_id), str(movie_id), str(rating)],
            cwd=str(self.base_dir),
            capture_output=True, text=True, timeout=10
        )
        return json.loads(result.stdout).get('status') == 'success'
```

---

## CSVSync Class

```python
class CSVSync:
    @staticmethod
    def export_movies():
        csv_path = Path(settings.BASE_DIR) / 'movies.csv'
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['movie_id', 'title', 'genre', 'year'])
            for movie in Movie.objects.all():
                writer.writerow([movie.movie_id, movie.title, 
                               movie.genre, movie.year])
    
    @staticmethod
    def export_users():
        # Exports users.csv with user_id, name, age
    
    @staticmethod
    def export_ratings():
        # Exports ratings.csv with user_id, movie_id, rating
    
    @staticmethod
    def sync_all():
        CSVSync.export_movies()
        CSVSync.export_users()
        CSVSync.export_ratings()
```

---

## Data Flow

### Rating Submission
```
User submits rating → Django saves to DB → CSVSync.sync_all() 
→ c_interface add_rating → C updates graph → Returns JSON success
```

### Get Recommendations
```
User requests → CSVSync.sync_all() → c_interface recommend 
→ C loads CSVs → Runs algorithm → Returns JSON array → Django displays
```

---

## CLI Commands

```bash
# Get recommendations
./c_interface recommend 101 10

# Add rating
./c_interface add_rating 101 5 4.5
```

---

## JSON Output Format

**Recommendations:**
```json
[{"movie_id":7,"title":"The Matrix","predicted_rating":4.82}]
```

**Add Rating:**
```json
{"status":"success"}
```
