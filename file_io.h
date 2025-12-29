#ifndef FILE_IO_H
#define FILE_IO_H

#include "hash_table.h"  // Add this line
#include "graph.h"       // Add this line

void load_movies(const char* filename, HashTable* movie_table);
void load_users(const char* filename, HashTable* user_table);
void load_ratings(const char* filename, Graph* graph, HashTable* movie_table, HashTable* user_table);
void save_rating(const char* filename, int user_id, int movie_id, float rating);

#endif
