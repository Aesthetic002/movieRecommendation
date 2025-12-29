#ifndef HASH_TABLE_H
#define HASH_TABLE_H

#define HASH_SIZE 1000

typedef struct HashNode {
    int key;
    void* data;
    struct HashNode* next;
} HashNode;

typedef struct HashTable {
    HashNode* buckets[HASH_SIZE];
    int size;
} HashTable;

HashTable* create_hash_table();
int hash_function(int key);
void hash_insert(HashTable* table, int key, void* data);
void* hash_search(HashTable* table, int key);
void hash_delete(HashTable* table, int key);
void free_hash_table(HashTable* table);

#endif
