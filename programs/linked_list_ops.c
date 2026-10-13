#include <stdio.h>
#include <stdlib.h>

struct Node {
    int data;
    struct Node* next;
};

struct Node* create_node(int data) {
    struct Node* new_node = (struct Node*)malloc(sizeof(struct Node));
    new_node->data = data;
    new_node->next = NULL;
    return new_node;
}

struct Node* reverse_list(struct Node* head) {
    struct Node* prev = NULL;
    struct Node* curr = head;
    struct Node* next = NULL;
    while (curr != NULL) {
        next = curr->next;
        curr->next = prev;
        prev = curr;
        curr = next;
    }
    return prev;
}

int main() {
    struct Node* head = create_node(0);
    struct Node* curr = head;
    for (int i = 1; i < 30000; i++) {
        curr->next = create_node(i);
        curr = curr->next;
    }

    for (int iter = 0; iter < 5; iter++) {
        head = reverse_list(head);
    }

    int count = 0;
    curr = head;
    while (curr != NULL) {
        count++;
        struct Node* temp = curr;
        curr = curr->next;
        free(temp);
    }
    printf("Linked list complete: processed %d nodes\n", count);
    return 0;
}
