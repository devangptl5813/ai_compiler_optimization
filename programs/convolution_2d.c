#include <stdio.h>
#include <stdlib.h>

#define W 200
#define H 200
#define K 5

void convolve(float input[H][W], float output[H][W], float kernel[K][K]) {
    int k_offset = K / 2;
    for (int y = k_offset; y < H - k_offset; y++) {
        for (int x = k_offset; x < W - k_offset; x++) {
            float sum = 0.0f;
            for (int ky = 0; ky < K; ky++) {
                for (int kx = 0; kx < K; kx++) {
                    int py = y + ky - k_offset;
                    int px = x + kx - k_offset;
                    sum += input[py][px] * kernel[ky][kx];
                }
            }
            output[y][x] = sum;
        }
    }
}

int main() {
    static float in[H][W], out[H][W];
    float kernel[K][K] = {
        {0.04, 0.04, 0.04, 0.04, 0.04},
        {0.04, 0.04, 0.04, 0.04, 0.04},
        {0.04, 0.04, 0.04, 0.04, 0.04},
        {0.04, 0.04, 0.04, 0.04, 0.04},
        {0.04, 0.04, 0.04, 0.04, 0.04}
    };
    for (int y = 0; y < H; y++)
        for (int x = 0; x < W; x++)
            in[y][x] = (float)(x + y);

    for (int iter = 0; iter < 5; iter++) {
        convolve(in, out, kernel);
    }
    printf("2D Convolution complete: out[50][50]=%.2f\n", out[50][50]);
    return 0;
}
