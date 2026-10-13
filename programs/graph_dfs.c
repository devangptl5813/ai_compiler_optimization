#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define V 250

void dfs_rec(int adj[V][V], bool visited[V], int u) {
    visited[u] = true;
    for (int v = 0; v < V; v++) {
        if (adj[u][v] && !visited[v]) {
            dfs_rec(adj, visited, v);
        }
    }
}

int main() {
    static int adj[V][V];
    for (int i = 0; i < V; i++) {
        for (int j = 0; j < V; j++) {
            adj[i][j] = ((i * j + 3) % 7 == 0) ? 1 : 0;
        }
    }
    bool visited[V];
    for (int run = 0; run < 10; run++) {
        for (int k = 0; k < V; k++) visited[k] = false;
        dfs_rec(adj, visited, run % V);
    }
    printf("Graph DFS complete.\n");
    return 0;
}
