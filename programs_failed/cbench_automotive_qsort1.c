/* Inlined source qsort.c */
//
// qsort.c
//
// Quick sort
//
// Copyright (C) 2002 Michael Ringgaard. All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions
// are met:
// 
// 1. Redistributions of source code must retain the above copyright 
//    notice, this list of conditions and the following disclaimer.  
// 2. Redistributions in binary form must reproduce the above copyright
//    notice, this list of conditions and the following disclaimer in the
//    documentation and/or other materials provided with the distribution.  
// 3. Neither the name of the project nor the names of its contributors
//    may be used to endorse or promote products derived from this software
//    without specific prior written permission. 
// 
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
// ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
// FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
// OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
// HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
// LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
// OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF 
// SUCH DAMAGE.
// 

#define CUTOFF 8

static void shortsort(char *lo, char *hi, unsigned width, int (*comp)(const void *, const void *));
static void swap(char *p, char *q, unsigned int width);

void qsortx(void *base, unsigned num, unsigned width, int (*comp)(const void *, const void *))
{
  char *lo, *hi;
  char *mid;
  char *loguy, *higuy;
  unsigned size;
  char *lostk[30], *histk[30];
  int stkptr;

  if (num < 2 || width == 0) return;
  stkptr = 0;

  lo = base;
  hi = (char *) base + width * (num - 1);

recurse:
  size = (hi - lo) / width + 1;

  if (size <= CUTOFF) 
  {
    shortsort(lo, hi, width, comp);
  }
  else 
  {
    mid = lo + (size / 2) * width;
    swap(mid, lo, width);

    loguy = lo;
    higuy = hi + width;

    for (;;) 
    {
      do { loguy += width; } while (loguy <= hi && comp(loguy, lo) <= 0);
      do { higuy -= width; } while (higuy > lo && comp(higuy, lo) >= 0);
      if (higuy < loguy) break;
      swap(loguy, higuy, width);
    }

    swap(lo, higuy, width);

    if (higuy - 1 - lo >= hi - loguy) 
    {
      if (lo + width < higuy) 
      {
        lostk[stkptr] = lo;
        histk[stkptr] = higuy - width;
        ++stkptr;
      }

      if (loguy < hi) 
      {
        lo = loguy;
        goto recurse;
      }
    }
    else
    {
      if (loguy < hi) 
      {
        lostk[stkptr] = loguy;
        histk[stkptr] = hi;
        ++stkptr;
      }

      if (lo + width < higuy) 
      {
        hi = higuy - width;
        goto recurse;
      }
    }
  }

  --stkptr;
  if (stkptr >= 0) 
  {
    lo = lostk[stkptr];
    hi = histk[stkptr];
    goto recurse;
  }
  else
    return;
}

static void shortsort(char *lo, char *hi, unsigned width, int (*comp)(const void *, const void *))
{
  char *p, *max;

  while (hi > lo) 
  {
    max = lo;
    for (p = lo+width; p <= hi; p += width) if (comp(p, max) > 0) max = p;
    swap(max, hi, width);
    hi -= width;
  }
}

static void swap(char *a, char *b, unsigned width)
{
  char tmp;

  if (a != b)
  {
    while (width--) 
    {
      tmp = *a;
      *a++ = *b;
      *b++ = tmp;
    }
  }
}

/* Inlined source qsort_large.c */
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#define UNLIMIT
#define MAXARRAY 60000 /* this number, if too large, will cause a seg. fault!! */

void qsortx(void *base, unsigned num, unsigned width,
            int (*comp)(const void *, const void *));

struct my3DVertexStruct {
  int x, y, z;
  double distance;
};

int compare(const void *elem1, const void *elem2)
{
  /* D = [(x1 - x2)^2 + (y1 - y2)^2 + (z1 - z2)^2]^(1/2) */
  /* sort based on distances from the origin... */

  double distance1, distance2;

  distance1 = (*((struct my3DVertexStruct *)elem1)).distance;
  distance2 = (*((struct my3DVertexStruct *)elem2)).distance;

  return (distance1 > distance2) ? 1 : ((distance1 == distance2) ? 0 : -1);
}

struct my3DVertexStruct array[MAXARRAY];

int
main1(int argc, char *argv[], int print) {
  FILE* fmisc=NULL;
  FILE *fp;
  int i,count=0;
  long x=0;
  long y=0;
  long z=0;

  if (argc<2) {
    fprintf(stderr,"Usage: qsort_large <file>\n");
    exit(EXIT_FAILURE);
  }
  else {
    fp = fopen(argv[1],"r");

    while((fscanf(fp, "%d", &x) == 1) && (fscanf(fp, "%d", &y) == 1) && (fscanf(fp, "%d", &z) == 1) &&  (count < MAXARRAY)) {
	 array[count].x = x;
	 array[count].y = y;
	 array[count].z = z;
	 array[count].distance = sqrt(pow(x, 2) + pow(y, 2) + pow(z, 2));
	 count++;
    }

    fclose(fp);
  }
  if (print==1) {
      printf("\nSorting %d vectors based on distance from the origin.\n\n",
             count);
  }
  qsortx(array,count,sizeof(struct my3DVertexStruct),compare);

  if (print==1) {
      if ((fmisc=fopen("tmp-output.tmp","wt"))==NULL)
          {
              fprintf(stderr,"\nError: Can't open output file\n");
              exit(EXIT_FAILURE);
          }
   for(i=0;i<count;i+=count/100)
     fprintf(fmisc, "%d %d %d\n", array[i].x, array[i].y, array[i].z);
  
   fclose(fmisc);
  }
  return 0;
}

/* Main file ctuning-rtl.c */
/*
#
# Collective Tuning Run-Time
# Part of Collective Mind
#
# See cM LICENSE.txt for licensing details.
# See cM Copyright.txt for copyright details.
#
# Developer(s): (C) Grigori Fursin, started on 2011.09
#
*/

#include <stdio.h>
#include <stdlib.h>

#ifdef OPENME
#include <openme.h>
#endif
#ifdef XOPENME
#include <xopenme.h>
#endif

int main1(int argc, char* argv[], int print);

int main(int argc, char* argv[])
{
  long ct_repeat=0;
  long ct_repeat_max=1;
  int ct_return=0;
  int print=1;

#ifdef OPENME
  openme_init(NULL,NULL,NULL,0);
  openme_callback("PROGRAM_START", NULL);
#endif
#ifdef XOPENME
  xopenme_init(1,0);
#endif

  if (getenv("CT_REPEAT_MAIN")!=NULL) ct_repeat_max=atol(getenv("CT_REPEAT_MAIN"));
  			  
#ifdef OPENME
  openme_callback("KERNEL_START", NULL);
#endif
#ifdef XOPENME
  xopenme_clock_start(0);
#endif
  for (ct_repeat=0; ct_repeat<ct_repeat_max; ct_repeat++)
  {
    ct_return=main1(argc, argv, print);
    print=0;
  }
#ifdef XOPENME
  xopenme_clock_end(0);
#endif
#ifdef OPENME
  openme_callback("KERNEL_END", NULL);
#endif
  

#ifdef XOPENME
  xopenme_dump_state();
  xopenme_finish();
#endif
#ifdef OPENME
  openme_callback("PROGRAM_END", NULL);
#endif

  return ct_return;
}
