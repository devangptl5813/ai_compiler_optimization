
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define REPEAT_FACTOR 1
#define BOARD_REPEAT_FACTOR 1
#define CALIB_SCALE 0

../trio/trio.h
../trio/triodef.h
../trio/triop.h
../trio/triostr.h
../trio/trio.c
../trio/triostr.c
../trio/trio_test.c

int main(void) {
    initialise_benchmark();
    int res = benchmark();
    verify_benchmark(res);
    return 0;
}
