#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "graph.h"
#include "hash_table.h"

Graph* create_graph() {
    Graph* graph = (Graph*)malloc(sizeof(Graph));
    graph->nodes = create_hash_table();
    return graph;
}

void add_graph_node(Graph* graph, int id, char type) {
    GraphNode* node = (GraphNode*)malloc(sizeof(GraphNode));
    node->id = id;
    node->type = type;
    node->edges = NULL;
    node->degree = 0;
    hash_insert(graph->nodes, id, node);
}

void add_edge(Graph* graph, int user_id, int movie_id, float rating) {
    GraphNode* user_node = (GraphNode*)hash_search(graph->nodes, user_id);
    GraphNode* movie_node = (GraphNode*)hash_search(graph->nodes, movie_id);
    
    if (user_node == NULL) {
        add_graph_node(graph, user_id, 'U');
        user_node = (GraphNode*)hash_search(graph->nodes, user_id);
    }
    if (movie_node == NULL) {
        add_graph_node(graph, movie_id, 'M');
        movie_node = (GraphNode*)hash_search(graph->nodes, movie_id);
    }
    
    EdgeNode* existing = user_node->edges;
    while (existing != NULL) {
        if (existing->target_id == movie_id) {
            existing->rating = rating;
            return;
        }
        existing = existing->next;
    }
    
    EdgeNode* edge1 = (EdgeNode*)malloc(sizeof(EdgeNode));
    edge1->target_id = movie_id;
    edge1->rating = rating;
    edge1->target_type = 'M';
    edge1->next = user_node->edges;
    user_node->edges = edge1;
    user_node->degree++;
    
    EdgeNode* edge2 = (EdgeNode*)malloc(sizeof(EdgeNode));
    edge2->target_id = user_id;
    edge2->rating = rating;
    edge2->target_type = 'U';
    edge2->next = movie_node->edges;
    movie_node->edges = edge2;
    movie_node->degree++;
}

void remove_edge(Graph* graph, int user_id, int movie_id) {
    GraphNode* user_node = (GraphNode*)hash_search(graph->nodes, user_id);
    GraphNode* movie_node = (GraphNode*)hash_search(graph->nodes, movie_id);
    
    if (user_node == NULL || movie_node == NULL) return;
    
    EdgeNode* current = user_node->edges;
    EdgeNode* prev = NULL;
    while (current != NULL) {
        if (current->target_id == movie_id) {
            if (prev == NULL) {
                user_node->edges = current->next;
            } else {
                prev->next = current->next;
            }
            free(current);
            user_node->degree--;
            break;
        }
        prev = current;
        current = current->next;
    }
    
    current = movie_node->edges;
    prev = NULL;
    while (current != NULL) {
        if (current->target_id == user_id) {
            if (prev == NULL) {
                movie_node->edges = current->next;
            } else {
                prev->next = current->next;
            }
            free(current);
            movie_node->degree--;
            break;
        }
        prev = current;
        current = current->next;
    }
}

EdgeNode* get_edges(Graph* graph, int id) {
    GraphNode* node = (GraphNode*)hash_search(graph->nodes, id);
    if (node == NULL) return NULL;
    return node->edges;
}

void print_graph_node(Graph* graph, int id) {
    GraphNode* node = (GraphNode*)hash_search(graph->nodes, id);
    if (node == NULL) {
        printf("Node not found\n");
        return;
    }
    
    printf("Node ID: %d, Type: %c, Degree: %d\n", node->id, node->type, node->degree);
    EdgeNode* edge = node->edges;
    while (edge != NULL) {
        printf("  -> %d (rating: %.1f)\n", edge->target_id, edge->rating);
        edge = edge->next;
    }
}

void free_graph(Graph* graph) {
    for (int i = 0; i < HASH_SIZE; i++) {
        HashNode* current = graph->nodes->buckets[i];
        while (current != NULL) {
            GraphNode* gnode = (GraphNode*)current->data;
            EdgeNode* edge = gnode->edges;
            while (edge != NULL) {
                EdgeNode* temp = edge;
                edge = edge->next;
                free(temp);
            }
            free(gnode);
            current = current->next;
        }
    }
    free_hash_table(graph->nodes);
    free(graph);
}
