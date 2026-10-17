#include <stdio.h>
#include <stdlib.h>

#define W 128
#define H 128

void gaussian_blur_separable(const float *in, float *out, float *temp, int w, int h) {
    float k[5] = {0.06136f, 0.24477f, 0.38774f, 0.24477f, 0.06136f};
    int x, y, i;
    for (y = 0; y < h; y++) {
        for (x = 0; x < w; x++) {
            float sum = 0.0f;
            for (i = -2; i <= 2; i++) {
                int cx = x + i;
                if (cx < 0) cx = 0;
                if (cx >= w) cx = w - 1;
                sum += in[y * w + cx] * k[i + 2];
            }
            temp[y * w + x] = sum;
        }
    }
    for (y = 0; y < h; y++) {
        for (x = 0; x < w; x++) {
            float sum = 0.0f;
            for (i = -2; i <= 2; i++) {
                int cy = y + i;
                if (cy < 0) cy = 0;
                if (cy >= h) cy = h - 1;
                sum += temp[cy * w + x] * k[i + 2];
            }
            out[y * w + x] = sum;
        }
    }
}

int main() {
    float *in = (float *)malloc(W * H * sizeof(float));
    float *out = (float *)malloc(W * H * sizeof(float));
    float *temp = (float *)malloc(W * H * sizeof(float));

    for (int i = 0; i < W * H; i++) {
        in[i] = (float)((i * 17) % 255);
    }
    for (int iter = 0; iter < 4; iter++) {
        gaussian_blur_separable(in, out, temp, W, H);
        in[iter % (W * H)] += 0.5f;
    }

    double checksum = 0.0;
    for (int i = 0; i < W * H; i += 29) {
        checksum += out[i];
    }
    printf("Gaussian blur complete: checksum=%.4f\n", checksum);
    free(in); free(out); free(temp);
    return 0;
}
