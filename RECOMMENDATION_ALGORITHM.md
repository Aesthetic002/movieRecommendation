# C Recommendation Engine - Technical Documentation

## Overview
This recommendation system uses **Collaborative Filtering** with **Cosine Similarity** to predict movie 
ratings and generate personalized recommendations. The algorithm is implemented entirely in C for maximum performance.

---

## Core Architecture

### 1. Data Structures

#### **Graph Structure** (`graph.c`, `graph.h`)
The foundation is a **bipartite graph** connecting users and movies:

```
Users ←→ Movies (via Ratings)

Example:
User 1 --[4.5]→ Movie A
User 1 --[3.0]→ Movie B
User 2 --[4.0]→ Movie A
User 2 --[5.0]→ Movie C
```

**Components:**
- **GraphNode**: Represents either a User or Movie node
  - `id`: Unique identifier
  - `type`: 'U' (User) or 'M' (Movie)
  - `edges`: Linked list of connections
  - `degree`: Number of connections

- **EdgeNode**: Represents a rating relationship
  - `target_id`: Connected user/movie ID
  - `rating`: Rating value (1.0 - 5.0)
  - `target_type`: Type of connected node
  - `next`: Pointer to next edge (linked list)

**Why Bipartite Graph?**
- Efficiently store sparse rating data
- O(1) lookup for user ratings
- Natural representation of user-item relationships
- Supports bidirectional traversal (user→movies, movie→users)

#### **Hash Tables** (`hash_table.c`, `hash_table.h`)
Used for O(1) average-case lookup of users, movies, and graph nodes:

```c
HashTable {
    buckets[HASH_SIZE]  // Array of 1009 buckets (prime number)
    Each bucket → Linked list of HashNodes
}
```

**Hash Function:**
```c
index = key % HASH_SIZE
```
Uses chaining for collision resolution.

---

## The Recommendation Algorithm

### Step 1: User Similarity Calculation
**Function:** `calculate_user_similarity()`

Uses **Cosine Similarity** to measure how similar two users' tastes are:

```
                    Σ(rating₁ × rating₂)
Similarity = ─────────────────────────────────
             √(Σ rating₁²) × √(Σ rating₂²)
```

**Algorithm:**
1. Get all movies rated by both users (common movies)
2. For each common movie:
   - Multiply the two ratings
   - Add to numerator
   - Add squared ratings to denominators
3. Calculate cosine similarity
4. Return value between 0.0 (no similarity) and 1.0 (identical taste)

**Example:**
```
User A ratings: Movie 1 (5.0), Movie 2 (4.0), Movie 3 (3.0)
User B ratings: Movie 1 (4.0), Movie 2 (5.0), Movie 3 (4.0)

Sum of products: (5×4) + (4×5) + (3×4) = 20 + 20 + 12 = 52
Sum A squared: 5² + 4² + 3² = 25 + 16 + 9 = 50
Sum B squared: 4² + 5² + 4² = 16 + 25 + 16 = 57

Similarity = 52 / (√50 × √57) = 52 / 53.39 = 0.974
(Very similar users!)
```

**Similarity Threshold:** Only users with similarity > 0.3 are considered

---

### Step 2: Find Similar Users
**Function:** `generate_recommendations()` (Part 1)

1. **Identify watched movies:**
   - Create array to track movies target user has already rated
   - Prevents recommending already-watched movies

2. **Find similar users:**
   - Iterate through all users in hash table
   - Calculate similarity with target user
   - Keep users with similarity > 0.3
   - Store in `SimilarUser` array with their similarity scores

**Data Structure:**
```c
SimilarUser {
    int user_id;
    float similarity;
}
```

---

### Step 3: Predict Ratings for Unwatched Movies
**Function:** `generate_recommendations()` (Part 2)

For each similar user:
1. Get all movies they rated
2. For each movie NOT watched by target user:
   - **Calculate weighted rating:**
     ```
     weighted_rating = similar_user_rating × similarity_score
     ```
   - Add to candidate movies list
   - Track total weight for averaging

**Example:**
```
Target User: hasn't watched Movie X

Similar User 1 (similarity: 0.8): rated Movie X as 5.0
Similar User 2 (similarity: 0.6): rated Movie X as 4.0
Similar User 3 (similarity: 0.9): rated Movie X as 4.5

Weighted ratings:
User 1: 5.0 × 0.8 = 4.0
User 2: 4.0 × 0.6 = 2.4
User 3: 4.5 × 0.9 = 4.05

Total weight: 0.8 + 0.6 + 0.9 = 2.3
Total score: 4.0 + 2.4 + 4.05 = 10.45

Predicted Rating = 10.45 / 2.3 = 4.54
```

---

### Step 4: Aggregate and Normalize Scores

For each candidate movie:

1. **Sum all weighted ratings** from similar users
2. **Sum all similarity weights** 
3. **Calculate predicted rating:**
   ```
   predicted_rating = sum_of_weighted_ratings / sum_of_weights
   ```

4. **Generate reason text:**
   ```c
   sprintf(reason, "Based on %d similar users (avg similarity: %.2f)", 
           count, avg_similarity);
   ```

**Why weighted average?**
- Users with higher similarity have more influence
- Prevents bias from users with very different tastes
- Normalizes predictions to 1.0-5.0 scale

---

### Step 5: Rank and Return Top N

1. **Sort candidate movies** by predicted rating (descending)
   - Uses qsort with `compare_movie_scores`
   
2. **Select top N movies** (default: 10)

3. **Return RecommendationList:**
   ```c
   RecommendationList {
       MovieScore* movies;  // Array of recommendations
       int count;           // Number of recommendations
   }
   
   MovieScore {
       int movie_id;
       float predicted_rating;
       char reason[200];
   }
   ```

---

## Integration with Django

### C Interface (`c_interface.c`)

**Command-line interface** for Django to call:

```bash
./c_interface recommend <user_id> <count>
```

**Process:**
1. Load data from CSV files:
   - `users.csv` → Hash table of users
   - `movies.csv` → Hash table of movies  
   - `ratings.csv` → Bipartite graph
   
2. Generate recommendations

3. **Output JSON:**
   ```json
   [
     {
       "movie_id": 123,
       "title": "The Matrix",
       "genre": "Sci-Fi",
       "year": 1999,
       "predicted_rating": 4.8,
       "reason": "Based on 15 similar users (avg similarity: 0.72)"
     }
   ]
   ```

4. Clean up memory

---

## Performance Characteristics

### Time Complexity

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| User lookup | O(1) avg | Hash table |
| Movie lookup | O(1) avg | Hash table |
| Get user ratings | O(r) | r = number of ratings |
| Calculate similarity | O(r₁ × r₂) | r₁, r₂ = rating counts |
| Find similar users | O(u × r²) | u = total users |
| Generate predictions | O(s × r) | s = similar users |
| Sort recommendations | O(m log m) | m = candidate movies |
| **Total** | **O(u × r²)** | Dominated by similarity calc |

### Space Complexity

| Structure | Complexity | Notes |
|-----------|-----------|-------|
| Graph nodes | O(u + m) | u users + m movies |
| Graph edges | O(r) | r total ratings |
| Hash tables | O(u + m) | Users + movies |
| Candidates array | O(m) | Max movies |
| **Total** | **O(u + m + r)** | Linear in data size |

---

## Algorithm Strengths

✅ **High-quality recommendations**
- Leverages collective intelligence
- Captures subtle taste patterns
- Works well with sparse data

✅ **Personalized**
- Based on actual user behavior
- Adapts to individual preferences
- No manual feature engineering needed

✅ **Efficient in C**
- Fast similarity calculations
- Optimized memory usage
- Sub-second response times

✅ **Explainable**
- Shows number of similar users
- Displays average similarity score
- Transparent reasoning

---

## Algorithm Limitations

⚠️ **Cold Start Problem**
- New users need ≥5 ratings
- New movies need user feedback
- Mitigated by dummy users in database

⚠️ **Computational Cost**
- Similarity calculation is O(r²) per user pair
- Scales quadratically with active users
- Solved by caching and batch processing

⚠️ **Data Sparsity**
- Users typically rate <1% of movies
- Requires minimum overlap for similarity
- Threshold of 0.3 filters weak signals

⚠️ **Filter Bubble**
- Only recommends similar to past ratings
- No serendipitous discoveries
- Could be enhanced with diversity metrics

---

## Example Walk-through

### Scenario
Target User (ID: 42) wants recommendations

**Step 1: User's Rating History**
```
Movie 1 (Action):     5.0 ⭐⭐⭐⭐⭐
Movie 5 (Action):     4.5 ⭐⭐⭐⭐
Movie 10 (Sci-Fi):    4.0 ⭐⭐⭐⭐
Movie 15 (Drama):     3.0 ⭐⭐⭐
```

**Step 2: Find Similar Users**
```
User 17: similarity 0.85 (rated: 1, 5, 10, 20, 25)
User 23: similarity 0.72 (rated: 1, 5, 8, 12, 30)
User 31: similarity 0.68 (rated: 5, 10, 15, 18, 22)
```

**Step 3: Calculate Predictions**

For **Movie 20** (unwatched):
```
User 17 rated: 5.0 (similarity: 0.85) → weight: 5.0 × 0.85 = 4.25
User 23 rated: 4.5 (similarity: 0.72) → weight: 4.5 × 0.72 = 3.24

Total: 4.25 + 3.24 = 7.49
Weights: 0.85 + 0.72 = 1.57
Predicted: 7.49 / 1.57 = 4.77
```

**Step 4: Top Recommendations**
```
1. Movie 20 (Sci-Fi)     - 4.77 ⭐ - "Based on 2 similar users"
2. Movie 25 (Action)     - 4.65 ⭐ - "Based on 1 similar users"
3. Movie 18 (Thriller)   - 4.52 ⭐ - "Based on 1 similar users"
...
```

---

## CSV Data Format

### users.csv
```
user_id,age
1,25
2,32
```

### movies.csv
```
movie_id,title,genre,year
1,The Matrix,Sci-Fi,1999
2,Inception,Sci-Fi,2010
```

### ratings.csv
```
user_id,movie_id,rating
1,1,5
1,2,4
2,1,4
```

---

## Memory Management

All memory is properly managed:

```c
// Allocation
Graph* graph = create_graph();
HashTable* users = create_hash_table();

// Usage
generate_recommendations(...);

// Cleanup
free_graph(graph);
free_hash_table(users);
free_recommendations(rec_list);
```

No memory leaks - verified with valgrind.

---

## Future Enhancements

### Potential Improvements

1. **Matrix Factorization**
   - Use SVD/ALS for better predictions
   - Handle sparsity more elegantly

2. **Hybrid Approach**
   - Combine collaborative + content-based
   - Add genre/actor similarity

3. **Temporal Dynamics**
   - Weight recent ratings higher
   - Track taste evolution over time

4. **Scalability**
   - Pre-compute similarity matrices
   - Use approximate nearest neighbors
   - Implement incremental updates

5. **Diversity**
   - Add novelty metric
   - Balance accuracy with exploration
   - Genre distribution constraints

---

## References

**Algorithms:**
- Collaborative Filtering: Goldberg et al. (1992)
- Cosine Similarity: Salton & McGill (1983)
- Item-Based CF: Sarwar et al. (2001)

**Implementation:**
- Graph representation for sparse matrices
- Hash tables for efficient lookups
- Weighted averaging for prediction

---

## Summary

This recommendation engine implements a **user-based collaborative filtering** algorithm:

1. 📊 **Build bipartite graph** of user-movie ratings
2. 🔍 **Calculate cosine similarity** between users
3. 👥 **Find most similar users** (threshold: 0.3)
4. 🎯 **Predict ratings** using weighted average
5. 🏆 **Rank and return** top N recommendations

**Key Innovation:** Pure C implementation for maximum performance while maintaining algorithmic sophistication comparable to modern Python-based systems.
