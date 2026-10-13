
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define POLYBENCH_DUMP_TARGET stderr
#define POLYBENCH_RESTRICT
#define POLYBENCH_C99_SELECT(x,y) x
#define POLYBENCH_LOOP_BOUND(x,y) x

#define POLYBENCH_1D(var, dim1, ddim1) var[dim1]
#define POLYBENCH_2D(var, dim1, dim2, ddim1, ddim2) var[dim1][dim2]
#define POLYBENCH_3D(var, dim1, dim2, dim3, ddim1, ddim2, ddim3) var[dim1][dim2][dim3]

#define POLYBENCH_1D_F(var, dim1, ddim1) var[dim1]
#define POLYBENCH_2D_F(var, dim1, dim2, ddim1, ddim2) var[dim1][dim2]
#define POLYBENCH_3D_F(var, dim1, dim2, dim3, ddim1, ddim2, ddim3) var[dim1][dim2][dim3]

#define POLYBENCH_ALLOC_1D_ARRAY(n1, type) (type(*)[n1])polybench_alloc_data(n1, sizeof(type))
#define POLYBENCH_ALLOC_2D_ARRAY(n1, n2, type) (type(*)[n1][n2])polybench_alloc_data((n1)*(n2), sizeof(type))
#define POLYBENCH_ALLOC_3D_ARRAY(n1, n2, n3, type) (type(*)[n1][n2][n3])polybench_alloc_data((n1)*(n2)*(n3), sizeof(type))

#define POLYBENCH_1D_ARRAY_DECL(var, type, dim1, ddim1) \
  type POLYBENCH_1D_F(POLYBENCH_DECL_VAR(var), dim1, ddim1); \
  var = POLYBENCH_ALLOC_1D_ARRAY(dim1, type);
#define POLYBENCH_2D_ARRAY_DECL(var, type, dim1, dim2, ddim1, ddim2) \
  type POLYBENCH_2D_F(POLYBENCH_DECL_VAR(var), dim1, dim2, ddim1, ddim2); \
  var = POLYBENCH_ALLOC_2D_ARRAY(dim1, dim2, type);
#define POLYBENCH_3D_ARRAY_DECL(var, type, dim1, dim2, dim3, ddim1, ddim2, ddim3) \
  type POLYBENCH_3D_F(POLYBENCH_DECL_VAR(var), dim1, dim2, dim3, ddim1, ddim2, ddim3); \
  var = POLYBENCH_ALLOC_3D_ARRAY(dim1, dim2, dim3, type);

#define POLYBENCH_DECL_VAR(var) (*var)
#define POLYBENCH_ARRAY(var) (*var)
#define POLYBENCH_FREE_ARRAY(var) polybench_free_data(var)

static void* polybench_alloc_data(unsigned long long n, int elt_size) {
    return malloc(n * elt_size);
}
static void polybench_free_data(void* ptr) {
    if (ptr) free(ptr);
}

#define polybench_start_instruments
#define polybench_stop_instruments
#define polybench_print_instruments
#define polybench_prevent_dce(func) func
#define POLYBENCH_DUMP_START
#define POLYBENCH_DUMP_BEGIN(s)
#define POLYBENCH_DUMP_END(s)
#define POLYBENCH_DUMP_FINISH

#define MINI_DATASET
/**
 * This version is stamped on May 10, 2016
 *
 * Contact:
 *   Louis-Noel Pouchet <pouchet.ohio-state.edu>
 *   Tomofumi Yuki <tomofumi.yuki.fr>
 *
 * Web address: http://polybench.sourceforge.net
 */
#ifndef _TRMM_H
# define _TRMM_H

/* Default to LARGE_DATASET. */
# if !defined(MINI_DATASET) && !defined(SMALL_DATASET) && !defined(MEDIUM_DATASET) && !defined(LARGE_DATASET) && !defined(EXTRALARGE_DATASET)
#  define LARGE_DATASET
# endif

# if !defined(M) && !defined(N)
/* Define sample dataset sizes. */
#  ifdef MINI_DATASET
#   define M 20
#   define N 30
#  endif

#  ifdef SMALL_DATASET
#   define M 60
#   define N 80
#  endif

#  ifdef MEDIUM_DATASET
#   define M 200
#   define N 240
#  endif

#  ifdef LARGE_DATASET
#   define M 1000
#   define N 1200
#  endif

#  ifdef EXTRALARGE_DATASET
#   define M 2000
#   define N 2600
#  endif


#endif /* !(M N) */

# define _PB_M POLYBENCH_LOOP_BOUND(M,m)
# define _PB_N POLYBENCH_LOOP_BOUND(N,n)


/* Default data type */
# if !defined(DATA_TYPE_IS_INT) && !defined(DATA_TYPE_IS_FLOAT) && !defined(DATA_TYPE_IS_DOUBLE)
#  define DATA_TYPE_IS_DOUBLE
# endif

#ifdef DATA_TYPE_IS_INT
#  define DATA_TYPE int
#  define DATA_PRINTF_MODIFIER "%d "
#endif

#ifdef DATA_TYPE_IS_FLOAT
#  define DATA_TYPE float
#  define DATA_PRINTF_MODIFIER "%0.2f "
#  define SCALAR_VAL(x) x##f
#  define SQRT_FUN(x) sqrtf(x)
#  define EXP_FUN(x) expf(x)
#  define POW_FUN(x,y) powf(x,y)
# endif

#ifdef DATA_TYPE_IS_DOUBLE
#  define DATA_TYPE double
#  define DATA_PRINTF_MODIFIER "%0.2lf "
#  define SCALAR_VAL(x) x
#  define SQRT_FUN(x) sqrt(x)
#  define EXP_FUN(x) exp(x)
#  define POW_FUN(x,y) pow(x,y)
# endif

#endif /* !_TRMM_H */

/**
 * This version is stamped on May 10, 2016
 *
 * Contact:
 *   Louis-Noel Pouchet <pouchet.ohio-state.edu>
 *   Tomofumi Yuki <tomofumi.yuki.fr>
 *
 * Web address: http://polybench.sourceforge.net
 */
/* trmm.c: this file is part of PolyBench/C */

#include <stdio.h>

#include <string.h>
#include <math.h>

/* Include polybench common header. */


/* Include benchmark-specific header. */



/* Array initialization. */
static
void init_array(int m, int n,
		DATA_TYPE *alpha,
		DATA_TYPE POLYBENCH_2D(A,M,M,m,m),
		DATA_TYPE POLYBENCH_2D(B,M,N,m,n))
{
  int i, j;

  *alpha = 1.5;
  for (i = 0; i < m; i++) {
    for (j = 0; j < i; j++) {
      A[i][j] = (DATA_TYPE)((i+j) % m)/m;
    }
    A[i][i] = 1.0;
    for (j = 0; j < n; j++) {
      B[i][j] = (DATA_TYPE)((n+(i-j)) % n)/n;
    }
 }

}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int m, int n,
		 DATA_TYPE POLYBENCH_2D(B,M,N,m,n))
{
  int i, j;

  POLYBENCH_DUMP_START;
  POLYBENCH_DUMP_BEGIN("B");
  for (i = 0; i < m; i++)
    for (j = 0; j < n; j++) {
	if ((i * m + j) % 20 == 0) fprintf (POLYBENCH_DUMP_TARGET, "\n");
	fprintf (POLYBENCH_DUMP_TARGET, DATA_PRINTF_MODIFIER, B[i][j]);
    }
  POLYBENCH_DUMP_END("B");
  POLYBENCH_DUMP_FINISH;
}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
static
void kernel_trmm(int m, int n,
		 DATA_TYPE alpha,
		 DATA_TYPE POLYBENCH_2D(A,M,M,m,m),
		 DATA_TYPE POLYBENCH_2D(B,M,N,m,n))
{
  int i, j, k;

//BLAS parameters
//SIDE   = 'L'
//UPLO   = 'L'
//TRANSA = 'T'
//DIAG   = 'U'
// => Form  B := alpha*A**T*B.
// A is MxM
// B is MxN
#pragma scop
  for (i = 0; i < _PB_M; i++)
     for (j = 0; j < _PB_N; j++) {
        for (k = i+1; k < _PB_M; k++)
           B[i][j] += A[k][i] * B[k][j];
        B[i][j] = alpha * B[i][j];
     }
#pragma endscop

}


int main(int argc, char** argv)
{
  /* Retrieve problem size. */
  int m = M;
  int n = N;

  /* Variable declaration/allocation. */
  DATA_TYPE alpha;
  POLYBENCH_2D_ARRAY_DECL(A,DATA_TYPE,M,M,m,m);
  POLYBENCH_2D_ARRAY_DECL(B,DATA_TYPE,M,N,m,n);

  /* Initialize array(s). */
  init_array (m, n, &alpha, POLYBENCH_ARRAY(A), POLYBENCH_ARRAY(B));

  /* Start timer. */
  polybench_start_instruments;

  /* Run kernel. */
  kernel_trmm (m, n, alpha, POLYBENCH_ARRAY(A), POLYBENCH_ARRAY(B));

  /* Stop and print timer. */
  polybench_stop_instruments;
  polybench_print_instruments;

  /* Prevent dead-code elimination. All live-out data must be printed
     by the function call in argument. */
  polybench_prevent_dce(print_array(m, n, POLYBENCH_ARRAY(B)));

  /* Be clean. */
  POLYBENCH_FREE_ARRAY(A);
  POLYBENCH_FREE_ARRAY(B);

  return 0;
}
