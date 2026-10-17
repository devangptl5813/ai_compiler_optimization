#include <stdio.h>
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
