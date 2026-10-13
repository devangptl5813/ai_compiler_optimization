#include <stdio.h>
#include <math.h>

int main() {
    double sum = 0.0;
    for (long i = 1; i <= 1500000; i++) {
        sum += sin((double)i) * cos((double)i) + exp(1.0 / i);
    }
    printf("Sum series complete: sum=%.4f\n", sum);
    return 0;
}
