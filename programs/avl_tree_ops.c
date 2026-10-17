#include <stdio.h>
#include <stdlib.h>

typedef struct AVLNode {
    int key;
    int height;
    struct AVLNode *left;
    struct AVLNode *right;
} AVLNode;

int max_val(int a, int b) { return (a > b) ? a : b; }
int get_height(AVLNode *n) { return n ? n->height : 0; }
int get_balance(AVLNode *n) { return n ? get_height(n->left) - get_height(n->right) : 0; }

AVLNode* create_node(int key) {
    AVLNode *node = (AVLNode *)malloc(sizeof(AVLNode));
    node->key = key;
    node->height = 1;
    node->left = NULL;
    node->right = NULL;
    return node;
}

AVLNode* right_rotate(AVLNode *y) {
    if (!y || !y->left) return y;
    AVLNode *x = y->left;
    AVLNode *t2 = x->right;
    x->right = y;
    y->left = t2;
    y->height = max_val(get_height(y->left), get_height(y->right)) + 1;
    x->height = max_val(get_height(x->left), get_height(x->right)) + 1;
    return x;
}

AVLNode* left_rotate(AVLNode *x) {
    if (!x || !x->right) return x;
    AVLNode *y = x->right;
    AVLNode *t2 = y->left;
    y->left = x;
    x->right = t2;
    y->height = max_val(get_height(y->left), get_height(y->right)) + 1;
    x->height = max_val(get_height(x->left), get_height(x->right)) + 1;
    return y;
}

AVLNode* insert_avl(AVLNode *node, int key) {
    if (!node) return create_node(key);
    if (key < node->key) node->left = insert_avl(node->left, key);
    else if (key > node->key) node->right = insert_avl(node->right, key);
    else return node;

    node->height = 1 + max_val(get_height(node->left), get_height(node->right));
    int balance = get_balance(node);

    if (balance > 1 && get_balance(node->left) >= 0) return right_rotate(node);
    if (balance > 1 && get_balance(node->left) < 0) {
        node->left = left_rotate(node->left);
        return right_rotate(node);
    }
    if (balance < -1 && get_balance(node->right) <= 0) return left_rotate(node);
    if (balance < -1 && get_balance(node->right) > 0) {
        node->right = right_rotate(node->right);
        return left_rotate(node);
    }
    return node;
}

int search_avl(AVLNode *root, int key) {
    AVLNode *curr = root;
    while (curr) {
        if (key == curr->key) return 1;
        curr = (key < curr->key) ? curr->left : curr->right;
    }
    return 0;
}

void free_avl(AVLNode *root) {
    if (root) {
        free_avl(root->left);
        free_avl(root->right);
        free(root);
    }
}

int main() {
    AVLNode *root = NULL;
    int i, found_count = 0;
    for (i = 0; i < 3000; i++) {
        int k = (i * 2654435761u) % 15000;
        root = insert_avl(root, k);
    }
    for (i = 0; i < 6000; i++) {
        found_count += search_avl(root, i * 2);
    }
    printf("AVL tree complete: found=%d, root_h=%d\n", found_count, get_height(root));
    free_avl(root);
    return 0;
}
