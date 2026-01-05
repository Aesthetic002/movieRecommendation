#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "file_io.h"
#include "movie.h"
#include "user.h"
#include "hash_table.h"
#include "graph.h"

void load_movies(const char* filename, HashTable* movie_table) {
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        printf("Creating sample movies data...\n");
        return;
    }
    
    char line[300];
    fgets(line, sizeof(line), file);
    
    while (fgets(line, sizeof(line), file)) {
        int id, year;
        char title[MAX_TITLE], genre[MAX_GENRE];
        
        if (sscanf(line, "%d,%[^,],%[^,],%d", &id, title, genre, &year) == 4) {
            Movie* movie = create_movie(id, title, genre, year);
            hash_insert(movie_table, id, movie);
        }
    }
    
    fclose(file);
    // printf("Movies loaded successfully.\n");  // Commented for JSON output
}

void load_users(const char* filename, HashTable* user_table) {
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        printf("Creating sample users data...\n");
        return;
    }
    
    char line[200];
    fgets(line, sizeof(line), file);
    
    while (fgets(line, sizeof(line), file)) {
        int id, age;
        char name[MAX_NAME];
        
        if (sscanf(line, "%d,%[^,],%d", &id, name, &age) == 3) {
            User* user = create_user(id, name, age);
            hash_insert(user_table, id, user);
        }
    }
    
    fclose(file);
    // printf("Users loaded successfully.\n");  // Commented for JSON output
}

void load_ratings(const char* filename, Graph* graph, HashTable* movie_table, HashTable* user_table) {
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        printf("Creating sample ratings data...\n");
        return;
    }
    
    char line[200];
    fgets(line, sizeof(line), file);
    
    while (fgets(line, sizeof(line), file)) {
        int user_id, movie_id;
        float rating;
        
        if (sscanf(line, "%d,%d,%f", &user_id, &movie_id, &rating) == 3) {
            add_edge(graph, user_id, movie_id, rating);
            
            User* user = (User*)hash_search(user_table, user_id);
            if (user != NULL) {
                user->ratings_count++;
                user->avg_rating_given = 
                    (user->avg_rating_given * (user->ratings_count - 1) + rating) / user->ratings_count;
            }
            
            Movie* movie = (Movie*)hash_search(movie_table, movie_id);
            if (movie != NULL) {
                movie->rating_count++;
                movie->avg_rating = 
                    (movie->avg_rating * (movie->rating_count - 1) + rating) / movie->rating_count;
            }
        }
    }
    
    fclose(file);
    // printf("Ratings loaded successfully.\n");  // Commented for JSON output
}

void save_rating(const char* filename, int user_id, int movie_id, float rating) {
    FILE* file = fopen(filename, "a");
    if (file == NULL) {
        printf("Error opening file for writing.\n");
        return;
    }
    
    fprintf(file, "%d,%d,%.1f\n", user_id, movie_id, rating);
    fclose(file);
}
