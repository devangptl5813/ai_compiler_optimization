#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LEN 200000

int run_length_encode(const char *src, char *dst) {
    int src_len = strlen(src);
    int j = 0;
    for (int i = 0; i < src_len; i++) {
        int count = 1;
        while (i + 1 < src_len && src[i] == src[i + 1]) {
            count++;
            i++;
        }
        dst[j++] = src[i];
        j += sprintf(&dst[j], "%d", count);
    }
    dst[j] = '\0';
    return j;
}

int main() {
    char *src = (char *)malloc(LEN + 1);
    char *dst = (char *)malloc(LEN * 2);
    for (int i = 0; i < LEN; i++) {
        src[i] = 'a' + ((i / 10) % 4);
    }
    src[LEN] = '\0';

    int compressed_len = 0;
    for (int iter = 0; iter < 3; iter++) {
        compressed_len = run_length_encode(src, dst);
    }
    printf("String compression complete: len=%d\n", compressed_len);
    free(src);
    free(dst);
    return 0;
}
