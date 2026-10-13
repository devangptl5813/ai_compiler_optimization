#include <stdio.h>

long long hanoi_count = 0;

void solve_hanoi(int n, char from, char to, char aux) {
    if (n == 1) {
        hanoi_count++;
        return;
    }
    solve_hanoi(n - 1, from, aux, to);
    hanoi_count++;
    solve_hanoi(n - 1, aux, to, from);
}

int main() {
    solve_hanoi(21, 'A', 'C', 'B');
    printf("Hanoi complete: moves=%lld\n", hanoi_count);
    return 0;
}
