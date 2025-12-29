#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "movie.h"
#include "user.h"
#include "hash_table.h"
#include "graph.h"
#include "recommendation.h"
#include "file_io.h"

void create_sample_data() {
    FILE* movies = fopen("movies.csv", "w");
    fprintf(movies, "movie_id,title,genre,year\n");
    fprintf(movies, "1,The Shawshank Redemption,Drama,1994\n");
    fprintf(movies, "2,The Godfather,Crime,1972\n");
    fprintf(movies, "3,The Dark Knight,Action,2008\n");
    fprintf(movies, "4,Pulp Fiction,Crime,1994\n");
    fprintf(movies, "5,Forrest Gump,Drama,1994\n");
    fprintf(movies, "6,Inception,Sci-Fi,2010\n");
    fprintf(movies, "7,The Matrix,Sci-Fi,1999\n");
    fprintf(movies, "8,Goodfellas,Crime,1990\n");
    fprintf(movies, "9,Interstellar,Sci-Fi,2014\n");
    fprintf(movies, "10,The Prestige,Mystery,2006\n");
    fclose(movies);
    
    FILE* users = fopen("users.csv", "w");
    fprintf(users, "user_id,name,age\n");
    fprintf(users, "101,Alice,25\n");
    fprintf(users, "102,Bob,30\n");
    fprintf(users, "103,Charlie,28\n");
    fprintf(users, "104,Diana,35\n");
    fprintf(users, "105,Eve,22\n");
    fclose(users);
    
    FILE* ratings = fopen("ratings.csv", "w");
    fprintf(ratings, "user_id,movie_id,rating\n");
    fprintf(ratings, "101,1,5.0\n");
    fprintf(ratings, "101,3,4.5\n");
    fprintf(ratings, "101,6,4.8\n");
    fprintf(ratings, "102,1,4.5\n");
    fprintf(ratings, "102,2,5.0\n");
    fprintf(ratings, "102,4,4.7\n");
    fprintf(ratings, "103,3,5.0\n");
    fprintf(ratings, "103,6,4.5\n");
    fprintf(ratings, "103,7,4.8\n");
    fprintf(ratings, "104,2,4.9\n");
    fprintf(ratings, "104,4,4.6\n");
    fprintf(ratings, "104,8,4.8\n");
    fprintf(ratings, "105,5,5.0\n");
    fprintf(ratings, "105,1,4.7\n");
    fprintf(ratings, "105,9,4.5\n");
    fclose(ratings);
}

void display_all_movies(HashTable* movie_table) {
    printf("\n=== ALL MOVIES ===\n");
    for (int i = 0; i < HASH_SIZE; i++) {
        HashNode* current = movie_table->buckets[i];
        while (current != NULL) {
            Movie* movie = (Movie*)current->data;
            printf("\n");
            print_movie(movie);
            current = current->next;
        }
    }
}

void display_all_users(HashTable* user_table) {
    printf("\n=== ALL USERS ===\n");
    for (int i = 0; i < HASH_SIZE; i++) {
        HashNode* current = user_table->buckets[i];
        while (current != NULL) {
            User* user = (User*)current->data;
            printf("\n");
            print_user(user);
            current = current->next;
        }
    }
}

void search_movie_by_title(HashTable* movie_table, const char* search_term) {
    printf("\n=== SEARCH RESULTS ===\n");
    int found = 0;
    for (int i = 0; i < HASH_SIZE; i++) {
        HashNode* current = movie_table->buckets[i];
        while (current != NULL) {
            Movie* movie = (Movie*)current->data;
            if (strstr(movie->title, search_term) != NULL) {
                printf("\n");
                print_movie(movie);
                found = 1;
            }
            current = current->next;
        }
    }
    if (!found) {
        printf("No movies found matching '%s'\n", search_term);
    }
}

void add_new_rating(Graph* graph, HashTable* user_table, HashTable* movie_table) {
    int user_id, movie_id;
    float rating;
    
    printf("\nEnter User ID: ");
    scanf("%d", &user_id);
    printf("Enter Movie ID: ");
    scanf("%d", &movie_id);
    printf("Enter Rating (1.0-5.0): ");
    scanf("%f", &rating);
    
    if (rating < 1.0 || rating > 5.0) {
        printf("Invalid rating. Must be between 1.0 and 5.0\n");
        return;
    }
    
    User* user = (User*)hash_search(user_table, user_id);
    Movie* movie = (Movie*)hash_search(movie_table, movie_id);
    
    if (user == NULL) {
        printf("User not found.\n");
        return;
    }
    if (movie == NULL) {
        printf("Movie not found.\n");
        return;
    }
    
    add_edge(graph, user_id, movie_id, rating);
    user->ratings_count++;
    user->avg_rating_given = (user->avg_rating_given * (user->ratings_count - 1) + rating) / user->ratings_count;
    movie->rating_count++;
    movie->avg_rating = (movie->avg_rating * (movie->rating_count - 1) + rating) / movie->rating_count;
    
    save_rating("ratings.csv", user_id, movie_id, rating);
    printf("\nRating added successfully!\n");
}

void display_user_ratings(Graph* graph, HashTable* movie_table, int user_id) {
    printf("\n=== USER RATINGS ===\n");
    EdgeNode* edges = get_edges(graph, user_id);
    if (edges == NULL) {
        printf("User has no ratings.\n");
        return;
    }
    
    while (edges != NULL) {
        Movie* movie = (Movie*)hash_search(movie_table, edges->target_id);
        if (movie != NULL) {
            printf("%s - Rating: %.1f\n", movie->title, edges->rating);
        }
        edges = edges->next;
    }
}

int main() {
    HashTable* movie_table = create_hash_table();
    HashTable* user_table = create_hash_table();
    Graph* graph = create_graph();
    
    int choice;
    int data_loaded = 0;
    
    while (1) {
        printf("\n========================================\n");
        printf("   MOVIE RECOMMENDATION SYSTEM\n");
        printf("========================================\n");
        printf("1.  Load data from files\n");
        printf("2.  Create sample data\n");
        printf("3.  Display all movies\n");
        printf("4.  Display all users\n");
        printf("5.  Search movie by title\n");
        printf("6.  Add new rating\n");
        printf("7.  Get recommendations for a user\n");
        printf("8.  Display user's ratings\n");
        printf("9.  Display graph statistics\n");
        printf("10. Exit\n");
        printf("========================================\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);
        
        switch (choice) {
            case 1:
                load_movies("movies.csv", movie_table);
                load_users("users.csv", user_table);
                load_ratings("ratings.csv", graph, movie_table, user_table);
                data_loaded = 1;
                break;
                
            case 2:
                create_sample_data();
                load_movies("movies.csv", movie_table);
                load_users("users.csv", user_table);
                load_ratings("ratings.csv", graph, movie_table, user_table);
                data_loaded = 1;
                break;
                
            case 3:
                if (!data_loaded) {
                    printf("Please load data first.\n");
                } else {
                    display_all_movies(movie_table);
                }
                break;
                
            case 4:
                if (!data_loaded) {
                    printf("Please load data first.\n");
                } else {
                    display_all_users(user_table);
                }
                break;
                
            case 5: {
                if (!data_loaded) {
                    printf("Please load data first.\n");
                } else {
                    char search_term[MAX_TITLE];
                    printf("Enter movie title to search: ");
                    scanf(" %[^\n]", search_term);
                    search_movie_by_title(movie_table, search_term);
                }
                break;
            }
                
            case 6:
                if (!data_loaded) {
                    printf("Please load data first.\n");
                } else {
                    add_new_rating(graph, user_table, movie_table);
                }
                break;
                
            case 7: {
                if (!data_loaded) {
                    printf("Please load data first.\n");
                } else {
                    int user_id, top_n;
                    printf("Enter User ID: ");
                    scanf("%d", &user_id);
                    printf("Enter number of recommendations: ");
                    scanf("%d", &top_n);
                    
                    RecommendationList* rec_list = generate_recommendations(
                        graph, user_table, movie_table, user_id, top_n);
                    print_recommendations(rec_list, movie_table);
                    free_recommendations(rec_list);
                }
                break;
            }
                
            case 8: {
                if (!data_loaded) {
                    printf("Please load data first.\n");
                } else {
                    int user_id;
                    printf("Enter User ID: ");
                    scanf("%d", &user_id);
                    display_user_ratings(graph, movie_table, user_id);
                }
                break;
            }
                
            case 9:
                if (!data_loaded) {
                    printf("Please load data first.\n");
                } else {
                    printf("\n=== SYSTEM STATISTICS ===\n");
                    printf("Total Movies: %d\n", movie_table->size);
                    printf("Total Users: %d\n", user_table->size);
                }
                break;
                
            case 10:
                printf("Thank you for using the Movie Recommendation System!\n");
                free_graph(graph);
                free_hash_table(movie_table);
                free_hash_table(user_table);
                return 0;
                
            default:
                printf("Invalid choice. Please try again.\n");
        }
    }
    
    return 0;
}
