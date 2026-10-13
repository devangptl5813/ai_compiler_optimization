
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define REPEAT_FACTOR 1
#define BOARD_REPEAT_FACTOR 1
#define CALIB_SCALE 0

/* BEEBS tarai benchmark

   Copyright (C) 2014 Embecosm Limited and University of Bristol

   Contributor James Pallister <james.pallister@bristol.ac.uk>

   This file is part of the Bristol/Embecosm Embedded Benchmark Suite.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program. If not, see <http://www.gnu.org/licenses/>. */



/* This scale factor will be changed to equalise the runtime of the
   benchmarks. */
#define SCALE_FACTOR    (REPEAT_FACTOR >> 0)

int tarai(int x, int y, int z)
{
    int ox = x;
    int oy = y;

    while (x > y)
    {
        ox = x;
        oy = y;

        x = tarai(x - 1, y, z);
        y = tarai(y - 1, z, ox);

        if (x <= y)
            break;

        z = tarai(z - 1, ox, oy);
    }

    return y;
}

int x, y, z;

int benchmark()
{
    volatile int cnt=0;

    cnt = tarai(x, y, z);

    return cnt;

}

void initialise_benchmark() {
  x = 9;
  y = 6;
  z = 3;
}

int verify_benchmark(int r) {
  int expected = 9;
  if (r != expected)
    return 0;
  return 1;
}


int main(void) {
    initialise_benchmark();
    int res = benchmark();
    verify_benchmark(res);
    return 0;
}
