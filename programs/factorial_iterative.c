#include <stdio.h>

double compute_series(int n) {
    double res = 1.0;
    for (int i = 1; i <= n; i++) {
        res += (double)i / (i + 1) * 0.99999;
    }
    return res;
}

int main() {
    double total = 0.0;
    for (int iter = 0; iter < 3000; iter++) {
        total += compute_series(1000);
    }
    printf("Factorial/Series complete: total=%.4f\n", total);
    return 0;
}
