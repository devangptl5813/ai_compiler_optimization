import os

programs = {}

programs["matrix_mult.c"] = r"""#include <stdio.h>
#include <stdlib.h>

#define N 180

void matrix_multiply(double A[N][N], double B[N][N], double C[N][N]) {
    int i, j, k;
    for (i = 0; i < N; i++) {
        for (j = 0; j < N; j++) {
            C[i][j] = 0.0;
            for (k = 0; k < N; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

int main() {
    static double A[N][N], B[N][N], C[N][N];
    int i, j, iter;
    for (i = 0; i < N; i++) {
        for (j = 0; j < N; j++) {
            A[i][j] = (i + j) * 0.5;
            B[i][j] = (i - j) * 0.2;
        }
    }
    for (iter = 0; iter < 2; iter++) {
        matrix_multiply(A, B, C);
    }
    printf("Matrix mult complete: C[0][0]=%.2f\n", C[0][0]);
    return 0;
}
"""

programs["bubble_sort.c"] = r"""#include <stdio.h>
#include <stdlib.h>

#define SIZE 2500

void bubble_sort(int arr[], int n) {
    int i, j, temp;
    for (i = 0; i < n - 1; i++) {
        for (j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

int main() {
    int *arr = (int *)malloc(SIZE * sizeof(int));
    int i;
    for (i = 0; i < SIZE; i++) {
        arr[i] = SIZE - i;
    }
    bubble_sort(arr, SIZE);
    printf("Bubble sort complete: arr[0]=%d, arr[%d]=%d\n", arr[0], SIZE-1, arr[SIZE-1]);
    free(arr);
    return 0;
}
"""

programs["quick_sort.c"] = r"""#include <stdio.h>
#include <stdlib.h>

#define SIZE 40000

void swap(int* a, int* b) {
    int t = *a;
    *a = *b;
    *b = t;
}

int partition(int arr[], int low, int high) {
    int pivot = arr[high];
    int i = (low - 1);
    for (int j = low; j <= high - 1; j++) {
        if (arr[j] < pivot) {
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[high]);
    return (i + 1);
}

void quick_sort(int arr[], int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quick_sort(arr, low, pi - 1);
        quick_sort(arr, pi + 1, high);
    }
}

int main() {
    int *arr = (int *)malloc(SIZE * sizeof(int));
    for (int i = 0; i < SIZE; i++) {
        arr[i] = (i * 37 + 17) % SIZE;
    }
    quick_sort(arr, 0, SIZE - 1);
    printf("Quick sort complete: arr[0]=%d\n", arr[0]);
    free(arr);
    return 0;
}
"""

programs["fibonacci.c"] = r"""#include <stdio.h>

long long fibonacci_recursive(int n) {
    if (n <= 1) return n;
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2);
}

int main() {
    long long sum = 0;
    for (int i = 0; i < 5; i++) {
        sum += fibonacci_recursive(30);
    }
    printf("Fibonacci complete: sum=%lld\n", sum);
    return 0;
}
"""

programs["string_processing.c"] = r"""#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define STR_LEN 30000

int is_palindrome(const char *str, int len) {
    int left = 0, right = len - 1;
    while (left < right) {
        if (str[left] != str[right]) return 0;
        left++;
        right--;
    }
    return 1;
}

void reverse_string(char *str, int len) {
    int left = 0, right = len - 1;
    while (left < right) {
        char temp = str[left];
        str[left] = str[right];
        str[right] = temp;
        left++;
        right--;
    }
}

int main() {
    char *buf = (char *)malloc(STR_LEN + 1);
    for (int i = 0; i < STR_LEN; i++) {
        buf[i] = 'a' + (i % 26);
    }
    buf[STR_LEN] = '\0';

    int pal_count = 0;
    for (int iter = 0; iter < 50; iter++) {
        reverse_string(buf, STR_LEN);
        if (is_palindrome(buf, STR_LEN)) {
            pal_count++;
        }
    }
    printf("String processing complete: pal_count=%d\n", pal_count);
    free(buf);
    return 0;
}
"""

programs["graph_bfs.c"] = r"""#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define V 300

void bfs(int adj[V][V], int start) {
    bool visited[V] = {false};
    int queue[V];
    int front = 0, rear = 0;

    visited[start] = true;
    queue[rear++] = start;

    int visited_count = 0;
    while (front < rear) {
        int curr = queue[front++];
        visited_count++;
        for (int i = 0; i < V; i++) {
            if (adj[curr][i] && !visited[i]) {
                visited[i] = true;
                queue[rear++] = i;
            }
        }
    }
}

int main() {
    static int adj[V][V];
    for (int i = 0; i < V; i++) {
        for (int j = 0; j < V; j++) {
            adj[i][j] = ((i + j) % 5 == 0) ? 1 : 0;
        }
    }
    for (int run = 0; run < 5; run++) {
        bfs(adj, run % V);
    }
    printf("Graph BFS complete.\n");
    return 0;
}
"""

programs["dynamic_programming.c"] = r"""#include <stdio.h>
#include <stdlib.h>

#define MAX(a, b) (((a) > (b)) ? (a) : (b))
#define ITEMS 150
#define CAPACITY 400

int knapsack(int W, int wt[], int val[], int n) {
    int i, w;
    int **K = (int **)malloc((n + 1) * sizeof(int *));
    for (i = 0; i <= n; i++)
        K[i] = (int *)malloc((W + 1) * sizeof(int));

    for (i = 0; i <= n; i++) {
        for (w = 0; w <= W; w++) {
            if (i == 0 || w == 0)
                K[i][w] = 0;
            else if (wt[i - 1] <= w)
                K[i][w] = MAX(val[i - 1] + K[i - 1][w - wt[i - 1]], K[i - 1][w]);
            else
                K[i][w] = K[i - 1][w];
        }
    }
    int result = K[n][W];
    for (i = 0; i <= n; i++) free(K[i]);
    free(K);
    return result;
}

int main() {
    int wt[ITEMS], val[ITEMS];
    for (int i = 0; i < ITEMS; i++) {
        wt[i] = (i % 20) + 1;
        val[i] = (i % 50) + 10;
    }
    int max_val = 0;
    for (int iter = 0; iter < 5; iter++) {
        max_val += knapsack(CAPACITY, wt, val, ITEMS);
    }
    printf("Knapsack DP complete: max_val=%d\n", max_val);
    return 0;
}
"""

programs["matrix_transpose.c"] = r"""#include <stdio.h>
#include <stdlib.h>

#define DIM 350

void transpose(double src[DIM][DIM], double dst[DIM][DIM]) {
    for (int i = 0; i < DIM; i++) {
        for (int j = 0; j < DIM; j++) {
            dst[j][i] = src[i][j];
        }
    }
}

int main() {
    static double src[DIM][DIM], dst[DIM][DIM];
    for (int i = 0; i < DIM; i++) {
        for (int j = 0; j < DIM; j++) {
            src[i][j] = i * 1.0 + j * 0.5;
        }
    }
    for (int iter = 0; iter < 30; iter++) {
        transpose(src, dst);
    }
    printf("Transpose complete: dst[0][0]=%.2f\n", dst[0][0]);
    return 0;
}
"""

programs["merge_sort.c"] = r"""#include <stdio.h>
#include <stdlib.h>

#define SIZE 30000

void merge(int arr[], int l, int m, int r) {
    int i, j, k;
    int n1 = m - l + 1;
    int n2 = r - m;
    int *L = (int *)malloc(n1 * sizeof(int));
    int *R = (int *)malloc(n2 * sizeof(int));

    for (i = 0; i < n1; i++) L[i] = arr[l + i];
    for (j = 0; j < n2; j++) R[j] = arr[m + 1 + j];

    i = 0; j = 0; k = l;
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k] = L[i]; i++;
        } else {
            arr[k] = R[j]; j++;
        }
        k++;
    }
    while (i < n1) { arr[k] = L[i]; i++; k++; }
    while (j < n2) { arr[k] = R[j]; j++; k++; }
    free(L); free(R);
}

void merge_sort(int arr[], int l, int r) {
    if (l < r) {
        int m = l + (r - l) / 2;
        merge_sort(arr, l, m);
        merge_sort(arr, m + 1, r);
        merge(arr, l, m, r);
    }
}

int main() {
    int *arr = (int *)malloc(SIZE * sizeof(int));
    for (int i = 0; i < SIZE; i++) arr[i] = SIZE - i;
    merge_sort(arr, 0, SIZE - 1);
    printf("Merge sort complete: arr[0]=%d\n", arr[0]);
    free(arr);
    return 0;
}
"""

programs["insertion_sort.c"] = r"""#include <stdio.h>
#include <stdlib.h>

#define SIZE 2500

void insertion_sort(int arr[], int n) {
    int i, key, j;
    for (i = 1; i < n; i++) {
        key = arr[i];
        j = i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j = j - 1;
        }
        arr[j + 1] = key;
    }
}

int main() {
    int *arr = (int *)malloc(SIZE * sizeof(int));
    for (int i = 0; i < SIZE; i++) arr[i] = (i * 13) % SIZE;
    insertion_sort(arr, SIZE);
    printf("Insertion sort complete: arr[0]=%d\n", arr[0]);
    free(arr);
    return 0;
}
"""

programs["factorial_iterative.c"] = r"""#include <stdio.h>

double compute_series(int n) {
    double res = 1.0;
    for (int i = 1; i <= n; i++) {
        res += (double)i / (i + 1) * 0.99999;
    }
    return res;
}

int main() {
    double total = 0.0;
    for (int iter = 0; iter < 3000; iter++) {
        total += compute_series(1000);
    }
    printf("Factorial/Series complete: total=%.4f\n", total);
    return 0;
}
"""

programs["towers_of_hanoi.c"] = r"""#include <stdio.h>

long long hanoi_count = 0;

void solve_hanoi(int n, char from, char to, char aux) {
    if (n == 1) {
        hanoi_count++;
        return;
    }
    solve_hanoi(n - 1, from, aux, to);
    hanoi_count++;
    solve_hanoi(n - 1, aux, to, from);
}

int main() {
    solve_hanoi(21, 'A', 'C', 'B');
    printf("Hanoi complete: moves=%lld\n", hanoi_count);
    return 0;
}
"""

programs["prime_sieve.c"] = r"""#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define LIMIT 2500000

int count_primes(int n) {
    bool *prime = (bool *)malloc((n + 1) * sizeof(bool));
    for (int i = 0; i <= n; i++) prime[i] = true;
    prime[0] = prime[1] = false;

    for (int p = 2; p * p <= n; p++) {
        if (prime[p]) {
            for (int i = p * p; i <= n; i += p) {
                prime[i] = false;
            }
        }
    }
    int count = 0;
    for (int i = 2; i <= n; i++) {
        if (prime[i]) count++;
    }
    free(prime);
    return count;
}

int main() {
    int primes = count_primes(LIMIT);
    printf("Prime sieve complete: count=%d\n", primes);
    return 0;
}
"""

programs["sum_series.c"] = r"""#include <stdio.h>
#include <math.h>

int main() {
    double sum = 0.0;
    for (long i = 1; i <= 1500000; i++) {
        sum += sin((double)i) * cos((double)i) + exp(1.0 / i);
    }
    printf("Sum series complete: sum=%.4f\n", sum);
    return 0;
}
"""

programs["string_pattern_match.c"] = r"""#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TEXT_LEN 50000
#define PAT_LEN 10

int naive_search(const char *text, const char *pat) {
    int M = strlen(pat);
    int N = strlen(text);
    int matches = 0;

    for (int i = 0; i <= N - M; i++) {
        int j;
        for (j = 0; j < M; j++) {
            if (text[i + j] != pat[j]) break;
        }
        if (j == M) matches++;
    }
    return matches;
}

int main() {
    char *text = (char *)malloc(TEXT_LEN + 1);
    for (int i = 0; i < TEXT_LEN; i++) text[i] = 'a' + (i % 5);
    text[TEXT_LEN] = '\0';
    char pat[] = "abcda";

    int total_matches = 0;
    for (int iter = 0; iter < 5; iter++) {
        total_matches += naive_search(text, pat);
    }
    printf("Pattern match complete: matches=%d\n", total_matches);
    free(text);
    return 0;
}
"""

programs["string_compression.c"] = r"""#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LEN 200000

int run_length_encode(const char *src, char *dst) {
    int src_len = strlen(src);
    int j = 0;
    for (int i = 0; i < src_len; i++) {
        int count = 1;
        while (i + 1 < src_len && src[i] == src[i + 1]) {
            count++;
            i++;
        }
        dst[j++] = src[i];
        j += sprintf(&dst[j], "%d", count);
    }
    dst[j] = '\0';
    return j;
}

int main() {
    char *src = (char *)malloc(LEN + 1);
    char *dst = (char *)malloc(LEN * 2);
    for (int i = 0; i < LEN; i++) {
        src[i] = 'a' + ((i / 10) % 4);
    }
    src[LEN] = '\0';

    int compressed_len = 0;
    for (int iter = 0; iter < 3; iter++) {
        compressed_len = run_length_encode(src, dst);
    }
    printf("String compression complete: len=%d\n", compressed_len);
    free(src);
    free(dst);
    return 0;
}
"""

programs["graph_dfs.c"] = r"""#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define V 250

void dfs_rec(int adj[V][V], bool visited[V], int u) {
    visited[u] = true;
    for (int v = 0; v < V; v++) {
        if (adj[u][v] && !visited[v]) {
            dfs_rec(adj, visited, v);
        }
    }
}

int main() {
    static int adj[V][V];
    for (int i = 0; i < V; i++) {
        for (int j = 0; j < V; j++) {
            adj[i][j] = ((i * j + 3) % 7 == 0) ? 1 : 0;
        }
    }
    bool visited[V];
    for (int run = 0; run < 10; run++) {
        for (int k = 0; k < V; k++) visited[k] = false;
        dfs_rec(adj, visited, run % V);
    }
    printf("Graph DFS complete.\n");
    return 0;
}
"""

programs["graph_dijkstra.c"] = r"""#include <stdio.h>
#include <stdbool.h>
#include <limits.h>

#define V 250

int min_distance(int dist[], bool spt_set[]) {
    int min = INT_MAX, min_index = -1;
    for (int v = 0; v < V; v++) {
        if (!spt_set[v] && dist[v] <= min) {
            min = dist[v];
            min_index = v;
        }
    }
    return min_index;
}

void dijkstra(int graph[V][V], int src) {
    int dist[V];
    bool spt_set[V];
    for (int i = 0; i < V; i++) {
        dist[i] = INT_MAX;
        spt_set[i] = false;
    }
    dist[src] = 0;

    for (int count = 0; count < V - 1; count++) {
        int u = min_distance(dist, spt_set);
        if (u == -1) break;
        spt_set[u] = true;
        for (int v = 0; v < V; v++) {
            if (!spt_set[v] && graph[u][v] && dist[u] != INT_MAX
                && dist[u] + graph[u][v] < dist[v]) {
                dist[v] = dist[u] + graph[u][v];
            }
        }
    }
}

int main() {
    static int graph[V][V];
    for (int i = 0; i < V; i++) {
        for (int j = 0; j < V; j++) {
            graph[i][j] = (i == j) ? 0 : ((i + j) % 11 + 1);
        }
    }
    for (int iter = 0; iter < 3; iter++) {
        dijkstra(graph, iter % V);
    }
    printf("Dijkstra complete.\n");
    return 0;
}
"""

programs["lcs_dp.c"] = r"""#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX(a, b) (((a) > (b)) ? (a) : (b))
#define LEN 600

int lcs(char *X, char *Y, int m, int n) {
    int **L = (int **)malloc((m + 1) * sizeof(int *));
    for (int i = 0; i <= m; i++) L[i] = (int *)malloc((n + 1) * sizeof(int));

    for (int i = 0; i <= m; i++) {
        for (int j = 0; j <= n; j++) {
            if (i == 0 || j == 0)
                L[i][j] = 0;
            else if (X[i - 1] == Y[j - 1])
                L[i][j] = L[i - 1][j - 1] + 1;
            else
                L[i][j] = MAX(L[i - 1][j], L[i][j - 1]);
        }
    }
    int result = L[m][n];
    for (int i = 0; i <= m; i++) free(L[i]);
    free(L);
    return result;
}

int main() {
    char *X = (char *)malloc(LEN + 1);
    char *Y = (char *)malloc(LEN + 1);
    for (int i = 0; i < LEN; i++) {
        X[i] = 'A' + (i % 4);
        Y[i] = 'A' + ((i * 3) % 4);
    }
    X[LEN] = Y[LEN] = '\0';

    int len_lcs = 0;
    for (int iter = 0; iter < 2; iter++) {
        len_lcs += lcs(X, Y, LEN, LEN);
    }
    printf("LCS DP complete: len=%d\n", len_lcs);
    free(X); free(Y);
    return 0;
}
"""

programs["coin_change_dp.c"] = r"""#include <stdio.h>
#include <stdlib.h>

#define COINS 10
#define AMOUNT 15000

int min_coins(int coins[], int n, int amount) {
    int *dp = (int *)malloc((amount + 1) * sizeof(int));
    dp[0] = 0;
    for (int i = 1; i <= amount; i++) dp[i] = 1000000;

    for (int i = 1; i <= amount; i++) {
        for (int j = 0; j < n; j++) {
            if (coins[j] <= i) {
                int sub_res = dp[i - coins[j]];
                if (sub_res != 1000000 && sub_res + 1 < dp[i]) {
                    dp[i] = sub_res + 1;
                }
            }
        }
    }
    int ans = dp[amount];
    free(dp);
    return ans;
}

int main() {
    int coins[] = {1, 2, 5, 10, 20, 50, 100, 200, 500, 1000};
    int res = min_coins(coins, COINS, AMOUNT);
    printf("Coin change complete: min_coins=%d\n", res);
    return 0;
}
"""

programs["linked_list_ops.c"] = r"""#include <stdio.h>
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
"""

programs["binary_search_tree.c"] = r"""#include <stdio.h>
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
"""

programs["hash_table_sim.c"] = r"""#include <stdio.h>
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
"""

programs["bitwise_ops.c"] = r"""#include <stdio.h>

unsigned int crc32_chunk(const unsigned char *buf, size_t len) {
    unsigned int crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= buf[i];
        for (int j = 0; j < 8; j++) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
        }
    }
    return ~crc;
}

int main() {
    unsigned char buffer[1024];
    for (int i = 0; i < 1024; i++) buffer[i] = (unsigned char)(i & 0xFF);

    unsigned int checksum = 0;
    for (int iter = 0; iter < 2500; iter++) {
        checksum += crc32_chunk(buffer, 1024);
    }
    printf("Bitwise complete: checksum=0x%X\n", checksum);
    return 0;
}
"""

programs["vector_dot_product.c"] = r"""#include <stdio.h>
#include <stdlib.h>

#define VEC_SIZE 1500000

double dot_product(const float* a, const float* b, int n) {
    double sum = 0.0;
    for (int i = 0; i < n; i++) {
        sum += (double)a[i] * b[i];
    }
    return sum;
}

int main() {
    float *a = (float *)malloc(VEC_SIZE * sizeof(float));
    float *b = (float *)malloc(VEC_SIZE * sizeof(float));
    for (int i = 0; i < VEC_SIZE; i++) {
        a[i] = i * 0.001f;
        b[i] = i * 0.002f;
    }
    double result = 0.0;
    for (int iter = 0; iter < 5; iter++) {
        result += dot_product(a, b, VEC_SIZE);
    }
    printf("Vector dot product complete: result=%.4f\n", result);
    free(a); free(b);
    return 0;
}
"""

programs["convolution_2d.c"] = r"""#include <stdio.h>
#include <stdlib.h>

#define W 200
#define H 200
#define K 5

void convolve(float input[H][W], float output[H][W], float kernel[K][K]) {
    int k_offset = K / 2;
    for (int y = k_offset; y < H - k_offset; y++) {
        for (int x = k_offset; x < W - k_offset; x++) {
            float sum = 0.0f;
            for (int ky = 0; ky < K; ky++) {
                for (int kx = 0; kx < K; kx++) {
                    int py = y + ky - k_offset;
                    int px = x + kx - k_offset;
                    sum += input[py][px] * kernel[ky][kx];
                }
            }
            output[y][x] = sum;
        }
    }
}

int main() {
    static float in[H][W], out[H][W];
    float kernel[K][K] = {
        {0.04, 0.04, 0.04, 0.04, 0.04},
        {0.04, 0.04, 0.04, 0.04, 0.04},
        {0.04, 0.04, 0.04, 0.04, 0.04},
        {0.04, 0.04, 0.04, 0.04, 0.04},
        {0.04, 0.04, 0.04, 0.04, 0.04}
    };
    for (int y = 0; y < H; y++)
        for (int x = 0; x < W; x++)
            in[y][x] = (float)(x + y);

    for (int iter = 0; iter < 5; iter++) {
        convolve(in, out, kernel);
    }
    printf("2D Convolution complete: out[50][50]=%.2f\n", out[50][50]);
    return 0;
}
"""

programs["n_queens_backtrack.c"] = r"""#include <stdio.h>
#include <stdbool.h>

#define N 11

int solutions = 0;

bool is_safe(int board[N][N], int row, int col) {
    int i, j;
    for (i = 0; i < col; i++)
        if (board[row][i]) return false;
    for (i = row, j = col; i >= 0 && j >= 0; i--, j--)
        if (board[i][j]) return false;
    for (i = row, j = col; j >= 0 && i < N; i++, j--)
        if (board[i][j]) return false;
    return true;
}

void solve_nq_util(int board[N][N], int col) {
    if (col >= N) {
        solutions++;
        return;
    }
    for (int i = 0; i < N; i++) {
        if (is_safe(board, i, col)) {
            board[i][col] = 1;
            solve_nq_util(board, col + 1);
            board[i][col] = 0;
        }
    }
}

int main() {
    int board[N][N] = {0};
    solve_nq_util(board, 0);
    printf("N-Queens complete: solutions=%d\n", solutions);
    return 0;
}
"""

programs["runge_kutta.c"] = r"""#include <stdio.h>

double dydx(double x, double y) {
    return (x - y) / 2.0;
}

double runge_kutta(double x0, double y0, double x, double h) {
    int n = (int)((x - x0) / h);
    double k1, k2, k3, k4;
    double y = y0;
    for (int i = 1; i <= n; i++) {
        k1 = h * dydx(x0, y);
        k2 = h * dydx(x0 + 0.5 * h, y + 0.5 * k1);
        k3 = h * dydx(x0 + 0.5 * h, y + 0.5 * k2);
        k4 = h * dydx(x0 + h, y + k3);

        y = y + (1.0 / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4);
        x0 = x0 + h;
    }
    return y;
}

int main() {
    double res = 0.0;
    for (int iter = 0; iter < 50; iter++) {
        res += runge_kutta(0, 1, 50.0, 0.0002);
    }
    printf("Runge-Kutta complete: res=%.4f\n", res);
    return 0;
}
"""

programs["monte_carlo_pi.c"] = r"""#include <stdio.h>

unsigned int lcg_rand(unsigned int *state) {
    *state = (*state * 1103515245 + 12345) & 0x7fffffff;
    return *state;
}

int main() {
    unsigned int state = 12345;
    long points_inside = 0;
    long total_points = 4000000;

    for (long i = 0; i < total_points; i++) {
        double x = (double)lcg_rand(&state) / 2147483647.0;
        double y = (double)lcg_rand(&state) / 2147483647.0;
        if (x * x + y * y <= 1.0) {
            points_inside++;
        }
    }
    double pi = 4.0 * points_inside / total_points;
    printf("Monte Carlo Pi complete: pi=%.5f\n", pi);
    return 0;
}
"""

programs["fast_fourier_sim.c"] = r"""#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846
#define N_FFT 1024

void fft_butterfly(double *real, double *imag, int n) {
    int i, j;
    for (i = 0; i < n; i++) {
        for (j = 0; j < n; j += 2) {
            double r_temp = real[j] * cos(PI/n) - imag[j] * sin(PI/n);
            double i_temp = real[j] * sin(PI/n) + imag[j] * cos(PI/n);
            real[j] += r_temp;
            imag[j] += i_temp;
        }
    }
}

int main() {
    double *real = (double *)malloc(N_FFT * sizeof(double));
    double *imag = (double *)malloc(N_FFT * sizeof(double));
    for (int i = 0; i < N_FFT; i++) {
        real[i] = sin(2 * PI * i / 100.0);
        imag[i] = 0.0;
    }
    for (int iter = 0; iter < 5; iter++) {
        fft_butterfly(real, imag, N_FFT);
    }
    printf("FFT Sim complete: real[0]=%.4f\n", real[0]);
    free(real); free(imag);
    return 0;
}
"""

programs["gemm_blocked.c"] = r"""#include <stdio.h>
#include <stdlib.h>

#define N 128
#define BLOCK_SIZE 32

void gemm_blocked(double *A, double *B, double *C, int n) {
    int ii, jj, kk, i, j, k;
    for (ii = 0; ii < n; ii += BLOCK_SIZE) {
        for (jj = 0; jj < n; jj += BLOCK_SIZE) {
            for (kk = 0; kk < n; kk += BLOCK_SIZE) {
                for (i = ii; i < ii + BLOCK_SIZE && i < n; i++) {
                    for (k = kk; k < kk + BLOCK_SIZE && k < n; k++) {
                        double a_ik = A[i * n + k];
                        for (j = jj; j < jj + BLOCK_SIZE && j < n; j++) {
                            C[i * n + j] += a_ik * B[k * n + j];
                        }
                    }
                }
            }
        }
    }
}

int main() {
    double *A = (double *)malloc(N * N * sizeof(double));
    double *B = (double *)malloc(N * N * sizeof(double));
    double *C = (double *)calloc(N * N, sizeof(double));
    int i;
    for (i = 0; i < N * N; i++) {
        A[i] = (double)(i % 100) * 0.05;
        B[i] = (double)((i * 7) % 100) * 0.03;
    }
    gemm_blocked(A, B, C, N);
    double checksum = 0.0;
    for (i = 0; i < N * N; i += 17) {
        checksum += C[i];
    }
    printf("GEMM Blocked complete: checksum=%.4f\n", checksum);
    free(A); free(B); free(C);
    return 0;
}
"""

programs["sobel_filter.c"] = r"""#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define W 128
#define H 128

void sobel_filter(const unsigned char *in, unsigned char *out, int w, int h) {
    int x, y;
    int gx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
    int gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};
    for (y = 1; y < h - 1; y++) {
        for (x = 1; x < w - 1; x++) {
            int sum_x = 0;
            int sum_y = 0;
            int ky, kx;
            for (ky = -1; ky <= 1; ky++) {
                for (kx = -1; kx <= 1; kx++) {
                    int val = in[(y + ky) * w + (x + kx)];
                    sum_x += val * gx[ky + 1][kx + 1];
                    sum_y += val * gy[ky + 1][kx + 1];
                }
            }
            int mag = (int)sqrt((double)(sum_x * sum_x + sum_y * sum_y));
            out[y * w + x] = (unsigned char)(mag > 255 ? 255 : mag);
        }
    }
}

int main() {
    unsigned char *in = (unsigned char *)malloc(W * H);
    unsigned char *out = (unsigned char *)malloc(W * H);
    int i, iter;
    for (i = 0; i < W * H; i++) {
        in[i] = (unsigned char)((i * 13 + 7) & 0xFF);
    }
    for (iter = 0; iter < 4; iter++) {
        sobel_filter(in, out, W, H);
    }
    long sum = 0;
    for (i = 0; i < W * H; i += 19) {
        sum += out[i];
    }
    printf("Sobel filter complete: sum=%ld\n", sum);
    free(in); free(out);
    return 0;
}
"""

programs["radix_sort.c"] = r"""#include <stdio.h>
#include <stdlib.h>

#define SIZE 20000

void radix_sort(unsigned int *arr, int n) {
    unsigned int *output = (unsigned int *)malloc(n * sizeof(unsigned int));
    int shift;
    for (shift = 0; shift < 32; shift += 8) {
        int count[256] = {0};
        int i;
        for (i = 0; i < n; i++) {
            count[(arr[i] >> shift) & 0xFF]++;
        }
        for (i = 1; i < 256; i++) {
            count[i] += count[i - 1];
        }
        for (i = n - 1; i >= 0; i--) {
            unsigned char byte = (arr[i] >> shift) & 0xFF;
            output[--count[byte]] = arr[i];
        }
        for (i = 0; i < n; i++) {
            arr[i] = output[i];
        }
    }
    free(output);
}

int main() {
    unsigned int *arr = (unsigned int *)malloc(SIZE * sizeof(unsigned int));
    int i, iter;
    unsigned int checksum = 0;
    for (iter = 0; iter < 2; iter++) {
        unsigned int seed = 1234567 + iter * 99;
        for (i = 0; i < SIZE; i++) {
            seed = seed * 1664525u + 1013904223u;
            arr[i] = seed;
        }
        radix_sort(arr, SIZE);
        checksum += arr[0] + arr[SIZE / 2] + arr[SIZE - 1];
    }
    printf("Radix sort complete: checksum=%u\n", checksum);
    free(arr);
    return 0;
}
"""

programs["avl_tree_ops.c"] = r"""#include <stdio.h>
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
"""

programs["sparse_matrix_csr.c"] = r"""#include <stdio.h>
#include <stdlib.h>

#define ROWS 1500
#define NNZ_PER_ROW 15

void spmv_csr(int num_rows, const int *row_ptr, const int *col_idx, const double *values, const double *x, double *y) {
    int i, j;
    for (i = 0; i < num_rows; i++) {
        double sum = 0.0;
        for (j = row_ptr[i]; j < row_ptr[i + 1]; j++) {
            sum += values[j] * x[col_idx[j]];
        }
        y[i] = sum;
    }
}

int main() {
    int total_nnz = ROWS * NNZ_PER_ROW;
    int *row_ptr = (int *)malloc((ROWS + 1) * sizeof(int));
    int *col_idx = (int *)malloc(total_nnz * sizeof(int));
    double *values = (double *)malloc(total_nnz * sizeof(double));
    double *x = (double *)malloc(ROWS * sizeof(double));
    double *y = (double *)malloc(ROWS * sizeof(double));

    int i, j, pos = 0;
    row_ptr[0] = 0;
    for (i = 0; i < ROWS; i++) {
        for (j = 0; j < NNZ_PER_ROW; j++) {
            col_idx[pos] = (i + j * 97) % ROWS;
            values[pos] = ((i + j) % 10 + 1) * 0.25;
            pos++;
        }
        row_ptr[i + 1] = pos;
        x[i] = (i % 50) * 0.1;
    }

    for (int iter = 0; iter < 20; iter++) {
        spmv_csr(ROWS, row_ptr, col_idx, values, x, y);
        x[iter % ROWS] += y[iter % ROWS] * 0.001;
    }

    double checksum = 0.0;
    for (i = 0; i < ROWS; i += 23) {
        checksum += y[i];
    }
    printf("CSR SpMV complete: checksum=%.4f\n", checksum);
    free(row_ptr); free(col_idx); free(values); free(x); free(y);
    return 0;
}
"""

programs["astar_pathfind.c"] = r"""#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define GRID_SZ 64
#define HEAP_CAP (GRID_SZ * GRID_SZ)

typedef struct {
    int x, y;
    int g, f;
} Node;

typedef struct {
    Node data[HEAP_CAP];
    int size;
} MinHeap;

void push_heap(MinHeap *h, Node n) {
    int i = h->size++;
    while (i > 0) {
        int p = (i - 1) / 2;
        if (h->data[p].f <= n.f) break;
        h->data[i] = h->data[p];
        i = p;
    }
    h->data[i] = n;
}

Node pop_heap(MinHeap *h) {
    Node ret = h->data[0];
    Node last = h->data[--h->size];
    int i = 0;
    while (i * 2 + 1 < h->size) {
        int left = i * 2 + 1, right = left + 1, smallest = left;
        if (right < h->size && h->data[right].f < h->data[left].f) smallest = right;
        if (h->data[smallest].f >= last.f) break;
        h->data[i] = h->data[smallest];
        i = smallest;
    }
    h->data[i] = last;
    return ret;
}

int astar(int grid[GRID_SZ][GRID_SZ], int sx, int sy, int gx, int gy) {
    static int g_score[GRID_SZ][GRID_SZ];
    static int visited[GRID_SZ][GRID_SZ];
    int x, y;
    for (y = 0; y < GRID_SZ; y++) {
        for (x = 0; x < GRID_SZ; x++) {
            g_score[y][x] = 999999;
            visited[y][x] = 0;
        }
    }
    MinHeap heap;
    heap.size = 0;
    g_score[sy][sx] = 0;
    Node start = {sx, sy, 0, abs(gx - sx) + abs(gy - sy)};
    push_heap(&heap, start);

    int dx[4] = {0, 0, 1, -1};
    int dy[4] = {1, -1, 0, 0};

    while (heap.size > 0) {
        Node curr = pop_heap(&heap);
        if (curr.x == gx && curr.y == gy) return curr.g;
        if (visited[curr.y][curr.x]) continue;
        visited[curr.y][curr.x] = 1;

        for (int d = 0; d < 4; d++) {
            int nx = curr.x + dx[d], ny = curr.y + dy[d];
            if (nx >= 0 && nx < GRID_SZ && ny >= 0 && ny < GRID_SZ && grid[ny][nx] == 0) {
                int tentative_g = curr.g + 1;
                if (tentative_g < g_score[ny][nx]) {
                    g_score[ny][nx] = tentative_g;
                    Node next = {nx, ny, tentative_g, tentative_g + abs(gx - nx) + abs(gy - ny)};
                    push_heap(&heap, next);
                }
            }
        }
    }
    return -1;
}

int main() {
    static int grid[GRID_SZ][GRID_SZ];
    int x, y, iter, total_dist = 0;
    for (y = 0; y < GRID_SZ; y++) {
        for (x = 0; x < GRID_SZ; x++) {
            grid[y][x] = ((x * 11 + y * 17) % 7 == 0) ? 1 : 0;
        }
    }
    grid[0][0] = 0;
    grid[GRID_SZ - 1][GRID_SZ - 1] = 0;

    for (iter = 0; iter < 12; iter++) {
        int target_x = (GRID_SZ - 1 - (iter % 8));
        int target_y = (GRID_SZ - 1 - ((iter * 3) % 8));
        grid[target_y][target_x] = 0;
        int d = astar(grid, 0, 0, target_x, target_y);
        total_dist += (d > 0 ? d : 0);
    }
    printf("A* Pathfind complete: total_dist=%d\n", total_dist);
    return 0;
}
"""

programs["crc64_calc.c"] = r"""#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define POLY64 0x42F0E1EBA9EA3693ULL
#define BUF_SZ (64 * 1024)

static uint64_t crc_table[256];

void init_crc64_table() {
    for (int i = 0; i < 256; i++) {
        uint64_t crc = (uint64_t)i << 56;
        for (int j = 0; j < 8; j++) {
            if (crc & 0x8000000000000000ULL) {
                crc = (crc << 1) ^ POLY64;
            } else {
                crc <<= 1;
            }
        }
        crc_table[i] = crc;
    }
}

uint64_t compute_crc64(const uint8_t *data, size_t len) {
    uint64_t crc = 0xFFFFFFFFFFFFFFFFULL;
    for (size_t i = 0; i < len; i++) {
        uint8_t table_idx = (uint8_t)((crc >> 56) ^ data[i]);
        crc = (crc << 8) ^ crc_table[table_idx];
    }
    return crc ^ 0xFFFFFFFFFFFFFFFFULL;
}

int main() {
    init_crc64_table();
    uint8_t *buf = (uint8_t *)malloc(BUF_SZ);
    for (size_t i = 0; i < BUF_SZ; i++) {
        buf[i] = (uint8_t)((i * 31 + 17) & 0xFF);
    }

    uint64_t final_crc = 0;
    for (int iter = 0; iter < 15; iter++) {
        buf[iter % 1024] ^= (uint8_t)iter;
        final_crc ^= compute_crc64(buf, BUF_SZ);
    }
    printf("CRC64 complete: crc=0x%016llX\n", (unsigned long long)final_crc);
    free(buf);
    return 0;
}
"""

programs["sudoku_solver.c"] = r"""#include <stdio.h>
#include <stdlib.h>

#define N 9

int is_valid(int board[N][N], int row, int col, int num) {
    for (int i = 0; i < N; i++) {
        if (board[row][i] == num || board[i][col] == num) return 0;
    }
    int start_r = (row / 3) * 3, start_c = (col / 3) * 3;
    for (int r = 0; r < 3; r++) {
        for (int c = 0; c < 3; c++) {
            if (board[start_r + r][start_c + c] == num) return 0;
        }
    }
    return 1;
}

int solve_sudoku(int board[N][N], int row, int col) {
    if (row == N - 1 && col == N) return 1;
    if (col == N) { row++; col = 0; }
    if (board[row][col] > 0) return solve_sudoku(board, row, col + 1);

    for (int num = 1; num <= 9; num++) {
        if (is_valid(board, row, col, num)) {
            board[row][col] = num;
            if (solve_sudoku(board, row, col + 1)) return 1;
            board[row][col] = 0;
        }
    }
    return 0;
}

int main() {
    int puzzle[N][N] = {
        {5, 3, 0, 0, 7, 0, 0, 0, 0},
        {6, 0, 0, 1, 9, 5, 0, 0, 0},
        {0, 9, 8, 0, 0, 0, 0, 6, 0},
        {8, 0, 0, 0, 6, 0, 0, 0, 3},
        {4, 0, 0, 8, 0, 3, 0, 0, 1},
        {7, 0, 0, 0, 2, 0, 0, 0, 6},
        {0, 6, 0, 0, 0, 0, 2, 8, 0},
        {0, 0, 0, 4, 1, 9, 0, 0, 5},
        {0, 0, 0, 0, 8, 0, 0, 7, 9}
    };
    int work[N][N];
    int solved_count = 0, checksum = 0;
    for (int iter = 0; iter < 15; iter++) {
        for (int r = 0; r < N; r++) {
            for (int c = 0; c < N; c++) {
                work[r][c] = puzzle[r][c];
            }
        }
        if (solve_sudoku(work, 0, 0)) {
            solved_count++;
            checksum += work[0][0] + work[4][4] + work[8][8];
        }
    }
    printf("Sudoku solver complete: solved=%d, checksum=%d\n", solved_count, checksum);
    return 0;
}
"""

programs["gaussian_blur.c"] = r"""#include <stdio.h>
#include <stdlib.h>

#define W 128
#define H 128

void gaussian_blur_separable(const float *in, float *out, float *temp, int w, int h) {
    float k[5] = {0.06136f, 0.24477f, 0.38774f, 0.24477f, 0.06136f};
    int x, y, i;
    for (y = 0; y < h; y++) {
        for (x = 0; x < w; x++) {
            float sum = 0.0f;
            for (i = -2; i <= 2; i++) {
                int cx = x + i;
                if (cx < 0) cx = 0;
                if (cx >= w) cx = w - 1;
                sum += in[y * w + cx] * k[i + 2];
            }
            temp[y * w + x] = sum;
        }
    }
    for (y = 0; y < h; y++) {
        for (x = 0; x < w; x++) {
            float sum = 0.0f;
            for (i = -2; i <= 2; i++) {
                int cy = y + i;
                if (cy < 0) cy = 0;
                if (cy >= h) cy = h - 1;
                sum += temp[cy * w + x] * k[i + 2];
            }
            out[y * w + x] = sum;
        }
    }
}

int main() {
    float *in = (float *)malloc(W * H * sizeof(float));
    float *out = (float *)malloc(W * H * sizeof(float));
    float *temp = (float *)malloc(W * H * sizeof(float));

    for (int i = 0; i < W * H; i++) {
        in[i] = (float)((i * 17) % 255);
    }
    for (int iter = 0; iter < 4; iter++) {
        gaussian_blur_separable(in, out, temp, W, H);
        in[iter % (W * H)] += 0.5f;
    }

    double checksum = 0.0;
    for (int i = 0; i < W * H; i += 29) {
        checksum += out[i];
    }
    printf("Gaussian blur complete: checksum=%.4f\n", checksum);
    free(in); free(out); free(temp);
    return 0;
}
"""

programs["lru_cache_sim.c"] = r"""#include <stdio.h>
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
"""

for fname, code in programs.items():
    path = os.path.join("programs", fname)
    with open(path, "w") as f:
        f.write(code)

print(f"Successfully generated {len(programs)} optimized benchmark C programs.")
