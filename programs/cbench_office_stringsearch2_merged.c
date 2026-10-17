#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef XOPENME
#include <xopenme.h>
#endif

static char str_misc[1024];

/*
 * Copyright (c) 1989, 1993
 *	The Regents of the University of California.  All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. All advertising materials mentioning features or use of this software
 *    must display the following acknowledgement:
 *	This product includes software developed by the University of
 *	California, Berkeley and its contributors.
 * 4. Neither the name of the University nor the names of its contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 * $FreeBSD: src/sys/libkern/strncmp.c,v 1.7 1999/08/28 00:46:38 peter Exp $
 */

int
local_strncmp(s1, s2, n)
	register const char *s1, *s2;
	register size_t n;
{

	if (n == 0)
		return (0);
	do {
		if (*s1 != *s2++)
			return (*(const unsigned char *)s1 -
				*(const unsigned char *)(s2 - 1));
		if (*s1++ == 0)
			break;
	} while (--n != 0);
	return (0);
}


char *strsearch2(char *string, char *search)
{
   int i;

   for (i=0; i<strlen(string); i++)
   {
     if (local_strncmp(&string[i], search, strlen(search))==0)
        return &string[i];
   }

   return NULL;
}




int main(int argc, char *argv[]) {
    char *text_corpus[] = {
        "The quick brown fox jumps over the lazy dog repeatedly.",
        "Computer compilers translate high-level code to assembly.",
        "Optimization passes enhance execution speed and decrease binary code size.",
        "Machine learning models predict optimal compiler flag sequences.",
        "Static code features include loops, arrays, pointers, and arithmetic ops.",
        "Benchmarking requires representative sample programs and stable measurement.",
        "Polybench, MiBench, cBench, and BEEBS serve as diverse empirical benchmarks.",
        NULL
    };
    char *search_patterns[] = {
        "compiler", "optimize", "bench", "speed", "model", "code", "dog", NULL
    };

    int matches = 0;
    int i, j;
    for (i = 0; text_corpus[i] != NULL; i++) {
        int tlen = strlen(text_corpus[i]);
        for (j = 0; search_patterns[j] != NULL; j++) {
            int plen = strlen(search_patterns[j]);
            int k;
            for (k = 0; k <= tlen - plen; k++) {
                if (local_strncmp(&text_corpus[i][k], search_patterns[j], plen) == 0) {
                    matches++;
                }
            }
        }
    }
    printf("String search completed with %d pattern matches.\n", matches);
    return 0;
}
