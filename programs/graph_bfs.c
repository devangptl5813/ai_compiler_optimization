#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define V 300

void bfs(int adj[V][V], int start) {
    bool visited[V] = {false};
    int queue[V];
    int front = 0, rear = 0;

    visited[start] = true;
    queue[rear++] = start;

    int visited_count = 0;
    while (front < rear) {
        int curr = queue[front++];
        visited_count++;
        for (int i = 0; i < V; i++) {
            if (adj[curr][i] && !visited[i]) {
                visited[i] = true;
                queue[rear++] = i;
            }
        }
    }
}

int main() {
    static int adj[V][V];
    for (int i = 0; i < V; i++) {
        for (int j = 0; j < V; j++) {
            adj[i][j] = ((i + j) % 5 == 0) ? 1 : 0;
        }
    }
    for (int run = 0; run < 5; run++) {
        bfs(adj, run % V);
    }
    printf("Graph BFS complete.\n");
    return 0;
}
