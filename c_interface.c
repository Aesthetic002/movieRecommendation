// CLI Interface for Django Integration - Minimal changes to existing code
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "movie.h"
#include "user.h"
#include "hash_table.h"
#include "graph.h"
#include "recommendation.h"
#include "file_io.h"

// Print recommendations in JSON format for Django to parse
void print_recommendations_json(RecommendationList* rec_list, HashTable* movie_table) {
    printf("[");
    for (int i = 0; i < rec_list->count; i++) {
        Movie* movie = (Movie*)hash_search(movie_table, rec_list->movies[i].movie_id);
        if (movie != NULL) {
            if (i > 0) printf(",");
            printf("{\"movie_id\":%d,\"title\":\"%s\",\"genre\":\"%s\",\"year\":%d,\"predicted_rating\":%.2f,\"reason\":\"%s\"}",
                   movie->movie_id,
                   movie->title,
                   movie->genre,
                   movie->year,
                   rec_list->movies[i].predicted_rating,
                   rec_list->movies[i].reason);
        }
    }
    printf("]\n");
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <command> [args]\n", argv[0]);
        fprintf(stderr, "Commands:\n");
        fprintf(stderr, "  recommend <user_id> <count> - Get recommendations for user\n");
        fprintf(stderr, "  add_rating <user_id> <movie_id> <rating> - Add a rating\n");
        return 1;
    }
    
    HashTable* movie_table = create_hash_table();
    HashTable* user_table = create_hash_table();
    Graph* graph = create_graph();
    
    // Load data (suppress output by redirecting to /dev/null or just remove prints from file_io.c)
    load_movies("movies.csv", movie_table);
    load_users("users.csv", user_table);
    load_ratings("ratings.csv", graph, movie_table, user_table);
    
    if (strcmp(argv[1], "recommend") == 0) {
        if (argc < 4) {
            fprintf(stderr, "Usage: recommend <user_id> <count>\n");
            return 1;
        }
        
        int user_id = atoi(argv[2]);
        int count = atoi(argv[3]);
        
        RecommendationList* rec_list = generate_recommendations(
            graph, user_table, movie_table, user_id, count);
        
        print_recommendations_json(rec_list, movie_table);
        free_recommendations(rec_list);
        
    } else if (strcmp(argv[1], "add_rating") == 0) {
        if (argc < 5) {
            fprintf(stderr, "Usage: add_rating <user_id> <movie_id> <rating>\n");
            return 1;
        }
        
        int user_id = atoi(argv[2]);
        int movie_id = atoi(argv[3]);
        float rating = atof(argv[4]);
        
        if (rating < 1.0 || rating > 5.0) {
            fprintf(stderr, "Invalid rating. Must be between 1.0 and 5.0\n");
            return 1;
        }
        
        User* user = (User*)hash_search(user_table, user_id);
        Movie* movie = (Movie*)hash_search(movie_table, movie_id);
        
        if (user == NULL || movie == NULL) {
            fprintf(stderr, "User or movie not found\n");
            return 1;
        }
        
        add_edge(graph, user_id, movie_id, rating);
        user->ratings_count++;
        user->avg_rating_given = (user->avg_rating_given * (user->ratings_count - 1) + rating) / user->ratings_count;
        movie->rating_count++;
        movie->avg_rating = (movie->avg_rating * (movie->rating_count - 1) + rating) / movie->rating_count;
        
        save_rating("ratings.csv", user_id, movie_id, rating);
        printf("{\"status\":\"success\"}\n");
        
    } else {
        fprintf(stderr, "Unknown command: %s\n", argv[1]);
        return 1;
    }
    
    free_graph(graph);
    free_hash_table(movie_table);
    free_hash_table(user_table);
    
    return 0;
}
