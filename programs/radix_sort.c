#include <stdio.h>
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
