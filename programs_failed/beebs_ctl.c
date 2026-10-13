
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define REPEAT_FACTOR 1
#define BOARD_REPEAT_FACTOR 1
#define CALIB_SCALE 0

/* This file is part of the Bristol/Embecosm Embedded Benchmark Suite.

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

/*****************************************************************************
 * FILE: ctl.h                                                               *
 * AUTHOR: Toni Schornboeck <schornboeck@c-plusplus.de>                      *
 *****************************************************************************
 * Das zentrale File der CTL                                                 *
 *****************************************************************************
 * Diese Datei darf frei unter der                                           *
 * GPL (http://www.gnu.org/copyleft/gpl.html) verwendet werden.              *
 *****************************************************************************/

#ifndef CTL_STANDARD_HEADER__
#define CTL_STANDARD_HEADER__
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>
#include <stdio.h>

#ifndef CTL_SIZE
#define	CTL_SIZE			100
#endif

#ifndef CTL_GROWFACTOR
#define CTL_GROWFACTOR		0.7
#endif

#ifdef	CTL_NORANGECHECK
#define	CTL_RANGE(x)		if(0)
#else
#define	CTL_RANGE(x)		if(x)
#endif

#define	CTL_OUT_OF_MEMORY	100
#define	CTL_WRONG_VALUE		101
#define	CTL_OUT_OF_RANGE	102
#define CTL_NOT_FOUND		103

struct CTL_STRUCT {
	size_t	BlockSize;
};
typedef struct CTL_STRUCT ctl_struct;

unsigned int ctl_errno;
unsigned int ctl_warning;

int ctl_SetBlockSize(ctl_struct* its, size_t BlockSize)
{
	if(BlockSize<1)
	{
		ctl_errno=CTL_WRONG_VALUE;
		return 1;
	}
	its->BlockSize=BlockSize;
	return 0;
}

#define CTL_GROW_ALLOC_SIZE(its) its->BlockSize=((size_t)(its->alloc+its->alloc*CTL_GROWFACTOR))

#endif

/* This file is part of the Bristol/Embecosm Embedded Benchmark Suite.

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

/*****************************************************************************
 * FILE: stack.h                                                             *
 * AUTHOR: Toni Schornboeck <schornboeck@c-plusplus.de>                      *
 *****************************************************************************
 * Implementierung eines FixedSize Stack fuer die CTL                        *
 *****************************************************************************
 * Diese Datei darf frei unter der                                           *
 * GPL (http://www.gnu.org/copyleft/gpl.html) verwendet werden.              *
 *****************************************************************************/

#include "ctl.h"

#define MAKE_STACK(type)							\
struct CTL_##type##STACK {							\
	type*	value;									\
	size_t	size;									\
	size_t	first;									\
	size_t	alloc;									\
};													\
													\
typedef struct CTL_##type##STACK ctl_##type##Stack;	\
													\
ctl_##type##Stack* ctl_##type##StackInitSize(int BlockSize)\
{													\
	ctl_##type##Stack* s=malloc_beebs(sizeof(ctl_##type##Stack));\
	if(!s)											\
	{												\
		return NULL;								\
	}												\
	s->alloc		= BlockSize;					\
	s->value		= malloc_beebs(BlockSize*sizeof(type));\
	if(!s->value)									\
	{												\
		return NULL;								\
	}												\
	s->first		= 0;							\
	s->size			= 0;							\
	return s;										\
}													\
													\
ctl_##type##Stack* ctl_##type##StackInit(void)		\
{													\
	return ctl_##type##StackInitSize(CTL_SIZE);		\
}													\
													\
ctl_##type##Stack* ctl_##type##StackInitCopy(ctl_##type##Stack* stack)\
{													\
	ctl_##type##Stack* s=malloc_beebs(sizeof(ctl_##type##Stack));\
	if(!s)											\
	{												\
		return NULL;								\
	}												\
	s->alloc		= stack->alloc;					\
	s->value		= malloc_beebs(stack->alloc*sizeof(type));\
	if(!s->value)									\
	{												\
		return NULL;								\
	}												\
	s->first		= stack->first;					\
	s->size			= stack->size;					\
	return s;										\
}													\
													\
void ctl_##type##StackFree(ctl_##type##Stack* s)	\
{													\
	free_beebs(s->value);									\
	free_beebs(s);										\
}													\
													\
int ctl_##type##StackPush(ctl_##type##Stack* s, type value)\
{													\
	if(++s->size>s->alloc)							\
	{												\
		s->size=s->alloc;							\
	}												\
	if(++s->first==s->size)							\
	{												\
		s->first=0;									\
	}												\
	s->value[s->first]=value;						\
	return 0;										\
}													\
													\
int ctl_##type##StackPop(ctl_##type##Stack* s, type* value)\
{													\
	if(s->size==0)									\
	{												\
		ctl_errno=CTL_OUT_OF_RANGE;					\
		return 1;									\
	}												\
													\
	if(value)*value=s->value[s->first];				\
	--s->size;										\
	if(s->size)										\
	{												\
		if(!s->first)								\
		{											\
			s->first=s->size-1;						\
			return 0;								\
		}											\
		--s->first;									\
	}												\
	return 0;										\
}


/* This file is part of the Bristol/Embecosm Embedded Benchmark Suite.

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

/*****************************************************************************
 * FILE: vector.h                                                            *
 * AUTHOR: Toni Schornboeck <schornboeck@c-plusplus.de>                      *
 *****************************************************************************
 * Implementierung eines vectors (dynamisches array) fuer die CTL            *
 *****************************************************************************
 * Diese Datei darf frei unter der                                           *
 * GPL (http://www.gnu.org/copyleft/gpl.html) verwendet werden.              *
 *****************************************************************************/

#include "ctl.h"


#define MAKE_VECTOR(type)									\
struct CTL_##type##VECTOR {									\
	size_t	BlockSize;										\
	type*	value;											\
	size_t	size;											\
	size_t	alloc;											\
};															\
															\
typedef struct CTL_##type##VECTOR ctl_##type##Vector;		\
															\
ctl_##type##Vector* ctl_##type##VectorInitSize(int BlockSize)\
{															\
	ctl_##type##Vector* s=malloc_beebs(sizeof(ctl_##type##Vector));\
	if(!s)													\
	{														\
		return NULL;										\
	}														\
	s->BlockSize	= BlockSize;							\
	s->value		= malloc_beebs(s->BlockSize*sizeof(type));	\
	if(!s->value)											\
	{														\
		ctl_errno	= CTL_OUT_OF_MEMORY;					\
		s->size		= 0;									\
		s->alloc	= 0;									\
		return NULL;										\
	}														\
	s->alloc		= s->BlockSize;							\
	s->size			= 0;									\
	return s;												\
}															\
															\
ctl_##type##Vector* ctl_##type##VectorInit(void)			\
{															\
	return ctl_##type##VectorInitSize(CTL_SIZE);			\
}															\
															\
ctl_##type##Vector* ctl_##type##VectorInitCopy(ctl_##type##Vector* vector)\
{															\
	ctl_##type##Vector* s=malloc_beebs(sizeof(ctl_##type##Vector));\
	if(!s)													\
	{														\
		return NULL;										\
	}														\
	s->BlockSize	= vector->BlockSize;					\
	s->value		= malloc_beebs(vector->alloc*sizeof(type));	\
	if(!s->value)											\
	{														\
		ctl_errno	= CTL_OUT_OF_MEMORY;					\
		s->size		= 0;									\
		s->alloc	= 0;									\
		return NULL;										\
	}														\
	memmove(s->value,vector->value,vector->size*sizeof(type));\
	s->alloc		= vector->alloc;						\
	s->size			= vector->size;							\
	return s;												\
}															\
															\
void ctl_##type##VectorFree(ctl_##type##Vector* s)			\
{															\
	free_beebs(s->value);											\
	free_beebs(s);												\
}															\
															\
int ctl_##type##VectorPush_Back(ctl_##type##Vector* s, type push)\
{															\
	if(s->alloc <= s->size)									\
	{														\
		type* secure;										\
		s->alloc+=s->BlockSize;								\
		secure=malloc_beebs(s->alloc*sizeof(type));				\
		if(!secure)											\
		{													\
			ctl_errno	= CTL_OUT_OF_MEMORY;				\
			s->alloc-=s->BlockSize;							\
			return 1;										\
		}													\
		memcpy(secure, s->value, s->size*sizeof(type));	  	\
		CTL_GROW_ALLOC_SIZE(s);								\
		s->value=secure;									\
	}														\
	s->value[s->size]=push;									\
	++s->size;												\
	return 0;												\
}															\
															\
int ctl_##type##VectorPop_Back(ctl_##type##Vector* s, type* value)\
{															\
	CTL_RANGE(s->size == 0)									\
	{														\
		ctl_errno = CTL_OUT_OF_RANGE;						\
		return 0;											\
	}														\
	--s->size;												\
	if(!value)												\
		return 0;											\
	*value = s->value[s->size];								\
	return 0;												\
}															\
															\
int ctl_##type##VectorSet(ctl_##type##Vector* s, type* vector, size_t size)\
{															\
	if(s->value==vector && s->size==size)					\
		return 0;											\
	if(s->alloc<size)										\
	{														\
		size_t alloc=(size/s->BlockSize+1)*s->BlockSize;	\
		type* secure;										\
		secure=malloc_beebs(alloc*sizeof(type));					\
		if(!secure)											\
		{													\
			ctl_errno	= CTL_OUT_OF_MEMORY;				\
			return 1;										\
		}													\
		memcpy(secure, s->value, s->size*sizeof(type));	  	\
		s->value=secure;									\
		s->alloc=alloc;										\
	}														\
	s->size=size;											\
	memmove(s->value,vector,size*sizeof(type));				\
	return 1;												\
}															\
															\
int ctl_##type##VectorSetVector(ctl_##type##Vector* s, ctl_##type##Vector* vector)\
{															\
	if(s==vector)											\
		return 0;											\
	if(s->alloc<vector->size)								\
	{														\
		size_t alloc=(vector->size/s->BlockSize+1)*s->BlockSize;\
		type* secure;										\
		secure=malloc_beebs(alloc*sizeof(type));					\
		if(!secure)											\
		{													\
			ctl_errno	= CTL_OUT_OF_MEMORY;				\
			return 1;										\
		}													\
		memcpy(secure, s->value, s->size*sizeof(type));	  	\
		s->alloc=alloc;										\
		s->value=secure;									\
	}														\
	memmove(s->value,vector->value,vector->size*sizeof(type));\
	s->size=vector->size;									\
	return 0;												\
}															\
															\
int ctl_##type##VectorSetAt(ctl_##type##Vector* s, size_t pos, type value)\
{															\
	CTL_RANGE(pos>=s->size)									\
	{														\
		ctl_errno=CTL_OUT_OF_RANGE;							\
		return 1;											\
	}														\
	s->value[pos]=value;									\
	return 0;												\
}															\
															\
int ctl_##type##VectorInsert(ctl_##type##Vector* s, size_t pos, type value)\
{															\
	CTL_RANGE(pos>=s->size)									\
	{														\
		ctl_errno=CTL_WRONG_VALUE;							\
		return ctl_errno;									\
	}														\
	if(s->size>=s->alloc)									\
	{														\
		type* secure;										\
		s->alloc+=s->BlockSize;								\
		secure=malloc_beebs(s->alloc*sizeof(type));				\
		if(!secure)											\
		{													\
			s->alloc-=s->BlockSize;							\
			ctl_errno=CTL_OUT_OF_MEMORY;					\
			return 1;										\
		}													\
		memcpy(secure, s->value, s->size*sizeof(type));	  	\
		s->alloc+=s->BlockSize;								\
		CTL_GROW_ALLOC_SIZE(s);								\
		s->value=secure;									\
	}														\
	memmove(&s->value[pos+1],&s->value[pos],(s->size-pos)*sizeof(type));\
	++s->size;												\
	s->value[pos]=value;									\
	return 0;												\
}															\
															\
int ctl_##type##VectorDelete(ctl_##type##Vector* s, size_t begin, size_t end)\
{															\
	CTL_RANGE(begin>end)									\
	{														\
		ctl_errno=CTL_WRONG_VALUE;							\
		return 1;											\
	}														\
	s->size-=(end-begin);									\
	memmove(&s->value[begin],&s->value[end],s->size*sizeof(type));\
	return 0;												\
}															\
															\
int ctl_##type##VectorShrink(ctl_##type##Vector* s)			\
{															\
	type* secure;											\
	secure=malloc_beebs(s->size*sizeof(type));					\
	if(!secure)												\
	{														\
		ctl_errno=CTL_OUT_OF_MEMORY;						\
		return 1;											\
	}														\
	memcpy(secure, s->value, s->size*sizeof(type));	  		\
	s->value=secure;										\
	return 0;												\
}

/* -*- mode: C++; c-file-style: "gnu-mode" -*- */
/* BEEBS vector benchmark

   Copyright (C) 2013 Embecosm Limited and University of Bristol

   Contributor: James Pallister <james.pallister@bristol.ac.uk>

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

typedef struct {
  int a, b;
} pair;

/* BEEBS heap is just an array */

#include <stddef.h>

#define HEAP_SIZE 8192
static char heap[HEAP_SIZE];
static void *heap_ptr;
static void *heap_end;

/* Initialize the BEEBS heap pointers */

static void
init_heap ()
{
    heap_ptr = (void *) heap;
    heap_end = heap_ptr + HEAP_SIZE;
}

/* BEEBS version of malloc.

   This is primarily to reduce library and OS dependencies. Malloc is
   generally not used in embedded code, or if it is, only in well defined
   contexts to pre-allocate a fixed amount of memory. So this simplistic
   implementation is just fine. */

static void *
malloc_beebs (size_t size)
{
    void *new_ptr = heap_ptr;

    if (((heap_ptr + size) > heap_end) || (0 == size))
	return NULL;
    else
	{
	    heap_ptr += size;
	    return new_ptr;
	}
}

/* BEEBS version of free.

   For our simplified version of memory handling, free can just do nothing. */

static void
free_beebs (void *ptr)
{
}

#ifdef CTL_VECTOR
#include "vector.h"

/* Create vector functions for different types.  */
MAKE_VECTOR(int)
MAKE_VECTOR(pair)

/* Container types.  */
typedef ctl_intVector int_container;
typedef ctl_pairVector pair_container;

#define CTL_INIT(type) ctl_##type##VectorInit ()
#define CTL_PUSH(type, vec, val) ctl_ ## type ## VectorPush_Back(vec, val)
#define CTL_DELETE(type, vec, a, b) ctl_ ## type ## VectorDelete(vec, a, b)
#define CTL_POP(type, vec, res) ctl_ ## type ## VectorPop_Back(vec, res)
#define CTL_FREE(type, vec) ctl_ ## type ## VectorFree(vec)

#elif defined CTL_STACK
#include "stack.h"

/* Create stack functions for different types.  */
MAKE_STACK(int)
MAKE_STACK(pair)

/* Container types.  */
typedef ctl_intStack int_container;
typedef ctl_pairStack pair_container;

#define CTL_INIT(type) ctl_ ## type ## StackInit ()
#define CTL_PUSH(type, stk, val) ctl_ ## type ## StackPush (stk, val)
#define CTL_POP(type, stk, res) ctl_ ## type ## StackPop (stk, res)
#define CTL_FREE(type, stk) ctl_ ## type ## StackFree (stk)

/* There's no DELETE for stacks.  */
#define CTL_DELETE(type, vec, a, b) do { } while (0)


#else
#error "Expected CTL_VECTOR or CTL_STACK to be defined"
#endif

static int init;
static int lim;
static int fact;
static int begin;
static int end;
static int end2;

int
benchmark (void)
{
  int_container *v;
  pair_container *v2;

  int cnt=0, i;

  v = CTL_INIT (int);

  for (i = init; i <= lim; ++i)
    CTL_PUSH (int, v, i * fact);

  CTL_DELETE (int, v, begin, end);

  while(v->size > 0)
  {
    int k;

    CTL_POP (int, v, &k);

    cnt += k;
  }

  CTL_FREE (int, v);

  v2 = CTL_INIT (pair);

  for (i = init; i <= lim; ++i)
  {
    pair p = {i, i*i};
    CTL_PUSH (pair, v2, p);
  }

  CTL_DELETE (pair, v2, begin, end2);

  while(v2->size > 0)
  {
    pair k;

    CTL_POP (pair, v2, &k);

    cnt += k.a*k.b;
  }

  CTL_FREE (pair, v2);

  return cnt;
}

void initialise_benchmark() {
  init = 1;
  lim = 100;
  fact = 11;
  begin = 4;
  end = 50;
  end2 = 8;
  init_heap ();
}

int verify_benchmark(int r)
{
#ifdef CTL_VECTOR
  int expected = 25542939;
#elif defined CTL_STACK
  int expected = 25558050;
#else
#error "Expected CTL_VECTOR or CTL_STACK to be defined"
#endif
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
