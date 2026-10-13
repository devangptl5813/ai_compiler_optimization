#include <stdio.h>
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
