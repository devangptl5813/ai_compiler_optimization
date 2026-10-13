#include <stdio.h>
#include <stdbool.h>
#include <limits.h>

#define V 250

int min_distance(int dist[], bool spt_set[]) {
    int min = INT_MAX, min_index = -1;
    for (int v = 0; v < V; v++) {
        if (!spt_set[v] && dist[v] <= min) {
            min = dist[v];
            min_index = v;
        }
    }
    return min_index;
}

void dijkstra(int graph[V][V], int src) {
    int dist[V];
    bool spt_set[V];
    for (int i = 0; i < V; i++) {
        dist[i] = INT_MAX;
        spt_set[i] = false;
    }
    dist[src] = 0;

    for (int count = 0; count < V - 1; count++) {
        int u = min_distance(dist, spt_set);
        if (u == -1) break;
        spt_set[u] = true;
        for (int v = 0; v < V; v++) {
            if (!spt_set[v] && graph[u][v] && dist[u] != INT_MAX
                && dist[u] + graph[u][v] < dist[v]) {
                dist[v] = dist[u] + graph[u][v];
            }
        }
    }
}

int main() {
    static int graph[V][V];
    for (int i = 0; i < V; i++) {
        for (int j = 0; j < V; j++) {
            graph[i][j] = (i == j) ? 0 : ((i + j) % 11 + 1);
        }
    }
    for (int iter = 0; iter < 3; iter++) {
        dijkstra(graph, iter % V);
    }
    printf("Dijkstra complete.\n");
    return 0;
}
