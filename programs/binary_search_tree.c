#include <stdio.h>
#include <stdlib.h>

struct BSTNode {
    int val;
    struct BSTNode *left, *right;
};

struct BSTNode* insert(struct BSTNode* node, int val) {
    if (node == NULL) {
        struct BSTNode* temp = (struct BSTNode*)malloc(sizeof(struct BSTNode));
        temp->val = val;
        temp->left = temp->right = NULL;
        return temp;
    }
    if (val < node->val)
        node->left = insert(node->left, val);
    else
        node->right = insert(node->right, val);
    return node;
}

void free_tree(struct BSTNode* root) {
    if (root != NULL) {
        free_tree(root->left);
        free_tree(root->right);
        free(root);
    }
}

int main() {
    struct BSTNode* root = NULL;
    for (int i = 0; i < 10000; i++) {
        int val = (i * 2654435761U) % 20000;
        root = insert(root, val);
    }
    printf("BST complete.\n");
    free_tree(root);
    return 0;
}
