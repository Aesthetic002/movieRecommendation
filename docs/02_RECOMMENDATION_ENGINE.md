# Recommendation Engine Documentation

## Overview

The recommendation engine implements **User-Based Collaborative Filtering** with **Cosine Similarity** to generate personalized movie recommendations. The algorithm identifies users with similar taste and recommends movies they enjoyed but the target user hasn't seen.

---

## Algorithm Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     RECOMMENDATION GENERATION PIPELINE                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │ Target   │───→│ Find Similar │───→│ Predict      │───→│ Rank &    │ │
│  │ User     │    │ Users        │    │ Ratings      │    │ Return    │ │
│  └──────────┘    └──────────────┘    └──────────────┘    └───────────┘ │
│       │                │                    │                   │       │
│       ▼                ▼                    ▼                   ▼       │
│  [Get ratings]   [Cosine         [Weighted avg   [Sort by       │       │
│   history]        similarity]     of ratings]     predicted     │       │
│                  [Threshold:0.3]                  rating]       │       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Cosine Similarity Calculation

**Function**: `calculate_user_similarity()`

### Mathematical Formula

```
                    Σ(rating₁ᵢ × rating₂ᵢ)
Similarity = ─────────────────────────────────────
             √(Σ rating₁ᵢ²) × √(Σ rating₂ᵢ²)
```

Where `i` represents each commonly rated movie.

### Implementation

```c
float calculate_user_similarity(Graph* graph, int user1_id, int user2_id) {
    EdgeNode* user1_edges = get_edges(graph, user1_id);
    EdgeNode* user2_edges = get_edges(graph, user2_id);
    
    if (user1_edges == NULL || user2_edges == NULL) return 0.0;
    
    float sum_product = 0.0;
    float sum1_squared = 0.0;
    float sum2_squared = 0.0;
    int common_count = 0;
    
    // Find common movies and calculate sums
    EdgeNode* edge1 = user1_edges;
    while (edge1 != NULL) {
        EdgeNode* edge2 = user2_edges;
        while (edge2 != NULL) {
            if (edge1->target_id == edge2->target_id) {
                sum_product += edge1->rating * edge2->rating;
                sum1_squared += edge1->rating * edge1->rating;
                sum2_squared += edge2->rating * edge2->rating;
                common_count++;
            }
            edge2 = edge2->next;
        }
        edge1 = edge1->next;
    }
    
    if (common_count == 0) return 0.0;
    
    float denominator = sqrt(sum1_squared) * sqrt(sum2_squared);
    if (denominator == 0) return 0.0;
    
    return sum_product / denominator;
}
```

### Example Calculation

```
User A ratings: Movie 1 (5.0), Movie 2 (4.0), Movie 3 (3.0)
User B ratings: Movie 1 (4.0), Movie 2 (5.0), Movie 3 (4.0), Movie 4 (2.0)

Common movies: 1, 2, 3

Sum of products: (5×4) + (4×5) + (3×4) = 20 + 20 + 12 = 52
Sum A² (common): 5² + 4² + 3² = 25 + 16 + 9 = 50
Sum B² (common): 4² + 5² + 4² = 16 + 25 + 16 = 57

Similarity = 52 / (√50 × √57) = 52 / (7.07 × 7.55) = 52 / 53.39 = 0.974

Result: Very similar users! (> 0.9)
```

### Similarity Thresholds

| Similarity | Interpretation | Action |
|------------|----------------|--------|
| 0.9 - 1.0 | Nearly identical taste | High weight |
| 0.7 - 0.9 | Very similar | Strong influence |
| 0.5 - 0.7 | Moderately similar | Moderate influence |
| 0.3 - 0.5 | Somewhat similar | Low influence |
| < 0.3 | Not similar enough | **Excluded** |

---

## Step 2: Finding Similar Users

**Function**: `generate_recommendations()` - Part 1

### Process

1. **Mark watched movies**:
   ```c
   int* watched_movies = (int*)calloc(10000, sizeof(int));
   EdgeNode* edge = target_edges;
   while (edge != NULL) {
       watched_movies[edge->target_id] = 1;
       edge = edge->next;
   }
   ```

2. **Calculate similarity with all users**:
   ```c
   for (each user in user_table) {
       if (user_id != target_user_id) {
           float similarity = calculate_user_similarity(
               graph, target_user_id, user_id
           );
           if (similarity > 0.3) {  // Threshold
               add_to_similar_users(user_id, similarity);
           }
       }
   }
   ```

3. **Store similar users**:
   ```c
   SimilarUser similar_users[1000];
   // Contains: { user_id, similarity_score }
   ```

---

## Step 3: Predicting Ratings

**Function**: `generate_recommendations()` - Part 2

### Weighted Rating Calculation

For each movie rated by similar users (but not by target):

```c
for (each similar_user) {
    for (each movie they rated >= 3.5) {
        if (!watched_by_target) {
            weighted_score = rating × similarity;
            add_to_candidates(movie_id, weighted_score);
        }
    }
}
```

### Aggregation Logic

```c
MovieScore candidate_movies[1000];

// When encountering a movie already in candidates:
if (movie already in candidates) {
    candidate->predicted_rating += rating * similarity;
} else {
    // New candidate
    candidate->movie_id = movie_id;
    candidate->predicted_rating = rating * similarity;
}
```

### Example

```
Target User: User 42 (hasn't watched Movie X)

Similar User 1 (similarity: 0.85): rated Movie X = 5.0
Similar User 2 (similarity: 0.72): rated Movie X = 4.0  
Similar User 3 (similarity: 0.68): rated Movie X = 4.5

Weighted contributions:
  User 1: 5.0 × 0.85 = 4.25
  User 2: 4.0 × 0.72 = 2.88
  User 3: 4.5 × 0.68 = 3.06

Total weighted score: 4.25 + 2.88 + 3.06 = 10.19

Note: Raw score used for ranking (not normalized to 5.0 scale)
```

---

## Step 4: Ranking and Output

### Sorting

```c
// Sort by predicted_rating in descending order
qsort(candidate_movies, candidate_count, sizeof(MovieScore), 
      compare_movie_scores);

int compare_movie_scores(const void* a, const void* b) {
    MovieScore* score_a = (MovieScore*)a;
    MovieScore* score_b = (MovieScore*)b;
    if (score_b->predicted_rating > score_a->predicted_rating) return 1;
    if (score_b->predicted_rating < score_a->predicted_rating) return -1;
    return 0;
}
```

### Returning Results

```c
RecommendationList* rec_list = malloc(sizeof(RecommendationList));
rec_list->count = min(candidate_count, top_n);  // Default: 10
rec_list->movies = malloc(sizeof(MovieScore) * rec_list->count);

for (int i = 0; i < rec_list->count; i++) {
    rec_list->movies[i] = candidate_movies[i];
}
```

---

## CLI Interface

**Source File**: `c_interface.c`

### Commands

1. **Get Recommendations**:
   ```bash
   ./c_interface recommend <user_id> <count>
   
   # Example:
   ./c_interface recommend 101 10
   ```

2. **Add Rating**:
   ```bash
   ./c_interface add_rating <user_id> <movie_id> <rating>
   
   # Example:
   ./c_interface add_rating 101 5 4.5
   ```

### JSON Output Format

```json
[
  {
    "movie_id": 7,
    "title": "The Matrix",
    "genre": "Sci-Fi",
    "year": 1999,
    "predicted_rating": 4.82,
    "reason": "Similar users rated this 4.8/5"
  },
  {
    "movie_id": 15,
    "title": "Inception",
    "genre": "Sci-Fi",
    "year": 2010,
    "predicted_rating": 4.65,
    "reason": "Similar users rated this 4.5/5"
  }
]
```

---

## Performance Analysis

### Time Complexity

| Operation | Complexity | Description |
|-----------|------------|-------------|
| Load data | O(n) | Read CSV files |
| User similarity | O(r₁ × r₂) | r = ratings per user |
| Find all similar | O(u × r²) | u = total users |
| Predict ratings | O(s × r) | s = similar users |
| Sort candidates | O(m log m) | m = candidate movies |
| **Total** | **O(u × r²)** | Dominated by similarity |

### Practical Performance

- **100 users, 50 movies**: < 10ms
- **1000 users, 500 movies**: < 100ms
- **10000 users, 5000 movies**: < 1 second

### Space Complexity

| Structure | Space |
|-----------|-------|
| watched_movies array | O(10000) = ~40KB |
| similar_users array | O(1000) = ~8KB |
| candidate_movies | O(1000) = ~200KB |
| **Total auxiliary** | **~250KB** |

---

## Algorithm Strengths

| Strength | Description |
|----------|-------------|
| **Personalized** | Based on actual user behavior patterns |
| **No Feature Engineering** | Works without movie metadata |
| **Serendipitous** | Can recommend unexpected gems |
| **Explainable** | "Users like you enjoyed this" |
| **Sparse-Data Friendly** | Works with partial ratings |

---

## Algorithm Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Cold Start** | New users need 5+ ratings | Default recommendations |
| **Scalability** | O(u²) for all pairs | Pre-compute similarities |
| **Filter Bubble** | Similar taste reinforcement | Add diversity metrics |
| **Popularity Bias** | Popular movies over-recommended | Penalize common items |

---

## Future Enhancements

### 1. Matrix Factorization
- Use SVD/ALS for latent factor models
- Better handling of sparsity
- Scalable to millions of users

### 2. Hybrid Approach
```
Final Score = α × Collaborative Score + β × Content Score
```
where content score uses genre/actor similarity.

### 3. Temporal Dynamics
- Weight recent ratings higher
- Decay old ratings over time
- Track preference evolution

### 4. Diversity Enhancement
- Add novelty metric
- Balance accuracy vs exploration
- Genre distribution constraints
