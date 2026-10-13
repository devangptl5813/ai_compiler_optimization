#include <stdio.h>
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
