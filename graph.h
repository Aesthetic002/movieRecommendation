#ifndef GRAPH_H
#define GRAPH_H

#include "hash_table.h"  // Add this line

typedef struct EdgeNode {
    int target_id;
    float rating;
    char target_type;
    struct EdgeNode* next;
} EdgeNode;

typedef struct GraphNode {
    int id;
    char type;
    EdgeNode* edges;
    int degree;
} GraphNode;

typedef struct Graph {
    HashTable* nodes;
} Graph;

Graph* create_graph();
void add_graph_node(Graph* graph, int id, char type);
void add_edge(Graph* graph, int user_id, int movie_id, float rating);
void remove_edge(Graph* graph, int user_id, int movie_id);
EdgeNode* get_edges(Graph* graph, int id);
void print_graph_node(Graph* graph, int id);
void free_graph(Graph* graph);

#endif
