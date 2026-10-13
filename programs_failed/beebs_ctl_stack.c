
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define REPEAT_FACTOR 1
#define BOARD_REPEAT_FACTOR 1
#define CALIB_SCALE 0

../ctl/ctl.h
../ctl/stack.h
../ctl/ctl.c

int main(void) {
    initialise_benchmark();
    int res = benchmark();
    verify_benchmark(res);
    return 0;
}
