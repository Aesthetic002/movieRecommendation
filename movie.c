#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "movie.h"

Movie* create_movie(int id, const char* title, const char* genre, int year) {
    Movie* movie = (Movie*)malloc(sizeof(Movie));
    movie->movie_id = id;
    strncpy(movie->title, title, MAX_TITLE - 1);
    movie->title[MAX_TITLE - 1] = '\0';
    strncpy(movie->genre, genre, MAX_GENRE - 1);
    movie->genre[MAX_GENRE - 1] = '\0';
    movie->year = year;
    movie->avg_rating = 0.0;
    movie->rating_count = 0;
    return movie;
}

void print_movie(Movie* movie) {
    printf("Movie ID: %d\n", movie->movie_id);
    printf("Title: %s\n", movie->title);
    printf("Genre: %s\n", movie->genre);
    printf("Year: %d\n", movie->year);
    printf("Average Rating: %.2f (%d ratings)\n", movie->avg_rating, movie->rating_count);
}
