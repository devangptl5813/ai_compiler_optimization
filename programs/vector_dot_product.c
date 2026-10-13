#include <stdio.h>
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
