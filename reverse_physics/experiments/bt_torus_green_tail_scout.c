/*
 * Numerical reconnaissance for a four-dimensional BT Green-tail family.
 *
 * This is deliberately not a certificate.  It solves
 *
 *   -Delta v = f_lambda - mean(f_lambda)
 *
 * on T_L^4 by an exact-symbol radix-two FFT, sets
 * u = v - min(v) + epsilon, and evaluates the complete nonlinear BT
 * residual-gradient quotient.  The source is the continuum critical-bubble
 * density 8 lambda^3/(lambda^2+|x|^2)^3.  Floating-point output is only a
 * guide for selecting or rejecting an analytic family.
 */

#include <complex.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

static void fft(double complex *a, int n, int inverse) {
    for (int i = 1, j = 0; i < n; ++i) {
        int bit = n >> 1;
        for (; j & bit; bit >>= 1) j ^= bit;
        j ^= bit;
        if (i < j) {
            double complex t = a[i];
            a[i] = a[j];
            a[j] = t;
        }
    }
    for (int len = 2; len <= n; len <<= 1) {
        double angle = (inverse ? 2.0 : -2.0) * M_PI / len;
        double complex root = cos(angle) + I * sin(angle);
        for (int i = 0; i < n; i += len) {
            double complex w = 1.0;
            for (int j = 0; j < len / 2; ++j) {
                double complex u = a[i + j];
                double complex v = a[i + j + len / 2] * w;
                a[i + j] = u + v;
                a[i + j + len / 2] = u - v;
                w *= root;
            }
        }
    }
    if (inverse) {
        for (int i = 0; i < n; ++i) a[i] /= n;
    }
}

static size_t index4(int x0, int x1, int x2, int x3, int L) {
    return (((size_t)x0 * L + x1) * L + x2) * L + x3;
}

static void fft4(double complex *data, int L, int inverse) {
    double complex *line = malloc((size_t)L * sizeof(*line));
    if (!line) exit(2);
    for (int axis = 0; axis < 4; ++axis) {
        for (int a = 0; a < L; ++a)
        for (int b = 0; b < L; ++b)
        for (int c = 0; c < L; ++c) {
            for (int t = 0; t < L; ++t) {
                int x[4];
                int q = 0;
                for (int d = 0; d < 4; ++d) {
                    if (d == axis) x[d] = t;
                    else x[d] = (q == 0 ? a : q == 1 ? b : c), ++q;
                }
                line[t] = data[index4(x[0], x[1], x[2], x[3], L)];
            }
            fft(line, L, inverse);
            for (int t = 0; t < L; ++t) {
                int x[4];
                int q = 0;
                for (int d = 0; d < 4; ++d) {
                    if (d == axis) x[d] = t;
                    else x[d] = (q == 0 ? a : q == 1 ? b : c), ++q;
                }
                data[index4(x[0], x[1], x[2], x[3], L)] = line[t];
            }
        }
    }
    free(line);
}

static size_t neighbor(size_t idx, int axis, int step, int L) {
    size_t stride = 1;
    for (int d = 3; d > axis; --d) stride *= (size_t)L;
    int coordinate = (int)((idx / stride) % (size_t)L);
    if (step > 0) return coordinate + 1 < L ? idx + stride : idx - stride * (L - 1);
    return coordinate > 0 ? idx - stride : idx + stride * (L - 1);
}

int main(int argc, char **argv) {
    if (argc != 4) {
        fprintf(stderr, "usage: %s L lambda epsilon\n", argv[0]);
        return 2;
    }
    int L = atoi(argv[1]);
    double lambda = atof(argv[2]);
    double epsilon = atof(argv[3]);
    if (L < 4 || (L & (L - 1)) || lambda <= 0.0 || epsilon <= 0.0) return 2;
    size_t N = (size_t)L * L * L * L;
    double complex *fourier = calloc(N, sizeof(*fourier));
    double *u = malloc(N * sizeof(*u));
    double *r = malloc(N * sizeof(*r));
    double *g = malloc(N * sizeof(*g));
    if (!fourier || !u || !r || !g) return 2;

    long double source_sum = 0.0L;
    for (int x0 = 0; x0 < L; ++x0)
    for (int x1 = 0; x1 < L; ++x1)
    for (int x2 = 0; x2 < L; ++x2)
    for (int x3 = 0; x3 < L; ++x3) {
        int x[4] = {x0, x1, x2, x3};
        double radius2 = 0.0;
        for (int d = 0; d < 4; ++d) {
            int z = x[d] <= L / 2 ? x[d] : x[d] - L;
            radius2 += (double)z * z;
        }
        double denominator = lambda * lambda + radius2;
        double source = 8.0 * lambda * lambda * lambda
                      / (denominator * denominator * denominator);
        size_t idx = index4(x0, x1, x2, x3, L);
        fourier[idx] = source;
        source_sum += source;
    }
    double mean = (double)(source_sum / N);
    for (size_t i = 0; i < N; ++i) fourier[i] -= mean;
    fft4(fourier, L, 0);
    for (int k0 = 0; k0 < L; ++k0)
    for (int k1 = 0; k1 < L; ++k1)
    for (int k2 = 0; k2 < L; ++k2)
    for (int k3 = 0; k3 < L; ++k3) {
        int k[4] = {k0, k1, k2, k3};
        double eigenvalue = 0.0;
        for (int d = 0; d < 4; ++d) {
            double s = sin(M_PI * k[d] / L);
            eigenvalue += 4.0 * s * s;
        }
        size_t idx = index4(k0, k1, k2, k3, L);
        fourier[idx] = eigenvalue == 0.0 ? 0.0 : fourier[idx] / eigenvalue;
    }
    fft4(fourier, L, 1);
    double minimum = creal(fourier[0]);
    for (size_t i = 1; i < N; ++i)
        if (creal(fourier[i]) < minimum) minimum = creal(fourier[i]);
    for (size_t i = 0; i < N; ++i) u[i] = creal(fourier[i]) - minimum + epsilon;

    long double R2 = 0.0L;
    for (size_t i = 0; i < N; ++i) {
        double laplacian = 0.0;
        for (int axis = 0; axis < 4; ++axis)
            laplacian += u[neighbor(i, axis, 1, L)]
                       + u[neighbor(i, axis, -1, L)] - 2.0 * u[i];
        r[i] = laplacian / u[i];
        R2 += (long double)r[i] * r[i];
    }
    long double G2 = 0.0L;
    for (size_t i = 0; i < N; ++i) {
        double value = 0.0;
        for (int axis = 0; axis < 4; ++axis)
        for (int step = -1; step <= 1; step += 2) {
            size_t j = neighbor(i, axis, step, L);
            value += r[j] * u[i] / u[j] - r[i] * u[j] / u[i];
        }
        g[i] = value;
        G2 += (long double)value * value;
    }
    double omega = 4.0 * sin(M_PI / L) * sin(M_PI / L);
    double maximum = u[0];
    for (size_t i = 1; i < N; ++i) if (u[i] > maximum) maximum = u[i];
    printf(
        "{\"L\":%d,\"lambda\":%.17g,\"epsilon\":%.17g,"
        "\"action\":%.17Lg,\"normalized_quotient\":%.17Lg,"
        "\"quotient\":%.17Lg,\"field_contrast\":%.17g,"
        "\"source_mass\":%.17Lg}\\n",
        L, lambda, epsilon, R2 / 2.0L, G2 / R2 / (omega * omega),
        G2 / R2, maximum / epsilon, source_sum
    );
    free(fourier);
    free(u);
    free(r);
    free(g);
    return 0;
}
