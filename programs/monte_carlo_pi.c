#include <stdio.h>

unsigned int lcg_rand(unsigned int *state) {
    *state = (*state * 1103515245 + 12345) & 0x7fffffff;
    return *state;
}

int main() {
    unsigned int state = 12345;
    long points_inside = 0;
    long total_points = 4000000;

    for (long i = 0; i < total_points; i++) {
        double x = (double)lcg_rand(&state) / 2147483647.0;
        double y = (double)lcg_rand(&state) / 2147483647.0;
        if (x * x + y * y <= 1.0) {
            points_inside++;
        }
    }
    double pi = 4.0 * points_inside / total_points;
    printf("Monte Carlo Pi complete: pi=%.5f\n", pi);
    return 0;
}
