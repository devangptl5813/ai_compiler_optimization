#include <stdio.h>
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
