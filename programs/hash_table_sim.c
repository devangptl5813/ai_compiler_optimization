#include <stdio.h>
#include <stdlib.h>

#define TABLE_SIZE 10007

struct HashNode {
    int key;
    int value;
    struct HashNode* next;
};

struct HashTable {
    struct HashNode* buckets[TABLE_SIZE];
};

unsigned int hash(int key) {
    return ((unsigned int)key * 2654435761U) % TABLE_SIZE;
}

void insert(struct HashTable* ht, int key, int val) {
    unsigned int idx = hash(key);
    struct HashNode* node = (struct HashNode*)malloc(sizeof(struct HashNode));
    node->key = key; node->value = val;
    node->next = ht->buckets[idx];
    ht->buckets[idx] = node;
}

int lookup(struct HashTable* ht, int key) {
    unsigned int idx = hash(key);
    struct HashNode* curr = ht->buckets[idx];
    while (curr) {
        if (curr->key == key) return curr->value;
        curr = curr->next;
    }
    return -1;
}

int main() {
    struct HashTable ht = { {NULL} };
    for (int i = 0; i < 15000; i++) {
        insert(&ht, i, i * 2);
    }
    int hits = 0;
    for (int i = 0; i < 25000; i++) {
        if (lookup(&ht, i % 20000) != -1) hits++;
    }
    printf("Hash table complete: hits=%d\n", hits);
    for (int i = 0; i < TABLE_SIZE; i++) {
        struct HashNode* curr = ht.buckets[i];
        while (curr) {
            struct HashNode* tmp = curr;
            curr = curr->next;
            free(tmp);
        }
    }
    return 0;
}
