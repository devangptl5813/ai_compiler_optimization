
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define REPEAT_FACTOR 1
#define BOARD_REPEAT_FACTOR 1
#define CALIB_SCALE 0



/* -*- mode: C++; c-file-style: "gnu-mode" -*- */
/* BEEBS template benchmark

   *** Put any preceding copyright here ***
   Copyright (C) 2013 Embecosm Limited and University of Bristol

   Contributor Jeremy Bennett <jeremy.bennett@embecosm.com>

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




/* This benchmark does not support verification */

int
verify_benchmark (int res __attribute ((unused)) )
{
  return -1;
}


void
initialise_benchmark (void)
{
}


int
benchmark (void)
{
  /* Code to benchmark goes here */
  return 0;
}




int main(void) {
    initialise_benchmark();
    int res = benchmark();
    verify_benchmark(res);
    return 0;
}
