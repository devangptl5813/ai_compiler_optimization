#include <stdio.h>
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
