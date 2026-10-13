#include <stdio.h>

long long fibonacci_recursive(int n) {
    if (n <= 1) return n;
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2);
}

int main() {
    long long sum = 0;
    for (int i = 0; i < 5; i++) {
        sum += fibonacci_recursive(30);
    }
    printf("Fibonacci complete: sum=%lld\n", sum);
    return 0;
}
