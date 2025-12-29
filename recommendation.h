#ifndef RECOMMENDATION_H
#define RECOMMENDATION_H

#include "hash_table.h"  // Add this line
#include "graph.h"       // Add this line

typedef struct MovieScore {
    int movie_id;
    float predicted_rating;
    char reason[200];
} MovieScore;

typedef struct RecommendationList {
    MovieScore* movies;
    int count;
} RecommendationList;

float calculate_user_similarity(Graph* graph, int user1_id, int user2_id);
RecommendationList* generate_recommendations(Graph* graph, HashTable* user_table, 
                                             HashTable* movie_table, int target_user_id, int top_n);
void print_recommendations(RecommendationList* rec_list, HashTable* movie_table);
void free_recommendations(RecommendationList* rec_list);

#endif
