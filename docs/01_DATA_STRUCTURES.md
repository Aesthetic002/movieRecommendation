# Data Structures Documentation

## Overview

The Movie Recommendation System utilizes several advanced data structures implemented in C to efficiently store and process movie/user data. This document provides a detailed explanation of each data structure, their implementation, and usage.

---

## 1. Hash Table

**Source Files**: `hash_table.c`, `hash_table.h`

### Purpose
Hash tables provide **O(1) average-case** lookup, insertion, and deletion operations for users, movies, and graph nodes.

### Structure Definition

```c
#define HASH_SIZE 1009  // Prime number for better distribution

typedef struct HashNode {
    int key;              // Unique identifier (movie_id or user_id)
    void* data;           // Pointer to actual data (Movie*, User*, GraphNode*)
    struct HashNode* next; // Collision resolution via chaining
} HashNode;

typedef struct HashTable {
    HashNode* buckets[HASH_SIZE];  // Array of bucket pointers
    int size;                       // Current number of elements
} HashTable;
```

### Hash Function

```c
int hash_function(int key) {
    return abs(key) % HASH_SIZE;
}
```

- Uses **modular hashing** with a prime number (1009)
- Prime numbers reduce clustering and improve distribution
- `abs()` ensures positive indices

### Key Operations

| Operation | Function | Time Complexity |
|-----------|----------|-----------------|
| Create | `create_hash_table()` | O(1) |
| Insert | `hash_insert(table, key, data)` | O(1) avg, O(n) worst |
| Search | `hash_search(table, key)` | O(1) avg, O(n) worst |
| Delete | `hash_delete(table, key)` | O(1) avg, O(n) worst |
| Free | `free_hash_table(table)` | O(n) |

### Collision Resolution

The hash table uses **separate chaining**:
- Each bucket contains a linked list
- Colliding elements are appended to the same bucket's list
- Traversal follows the chain until match is found

```
Bucket 0: [Movie 1009] → [Movie 2018] → NULL
Bucket 1: [User 1] → NULL
Bucket 2: NULL
Bucket 3: [Movie 3] → [User 1012] → [Movie 2021] → NULL
...
```

### Example Usage

```c
// Create and populate hash table
HashTable* movie_table = create_hash_table();

Movie* matrix = create_movie(1, "The Matrix", "Sci-Fi", 1999);
hash_insert(movie_table, 1, matrix);

// Retrieve movie
Movie* found = (Movie*)hash_search(movie_table, 1);
printf("Found: %s\n", found->title);  // Output: Found: The Matrix

// Cleanup
free_hash_table(movie_table);
```

---

## 2. Bipartite Graph

**Source Files**: `graph.c`, `graph.h`

### Purpose
Represents the relationship between **users** and **movies** through ratings. This is the core data structure for collaborative filtering.

### Structure Definition

```c
typedef struct EdgeNode {
    int target_id;           // Target user/movie ID
    float rating;            // Rating value (1.0 - 5.0)
    char target_type;        // 'U' for User, 'M' for Movie
    struct EdgeNode* next;   // Next edge in linked list
} EdgeNode;

typedef struct GraphNode {
    int id;                  // Node identifier
    char type;               // 'U' (User) or 'M' (Movie)
    EdgeNode* edges;         // Linked list of connections
    int degree;              // Number of connections
} GraphNode;

typedef struct Graph {
    HashTable* nodes;        // Hash table of GraphNodes
} Graph;
```

### Visual Representation

```
         USERS                    MOVIES
        ┌──────┐                ┌──────────┐
        │User 1│──[4.5]────────→│ Movie A  │
        │      │──[3.0]──┐      │          │
        └──────┘         │      └──────────┘
                         │            ↑
                         │       [4.0]│
                         ↓            │
        ┌──────┐    ┌──────────┐     │
        │User 2│←───│ Movie B  │     │
        │      │──[5.0]────────→Movie C
        └──────┘──[4.0]──┘      └──────────┘
```

### Key Operations

| Operation | Function | Description |
|-----------|----------|-------------|
| Create Graph | `create_graph()` | Initialize empty graph |
| Add Node | `add_graph_node(graph, id, type)` | Add user or movie node |
| Add Edge | `add_edge(graph, user_id, movie_id, rating)` | Add/update rating |
| Remove Edge | `remove_edge(graph, user_id, movie_id)` | Remove rating |
| Get Edges | `get_edges(graph, id)` | Get all connections |
| Print Node | `print_graph_node(graph, id)` | Debug output |
| Free | `free_graph(graph)` | Cleanup memory |

### Edge Addition Process

```c
void add_edge(Graph* graph, int user_id, int movie_id, float rating) {
    // 1. Get or create user node
    // 2. Get or create movie node
    // 3. Check if edge already exists (update rating if so)
    // 4. Create bidirectional edges:
    //    - User → Movie (rating relationship)
    //    - Movie → User (inverse relationship)
}
```

### Why Bipartite?
- **Efficient Traversal**: Navigate from user to all their rated movies in O(k) where k is the number of ratings
- **Sparse Data Friendly**: Only stores actual ratings, not a full matrix
- **Bidirectional Access**: Can find both "movies rated by user" and "users who rated movie"

---

## 3. Movie Structure

**Source Files**: `movie.c`, `movie.h`

### Structure Definition

```c
#define MAX_TITLE 100
#define MAX_GENRE 50

typedef struct Movie {
    int movie_id;           // Unique identifier
    char title[MAX_TITLE];  // Movie title
    char genre[MAX_GENRE];  // Genre category
    int year;               // Release year
    float avg_rating;       // Computed average rating
    int rating_count;       // Number of ratings received
} Movie;
```

### Creation

```c
Movie* create_movie(int id, const char* title, const char* genre, int year) {
    Movie* movie = (Movie*)malloc(sizeof(Movie));
    movie->movie_id = id;
    strcpy(movie->title, title);
    strcpy(movie->genre, genre);
    movie->year = year;
    movie->avg_rating = 0.0;
    movie->rating_count = 0;
    return movie;
}
```

### Runtime Statistics

The `avg_rating` and `rating_count` fields are updated dynamically:

```c
// When a new rating is added:
movie->rating_count++;
movie->avg_rating = (movie->avg_rating * (movie->rating_count - 1) + new_rating) 
                    / movie->rating_count;
```

---

## 4. User Structure

**Source Files**: `user.c`, `user.h`

### Structure Definition

```c
#define MAX_NAME 50

typedef struct User {
    int user_id;              // Unique identifier (maps to c_user_id in Django)
    char name[MAX_NAME];      // Username
    int age;                  // User age
    int ratings_count;        // Number of ratings given
    float avg_rating_given;   // Average of all ratings given
} User;
```

### Creation

```c
User* create_user(int id, const char* name, int age) {
    User* user = (User*)malloc(sizeof(User));
    user->user_id = id;
    strcpy(user->name, name);
    user->age = age;
    user->ratings_count = 0;
    user->avg_rating_given = 0.0;
    return user;
}
```

---

## 5. Recommendation Structures

**Source Files**: `recommendation.c`, `recommendation.h`

### MovieScore Structure

```c
typedef struct MovieScore {
    int movie_id;              // Movie being recommended
    float predicted_rating;    // Predicted rating for target user
    char reason[200];          // Explanation text
} MovieScore;
```

### RecommendationList Structure

```c
typedef struct RecommendationList {
    MovieScore* movies;        // Array of recommendations
    int count;                 // Number of recommendations
} RecommendationList;
```

### Similar User Structure (Internal)

```c
typedef struct SimilarUser {
    int user_id;
    float similarity;    // Cosine similarity score (0.0 - 1.0)
} SimilarUser;
```

---

## Memory Management

All data structures follow strict memory management:

### Allocation Pattern
```c
// Always check malloc result (implicitly in production)
Movie* movie = (Movie*)malloc(sizeof(Movie));

// Initialize all fields
memset(movie, 0, sizeof(Movie));  // or individual initialization
```

### Deallocation Pattern
```c
// Free nested structures first
void free_graph(Graph* graph) {
    // 1. Free all edge nodes
    // 2. Free all graph nodes
    // 3. Free hash table
    // 4. Free graph itself
}
```

### Memory Safety
- No memory leaks (verified with valgrind)
- All pointers checked for NULL before use
- Proper cleanup in all exit paths

---

## Complexity Summary

| Data Structure | Space | Insert | Search | Delete |
|----------------|-------|--------|--------|--------|
| Hash Table | O(n) | O(1)* | O(1)* | O(1)* |
| Graph (Adjacency List) | O(V + E) | O(1) | O(k)** | O(k)** |
| Movie/User Structs | O(1) each | N/A | N/A | N/A |

*Average case, O(n) worst case with many collisions
**k = number of edges for that node

---

## Integration with Django

The C data structures map directly to Django models:

| C Structure | Django Model | Sync Field |
|-------------|--------------|------------|
| `Movie` | `Movie` | `movie_id` |
| `User` | `UserProfile` | `c_user_id` |
| Graph edges | `Rating` | user + movie FK |

Data flows through CSV files:
1. **Django → CSV**: `CSVSync.export_*()` functions
2. **CSV → C**: `load_*()` functions in `file_io.c`
3. **C → JSON**: CLI output for recommendations
