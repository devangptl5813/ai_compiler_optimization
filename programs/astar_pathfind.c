#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define GRID_SZ 64
#define HEAP_CAP (GRID_SZ * GRID_SZ)

typedef struct {
    int x, y;
    int g, f;
} Node;

typedef struct {
    Node data[HEAP_CAP];
    int size;
} MinHeap;

void push_heap(MinHeap *h, Node n) {
    int i = h->size++;
    while (i > 0) {
        int p = (i - 1) / 2;
        if (h->data[p].f <= n.f) break;
        h->data[i] = h->data[p];
        i = p;
    }
    h->data[i] = n;
}

Node pop_heap(MinHeap *h) {
    Node ret = h->data[0];
    Node last = h->data[--h->size];
    int i = 0;
    while (i * 2 + 1 < h->size) {
        int left = i * 2 + 1, right = left + 1, smallest = left;
        if (right < h->size && h->data[right].f < h->data[left].f) smallest = right;
        if (h->data[smallest].f >= last.f) break;
        h->data[i] = h->data[smallest];
        i = smallest;
    }
    h->data[i] = last;
    return ret;
}

int astar(int grid[GRID_SZ][GRID_SZ], int sx, int sy, int gx, int gy) {
    static int g_score[GRID_SZ][GRID_SZ];
    static int visited[GRID_SZ][GRID_SZ];
    int x, y;
    for (y = 0; y < GRID_SZ; y++) {
        for (x = 0; x < GRID_SZ; x++) {
            g_score[y][x] = 999999;
            visited[y][x] = 0;
        }
    }
    MinHeap heap;
    heap.size = 0;
    g_score[sy][sx] = 0;
    Node start = {sx, sy, 0, abs(gx - sx) + abs(gy - sy)};
    push_heap(&heap, start);

    int dx[4] = {0, 0, 1, -1};
    int dy[4] = {1, -1, 0, 0};

    while (heap.size > 0) {
        Node curr = pop_heap(&heap);
        if (curr.x == gx && curr.y == gy) return curr.g;
        if (visited[curr.y][curr.x]) continue;
        visited[curr.y][curr.x] = 1;

        for (int d = 0; d < 4; d++) {
            int nx = curr.x + dx[d], ny = curr.y + dy[d];
            if (nx >= 0 && nx < GRID_SZ && ny >= 0 && ny < GRID_SZ && grid[ny][nx] == 0) {
                int tentative_g = curr.g + 1;
                if (tentative_g < g_score[ny][nx]) {
                    g_score[ny][nx] = tentative_g;
                    Node next = {nx, ny, tentative_g, tentative_g + abs(gx - nx) + abs(gy - ny)};
                    push_heap(&heap, next);
                }
            }
        }
    }
    return -1;
}

int main() {
    static int grid[GRID_SZ][GRID_SZ];
    int x, y, iter, total_dist = 0;
    for (y = 0; y < GRID_SZ; y++) {
        for (x = 0; x < GRID_SZ; x++) {
            grid[y][x] = ((x * 11 + y * 17) % 7 == 0) ? 1 : 0;
        }
    }
    grid[0][0] = 0;
    grid[GRID_SZ - 1][GRID_SZ - 1] = 0;

    for (iter = 0; iter < 12; iter++) {
        int target_x = (GRID_SZ - 1 - (iter % 8));
        int target_y = (GRID_SZ - 1 - ((iter * 3) % 8));
        grid[target_y][target_x] = 0;
        int d = astar(grid, 0, 0, target_x, target_y);
        total_dist += (d > 0 ? d : 0);
    }
    printf("A* Pathfind complete: total_dist=%d\n", total_dist);
    return 0;
}
