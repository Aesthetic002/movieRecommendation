#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "recommendation.h"
#include "graph.h"
#include "hash_table.h"
#include "user.h"
#include "movie.h"

float calculate_user_similarity(Graph* graph, int user1_id, int user2_id) {
    EdgeNode* user1_edges = get_edges(graph, user1_id);
    EdgeNode* user2_edges = get_edges(graph, user2_id);
    
    if (user1_edges == NULL || user2_edges == NULL) return 0.0;
    
    float sum_product = 0.0;
    float sum1_squared = 0.0;
    float sum2_squared = 0.0;
    int common_count = 0;
    
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

int compare_movie_scores(const void* a, const void* b) {
    MovieScore* score_a = (MovieScore*)a;
    MovieScore* score_b = (MovieScore*)b;
    if (score_b->predicted_rating > score_a->predicted_rating) return 1;
    if (score_b->predicted_rating < score_a->predicted_rating) return -1;
    return 0;
}

RecommendationList* generate_recommendations(Graph* graph, HashTable* user_table, 
                                             HashTable* movie_table, int target_user_id, int top_n) {
    EdgeNode* target_edges = get_edges(graph, target_user_id);
    if (target_edges == NULL) {
        printf("User has no ratings yet.\n");
        return NULL;
    }
    
    int* watched_movies = (int*)calloc(10000, sizeof(int));
    EdgeNode* edge = target_edges;
    while (edge != NULL) {
        watched_movies[edge->target_id] = 1;
        edge = edge->next;
    }
    
    typedef struct {
        int user_id;
        float similarity;
    } SimilarUser;
    
    SimilarUser* similar_users = (SimilarUser*)malloc(sizeof(SimilarUser) * 1000);
    int similar_count = 0;
    
    for (int i = 0; i < HASH_SIZE; i++) {
        HashNode* current = user_table->buckets[i];
        while (current != NULL) {
            User* user = (User*)current->data;
            if (user->user_id != target_user_id) {
                float similarity = calculate_user_similarity(graph, target_user_id, user->user_id);
                if (similarity > 0.3) {
                    similar_users[similar_count].user_id = user->user_id;
                    similar_users[similar_count].similarity = similarity;
                    similar_count++;
                }
            }
            current = current->next;
        }
    }
    
    if (similar_count == 0) {
        printf("No similar users found.\n");
        free(watched_movies);
        free(similar_users);
        return NULL;
    }
    
    MovieScore* candidate_movies = (MovieScore*)malloc(sizeof(MovieScore) * 1000);
    int candidate_count = 0;
    
    for (int i = 0; i < similar_count; i++) {
        EdgeNode* similar_user_edges = get_edges(graph, similar_users[i].user_id);
        EdgeNode* movie_edge = similar_user_edges;
        
        while (movie_edge != NULL) {
            if (!watched_movies[movie_edge->target_id] && movie_edge->rating >= 3.5) {
                int found = 0;
                for (int j = 0; j < candidate_count; j++) {
                    if (candidate_movies[j].movie_id == movie_edge->target_id) {
                        candidate_movies[j].predicted_rating += 
                            movie_edge->rating * similar_users[i].similarity;
                        found = 1;
                        break;
                    }
                }
                if (!found) {
                    candidate_movies[candidate_count].movie_id = movie_edge->target_id;
                    candidate_movies[candidate_count].predicted_rating = 
                        movie_edge->rating * similar_users[i].similarity;
                    snprintf(candidate_movies[candidate_count].reason, 200, 
                            "Similar users rated this %.1f/5", movie_edge->rating);
                    candidate_count++;
                }
            }
            movie_edge = movie_edge->next;
        }
    }
    
    qsort(candidate_movies, candidate_count, sizeof(MovieScore), compare_movie_scores);
    
    RecommendationList* rec_list = (RecommendationList*)malloc(sizeof(RecommendationList));
    rec_list->count = (candidate_count < top_n) ? candidate_count : top_n;
    rec_list->movies = (MovieScore*)malloc(sizeof(MovieScore) * rec_list->count);
    
    for (int i = 0; i < rec_list->count; i++) {
        rec_list->movies[i] = candidate_movies[i];
    }
    
    free(watched_movies);
    free(similar_users);
    free(candidate_movies);
    
    return rec_list;
}

void print_recommendations(RecommendationList* rec_list, HashTable* movie_table) {
    if (rec_list == NULL || rec_list->count == 0) {
        printf("No recommendations available.\n");
        return;
    }
    
    printf("\n=== TOP RECOMMENDATIONS ===\n");
    for (int i = 0; i < rec_list->count; i++) {
        Movie* movie = (Movie*)hash_search(movie_table, rec_list->movies[i].movie_id);
        if (movie != NULL) {
            printf("\n%d. %s (%d)\n", i + 1, movie->title, movie->year);
            printf("   Genre: %s\n", movie->genre);
            printf("   Predicted Score: %.2f\n", rec_list->movies[i].predicted_rating);
            printf("   Reason: %s\n", rec_list->movies[i].reason);
        }
    }
}

void free_recommendations(RecommendationList* rec_list) {
    if (rec_list != NULL) {
        free(rec_list->movies);
        free(rec_list);
    }
}
