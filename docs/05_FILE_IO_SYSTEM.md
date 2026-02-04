# File I/O System Documentation

## Overview

The file I/O system manages persistent data storage using CSV files, serving as the data bridge between Django and the C recommendation engine.

---

## CSV File Formats

### movies.csv

```csv
movie_id,title,genre,year
1,The Matrix,Sci-Fi,1999
2,Inception,Sci-Fi,2010
3,The Godfather,Crime,1972
```

| Column | Type | Description |
|--------|------|-------------|
| `movie_id` | int | Unique movie identifier |
| `title` | string | Movie title (max 100 chars) |
| `genre` | string | Genre category |
| `year` | int | Release year |

### users.csv

```csv
user_id,name,age
101,john_doe,25
102,jane_smith,32
```

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | int | Unique user ID (maps to c_user_id) |
| `name` | string | Username |
| `age` | int | User age |

### ratings.csv

```csv
user_id,movie_id,rating
101,1,5.0
101,2,4.5
102,1,4.0
```

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | int | User who rated |
| `movie_id` | int | Movie being rated |
| `rating` | float | Rating value (1.0 - 5.0) |

---

## C File I/O Functions

**Source File**: `file_io.c`

### load_movies()

```c
void load_movies(const char* filename, HashTable* movie_table) {
    FILE* file = fopen(filename, "r");
    if (file == NULL) return;
    
    char line[300];
    fgets(line, sizeof(line), file);  // Skip header
    
    while (fgets(line, sizeof(line), file)) {
        int id, year;
        char title[MAX_TITLE], genre[MAX_GENRE];
        
        if (sscanf(line, "%d,%[^,],%[^,],%d", 
                   &id, title, genre, &year) == 4) {
            Movie* movie = create_movie(id, title, genre, year);
            hash_insert(movie_table, id, movie);
        }
    }
    fclose(file);
}
```

### load_users()

```c
void load_users(const char* filename, HashTable* user_table) {
    FILE* file = fopen(filename, "r");
    if (file == NULL) return;
    
    char line[200];
    fgets(line, sizeof(line), file);  // Skip header
    
    while (fgets(line, sizeof(line), file)) {
        int id, age;
        char name[MAX_NAME];
        
        if (sscanf(line, "%d,%[^,],%d", &id, name, &age) == 3) {
            User* user = create_user(id, name, age);
            hash_insert(user_table, id, user);
        }
    }
    fclose(file);
}
```

### load_ratings()

```c
void load_ratings(const char* filename, Graph* graph, 
                  HashTable* movie_table, HashTable* user_table) {
    FILE* file = fopen(filename, "r");
    if (file == NULL) return;
    
    char line[200];
    fgets(line, sizeof(line), file);  // Skip header
    
    while (fgets(line, sizeof(line), file)) {
        int user_id, movie_id;
        float rating;
        
        if (sscanf(line, "%d,%d,%f", &user_id, &movie_id, &rating) == 3) {
            add_edge(graph, user_id, movie_id, rating);
            
            // Update user stats
            User* user = (User*)hash_search(user_table, user_id);
            if (user != NULL) {
                user->ratings_count++;
                user->avg_rating_given = 
                    (user->avg_rating_given * (user->ratings_count - 1) + rating) 
                    / user->ratings_count;
            }
            
            // Update movie stats
            Movie* movie = (Movie*)hash_search(movie_table, movie_id);
            if (movie != NULL) {
                movie->rating_count++;
                movie->avg_rating = 
                    (movie->avg_rating * (movie->rating_count - 1) + rating) 
                    / movie->rating_count;
            }
        }
    }
    fclose(file);
}
```

### save_rating()

```c
void save_rating(const char* filename, int user_id, 
                 int movie_id, float rating) {
    FILE* file = fopen(filename, "a");  // Append mode
    if (file == NULL) return;
    
    fprintf(file, "%d,%d,%.1f\n", user_id, movie_id, rating);
    fclose(file);
}
```

---

## Django CSV Sync

**Source File**: `movies/c_engine.py` - CSVSync class

### Export Functions
- `export_movies()` - Django Movie → movies.csv
- `export_users()` - Django UserProfile → users.csv  
- `export_ratings()` - Django Rating → ratings.csv
- `sync_all()` - Runs all exports

### Import Functions
- `import_movies()` - movies.csv → Django Movie model

---

## Error Handling

```c
FILE* file = fopen(filename, "r");
if (file == NULL) {
    printf("Creating sample data...\n");
    return;  // Graceful degradation
}
```

Files are handled safely with:
- NULL checks after fopen()
- Proper fclose() calls
- Graceful handling of missing files
