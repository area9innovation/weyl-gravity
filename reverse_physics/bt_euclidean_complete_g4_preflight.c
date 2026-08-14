/* Streaming binary64 preflight for the complete free-Gaussian BT g^4 score.

   This is supporting numerical analysis, not an exact certificate.  It uses
   a dependency-free radix-two FFT and O(L^4) memory.  The exact theorem rail
   is bt_euclidean_complete_g4_connected_normalization.py.
*/

#include <complex.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static uint64_t rng_state;

static uint64_t next_u64(void) {
    uint64_t x = rng_state;
    x ^= x >> 12;
    x ^= x << 25;
    x ^= x >> 27;
    rng_state = x;
    return x * UINT64_C(2685821657736338717);
}

static double uniform_open(void) {
    return ((next_u64() >> 11) + 0.5) * 0x1.0p-53;
}

static double normal_sample(void) {
    static int has_spare = 0;
    static double spare;
    if (has_spare) {
        has_spare = 0;
        return spare;
    }
    const double radius = sqrt(-2.0 * log(uniform_open()));
    const double angle = 2.0 * acos(-1.0) * uniform_open();
    spare = radius * sin(angle);
    has_spare = 1;
    return radius * cos(angle);
}

static void fft_line(double complex *data, size_t start, size_t stride,
                     int length, int inverse) {
    for (int i = 1, j = 0; i < length; ++i) {
        int bit = length >> 1;
        for (; j & bit; bit >>= 1) {
            j ^= bit;
        }
        j ^= bit;
        if (i < j) {
            const size_t left = start + (size_t)i * stride;
            const size_t right = start + (size_t)j * stride;
            const double complex temporary = data[left];
            data[left] = data[right];
            data[right] = temporary;
        }
    }
    for (int width = 2; width <= length; width <<= 1) {
        const double angle = (inverse ? 2.0 : -2.0) * acos(-1.0) / width;
        const double complex root = cos(angle) + I * sin(angle);
        for (int base = 0; base < length; base += width) {
            double complex factor = 1.0;
            for (int offset = 0; offset < width / 2; ++offset) {
                const size_t even_index = start + (size_t)(base + offset) * stride;
                const size_t odd_index = start + (size_t)(base + offset + width / 2) * stride;
                const double complex even = data[even_index];
                const double complex odd = factor * data[odd_index];
                data[even_index] = even + odd;
                data[odd_index] = even - odd;
                factor *= root;
            }
        }
    }
    if (inverse) {
        for (int i = 0; i < length; ++i) {
            data[start + (size_t)i * stride] /= length;
        }
    }
}

static void fft4(double complex *data, int length, int inverse) {
    const size_t volume = (size_t)length * length * length * length;
    size_t stride = 1;
    for (int axis = 0; axis < 4; ++axis) {
        const size_t block = stride * (size_t)length;
        for (size_t outer = 0; outer < volume; outer += block) {
            for (size_t inner = 0; inner < stride; ++inner) {
                fft_line(data, outer + inner, stride, length, inverse);
            }
        }
        stride *= (size_t)length;
    }
}

static size_t neighbor(size_t index, size_t stride, int length, int shift) {
    const int coordinate = (int)((index / stride) % (size_t)length);
    if (shift > 0) {
        return coordinate + 1 == length ? index - (size_t)(length - 1) * stride
                                        : index + stride;
    }
    return coordinate == 0 ? index + (size_t)(length - 1) * stride
                           : index - stride;
}

typedef struct {
    double a;
    double b;
    double c;
    double w1;
    double w2;
    double r0;
} coefficients;

static coefficients score_coefficients(double complex *field, int length) {
    const size_t volume = (size_t)length * length * length * length;
    const double momentum = 2.0 * acos(-1.0) / length;
    const double omega = 4.0 * sin(0.5 * momentum) * sin(0.5 * momentum);
    const double variance = 2.0 / (volume * omega * omega);
    double projection = 0.0;
    double norm = 0.0;
    for (size_t index = 0; index < volume; ++index) {
        const int x0 = (int)(index % (size_t)length);
        const double h = cos(momentum * x0);
        projection += creal(field[index]) * h;
        norm += h * h;
    }
    const double fiber = projection / norm;
    for (size_t index = 0; index < volume; ++index) {
        const int x0 = (int)(index % (size_t)length);
        field[index] = creal(field[index]) - fiber * cos(momentum * x0);
    }

    double alpha0 = 0.0, alpha1 = 0.0, alpha2 = 0.0, alpha3 = 0.0;
    double beta0 = 0.0, beta1 = 0.0, beta2 = 0.0, beta3 = 0.0, beta4 = 0.0;
    double cubic_score = 0.0;
    for (size_t index = 0; index < volume; ++index) {
        const int x0 = (int)(index % (size_t)length);
        const double h = cos(momentum * x0);
        double a0 = 0.0, a1 = 0.0;
        double b0 = 0.0, b1 = 0.0, b2 = 0.0;
        double c0 = 0.0, c1 = 0.0, c2 = 0.0, c3 = 0.0;
        double d0 = 0.0, d1 = 0.0;
        size_t stride = 1;
        for (int axis = 0; axis < 4; ++axis) {
            for (int shift = -1; shift <= 1; shift += 2) {
                const size_t other = neighbor(index, stride, length, shift);
                const int other_x0 = (int)(other % (size_t)length);
                const double y = creal(field[other]) - creal(field[index]);
                const double e = cos(momentum * other_x0) - h;
                const double y2 = y * y;
                const double e2 = e * e;
                a0 += y;
                a1 += e;
                b0 += y2;
                b1 += y * e;
                b2 += e2;
                c0 += y2 * y;
                c1 += y2 * e;
                c2 += y * e2;
                c3 += e2 * e;
                d0 += y2 * y2;
                d1 += y2 * y * e;
            }
            stride *= (size_t)length;
        }
        alpha0 += 0.5 * a0 * b0;
        alpha1 += 0.5 * (a1 * b0 + 2.0 * a0 * b1);
        alpha2 += 0.5 * (a0 * b2 + 2.0 * a1 * b1);
        alpha3 += 0.5 * a1 * b2;
        beta0 += a0 * c0 / 6.0 + b0 * b0 / 8.0;
        beta1 += (a1 * c0 + 3.0 * a0 * c1) / 6.0 + b0 * b1 / 2.0;
        beta2 += (3.0 * a1 * c1 + 3.0 * a0 * c2) / 6.0
                 + b1 * b1 / 2.0 + b0 * b2 / 4.0;
        beta3 += (3.0 * a1 * c2 + a0 * c3) / 6.0 + b1 * b2 / 2.0;
        beta4 += a1 * c3 / 6.0 + b2 * b2 / 8.0;
        cubic_score += (a1 * d0 + 4.0 * a0 * d1) / 24.0
                       + (2.0 * b1 * c0 + 3.0 * b0 * c1) / 12.0;
    }
    const double w1 = alpha0 + variance * alpha2;
    const double var_s1 = variance * alpha1 * alpha1
        + variance * variance * (2.0 * alpha2 * alpha2 + 6.0 * alpha1 * alpha3)
        + 15.0 * variance * variance * variance * alpha3 * alpha3;
    const double w2 = beta0 + variance * beta2
                      + 3.0 * variance * variance * beta4 - 0.5 * var_s1;
    coefficients result = {
        alpha1, beta1, cubic_score, w1, w2, 0.5 * w1 * w1 - w2
    };
    return result;
}

static coefficients one_sample(double complex *data, int length) {
    const size_t volume = (size_t)length * length * length * length;
    double mean = 0.0;
    for (size_t index = 0; index < volume; ++index) {
        const double value = normal_sample();
        data[index] = value;
        mean += value;
    }
    mean /= volume;
    for (size_t index = 0; index < volume; ++index) {
        data[index] -= mean;
    }
    fft4(data, length, 0);
    const double pi = acos(-1.0);
    for (size_t index = 0; index < volume; ++index) {
        size_t rest = index;
        double omega = 0.0;
        for (int axis = 0; axis < 4; ++axis) {
            const int coordinate = (int)(rest % (size_t)length);
            rest /= (size_t)length;
            const double sine = sin(pi * coordinate / length);
            omega += 4.0 * sine * sine;
        }
        data[index] = index == 0 ? 0.0 : data[index] / omega;
    }
    fft4(data, length, 1);
    return score_coefficients(data, length);
}

int main(int argc, char **argv) {
    if (argc != 4) {
        fprintf(stderr, "usage: %s LENGTH SAMPLES SEED\n", argv[0]);
        return 2;
    }
    const int length = atoi(argv[1]);
    const int samples = atoi(argv[2]);
    const uint64_t seed = (uint64_t)strtoull(argv[3], NULL, 10);
    rng_state = seed;
    if (length < 4 || (length & (length - 1)) || samples < 2 || rng_state == 0) {
        fprintf(stderr, "length must be a power of two >=4; samples>=2; seed!=0\n");
        return 2;
    }
    const size_t volume = (size_t)length * length * length * length;
    double complex *data = calloc(volume, sizeof(*data));
    if (!data) {
        perror("calloc");
        return 1;
    }

    /* Variables are Y, A^2, R0, D^2, B^2.  Keep the complete second-moment
       matrix so the delta-method error of E[Y]-E[A^2]E[R0] is reproducible. */
    long double means[5] = {0.0L, 0.0L, 0.0L, 0.0L, 0.0L};
    long double centered_products[5][5] = {{0.0L}};
    for (int sample = 0; sample < samples; ++sample) {
        const coefficients value = one_sample(data, length);
        const double a2 = value.a * value.a;
        const double y = value.b * value.b + 2.0 * value.a * value.c
                         - 2.0 * value.a * value.b * value.w1 + a2 * value.r0;
        const double d = value.b - 0.5 * value.w1 * value.a;
        const double row[5] = {y, a2, value.r0, d * d, value.b * value.b};
        long double delta[5], updated_delta[5];
        for (int i = 0; i < 5; ++i) {
            delta[i] = (long double)row[i] - means[i];
            means[i] += delta[i] / (sample + 1);
            updated_delta[i] = (long double)row[i] - means[i];
        }
        for (int i = 0; i < 5; ++i) {
            for (int j = 0; j < 5; ++j) {
                centered_products[i][j] += delta[i] * updated_delta[j];
            }
        }
    }
    long double covariance[5][5];
    for (int i = 0; i < 5; ++i) {
        for (int j = 0; j < 5; ++j) {
            covariance[i][j] = centered_products[i][j] / (samples - 1);
        }
    }
    const long double m4 = means[0] - means[1] * means[2];
    const long double gradient[3] = {1.0L, -means[2], -means[1]};
    long double influence_variance = 0.0L;
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            influence_variance += gradient[i] * covariance[i][j] * gradient[j];
        }
    }
    const long double standard_error = sqrtl(fmaxl(0.0L, influence_variance) / samples);
    const double omega = 4.0 * sin(acos(-1.0) / length) * sin(acos(-1.0) / length);
    const double scale = volume * omega;
    printf("{\"length\":%d,\"volume\":%zu,\"samples\":%d,"
           "\"seed\":%llu,\"z2\":%.17Lg,\"A2\":%.17Lg,"
           "\"B2\":%.17Lg,\"D2\":%.17Lg,\"cross\":%.17Lg,\"M4\":%.17Lg,"
           "\"M4_standard_error\":%.17Lg,\"M4_over_N_omega\":%.17Lg,"
           "\"standard_error_over_N_omega\":%.17Lg,"
           "\"M4_over_N_omega2\":%.17Lg}\n",
           length, volume, samples, (unsigned long long)seed,
           means[2], means[1], means[4], means[3], m4 - means[3], m4, standard_error,
           m4 / (long double)scale, standard_error / (long double)scale,
           m4 / ((long double)scale * omega));
    free(data);
    return 0;
}
