/* Binary64 preflight for the free-Gaussian quartic BT zero-fiber score.

   This is supporting numerical analysis, not an exact certificate.  It uses
   a dependency-free radix-two FFT and streams samples with O(L^4) memory.
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
            const double complex tmp = data[left];
            data[left] = data[right];
            data[right] = tmp;
        }
    }
    for (int width = 2; width <= length; width <<= 1) {
        const double angle = (inverse ? 2.0 : -2.0) * acos(-1.0) / width;
        const double complex root = cos(angle) + I * sin(angle);
        for (int base = 0; base < length; base += width) {
            double complex factor = 1.0;
            for (int offset = 0; offset < width / 2; ++offset) {
                const size_t even_index =
                    start + (size_t)(base + offset) * stride;
                const size_t odd_index =
                    start + (size_t)(base + offset + width / 2) * stride;
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

static double quartic_score(double complex *field, int length) {
    const size_t volume = (size_t)length * length * length * length;
    const double momentum = 2.0 * acos(-1.0) / length;
    const double omega = 4.0 * sin(0.5 * momentum) * sin(0.5 * momentum);
    double projection = 0.0;
    double norm = 0.0;
    for (size_t index = 0; index < volume; ++index) {
        const int x0 = (int)(index % (size_t)length);
        const double h = cos(momentum * x0);
        projection += creal(field[index]) * h;
        norm += h * h;
    }
    const double coefficient = projection / norm;
    for (size_t index = 0; index < volume; ++index) {
        const int x0 = (int)(index % (size_t)length);
        field[index] = creal(field[index]) - coefficient * cos(momentum * x0);
    }

    double score = 0.0;
    for (size_t index = 0; index < volume; ++index) {
        const int x0 = (int)(index % (size_t)length);
        const double h = cos(momentum * x0);
        double a = 0.0, b = 0.0, c = 0.0, db = 0.0, dc = 0.0;
        size_t stride = 1;
        for (int axis = 0; axis < 4; ++axis) {
            for (int shift = -1; shift <= 1; shift += 2) {
                const size_t other = neighbor(index, stride, length, shift);
                const double difference = creal(field[other]) - creal(field[index]);
                const int other_x0 = (int)(other % (size_t)length);
                const double dh = cos(momentum * other_x0) - h;
                a += difference;
                b += difference * difference;
                c += difference * difference * difference;
                db += 2.0 * difference * dh;
                dc += 3.0 * difference * difference * dh;
            }
            stride *= (size_t)length;
        }
        const double da = -omega * h;
        score += (da * c + a * dc) / 6.0 + b * db / 4.0;
    }
    return score;
}

static double one_sample(double complex *data, int length) {
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
    return quartic_score(data, length);
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
    double mean = 0.0, m2 = 0.0;
    for (int sample = 1; sample <= samples; ++sample) {
        const double value = one_sample(data, length);
        const double delta = value - mean;
        mean += delta / sample;
        m2 += delta * (value - mean);
    }
    const double variance = m2 / (samples - 1);
    const double omega = 4.0 * sin(acos(-1.0) / length) *
                         sin(acos(-1.0) / length);
    const double normalized = variance / (volume * omega * omega);
    printf("{\"length\":%d,\"volume\":%zu,\"samples\":%d,"
           "\"seed\":%llu,\"mean\":%.17g,\"variance\":%.17g,"
           "\"variance_over_N_omega2\":%.17g,"
           "\"ratio_over_L2\":%.17g}\n",
           length, volume, samples, (unsigned long long)seed, mean,
           variance, normalized, normalized / ((double)length * length));
    free(data);
    return 0;
}
