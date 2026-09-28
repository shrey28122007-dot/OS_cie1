/* locality.c - row-major vs column-major sum of an N x N int array.
   Compile with -O0 so the compiler does not interchange the loops.
   Usage: ./locality_c [N] [RUNS]   Prints: row_seconds col_seconds sum_row sum_col */
#include <stdio.h>
#include <stdlib.h>
#ifdef _WIN32
#include <windows.h>
#else
#include <time.h>
#endif

static double now(void) {
#ifdef _WIN32
    static LARGE_INTEGER frequency;
    LARGE_INTEGER counter;
    if (frequency.QuadPart == 0) QueryPerformanceFrequency(&frequency);
    QueryPerformanceCounter(&counter);
    return (double)counter.QuadPart / frequency.QuadPart;
#else
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec * 1e-9;
#endif
}

int main(int argc, char **argv) {
    int n = argc > 1 ? atoi(argv[1]) : 4096;
    int runs = argc > 2 ? atoi(argv[2]) : 5;
    int *a = malloc((size_t)n * n * sizeof(int));
    for (size_t i = 0; i < (size_t)n * n; i++) a[i] = 1;

    for (int r = 0; r < runs; r++) {
        long long s1 = 0, s2 = 0;
        double t0 = now();
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) s1 += a[(size_t)i * n + j];   /* row-major */
        double t1 = now();
        for (int j = 0; j < n; j++)
            for (int i = 0; i < n; i++) s2 += a[(size_t)i * n + j];   /* column-major */
        double t2 = now();
        printf("%.6f %.6f %lld %lld\n", t1 - t0, t2 - t1, s1, s2);
    }
    free(a);
    return 0;
}