#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846
#define N_FFT 1024

void fft_butterfly(double *real, double *imag, int n) {
    int i, j;
    for (i = 0; i < n; i++) {
        for (j = 0; j < n; j += 2) {
            double r_temp = real[j] * cos(PI/n) - imag[j] * sin(PI/n);
            double i_temp = real[j] * sin(PI/n) + imag[j] * cos(PI/n);
            real[j] += r_temp;
            imag[j] += i_temp;
        }
    }
}

int main() {
    double *real = (double *)malloc(N_FFT * sizeof(double));
    double *imag = (double *)malloc(N_FFT * sizeof(double));
    for (int i = 0; i < N_FFT; i++) {
        real[i] = sin(2 * PI * i / 100.0);
        imag[i] = 0.0;
    }
    for (int iter = 0; iter < 5; iter++) {
        fft_butterfly(real, imag, N_FFT);
    }
    printf("FFT Sim complete: real[0]=%.4f\n", real[0]);
    free(real); free(imag);
    return 0;
}
