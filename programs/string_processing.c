#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define STR_LEN 30000

int is_palindrome(const char *str, int len) {
    int left = 0, right = len - 1;
    while (left < right) {
        if (str[left] != str[right]) return 0;
        left++;
        right--;
    }
    return 1;
}

void reverse_string(char *str, int len) {
    int left = 0, right = len - 1;
    while (left < right) {
        char temp = str[left];
        str[left] = str[right];
        str[right] = temp;
        left++;
        right--;
    }
}

int main() {
    char *buf = (char *)malloc(STR_LEN + 1);
    for (int i = 0; i < STR_LEN; i++) {
        buf[i] = 'a' + (i % 26);
    }
    buf[STR_LEN] = '\0';

    int pal_count = 0;
    for (int iter = 0; iter < 50; iter++) {
        reverse_string(buf, STR_LEN);
        if (is_palindrome(buf, STR_LEN)) {
            pal_count++;
        }
    }
    printf("String processing complete: pal_count=%d\n", pal_count);
    free(buf);
    return 0;
}
