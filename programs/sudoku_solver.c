#include <stdio.h>
#include <stdlib.h>

#define N 9

int is_valid(int board[N][N], int row, int col, int num) {
    for (int i = 0; i < N; i++) {
        if (board[row][i] == num || board[i][col] == num) return 0;
    }
    int start_r = (row / 3) * 3, start_c = (col / 3) * 3;
    for (int r = 0; r < 3; r++) {
        for (int c = 0; c < 3; c++) {
            if (board[start_r + r][start_c + c] == num) return 0;
        }
    }
    return 1;
}

int solve_sudoku(int board[N][N], int row, int col) {
    if (row == N - 1 && col == N) return 1;
    if (col == N) { row++; col = 0; }
    if (board[row][col] > 0) return solve_sudoku(board, row, col + 1);

    for (int num = 1; num <= 9; num++) {
        if (is_valid(board, row, col, num)) {
            board[row][col] = num;
            if (solve_sudoku(board, row, col + 1)) return 1;
            board[row][col] = 0;
        }
    }
    return 0;
}

int main() {
    int puzzle[N][N] = {
        {5, 3, 0, 0, 7, 0, 0, 0, 0},
        {6, 0, 0, 1, 9, 5, 0, 0, 0},
        {0, 9, 8, 0, 0, 0, 0, 6, 0},
        {8, 0, 0, 0, 6, 0, 0, 0, 3},
        {4, 0, 0, 8, 0, 3, 0, 0, 1},
        {7, 0, 0, 0, 2, 0, 0, 0, 6},
        {0, 6, 0, 0, 0, 0, 2, 8, 0},
        {0, 0, 0, 4, 1, 9, 0, 0, 5},
        {0, 0, 0, 0, 8, 0, 0, 7, 9}
    };
    int work[N][N];
    int solved_count = 0, checksum = 0;
    for (int iter = 0; iter < 15; iter++) {
        for (int r = 0; r < N; r++) {
            for (int c = 0; c < N; c++) {
                work[r][c] = puzzle[r][c];
            }
        }
        if (solve_sudoku(work, 0, 0)) {
            solved_count++;
            checksum += work[0][0] + work[4][4] + work[8][8];
        }
    }
    printf("Sudoku solver complete: solved=%d, checksum=%d\n", solved_count, checksum);
    return 0;
}
