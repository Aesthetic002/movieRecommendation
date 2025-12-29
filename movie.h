#ifndef MOVIE_H
#define MOVIE_H

#define MAX_TITLE 100
#define MAX_GENRE 50

typedef struct Movie {
    int movie_id;
    char title[MAX_TITLE];
    char genre[MAX_GENRE];
    int year;
    float avg_rating;
    int rating_count;
} Movie;

Movie* create_movie(int id, const char* title, const char* genre, int year);
void print_movie(Movie* movie);

#endif
