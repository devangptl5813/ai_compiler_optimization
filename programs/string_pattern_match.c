#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TEXT_LEN 50000
#define PAT_LEN 10

int naive_search(const char *text, const char *pat) {
    int M = strlen(pat);
    int N = strlen(text);
    int matches = 0;

    for (int i = 0; i <= N - M; i++) {
        int j;
        for (j = 0; j < M; j++) {
            if (text[i + j] != pat[j]) break;
        }
        if (j == M) matches++;
    }
    return matches;
}

int main() {
    char *text = (char *)malloc(TEXT_LEN + 1);
    for (int i = 0; i < TEXT_LEN; i++) text[i] = 'a' + (i % 5);
    text[TEXT_LEN] = '\0';
    char pat[] = "abcda";

    int total_matches = 0;
    for (int iter = 0; iter < 5; iter++) {
        total_matches += naive_search(text, pat);
    }
    printf("Pattern match complete: matches=%d\n", total_matches);
    free(text);
    return 0;
}
