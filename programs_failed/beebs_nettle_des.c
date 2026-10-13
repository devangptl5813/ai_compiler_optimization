
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define REPEAT_FACTOR 1
#define BOARD_REPEAT_FACTOR 1
#define CALIB_SCALE 0

/* BEEBS nettle-des benchmark

   Copyright (C) 1992  Dana L. How
   Copyright (C) 2001 Niels Möller
   Copyright (C) 2014 Embecosm Limited and University of Bristol

   Contributor Pierre Langlois <pierre.langlois@embecosm.com>

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
   along with this program. If not, see <http://www.gnu.org/licenses/>.
*/

/*	des - fast & portable DES encryption & decryption.
 *	Copyright (C) 1992  Dana L. How
 *	Please see the file `descore.README' for the complete copyright notice.
 */

/* optional customization:
 * the idea here is to alter the code so it will still run correctly
 * on any machine,  but the quickest on the specific machine in mind.
 * note that these silly tweaks can give you a 15%-20% speed improvement
 * on the sparc -- it's probably even more significant on the 68000. */

#define	REGISTER	register

/* is auto inc/dec faster than 7bit unsigned indexing? */
#define	FIXR
#define	FIXS
#define	PREV(v,o)	v[o]
#define	NEXT(v,o)	v[o]

/* if no machine type, default is indexing, 6 registers and cheap literals */
#define	vax


/* handle a compiler which can't reallocate registers */
/* The BYTE type is used as parameter for the encrypt/decrypt functions.
 * It's pretty bad to have the function prototypes depend on
 * a macro definition that the users of the function doesn't
 * know about. /Niels */
#if	0			/* didn't feel like deleting */
#define	SREGFREE	; s = (uint8_t *) D
#define	DEST		s
#define	D		m0
#define	BYTE		uint32_t
#else
#define	SREGFREE
#define	DEST		d
#define	D		d
#define	BYTE		uint8_t
#endif

/* handle constants in the optimal way for 386 & vax */
/* 386: we declare 3 register variables (see above) and use 3 more variables;
 * vax: we use 6 variables, all declared register;
 * we assume address literals are cheap & unrestricted;
 * we assume immediate constants are cheap & unrestricted. */
#if	defined(i386) || defined(vax)
#define	MQ0	 des_bigmap
#define	MQ1	(des_bigmap +  64)
#define	MQ2	(des_bigmap + 128)
#define	MQ3	(des_bigmap + 192)
#define	HQ0(z)				/*	z |= 0x01000000L; */
#define	HQ2(z)				/*	z |= 0x03000200L; */
#define	LQ0(z)	0xFCFC & z
#define	LQ1(z)	0xFCFC & z
#define	LQ2(z)	0xFCFC & z
#define	LQ3(z)	0xFCFC & z
#define	SQ	16
#define	MS0	 des_keymap 
#define	MS1	(des_keymap +  64)
#define	MS2	(des_keymap + 128)
#define	MS3	(des_keymap + 192)
#define	MS4	(des_keymap + 256)
#define	MS5	(des_keymap + 320)
#define	MS6	(des_keymap + 384)
#define	MS7	(des_keymap + 448)
#define	HS(z)
#define	LS0(z)	0xFC & z
#define	LS1(z)	0xFC & z
#define	LS2(z)	0xFC & z
#define	LS3(z)	0xFC & z
#define	REGQUICK
#define	SETQUICK
#define	REGSMALL
#define	SETSMALL
#endif	/* defined(i386) || defined(vax) */

/* handle constants in the optimal way for mc68000 */
/* in addition to the core 6 variables, we declare 3 registers holding constants
 * and 4 registers holding address literals.
 * at most 6 data values and 5 address values are actively used at once.
 * we assume address literals are so expensive we never use them;
 * we assume constant index offsets > 127 are expensive, so they are not used.
 * we assume all constants are expensive and put them in registers,
 * including shift counts greater than 8. */
#if	defined(mc68000)
#define	MQ0	m0
#define	MQ1	m1
#define	MQ2	m2
#define	MQ3	m3
#define	HQ0(z)
#define	HQ2(z)
#define	LQ0(z)	k0 & z
#define	LQ1(z)	k0 & z
#define	LQ2(z)	k0 & z
#define	LQ3(z)	k0 & z
#define	SQ	k1
#define	MS0	m0
#define	MS1	m0
#define	MS2	m1
#define	MS3	m1
#define	MS4	m2
#define	MS5	m2
#define	MS6	m3
#define	MS7	m3
#define	HS(z)	z |= k0;
#define	LS0(z)	k1 & z
#define	LS1(z)	k2 & z
#define	LS2(z)	k1 & z
#define	LS3(z)	k2 & z
#define	REGQUICK				\
	register uint32_t k0, k1;		\
	register uint32_t *m0, *m1, *m2, *m3;
#define	SETQUICK				\
	; k0 = 0xFCFC				\
	; k1 = 16				\
	/*k2 = 28 to speed up ROL */		\
	; m0 = des_bigmap			\
	; m1 = m0 + 64				\
	; m2 = m1 + 64				\
	; m3 = m2 + 64
#define	REGSMALL				\
	register uint32_t k0, k1, k2;		\
	register uint32_t *m0, *m1, *m2, *m3;
#define	SETSMALL				\
	; k0 = 0x01000100L			\
	; k1 = 0x0FC				\
	; k2 = 0x1FC				\
	; m0 = des_keymap			\
	; m1 = m0 + 128				\
	; m2 = m1 + 128				\
	; m3 = m2 + 128
#endif	/* defined(mc68000) */

/* handle constants in the optimal way for sparc */
/* in addition to the core 6 variables, we either declare:
 * 4 registers holding address literals and 1 register holding a constant, or
 * 8 registers holding address literals.
 * up to 14 register variables are declared (sparc has %i0-%i5, %l0-%l7).
 * we assume address literals are so expensive we never use them;
 * we assume any constant with >10 bits is expensive and put it in a register,
 * and any other is cheap and is coded in-line. */
#if	defined(sparc)
#define	MQ0	m0
#define	MQ1	m1
#define	MQ2	m2
#define	MQ3	m3
#define	HQ0(z)
#define	HQ2(z)
#define	LQ0(z)	k0 & z
#define	LQ1(z)	k0 & z
#define	LQ2(z)	k0 & z
#define	LQ3(z)	k0 & z
#define	SQ	16
#define	MS0	m0
#define	MS1	m1
#define	MS2	m2
#define	MS3	m3
#define	MS4	m4
#define	MS5	m5
#define	MS6	m6
#define	MS7	m7
#define	HS(z)
#define	LS0(z)	0xFC & z
#define	LS1(z)	0xFC & z
#define	LS2(z)	0xFC & z
#define	LS3(z)	0xFC & z
#define	REGQUICK				\
	register uint32_t k0;			\
	register uint32_t *m0, *m1, *m2, *m3;
#define	SETQUICK				\
	; k0 = 0xFCFC				\
	; m0 = des_bigmap			\
	; m1 = m0 + 64				\
	; m2 = m1 + 64				\
	; m3 = m2 + 64
#define	REGSMALL				\
	register uint32_t *m0, *m1, *m2, *m3, *m4, *m5, *m6, *m7;
#define	SETSMALL				\
	; m0 = des_keymap			\
	; m1 = m0 + 64				\
	; m2 = m1 + 64				\
	; m3 = m2 + 64				\
	; m4 = m3 + 64				\
	; m5 = m4 + 64				\
	; m6 = m5 + 64				\
	; m7 = m6 + 64
#endif	/* defined(sparc) */


/* some basic stuff */

/* generate addresses from a base and an index */
/* FIXME: This is used only as *ADD(msi,lsi(z)) or *ADD(mqi,lqi(z)).
 * Why not use plain indexing instead? /Niels */
#define	ADD(b,x)	(uint32_t *) ((uint8_t *)b + (x))

/* low level rotate operations */
#define	NOP(d,c,o)
#define	ROL(d,c,o)	d = d << c | d >> o
#define	ROR(d,c,o)	d = d >> c | d << o
#define	ROL1(d)		ROL(d, 1, 31)
#define	ROR1(d)		ROR(d, 1, 31)

/* elementary swap for doing IP/FP */
#define	SWAP(x,y,m,b)				\
	z  = ((x >> b) ^ y) & m;		\
	x ^= z << b;				\
	y ^= z


/* the following macros contain all the important code fragments */

/* load input data, then setup special registers holding constants */
#define	TEMPQUICK(LOAD)				\
	REGQUICK				\
	LOAD()					\
	SETQUICK
#define	TEMPSMALL(LOAD)				\
	REGSMALL				\
	LOAD()					\
	SETSMALL

/* load data */
#define	LOADDATA(x,y)				\
	FIXS					\
	y  = PREV(s, 7); y<<= 8;		\
	y |= PREV(s, 6); y<<= 8;		\
	y |= PREV(s, 5); y<<= 8;		\
	y |= PREV(s, 4);			\
	x  = PREV(s, 3); x<<= 8;		\
	x |= PREV(s, 2); x<<= 8;		\
	x |= PREV(s, 1); x<<= 8;		\
	x |= PREV(s, 0)				\
	SREGFREE
/* load data without initial permutation and put into efficient position */
#define	LOADCORE()				\
	LOADDATA(x, y);				\
	ROR1(x);				\
	ROR1(y)
/* load data, do the initial permutation and put into efficient position */
#define	LOADFIPS()				\
	LOADDATA(y, x);				\
	SWAP(x, y, 0x0F0F0F0FL, 004);		\
	SWAP(y, x, 0x0000FFFFL, 020);		\
	SWAP(x, y, 0x33333333L, 002);		\
	SWAP(y, x, 0x00FF00FFL, 010);		\
	ROR1(x);				\
	z  = (x ^ y) & 0x55555555L;		\
	y ^= z;					\
	x ^= z;					\
	ROR1(y)


/* core encryption/decryption operations */
/* S box mapping and P perm */
#define	KEYMAPSMALL(x,z,mq0,mq1,hq,lq0,lq1,sq,ms0,ms1,ms2,ms3,hs,ls0,ls1,ls2,ls3)\
	hs(z)					\
	x ^= *ADD(ms3, ls3(z));			\
	z>>= 8;					\
	x ^= *ADD(ms2, ls2(z));			\
	z>>= 8;					\
	x ^= *ADD(ms1, ls1(z));			\
	z>>= 8;					\
	x ^= *ADD(ms0, ls0(z))
/* alternate version: use 64k of tables */
#define	KEYMAPQUICK(x,z,mq0,mq1,hq,lq0,lq1,sq,ms0,ms1,ms2,ms3,hs,ls0,ls1,ls2,ls3)\
	hq(z)					\
	x ^= *ADD(mq0, lq0(z));			\
	z>>= sq;				\
	x ^= *ADD(mq1, lq1(z))
/* apply 24 key bits and do the odd  s boxes */
#define	S7S1(x,y,z,r,m,KEYMAP,LOAD)		\
	z  = LOAD(r, m);			\
	z ^= y;					\
	KEYMAP(x,z,MQ0,MQ1,HQ0,LQ0,LQ1,SQ,MS0,MS1,MS2,MS3,HS,LS0,LS1,LS2,LS3)
/* apply 24 key bits and do the even s boxes */
#define	S6S0(x,y,z,r,m,KEYMAP,LOAD)		\
	z  = LOAD(r, m);			\
	z ^= y;					\
	ROL(z, 4, 28);				\
	KEYMAP(x,z,MQ2,MQ3,HQ2,LQ2,LQ3,SQ,MS4,MS5,MS6,MS7,HS,LS0,LS1,LS2,LS3)
/* actual iterations.  equivalent except for UPDATE & swapping m and n */
#define	ENCR(x,y,z,r,m,n,KEYMAP)		\
	S7S1(x,y,z,r,m,KEYMAP,NEXT);		\
	S6S0(x,y,z,r,n,KEYMAP,NEXT)
#define	DECR(x,y,z,r,m,n,KEYMAP)		\
	S6S0(x,y,z,r,m,KEYMAP,PREV);		\
	S7S1(x,y,z,r,n,KEYMAP,PREV)

/* write out result in correct byte order */
#define	SAVEDATA(x,y)				\
	NEXT(DEST, 0) = x; x>>= 8;		\
	NEXT(DEST, 1) = x; x>>= 8;		\
	NEXT(DEST, 2) = x; x>>= 8;		\
	NEXT(DEST, 3) = x;			\
	NEXT(DEST, 4) = y; y>>= 8;		\
	NEXT(DEST, 5) = y; y>>= 8;		\
	NEXT(DEST, 6) = y; y>>= 8;		\
	NEXT(DEST, 7) = y
/* write out result */
#define	SAVECORE()				\
	ROL1(x);				\
	ROL1(y);				\
	SAVEDATA(y, x)
/* do final permutation and write out result */
#define	SAVEFIPS()				\
	ROL1(x);				\
	z  = (x ^ y) & 0x55555555L;		\
	y ^= z;					\
	x ^= z;					\
	ROL1(y);				\
	SWAP(x, y, 0x00FF00FFL, 010);		\
	SWAP(y, x, 0x33333333L, 002);		\
	SWAP(x, y, 0x0000FFFFL, 020);		\
	SWAP(y, x, 0x0F0F0F0FL, 004);		\
	SAVEDATA(x, y)


/* the following macros contain the encryption/decryption skeletons */

#define	ENCRYPT(NAME, TEMP, LOAD, KEYMAP, SAVE)	\
						\
void						\
NAME(REGISTER BYTE *D,				\
     REGISTER const uint32_t *r,		\
     REGISTER const uint8_t *s)			\
{						\
	register uint32_t x, y, z;		\
						\
	/* declare temps & load data */		\
	TEMP(LOAD);				\
						\
	/* do the 16 iterations */		\
	ENCR(x,y,z,r, 0, 1,KEYMAP);		\
	ENCR(y,x,z,r, 2, 3,KEYMAP);		\
	ENCR(x,y,z,r, 4, 5,KEYMAP);		\
	ENCR(y,x,z,r, 6, 7,KEYMAP);		\
	ENCR(x,y,z,r, 8, 9,KEYMAP);		\
	ENCR(y,x,z,r,10,11,KEYMAP);		\
	ENCR(x,y,z,r,12,13,KEYMAP);		\
	ENCR(y,x,z,r,14,15,KEYMAP);		\
	ENCR(x,y,z,r,16,17,KEYMAP);		\
	ENCR(y,x,z,r,18,19,KEYMAP);		\
	ENCR(x,y,z,r,20,21,KEYMAP);		\
	ENCR(y,x,z,r,22,23,KEYMAP);		\
	ENCR(x,y,z,r,24,25,KEYMAP);		\
	ENCR(y,x,z,r,26,27,KEYMAP);		\
	ENCR(x,y,z,r,28,29,KEYMAP);		\
	ENCR(y,x,z,r,30,31,KEYMAP);		\
						\
	/* save result */			\
	SAVE();					\
						\
	return;					\
}

#define	DECRYPT(NAME, TEMP, LOAD, KEYMAP, SAVE)	\
						\
void						\
NAME(REGISTER BYTE *D,				\
     REGISTER const uint32_t *r,		\
     REGISTER const uint8_t *s)			\
{						\
	register uint32_t x, y, z;		\
						\
	/* declare temps & load data */		\
	TEMP(LOAD);				\
						\
	/* do the 16 iterations */		\
	FIXR					\
	DECR(x,y,z,r,31,30,KEYMAP);		\
	DECR(y,x,z,r,29,28,KEYMAP);		\
	DECR(x,y,z,r,27,26,KEYMAP);		\
	DECR(y,x,z,r,25,24,KEYMAP);		\
	DECR(x,y,z,r,23,22,KEYMAP);		\
	DECR(y,x,z,r,21,20,KEYMAP);		\
	DECR(x,y,z,r,19,18,KEYMAP);		\
	DECR(y,x,z,r,17,16,KEYMAP);		\
	DECR(x,y,z,r,15,14,KEYMAP);		\
	DECR(y,x,z,r,13,12,KEYMAP);		\
	DECR(x,y,z,r,11,10,KEYMAP);		\
	DECR(y,x,z,r, 9, 8,KEYMAP);		\
	DECR(x,y,z,r, 7, 6,KEYMAP);		\
	DECR(y,x,z,r, 5, 4,KEYMAP);		\
	DECR(x,y,z,r, 3, 2,KEYMAP);		\
	DECR(y,x,z,r, 1, 0,KEYMAP);		\
						\
	/* save result */			\
	SAVE();					\
						\
	return;					\
}

/* BEEBS nettle-des benchmark

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

/* automagically made - do not fuss with this */

 0x02080008, 0x02082000, 0x00002008, 0x00000000,
 0x02002000, 0x00080008, 0x02080000, 0x02082008,
 0x00000008, 0x02000000, 0x00082000, 0x00002008,
 0x00082008, 0x02002008, 0x02000008, 0x02080000,
 0x00002000, 0x00082008, 0x00080008, 0x02002000,
 0x02082008, 0x02000008, 0x00000000, 0x00082000,
 0x02000000, 0x00080000, 0x02002008, 0x02080008,
 0x00080000, 0x00002000, 0x02082000, 0x00000008,
 0x00080000, 0x00002000, 0x02000008, 0x02082008,
 0x00002008, 0x02000000, 0x00000000, 0x00082000,
 0x02080008, 0x02002008, 0x02002000, 0x00080008,
 0x02082000, 0x00000008, 0x00080008, 0x02002000,
 0x02082008, 0x00080000, 0x02080000, 0x02000008,
 0x00082000, 0x00002008, 0x02002008, 0x02080000,
 0x00000008, 0x02082000, 0x00082008, 0x00000000,
 0x02000000, 0x02080008, 0x00002000, 0x00082008,

 0x08000004, 0x00020004, 0x00000000, 0x08020200,
 0x00020004, 0x00000200, 0x08000204, 0x00020000,
 0x00000204, 0x08020204, 0x00020200, 0x08000000,
 0x08000200, 0x08000004, 0x08020000, 0x00020204,
 0x00020000, 0x08000204, 0x08020004, 0x00000000,
 0x00000200, 0x00000004, 0x08020200, 0x08020004,
 0x08020204, 0x08020000, 0x08000000, 0x00000204,
 0x00000004, 0x00020200, 0x00020204, 0x08000200,
 0x00000204, 0x08000000, 0x08000200, 0x00020204,
 0x08020200, 0x00020004, 0x00000000, 0x08000200,
 0x08000000, 0x00000200, 0x08020004, 0x00020000,
 0x00020004, 0x08020204, 0x00020200, 0x00000004,
 0x08020204, 0x00020200, 0x00020000, 0x08000204,
 0x08000004, 0x08020000, 0x00020204, 0x00000000,
 0x00000200, 0x08000004, 0x08000204, 0x08020200,
 0x08020000, 0x00000204, 0x00000004, 0x08020004,

 0x80040100, 0x01000100, 0x80000000, 0x81040100,
 0x00000000, 0x01040000, 0x81000100, 0x80040000,
 0x01040100, 0x81000000, 0x01000000, 0x80000100,
 0x81000000, 0x80040100, 0x00040000, 0x01000000,
 0x81040000, 0x00040100, 0x00000100, 0x80000000,
 0x00040100, 0x81000100, 0x01040000, 0x00000100,
 0x80000100, 0x00000000, 0x80040000, 0x01040100,
 0x01000100, 0x81040000, 0x81040100, 0x00040000,
 0x81040000, 0x80000100, 0x00040000, 0x81000000,
 0x00040100, 0x01000100, 0x80000000, 0x01040000,
 0x81000100, 0x00000000, 0x00000100, 0x80040000,
 0x00000000, 0x81040000, 0x01040100, 0x00000100,
 0x01000000, 0x81040100, 0x80040100, 0x00040000,
 0x81040100, 0x80000000, 0x01000100, 0x80040100,
 0x80040000, 0x00040100, 0x01040000, 0x81000100,
 0x80000100, 0x01000000, 0x81000000, 0x01040100,

 0x04010801, 0x00000000, 0x00010800, 0x04010000,
 0x04000001, 0x00000801, 0x04000800, 0x00010800,
 0x00000800, 0x04010001, 0x00000001, 0x04000800,
 0x00010001, 0x04010800, 0x04010000, 0x00000001,
 0x00010000, 0x04000801, 0x04010001, 0x00000800,
 0x00010801, 0x04000000, 0x00000000, 0x00010001,
 0x04000801, 0x00010801, 0x04010800, 0x04000001,
 0x04000000, 0x00010000, 0x00000801, 0x04010801,
 0x00010001, 0x04010800, 0x04000800, 0x00010801,
 0x04010801, 0x00010001, 0x04000001, 0x00000000,
 0x04000000, 0x00000801, 0x00010000, 0x04010001,
 0x00000800, 0x04000000, 0x00010801, 0x04000801,
 0x04010800, 0x00000800, 0x00000000, 0x04000001,
 0x00000001, 0x04010801, 0x00010800, 0x04010000,
 0x04010001, 0x00010000, 0x00000801, 0x04000800,
 0x04000801, 0x00000001, 0x04010000, 0x00010800,

 0x00000400, 0x00000020, 0x00100020, 0x40100000,
 0x40100420, 0x40000400, 0x00000420, 0x00000000,
 0x00100000, 0x40100020, 0x40000020, 0x00100400,
 0x40000000, 0x00100420, 0x00100400, 0x40000020,
 0x40100020, 0x00000400, 0x40000400, 0x40100420,
 0x00000000, 0x00100020, 0x40100000, 0x00000420,
 0x40100400, 0x40000420, 0x00100420, 0x40000000,
 0x40000420, 0x40100400, 0x00000020, 0x00100000,
 0x40000420, 0x00100400, 0x40100400, 0x40000020,
 0x00000400, 0x00000020, 0x00100000, 0x40100400,
 0x40100020, 0x40000420, 0x00000420, 0x00000000,
 0x00000020, 0x40100000, 0x40000000, 0x00100020,
 0x00000000, 0x40100020, 0x00100020, 0x00000420,
 0x40000020, 0x00000400, 0x40100420, 0x00100000,
 0x00100420, 0x40000000, 0x40000400, 0x40100420,
 0x40100000, 0x00100420, 0x00100400, 0x40000400,

 0x00800000, 0x00001000, 0x00000040, 0x00801042,
 0x00801002, 0x00800040, 0x00001042, 0x00801000,
 0x00001000, 0x00000002, 0x00800002, 0x00001040,
 0x00800042, 0x00801002, 0x00801040, 0x00000000,
 0x00001040, 0x00800000, 0x00001002, 0x00000042,
 0x00800040, 0x00001042, 0x00000000, 0x00800002,
 0x00000002, 0x00800042, 0x00801042, 0x00001002,
 0x00801000, 0x00000040, 0x00000042, 0x00801040,
 0x00801040, 0x00800042, 0x00001002, 0x00801000,
 0x00001000, 0x00000002, 0x00800002, 0x00800040,
 0x00800000, 0x00001040, 0x00801042, 0x00000000,
 0x00001042, 0x00800000, 0x00000040, 0x00001002,
 0x00800042, 0x00000040, 0x00000000, 0x00801042,
 0x00801002, 0x00801040, 0x00000042, 0x00001000,
 0x00001040, 0x00801002, 0x00800040, 0x00000042,
 0x00000002, 0x00001042, 0x00801000, 0x00800002,

 0x10400000, 0x00404010, 0x00000010, 0x10400010,
 0x10004000, 0x00400000, 0x10400010, 0x00004010,
 0x00400010, 0x00004000, 0x00404000, 0x10000000,
 0x10404010, 0x10000010, 0x10000000, 0x10404000,
 0x00000000, 0x10004000, 0x00404010, 0x00000010,
 0x10000010, 0x10404010, 0x00004000, 0x10400000,
 0x10404000, 0x00400010, 0x10004010, 0x00404000,
 0x00004010, 0x00000000, 0x00400000, 0x10004010,
 0x00404010, 0x00000010, 0x10000000, 0x00004000,
 0x10000010, 0x10004000, 0x00404000, 0x10400010,
 0x00000000, 0x00404010, 0x00004010, 0x10404000,
 0x10004000, 0x00400000, 0x10404010, 0x10000000,
 0x10004010, 0x10400000, 0x00400000, 0x10404010,
 0x00004000, 0x00400010, 0x10400010, 0x00004010,
 0x00400010, 0x00000000, 0x10404000, 0x10000010,
 0x10400000, 0x10004010, 0x00000010, 0x00404000,

 0x00208080, 0x00008000, 0x20200000, 0x20208080,
 0x00200000, 0x20008080, 0x20008000, 0x20200000,
 0x20008080, 0x00208080, 0x00208000, 0x20000080,
 0x20200080, 0x00200000, 0x00000000, 0x20008000,
 0x00008000, 0x20000000, 0x00200080, 0x00008080,
 0x20208080, 0x00208000, 0x20000080, 0x00200080,
 0x20000000, 0x00000080, 0x00008080, 0x20208000,
 0x00000080, 0x20200080, 0x20208000, 0x00000000,
 0x00000000, 0x20208080, 0x00200080, 0x20008000,
 0x00208080, 0x00008000, 0x20000080, 0x00200080,
 0x20208000, 0x00000080, 0x00008080, 0x20200000,
 0x20008080, 0x20000000, 0x20200000, 0x00208000,
 0x20208080, 0x00008080, 0x00208000, 0x20200080,
 0x00200000, 0x20000080, 0x20008000, 0x00000000,
 0x00008000, 0x00200000, 0x20200080, 0x00208080,
 0x20000000, 0x20208000, 0x00000080, 0x20008080,


/* BEEBS nettle-des benchmark

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

/* automagically made - do not fuss with this */

 34, 13,  5, 46, 47, 18, 32, 41, 11, 53, 33, 20,
 14, 36, 30, 24, 49,  2, 15, 37, 42, 50,  0, 21,
 38, 48,  6, 26, 39,  4, 52, 25, 12, 27, 31, 40,
  1, 17, 28, 29, 23, 51, 35,  7,  3, 22,  9, 43,

 41, 20, 12, 53, 54, 25, 39, 48, 18, 31, 40, 27,
 21, 43, 37,  0,  1,  9, 22, 44, 49,  2,  7, 28,
 45, 55, 13, 33, 46, 11,  6, 32, 19, 34, 38, 47,
  8, 24, 35, 36, 30,  3, 42, 14, 10, 29, 16, 50,

 55, 34, 26, 38, 11, 39, 53,  5, 32, 45, 54, 41,
 35,  2, 51, 14, 15, 23, 36,  3,  8, 16, 21, 42,
  6, 12, 27, 47, 31, 25, 20, 46, 33, 48, 52,  4,
 22,  7, 49, 50, 44, 17,  1, 28, 24, 43, 30,  9,

 12, 48, 40, 52, 25, 53, 38, 19, 46,  6, 11, 55,
 49, 16, 10, 28, 29, 37, 50, 17, 22, 30, 35,  1,
 20, 26, 41,  4, 45, 39, 34, 31, 47,  5, 13, 18,
 36, 21,  8,  9,  3,  0, 15, 42,  7,  2, 44, 23,

 26,  5, 54, 13, 39, 38, 52, 33, 31, 20, 25, 12,
  8, 30, 24, 42, 43, 51,  9,  0, 36, 44, 49, 15,
 34, 40, 55, 18,  6, 53, 48, 45,  4, 19, 27, 32,
 50, 35, 22, 23, 17, 14, 29,  1, 21, 16,  3, 37,

 40, 19, 11, 27, 53, 52, 13, 47, 45, 34, 39, 26,
 22, 44,  7,  1,  2, 10, 23, 14, 50,  3,  8, 29,
 48, 54, 12, 32, 20, 38,  5,  6, 18, 33, 41, 46,
  9, 49, 36, 37,  0, 28, 43, 15, 35, 30, 17, 51,

 54, 33, 25, 41, 38, 13, 27,  4,  6, 48, 53, 40,
 36,  3, 21, 15, 16, 24, 37, 28,  9, 17, 22, 43,
  5, 11, 26, 46, 34, 52, 19, 20, 32, 47, 55, 31,
 23,  8, 50, 51, 14, 42,  2, 29, 49, 44,  0, 10,

 11, 47, 39, 55, 52, 27, 41, 18, 20,  5, 38, 54,
 50, 17, 35, 29, 30,  7, 51, 42, 23,  0, 36,  2,
 19, 25, 40, 31, 48, 13, 33, 34, 46,  4, 12, 45,
 37, 22,  9, 10, 28,  1, 16, 43,  8,  3, 14, 24,

 18, 54, 46,  5,  6, 34, 48, 25, 27, 12, 45,  4,
  2, 24, 42, 36, 37, 14,  3, 49, 30,  7, 43,  9,
 26, 32, 47, 38, 55, 20, 40, 41, 53, 11, 19, 52,
 44, 29, 16, 17, 35,  8, 23, 50, 15, 10, 21,  0,

 32, 11, 31, 19, 20, 48,  5, 39, 41, 26,  6, 18,
 16,  7,  1, 50, 51, 28, 17,  8, 44, 21,  2, 23,
 40, 46,  4, 52, 12, 34, 54, 55, 38, 25, 33, 13,
  3, 43, 30,  0, 49, 22, 37,  9, 29, 24, 35, 14,

 46, 25, 45, 33, 34,  5, 19, 53, 55, 40, 20, 32,
 30, 21, 15,  9, 10, 42,  0, 22,  3, 35, 16, 37,
 54, 31, 18, 13, 26, 48, 11, 12, 52, 39, 47, 27,
 17,  2, 44, 14,  8, 36, 51, 23, 43,  7, 49, 28,

 31, 39,  6, 47, 48, 19, 33, 38, 12, 54, 34, 46,
 44, 35, 29, 23, 24,  1, 14, 36, 17, 49, 30, 51,
 11, 45, 32, 27, 40,  5, 25, 26, 13, 53,  4, 41,
  0, 16,  3, 28, 22, 50, 10, 37,  2, 21,  8, 42,

 45, 53, 20,  4,  5, 33, 47, 52, 26, 11, 48, 31,
  3, 49, 43, 37,  7, 15, 28, 50,  0,  8, 44, 10,
 25,  6, 46, 41, 54, 19, 39, 40, 27, 38, 18, 55,
 14, 30, 17, 42, 36,  9, 24, 51, 16, 35, 22,  1,

  6, 38, 34, 18, 19, 47,  4, 13, 40, 25,  5, 45,
 17,  8,  2, 51, 21, 29, 42,  9, 14, 22,  3, 24,
 39, 20, 31, 55, 11, 33, 53, 54, 41, 52, 32, 12,
 28, 44,  0,  1, 50, 23,  7, 10, 30, 49, 36, 15,

 20, 52, 48, 32, 33,  4, 18, 27, 54, 39, 19,  6,
  0, 22, 16, 10, 35, 43,  1, 23, 28, 36, 17,  7,
 53, 34, 45, 12, 25, 47, 38, 11, 55, 13, 46, 26,
 42,  3, 14, 15,  9, 37, 21, 24, 44,  8, 50, 29,

 27,  6, 55, 39, 40, 11, 25, 34,  4, 46, 26, 13,
  7, 29, 23, 17, 42, 50,  8, 30, 35, 43, 24, 14,
 31, 41, 52, 19, 32, 54, 45, 18,  5, 20, 53, 33,
 49, 10, 21, 22, 16, 44, 28,  0, 51, 15,  2, 36,



/* BEEBS nettle-des benchmark

   Copyright (C) 1992  Dana L. How
   Copyright (C) 2001 Niels Möller
   Copyright (C) 2014 Embecosm Limited and University of Bristol

   Contributor Pierre Langlois <pierre.langlois@embecosm.com>

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


#include <stdint.h>

/* This scale factor will be changed to equalise the runtime of the
   benchmarks. */
#define SCALE_FACTOR    (REPEAT_FACTOR >> 0)

static const uint8_t data[16] = {
  0x0,0x1,0x2,0x3,0x4,0x5,0x6,0x7,0x8,0x9,0xa,0xb,0xc,0xd,0xe,0xf
};

static uint8_t result[16];


#include "desCode.h"

#define DES_KEY_SIZE 8
#define DES_BLOCK_SIZE 8

/* Expanded key length */
#define _DES_KEY_LENGTH 32

struct des_ctx
{
  uint32_t key[_DES_KEY_LENGTH];
} des_ctx;

/* various tables */

static const uint32_t
des_keymap[] = {
#include	"keymap.h"
};

static const uint8_t
rotors[] = {
#include	"rotors.h"
};

static ENCRYPT(DesSmallFipsEncrypt,TEMPSMALL, LOADFIPS,KEYMAPSMALL,SAVEFIPS)
static DECRYPT(DesSmallFipsDecrypt,TEMPSMALL, LOADFIPS,KEYMAPSMALL,SAVEFIPS)


/* Weak and semiweak keys, excluding parity:
 *
 * 00 00 00 00  00 00 00 00
 * 7f 7f 7f 7f  7f 7f 7f 7f
 * 0f 0f 0f 0f  07 07 07 07
 * 70 70 70 70  78 78 78 78
 *
 * 00 7f 00 7f  00 7f 00 7f
 * 7f 00 7f 00  7f 00 7f 00
 *
 * 0f 70 0f 70  07 78 07 78
 * 70 0f 70 0f  78 07 78 07
 *
 * 00 70 00 70  00 78 00 78
 * 70 00 70 00  78 00 78 00
 *
 * 0f 7f 0f 7f  07 7f 07 7f
 * 7f 0f 7f 0f  7f 07 7f 07
 *
 * 00 0f 00 0f  00 07 00 07
 * 0f 00 0f 00  07 00 07 00
 *
 * 70 7f 70 7f  78 7f 78 7f
 * 7f 70 7f 70  7f 78 7f 78
 */

static int
des_weak_p(const uint8_t *key)
{
  /* Hash function generated using gperf. */
  static const unsigned char asso_values[0x81] =
    {
      16,  9, 26, 26, 26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26,  6,  2, 26, 26, 26,
      26, 26, 26, 26, 26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26, 26, 26, 26, 26,
      26, 26,  3,  1, 26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26, 26,  0,  0
    };

  static const int8_t weak_key_hash[26][4] =
    {
      /*  0 */ {0x7f,0x7f, 0x7f,0x7f},
      /*  1 */ {0x7f,0x70, 0x7f,0x78},
      /*  2 */ {0x7f,0x0f, 0x7f,0x07},
      /*  3 */ {0x70,0x7f, 0x78,0x7f},
      /*  4 */ {0x70,0x70, 0x78,0x78},
      /*  5 */ {0x70,0x0f, 0x78,0x07},
      /*  6 */ {0x0f,0x7f, 0x07,0x7f},
      /*  7 */ {0x0f,0x70, 0x07,0x78},
      /*  8 */ {0x0f,0x0f, 0x07,0x07},
      /*  9 */ {0x7f,0x00, 0x7f,0x00},
      /* 10 */ {-1,-1,-1,-1},
      /* 11 */ {-1,-1,-1,-1},
      /* 12 */ {0x70,0x00, 0x78,0x00},
      /* 13 */ {-1,-1,-1,-1},
      /* 14 */ {-1,-1,-1,-1},
      /* 15 */ {0x0f,0x00, 0x07,0x00},
      /* 16 */ {0x00,0x7f, 0x00,0x7f},
      /* 17 */ {0x00,0x70, 0x00,0x78},
      /* 18 */ {0x00,0x0f, 0x00,0x07},
      /* 19 */ {-1,-1,-1,-1},
      /* 20 */ {-1,-1,-1,-1},
      /* 21 */ {-1,-1,-1,-1},
      /* 22 */ {-1,-1,-1,-1},
      /* 23 */ {-1,-1,-1,-1},
      /* 24 */ {-1,-1,-1,-1},
      /* 25 */ {0x00,0x00, 0x00,0x00}
    };

  int8_t k0 = key[0] >> 1;
  int8_t k1 = key[1] >> 1;

  unsigned hash = asso_values[k1 + 1] + asso_values[k0];
  const int8_t *candidate = weak_key_hash[hash];

  if (hash > 25)
    return 0;
  if (k0 != candidate[0]
      || k1 != candidate[1])
    return 0;

  if ( (key[2] >> 1) != k0
       || (key[3] >> 1) != k1)
    return 0;

  k0 = key[4] >> 1;
  k1 = key[5] >> 1;
  if (k0 != candidate[2]
      || k1 != candidate[3])
    return 0;
  if ( (key[6] >> 1) != k0
       || (key[7] >> 1) != k1)
    return 0;

  return 1;
}

int
des_set_key(struct des_ctx *ctx, const uint8_t *key)
{
  register uint32_t n, w;
  register char * b0, * b1;
  char bits0[56], bits1[56];
  uint32_t *method;
  const uint8_t *k;

  /* explode the bits */
  n = 56;
  b0 = bits0;
  b1 = bits1;
  k = key;
  do {
    w = (256 | *k++) << 2;
    do {
      --n;
      b1[n] = 8 & w;
      w >>= 1;
      b0[n] = 4 & w;
    } while ( w >= 16 );
  } while ( n );

  /* put the bits in the correct places */
  n = 16;
  k = rotors;
  method = ctx->key;

  do {
    w   = (b1[k[ 0   ]] | b0[k[ 1   ]]) << 4;
    w  |= (b1[k[ 2   ]] | b0[k[ 3   ]]) << 2;
    w  |=  b1[k[ 4   ]] | b0[k[ 5   ]];
    w <<= 8;
    w  |= (b1[k[ 6   ]] | b0[k[ 7   ]]) << 4;
    w  |= (b1[k[ 8   ]] | b0[k[ 9   ]]) << 2;
    w  |=  b1[k[10   ]] | b0[k[11   ]];
    w <<= 8;
    w  |= (b1[k[12   ]] | b0[k[13   ]]) << 4;
    w  |= (b1[k[14   ]] | b0[k[15   ]]) << 2;
    w  |=  b1[k[16   ]] | b0[k[17   ]];
    w <<= 8;
    w  |= (b1[k[18   ]] | b0[k[19   ]]) << 4;
    w  |= (b1[k[20   ]] | b0[k[21   ]]) << 2;
    w  |=  b1[k[22   ]] | b0[k[23   ]];

    method[0] = w;

    w   = (b1[k[ 0+24]] | b0[k[ 1+24]]) << 4;
    w  |= (b1[k[ 2+24]] | b0[k[ 3+24]]) << 2;
    w  |=  b1[k[ 4+24]] | b0[k[ 5+24]];
    w <<= 8;
    w  |= (b1[k[ 6+24]] | b0[k[ 7+24]]) << 4;
    w  |= (b1[k[ 8+24]] | b0[k[ 9+24]]) << 2;
    w  |=  b1[k[10+24]] | b0[k[11+24]];
    w <<= 8;
    w  |= (b1[k[12+24]] | b0[k[13+24]]) << 4;
    w  |= (b1[k[14+24]] | b0[k[15+24]]) << 2;
    w  |=  b1[k[16+24]] | b0[k[17+24]];
    w <<= 8;
    w  |= (b1[k[18+24]] | b0[k[19+24]]) << 4;
    w  |= (b1[k[20+24]] | b0[k[21+24]]) << 2;
    w  |=  b1[k[22+24]] | b0[k[23+24]];

    ROR(w, 4, 28);		/* could be eliminated */
    method[1] = w;

    k	+= 48;
    method	+= 2;
  } while ( --n );

  return !des_weak_p (key);
}

void
des_encrypt(const struct des_ctx *ctx,
	    int length, uint8_t *dst,
	    const uint8_t *src)
{
  while (length)
    {
      DesSmallFipsEncrypt(dst, ctx->key, src);
      length -= DES_BLOCK_SIZE;
      src += DES_BLOCK_SIZE;
      dst += DES_BLOCK_SIZE;
    }
}

void
des_decrypt(const struct des_ctx *ctx,
	    int length, uint8_t *dst,
	    const uint8_t *src)
{
  while (length)
    {
      DesSmallFipsDecrypt(dst, ctx->key, src);
      length -= DES_BLOCK_SIZE;
      src += DES_BLOCK_SIZE;
      dst += DES_BLOCK_SIZE;
    }
}


void
initialise_benchmark (void)
{
}


int
benchmark (void)
{
  des_encrypt(&des_ctx, 16, result, data);
  des_decrypt(&des_ctx, 16, result, result);
  return 0;
}

int verify_benchmark(int unused) {
  int i;
  // #include <stdio.h>
  // for (i=0; i<16; i++)
  //   printf("%d, ", result[i]);
  uint8_t expected[16] =
    {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15};
  for (i=0; i<16; i++)
    if (result[i] != expected[i])
      return 0;
  return 1;
}


int main(void) {
    initialise_benchmark();
    int res = benchmark();
    verify_benchmark(res);
    return 0;
}
