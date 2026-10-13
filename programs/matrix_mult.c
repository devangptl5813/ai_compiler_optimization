#include <stdio.h>
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
