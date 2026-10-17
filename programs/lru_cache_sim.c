#include <stdio.h>
#include <stdlib.h>

#define CAPACITY 512
#define HASH_SIZE 1024

typedef struct Node {
    int key;
    int val;
    struct Node *prev;
    struct Node *next;
} Node;

typedef struct {
    int capacity;
    int size;
    Node *head;
    Node *tail;
    Node *hash_table[HASH_SIZE];
} LRUCache;

LRUCache* create_cache(int cap) {
    LRUCache *cache = (LRUCache *)calloc(1, sizeof(LRUCache));
    cache->capacity = cap;
    cache->head = (Node *)calloc(1, sizeof(Node));
    cache->tail = (Node *)calloc(1, sizeof(Node));
    cache->head->next = cache->tail;
    cache->tail->prev = cache->head;
    return cache;
}

void remove_node(Node *node) {
    node->prev->next = node->next;
    node->next->prev = node->prev;
}

void add_to_head(LRUCache *cache, Node *node) {
    node->next = cache->head->next;
    node->prev = cache->head;
    cache->head->next->prev = node;
    cache->head->next = node;
}

int lru_get(LRUCache *cache, int key) {
    int slot = key % HASH_SIZE;
    Node *curr = cache->hash_table[slot];
    if (!curr || curr->key != key) return -1;
    remove_node(curr);
    add_to_head(cache, curr);
    return curr->val;
}

void lru_put(LRUCache *cache, int key, int val) {
    int slot = key % HASH_SIZE;
    Node *curr = cache->hash_table[slot];
    if (curr && curr->key == key) {
        curr->val = val;
        remove_node(curr);
        add_to_head(cache, curr);
        return;
    }
    if (cache->size >= cache->capacity) {
        Node *lru = cache->tail->prev;
        cache->hash_table[lru->key % HASH_SIZE] = NULL;
        remove_node(lru);
        free(lru);
        cache->size--;
    }
    Node *new_node = (Node *)malloc(sizeof(Node));
    new_node->key = key;
    new_node->val = val;
    cache->hash_table[slot] = new_node;
    add_to_head(cache, new_node);
    cache->size++;
}

void free_cache(LRUCache *cache) {
    Node *curr = cache->head;
    while (curr) {
        Node *nxt = curr->next;
        free(curr);
        curr = nxt;
    }
    free(cache);
}

int main() {
    LRUCache *cache = create_cache(CAPACITY);
    int hits = 0, misses = 0;
    for (int iter = 0; iter < 12000; iter++) {
        int key = (iter * 17) % (CAPACITY * 2);
        if (iter % 3 == 0) {
            lru_put(cache, key, iter);
        } else {
            int v = lru_get(cache, key);
            if (v >= 0) hits++; else misses++;
        }
    }
    printf("LRU Cache complete: hits=%d, misses=%d\n", hits, misses);
    free_cache(cache);
    return 0;
}
