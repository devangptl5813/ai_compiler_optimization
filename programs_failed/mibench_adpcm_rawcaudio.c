/*
** adpcm.h - include file for adpcm coder.
**
** Version 1.0, 7-Jul-92.
*/

struct adpcm_state {
    short	valprev;	/* Previous output value */
    char	index;		/* Index into stepsize table */
};

#ifdef __STDC__
#define ARGS(x) x
#else
#define ARGS(x) ()
#endif

void adpcm_coder ARGS((short [], char [], int, struct adpcm_state *));
void adpcm_decoder ARGS((char [], short [], int, struct adpcm_state *));

/* libst.h - include file for portable sound tools library
**
** Copyright (C) 1989 by Jef Poskanzer.
**
** Permission to use, copy, modify, and distribute this software and its
** documentation for any purpose and without fee is hereby granted, provided
** that the above copyright notice appear in all copies and that both that
** copyright notice and this permission notice appear in supporting
** documentation.  This software is provided "as is" without express or
** implied warranty.
*/

#define SAMPLES_PER_SECOND 8192

#define MINLIN -32768
#define MAXLIN 32767
#define LINCLIP(x) do { if ( x < MINLIN ) x = MINLIN ; else if ( x > MAXLIN ) x = MAXLIN; } while ( 0 )

unsigned char st_linear_to_ulaw( /* int sample */ );
int st_ulaw_to_linear_slow( /* unsigned char ulawbyte */ );

/*
** This macro converts from ulaw to 16 bit linear, faster.
**
** Jef Poskanzer
** 23 October 1989
**
** Input: 8 bit ulaw sample
** Output: signed 16 bit linear sample
*/
#define st_ulaw_to_linear(ulawbyte) ulaw_table[ulawbyte]

static int ulaw_table[256] = {
    -32124, -31100, -30076, -29052, -28028, -27004, -25980, -24956,
    -23932, -22908, -21884, -20860, -19836, -18812, -17788, -16764,
    -15996, -15484, -14972, -14460, -13948, -13436, -12924, -12412,
    -11900, -11388, -10876, -10364,  -9852,  -9340,  -8828,  -8316,
     -7932,  -7676,  -7420,  -7164,  -6908,  -6652,  -6396,  -6140,
     -5884,  -5628,  -5372,  -5116,  -4860,  -4604,  -4348,  -4092,
     -3900,  -3772,  -3644,  -3516,  -3388,  -3260,  -3132,  -3004,
     -2876,  -2748,  -2620,  -2492,  -2364,  -2236,  -2108,  -1980,
     -1884,  -1820,  -1756,  -1692,  -1628,  -1564,  -1500,  -1436,
     -1372,  -1308,  -1244,  -1180,  -1116,  -1052,   -988,   -924,
      -876,   -844,   -812,   -780,   -748,   -716,   -684,   -652,
      -620,   -588,   -556,   -524,   -492,   -460,   -428,   -396,
      -372,   -356,   -340,   -324,   -308,   -292,   -276,   -260,
      -244,   -228,   -212,   -196,   -180,   -164,   -148,   -132,
      -120,   -112,   -104,    -96,    -88,    -80,    -72,    -64,
       -56,    -48,    -40,    -32,    -24,    -16,     -8,      0,
     32124,  31100,  30076,  29052,  28028,  27004,  25980,  24956,
     23932,  22908,  21884,  20860,  19836,  18812,  17788,  16764,
     15996,  15484,  14972,  14460,  13948,  13436,  12924,  12412,
     11900,  11388,  10876,  10364,   9852,   9340,   8828,   8316,
      7932,   7676,   7420,   7164,   6908,   6652,   6396,   6140,
      5884,   5628,   5372,   5116,   4860,   4604,   4348,   4092,
      3900,   3772,   3644,   3516,   3388,   3260,   3132,   3004,
      2876,   2748,   2620,   2492,   2364,   2236,   2108,   1980,
      1884,   1820,   1756,   1692,   1628,   1564,   1500,   1436,
      1372,   1308,   1244,   1180,   1116,   1052,    988,    924,
       876,    844,    812,    780,    748,    716,    684,    652,
       620,    588,    556,    524,    492,    460,    428,    396,
       372,    356,    340,    324,    308,    292,    276,    260,
       244,    228,    212,    196,    180,    164,    148,    132,
       120,    112,    104,     96,     88,     80,     72,     64,
	56,     48,     40,     32,     24,     16,      8,      0 };

/***********************************************************
Copyright 1992 by Stichting Mathematisch Centrum, Amsterdam, The
Netherlands.

                        All Rights Reserved

Permission to use, copy, modify, and distribute this software and its 
documentation for any purpose and without fee is hereby granted, 
provided that the above copyright notice appear in all copies and that
both that copyright notice and this permission notice appear in 
supporting documentation, and that the names of Stichting Mathematisch
Centrum or CWI not be used in advertising or publicity pertaining to
distribution of the software without specific, written prior permission.

STICHTING MATHEMATISCH CENTRUM DISCLAIMS ALL WARRANTIES WITH REGARD TO
THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS, IN NO EVENT SHALL STICHTING MATHEMATISCH CENTRUM BE LIABLE
FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

******************************************************************/

/*
** Intel/DVI ADPCM coder/decoder.
**
** The algorithm for this coder was taken from the IMA Compatability Project
** proceedings, Vol 2, Number 2; May 1992.
**
** Version 1.2, 18-Dec-92.
**
** Change log:
** - Fixed a stupid bug, where the delta was computed as
**   stepsize*code/4 in stead of stepsize*(code+0.5)/4.
** - There was an off-by-one error causing it to pick
**   an incorrect delta once in a blue moon.
** - The NODIVMUL define has been removed. Computations are now always done
**   using shifts, adds and subtracts. It turned out that, because the standard
**   is defined using shift/add/subtract, you needed bits of fixup code
**   (because the div/mul simulation using shift/add/sub made some rounding
**   errors that real div/mul don't make) and all together the resultant code
**   ran slower than just using the shifts all the time.
** - Changed some of the variable names to be more meaningful.
*/

#include "adpcm.h"
#include <stdio.h> /*DBG*/

#ifndef __STDC__
#define signed
#endif

/* Intel ADPCM step variation table */
static int indexTable[16] = {
    -1, -1, -1, -1, 2, 4, 6, 8,
    -1, -1, -1, -1, 2, 4, 6, 8,
};

static int stepsizeTable[89] = {
    7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
    19, 21, 23, 25, 28, 31, 34, 37, 41, 45,
    50, 55, 60, 66, 73, 80, 88, 97, 107, 118,
    130, 143, 157, 173, 190, 209, 230, 253, 279, 307,
    337, 371, 408, 449, 494, 544, 598, 658, 724, 796,
    876, 963, 1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066,
    2272, 2499, 2749, 3024, 3327, 3660, 4026, 4428, 4871, 5358,
    5894, 6484, 7132, 7845, 8630, 9493, 10442, 11487, 12635, 13899,
    15289, 16818, 18500, 20350, 22385, 24623, 27086, 29794, 32767
};
    
void
adpcm_coder(indata, outdata, len, state)
    short indata[];
    char outdata[];
    int len;
    struct adpcm_state *state;
{
    short *inp;			/* Input buffer pointer */
    signed char *outp;		/* output buffer pointer */
    int val;			/* Current input sample value */
    int sign;			/* Current adpcm sign bit */
    int delta;			/* Current adpcm output value */
    int diff;			/* Difference between val and valprev */
    int step;			/* Stepsize */
    int valpred;		/* Predicted output value */
    int vpdiff;			/* Current change to valpred */
    int index;			/* Current step change index */
    int outputbuffer;		/* place to keep previous 4-bit value */
    int bufferstep;		/* toggle between outputbuffer/output */

    outp = (signed char *)outdata;
    inp = indata;

    valpred = state->valprev;
    index = state->index;
    step = stepsizeTable[index];
    
    bufferstep = 1;

    for ( ; len > 0 ; len-- ) {
	val = *inp++;

	/* Step 1 - compute difference with previous value */
	diff = val - valpred;
	sign = (diff < 0) ? 8 : 0;
	if ( sign ) diff = (-diff);

	/* Step 2 - Divide and clamp */
	/* Note:
	** This code *approximately* computes:
	**    delta = diff*4/step;
	**    vpdiff = (delta+0.5)*step/4;
	** but in shift step bits are dropped. The net result of this is
	** that even if you have fast mul/div hardware you cannot put it to
	** good use since the fixup would be too expensive.
	*/
	delta = 0;
	vpdiff = (step >> 3);
	
	if ( diff >= step ) {
	    delta = 4;
	    diff -= step;
	    vpdiff += step;
	}
	step >>= 1;
	if ( diff >= step  ) {
	    delta |= 2;
	    diff -= step;
	    vpdiff += step;
	}
	step >>= 1;
	if ( diff >= step ) {
	    delta |= 1;
	    vpdiff += step;
	}

	/* Step 3 - Update previous value */
	if ( sign )
	  valpred -= vpdiff;
	else
	  valpred += vpdiff;

	/* Step 4 - Clamp previous value to 16 bits */
	if ( valpred > 32767 )
	  valpred = 32767;
	else if ( valpred < -32768 )
	  valpred = -32768;

	/* Step 5 - Assemble value, update index and step values */
	delta |= sign;
	
	index += indexTable[delta];
	if ( index < 0 ) index = 0;
	if ( index > 88 ) index = 88;
	step = stepsizeTable[index];

	/* Step 6 - Output value */
	if ( bufferstep ) {
	    outputbuffer = (delta << 4) & 0xf0;
	} else {
	    *outp++ = (delta & 0x0f) | outputbuffer;
	}
	bufferstep = !bufferstep;
    }

    /* Output last step, if needed */
    if ( !bufferstep )
      *outp++ = outputbuffer;
    
    state->valprev = valpred;
    state->index = index;
}

void
adpcm_decoder(indata, outdata, len, state)
    char indata[];
    short outdata[];
    int len;
    struct adpcm_state *state;
{
    signed char *inp;		/* Input buffer pointer */
    short *outp;		/* output buffer pointer */
    int sign;			/* Current adpcm sign bit */
    int delta;			/* Current adpcm output value */
    int step;			/* Stepsize */
    int valpred;		/* Predicted value */
    int vpdiff;			/* Current change to valpred */
    int index;			/* Current step change index */
    int inputbuffer;		/* place to keep next 4-bit value */
    int bufferstep;		/* toggle between inputbuffer/input */

    outp = outdata;
    inp = (signed char *)indata;

    valpred = state->valprev;
    index = state->index;
    step = stepsizeTable[index];

    bufferstep = 0;
    
    for ( ; len > 0 ; len-- ) {
	
	/* Step 1 - get the delta value */
	if ( bufferstep ) {
	    delta = inputbuffer & 0xf;
	} else {
	    inputbuffer = *inp++;
	    delta = (inputbuffer >> 4) & 0xf;
	}
	bufferstep = !bufferstep;

	/* Step 2 - Find new index value (for later) */
	index += indexTable[delta];
	if ( index < 0 ) index = 0;
	if ( index > 88 ) index = 88;

	/* Step 3 - Separate sign and magnitude */
	sign = delta & 8;
	delta = delta & 7;

	/* Step 4 - Compute difference and new predicted value */
	/*
	** Computes 'vpdiff = (delta+0.5)*step/4', but see comment
	** in adpcm_coder.
	*/
	vpdiff = step >> 3;
	if ( delta & 4 ) vpdiff += step;
	if ( delta & 2 ) vpdiff += step>>1;
	if ( delta & 1 ) vpdiff += step>>2;

	if ( sign )
	  valpred -= vpdiff;
	else
	  valpred += vpdiff;

	/* Step 5 - clamp output value */
	if ( valpred > 32767 )
	  valpred = 32767;
	else if ( valpred < -32768 )
	  valpred = -32768;

	/* Step 6 - Update step value */
	step = stepsizeTable[index];

	/* Step 7 - Output value */
	*outp++ = valpred;
    }

    state->valprev = valpred;
    state->index = index;
}

/* testd - Test adpcm decoder */

#include "adpcm.h"
#include <stdio.h>

struct adpcm_state state;

#define NSAMPLES 1000

char	abuf[NSAMPLES/2];
short	sbuf[NSAMPLES];

main() {
    int n;

    while(1) {
	n = read(0, abuf, NSAMPLES/2);
	if ( n < 0 ) {
	    perror("input file");
	    exit(1);
	}
	if ( n == 0 ) break;
	adpcm_decoder(abuf, sbuf, n*2, &state);
	write(1, sbuf, n*4);
    }
    fprintf(stderr, "Final valprev=%d, index=%d\n",
	    state.valprev, state.index);
    exit(0);
}

/*
** sgicaudio - Simple AIFF file compressor.
**
** Needs libaf, which is in the Digital Media developers option.
*/

#include <stdio.h>
#include <audio.h>
#include <audiofile.h>
#include "adpcm.h"

#define NFRAMES 8000

struct adpcm_state astate;
short ibuf[NFRAMES];
char obuf[NFRAMES/2];

main(argc, argv)
    int argc;
    char **argv;
{
    AFfilehandle af;
    FILE *of;
    long fmt, width;
    long count;
    
    if ( argc < 2 || argc > 3 ) {
	fprintf(stderr, "Usage: %s aifffile [adpcmfile]\n", argv[0]);
	exit(1);
    }
    /*
    ** Open input file and check format
    */
    if ( (af = AFopenfile(argv[1], "r", NULL)) == 0 ) {
	perror(argv[1]);
	exit(1);
    }
    AFgetsampfmt(af, AF_DEFAULT_TRACK, &fmt, &width);
    if ( AFgetchannels(af, AF_DEFAULT_TRACK) != 1 || fmt != AF_SAMPFMT_TWOSCOMP
	|| width != 16 ) {
	fprintf(stderr, "%s: %s: only 16bit mono integer files supported\n",
		argv[0], argv[1]);
	exit(1);
    }
    if ( AFgetrate(af, AF_DEFAULT_TRACK) != 8000.0 )
      fprintf(stderr, "%s: %s: WARNING: not 8Khz\n", argv[0], argv[1]);
    /*
    ** Open output file
    */
    if ( argc == 3 ) {
	if ( (of=fopen(argv[2], "w")) == 0 ) {
	    perror(argv[2]);
	    exit(1);
	}
    } else {
	of = stdout;
    }
    /*
    ** Copy loop
    */
    while (1) {
	count = AFreadframes(af, AF_DEFAULT_TRACK, ibuf, NFRAMES);
	if ( count <= 0 ) break;
	if ( count & 1 ) {
	    ibuf[count] = ibuf[count-1];
	    count++;
	}
	adpcm_coder(ibuf, obuf, count, &astate);
	fwrite(obuf, 1, (count+1)/2, of);
    }
    fclose(of);
    AFclosefile(af);
    exit(0);
}

/*
** sgidaudio - Simple AIFF file decompressor.
**
** Needs libaf, which is in the Digital Media developers option.
*/

#include <stdio.h>
#include <audio.h>
#include <audiofile.h>
#include "adpcm.h"

#define NFRAMES 8000

struct adpcm_state astate;
char ibuf[NFRAMES/2];
short obuf[NFRAMES];

main(argc, argv)
    int argc;
    char **argv;
{
    AFfilehandle af;
    AFfilesetup afsetup;
    FILE *of;
    long fmt, width;
    long count;
    int outindex;
    
    if ( argc < 2 || argc > 3 ) {
	fprintf(stderr, "Usage: %s [adpcmfile] aifffile\n", argv[0]);
	exit(1);
    }
    /*
    ** Open input file
    */
    if ( argc == 3 ) {
	if ( (of = fopen(argv[1], "r")) == NULL ) {
	    perror(argv[1]);
	    exit(1);
	}
	outindex = 2;
    } else {
	of = stdin;
	outindex = 1;
    }
    /*
    ** Open output file
    */
    afsetup = AFnewfilesetup();
    AFinitchannels(afsetup, AF_DEFAULT_TRACK, 1);
    AFinitrate(afsetup, AF_DEFAULT_TRACK, 8000.0);
    AFinitsampfmt(afsetup, AF_DEFAULT_TRACK, AF_SAMPFMT_TWOSCOMP, 16);
    if ( (af = AFopenfile(argv[outindex], "w", afsetup)) == 0 ) {
	perror(argv[outindex]);
	exit(1);
    }
    /*
    ** Copy loop
    */
    while (1) {
	count = fread(ibuf, 1, NFRAMES/2, of);
	if ( count <= 0 ) break;
	count = count*2;
	adpcm_decoder(ibuf, obuf, count, &astate);
	AFwriteframes(af, AF_DEFAULT_TRACK, obuf, count);
    }
    fclose(of);
    AFclosefile(af);
    exit(0);
}

#include <stdio.h>
#include <strings.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <multimedia/ulaw2linear.h>
#include <multimedia/libaudio.h>
#include "adpcm.h"

#ifdef __STDC__
#define A(x) x
#else
#define A(x) ()
#endif

extern char *strdup A((char *));
extern char *strstr A((char *, char *));


main(argc, argv)
    int argc;
    char *argv[];
{

int file,outfile;		/* input file */
Audio_hdr audiohdr;		/* Audio File header */
int cnt;			/* how much read ? */
register char *ulaw;		/* pointer to ulaw output from pcm conv */
register short *pcm;		/* pointer to pcm output from ulaw conv */
char ulawbuf[BUFSIZ];		/* to hold ulaw data */
short pcmbuf[BUFSIZ];		/* to hold pcm data */
int decompress=0;		/* just a flag */
struct stat statbuf;
char *newfn;			/* output file name */
char *p;			/* temporary character pointer */
struct adpcm_state state;
int pos;


/* this program can be called with two different names, if it
   is called as caudio then we want to compress the file and if
   it is called with uaudio then we want to uncompress it */

        pos = strlen(argv[0]) - strlen("caudio");
        if (strcmp(argv[0]+pos,"daudio") == 0) 
		decompress=1;
        else if ( strcmp(argv[0]+pos,"caudio") != 0) {
	    puts("Progname should end in 'caudio' or 'daudio'");
	    exit(1);
	}

	if (argc < 2) {
		puts("No input file(s) specified");
		exit(1);
	}

/* Now we pass through the entire list of input files and compress
   each file found */

	while (argc-- > 1) {
		if ((file = open(*++argv,O_RDONLY)) == NULL) {
			perror("couldn't open input file");
			exit(1);
		}
		if (!decompress) {
			if (! audio_isaudiofile(*argv)) {
				perror("not an audio file");
				exit(2);
			}
			if (audio_read_filehdr(file, &audiohdr, 
					(char *)NULL, 0) != AUDIO_SUCCESS) {
				perror("bad header");
				exit(3);
			}
			newfn=(char *) malloc(strlen(*argv)+5);
			sprintf(newfn,"%s.pcm",*argv);

			if ((outfile = open(newfn, O_RDWR |O_CREAT | O_EXCL,
					    0644)) < 0) {
				printf("%s already exists\n",newfn);
				free(newfn);
				continue;
			}
			while ((cnt = read(file, (char *) ulawbuf,
					   sizeof ulawbuf)) > 0) {
				ulaw = ulawbuf;
				pcm = pcmbuf;

				/* translate all from ulaw to 16 bit pcm */
				while (ulaw != ulawbuf+cnt) {
					*pcm++ = (ushort) audio_u2s(*ulaw++);
				}

				/* now quantize it using adpcm */
				adpcm_coder(pcmbuf, ulawbuf, cnt, &state);
				write(outfile, ulawbuf, cnt/2);
			}
			close(outfile);
			free(newfn);
		}
		else {
			newfn=strdup(*argv);
			if ((p=strstr(newfn,".pcm")) == NULL) {
				puts("not a valid pcm file");
				continue;
			}
			*p='\0';		/* take off .pcm suffix */

			if ((outfile = open(newfn, O_RDWR |O_CREAT | O_EXCL,
					    0644)) < 0) {
				printf("%s already exists\n",newfn);
				free(newfn);
				continue;
			}
			fstat(file,&statbuf);
			audiohdr.sample_rate = 8000;
			audiohdr.samples_per_unit = 1;
			audiohdr.bytes_per_unit = 1;
			audiohdr.channels = 1;
			audiohdr.encoding = AUDIO_ENCODING_ULAW;

			/* now tell it how big the audio file is. The original
			 * file has exactly twice as many playable bytes as
			 * this one, so we double the current number.
			 * There are also 32Bytes in
			 * the sound header, but they don't count */
			audiohdr.data_size = statbuf.st_size * 2;

			if (audio_write_filehdr(outfile, &audiohdr, NULL, 0) 
							!= AUDIO_SUCCESS) {
				perror("writing header");
				exit(5);
			}
			while ((cnt = read(file, ulawbuf, sizeof(ulawbuf)/2))
			                                     > 0) {
				ulaw = ulawbuf;
				pcm = pcmbuf;

				/* first we decode from adpcm format */
				adpcm_decoder(ulawbuf, pcmbuf, cnt*2, &state);

				/* now translate from 16bit pcm to Sun
				 * mulaw format */
				while (pcm != pcmbuf+cnt*2) {
					*ulaw++ = audio_s2u(*pcm++);
				}
				write(outfile, ulawbuf, cnt*2);
			}
		}
	}
	exit(0);
}

/*
** Timing - Test timing on adpcm coder and decoder.
**
** The program creates 10Kb garbage, and runs the compressor and
** the decompressor on it.
*/

#include <stdio.h>
#include <math.h>
#include "adpcm.h"

#define DATASIZE 10*1024	/* Data block size */
#define DURATION 10		/* How many seconds to measure */

short pcmdata[DATASIZE];
char adpcmdata[DATASIZE/2];
short pcmdata_2[DATASIZE];

struct adpcm_state coder_1_state, coder_2_state, decoder_state;

main() {
    int i;
    int t0, t1, t2, t3;
    int count = 0, count2;

    for(i=0; i<DATASIZE; i++)
      pcmdata[i] = random() & 0xffff;

    t0 = time(0);
    do {
	adpcm_coder(pcmdata, adpcmdata, DATASIZE, &coder_1_state);
	t1 = time(0);
	count++;
    } while (t1 < t0+DURATION);
    printf("Coder: %d Ksample/second\n", count*DATASIZE/(1000*(t1-t0)));
    printf("  (coded %d blocks of %d samples in %d seconds)\n",
	   count, DATASIZE, t1-t0);
    t2 = time(0);
    count2 = count;
    while ( count2 > 0 ) {
	adpcm_coder(pcmdata, adpcmdata, DATASIZE, &coder_2_state);
	adpcm_decoder(adpcmdata, pcmdata_2, DATASIZE, &decoder_state);
	count2--;
    }
    t3 = time(0);
    printf("Decoder: %d Ksample/second\n",
	   count*DATASIZE/(1000*(t3-t2-t1+t0)));
    printf("  (coded&decoded %d blocks of %d samples in %d seconds)\n",
	   count, DATASIZE, t3-t2);
    exit(0);
}

/* testc - Test adpcm coder */

#include "adpcm.h"
#include <stdio.h>

struct adpcm_state state;

#define NSAMPLES 1000

char	abuf[NSAMPLES/2];
short	sbuf[NSAMPLES];

main() {
    int n;

    while(1) {
	n = read(0, sbuf, NSAMPLES*2);
	if ( n < 0 ) {
	    perror("input file");
	    exit(1);
	}
	if ( n == 0 ) break;
	adpcm_coder(sbuf, abuf, n/2, &state);
	write(1, abuf, n/4);
    }
    fprintf(stderr, "Final valprev=%d, index=%d\n",
	    state.valprev, state.index);
    exit(0);
}
