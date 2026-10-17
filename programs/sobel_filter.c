#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define W 128
#define H 128

void sobel_filter(const unsigned char *in, unsigned char *out, int w, int h) {
    int x, y;
    int gx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
    int gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};
    for (y = 1; y < h - 1; y++) {
        for (x = 1; x < w - 1; x++) {
            int sum_x = 0;
            int sum_y = 0;
            int ky, kx;
            for (ky = -1; ky <= 1; ky++) {
                for (kx = -1; kx <= 1; kx++) {
                    int val = in[(y + ky) * w + (x + kx)];
                    sum_x += val * gx[ky + 1][kx + 1];
                    sum_y += val * gy[ky + 1][kx + 1];
                }
            }
            int mag = (int)sqrt((double)(sum_x * sum_x + sum_y * sum_y));
            out[y * w + x] = (unsigned char)(mag > 255 ? 255 : mag);
        }
    }
}

int main() {
    unsigned char *in = (unsigned char *)malloc(W * H);
    unsigned char *out = (unsigned char *)malloc(W * H);
    int i, iter;
    for (i = 0; i < W * H; i++) {
        in[i] = (unsigned char)((i * 13 + 7) & 0xFF);
    }
    for (iter = 0; iter < 4; iter++) {
        sobel_filter(in, out, W, H);
    }
    long sum = 0;
    for (i = 0; i < W * H; i += 19) {
        sum += out[i];
    }
    printf("Sobel filter complete: sum=%ld\n", sum);
    free(in); free(out);
    return 0;
}
