#include <stdio.h>
#include <stdlib.h>

#define N 150

void compute_grid(double grid[N][N]) {
    for (int i = 1; i < N - 1; i++) {
        for (int j = 1; j < N - 1; j++) {
            grid[i][j] = (grid[i-1][j] + grid[i+1][j] + grid[i][j-1] + grid[i][j+1]) * 0.25;
        }
    }
}

int main() {
    static double grid[N][N];
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            grid[i][j] = (i == 0 || j == 0 || i == N-1 || j == N-1) ? 100.0 : 0.0;
        }
    }
    for (int iter = 0; iter < 100; iter++) {
        compute_grid(grid);
    }
    printf("Grid compute complete: center=%.2f\n", grid[N/2][N/2]);
    return 0;
}
