#include <stdio.h>
#include <stdlib.h>
#include "hash_table.h"

HashTable* create_hash_table() {
    HashTable* table = (HashTable*)malloc(sizeof(HashTable));
    for (int i = 0; i < HASH_SIZE; i++) {
        table->buckets[i] = NULL;
    }
    table->size = 0;
    return table;
}

int hash_function(int key) {
    return abs(key) % HASH_SIZE;
}

void hash_insert(HashTable* table, int key, void* data) {
    int index = hash_function(key);
    HashNode* existing = table->buckets[index];
    
    while (existing != NULL) {
        if (existing->key == key) {
            existing->data = data;
            return;
        }
        existing = existing->next;
    }
    
    HashNode* new_node = (HashNode*)malloc(sizeof(HashNode));
    new_node->key = key;
    new_node->data = data;
    new_node->next = table->buckets[index];
    table->buckets[index] = new_node;
    table->size++;
}

void* hash_search(HashTable* table, int key) {
    int index = hash_function(key);
    HashNode* current = table->buckets[index];
    
    while (current != NULL) {
        if (current->key == key) {
            return current->data;
        }
        current = current->next;
    }
    return NULL;
}

void hash_delete(HashTable* table, int key) {
    int index = hash_function(key);
    HashNode* current = table->buckets[index];
    HashNode* prev = NULL;
    
    while (current != NULL) {
        if (current->key == key) {
            if (prev == NULL) {
                table->buckets[index] = current->next;
            } else {
                prev->next = current->next;
            }
            free(current);
            table->size--;
            return;
        }
        prev = current;
        current = current->next;
    }
}

void free_hash_table(HashTable* table) {
    for (int i = 0; i < HASH_SIZE; i++) {
        HashNode* current = table->buckets[i];
        while (current != NULL) {
            HashNode* temp = current;
            current = current->next;
            free(temp);
        }
    }
    free(table);
}
