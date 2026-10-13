#include <stdio.h>
#include <stdbool.h>

#define N 11

int solutions = 0;

bool is_safe(int board[N][N], int row, int col) {
    int i, j;
    for (i = 0; i < col; i++)
        if (board[row][i]) return false;
    for (i = row, j = col; i >= 0 && j >= 0; i--, j--)
        if (board[i][j]) return false;
    for (i = row, j = col; j >= 0 && i < N; i++, j--)
        if (board[i][j]) return false;
    return true;
}

void solve_nq_util(int board[N][N], int col) {
    if (col >= N) {
        solutions++;
        return;
    }
    for (int i = 0; i < N; i++) {
        if (is_safe(board, i, col)) {
            board[i][col] = 1;
            solve_nq_util(board, col + 1);
            board[i][col] = 0;
        }
    }
}

int main() {
    int board[N][N] = {0};
    solve_nq_util(board, 0);
    printf("N-Queens complete: solutions=%d\n", solutions);
    return 0;
}
