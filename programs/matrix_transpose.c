#include <stdio.h>
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
