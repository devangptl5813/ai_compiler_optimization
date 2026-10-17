#include <stdio.h>
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
