#include <stdio.h>

double dydx(double x, double y) {
    return (x - y) / 2.0;
}

double runge_kutta(double x0, double y0, double x, double h) {
    int n = (int)((x - x0) / h);
    double k1, k2, k3, k4;
    double y = y0;
    for (int i = 1; i <= n; i++) {
        k1 = h * dydx(x0, y);
        k2 = h * dydx(x0 + 0.5 * h, y + 0.5 * k1);
        k3 = h * dydx(x0 + 0.5 * h, y + 0.5 * k2);
        k4 = h * dydx(x0 + h, y + k3);

        y = y + (1.0 / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4);
        x0 = x0 + h;
    }
    return y;
}

int main() {
    double res = 0.0;
    for (int iter = 0; iter < 50; iter++) {
        res += runge_kutta(0, 1, 50.0, 0.0002);
    }
    printf("Runge-Kutta complete: res=%.4f\n", res);
    return 0;
}
