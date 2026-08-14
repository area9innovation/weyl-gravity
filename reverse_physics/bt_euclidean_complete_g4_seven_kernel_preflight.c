/* Deterministic binary64 preflight for the seven generic-L BT g^4 kernels.

   The certified affine atlas has fourteen unfactorized entries.  Global
   momentum inversion pairs them into the seven expressions below.  This
   evaluator is supporting numerical analysis only: its purpose is to locate
   the hard/one-soft/all-soft asymptotic carriers before an analytic bound.
   It uses O(L^4) memory and streams the O(L^8) pair sum.
*/

#include <complex.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int x[4];
} momentum;

static int length;
static size_t volume;
static double *omega_table;
static double complex *edge_phase;

static size_t encode(momentum k) {
    size_t index = 0;
    size_t stride = 1;
    for (int axis = 0; axis < 4; ++axis) {
        int value = k.x[axis] % length;
        if (value < 0) {
            value += length;
        }
        index += (size_t)value * stride;
        stride *= (size_t)length;
    }
    return index;
}

static momentum decode(size_t index) {
    momentum result;
    for (int axis = 0; axis < 4; ++axis) {
        result.x[axis] = (int)(index % (size_t)length);
        index /= (size_t)length;
    }
    return result;
}

static momentum add(momentum left, momentum right) {
    momentum result;
    for (int axis = 0; axis < 4; ++axis) {
        result.x[axis] = (left.x[axis] + right.x[axis]) % length;
    }
    return result;
}

static momentum neg(momentum value) {
    momentum result;
    for (int axis = 0; axis < 4; ++axis) {
        result.x[axis] = value.x[axis] ? length - value.x[axis] : 0;
    }
    return result;
}

static double omega(momentum value) {
    return omega_table[encode(value)];
}

static double propagator(momentum value) {
    const double w = omega(value);
    return w == 0.0 ? 0.0 : 1.0 / (w * w);
}

static double complex b_symbol(const momentum *values, int count) {
    double complex result = 0.0;
    for (int axis = 0; axis < 4; ++axis) {
        for (int sign_index = 0; sign_index < 2; ++sign_index) {
            double complex product = 1.0;
            for (int item = 0; item < count; ++item) {
                const int coordinate = values[item].x[axis] % length;
                const size_t index =
                    ((size_t)sign_index * (size_t)length) +
                    (size_t)coordinate;
                product *= edge_phase[index];
            }
            result += product;
        }
    }
    return result;
}

static double kernel3(momentum a, momentum b, momentum c) {
    const double wa = omega(a);
    const double wb = omega(b);
    const double wc = omega(c);
    return (wa * wa + wb * wb + wc * wc
            - 2.0 * (wa * wb + wa * wc + wb * wc)) / 6.0;
}

static double kernel4(momentum a, momentum b, momentum c, momentum d) {
    const momentum values[4] = {a, b, c, d};
    double complex result = 0.0;
    for (int singled = 0; singled < 4; ++singled) {
        momentum rest[3];
        int cursor = 0;
        for (int item = 0; item < 4; ++item) {
            if (item != singled) {
                rest[cursor++] = values[item];
            }
        }
        result += b_symbol(&values[singled], 1) * b_symbol(rest, 3);
    }
    const int pairs[3][2] = {{0, 1}, {0, 2}, {0, 3}};
    for (int pairing = 0; pairing < 3; ++pairing) {
        momentum left[2] = {
            values[pairs[pairing][0]], values[pairs[pairing][1]]
        };
        momentum right[2];
        int cursor = 0;
        for (int item = 0; item < 4; ++item) {
            if (item != pairs[pairing][0] && item != pairs[pairing][1]) {
                right[cursor++] = values[item];
            }
        }
        result += b_symbol(left, 2) * b_symbol(right, 2);
    }
    return creal(result) / 24.0;
}

static double kernel5(momentum a, momentum b, momentum c, momentum d,
                      momentum e) {
    const momentum values[5] = {a, b, c, d, e};
    double complex result = 0.0;
    for (int singled = 0; singled < 5; ++singled) {
        momentum rest[4];
        int cursor = 0;
        for (int item = 0; item < 5; ++item) {
            if (item != singled) {
                rest[cursor++] = values[item];
            }
        }
        result += b_symbol(&values[singled], 1) * b_symbol(rest, 4);
    }
    for (int left0 = 0; left0 < 5; ++left0) {
        for (int left1 = left0 + 1; left1 < 5; ++left1) {
            momentum left[2] = {values[left0], values[left1]};
            momentum right[3];
            int cursor = 0;
            for (int item = 0; item < 5; ++item) {
                if (item != left0 && item != left1) {
                    right[cursor++] = values[item];
                }
            }
            result += b_symbol(left, 2) * b_symbol(right, 3);
        }
    }
    return creal(result) / 120.0;
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "usage: %s LENGTH\n", argv[0]);
        return 2;
    }
    length = atoi(argv[1]);
    if (length < 5) {
        fprintf(stderr, "LENGTH must be at least 5\n");
        return 2;
    }
    volume = 1;
    for (int axis = 0; axis < 4; ++axis) {
        if (volume > SIZE_MAX / (size_t)length) {
            fprintf(stderr, "volume overflow\n");
            return 2;
        }
        volume *= (size_t)length;
    }
    omega_table = calloc(volume, sizeof(*omega_table));
    edge_phase = calloc((size_t)2 * (size_t)length, sizeof(*edge_phase));
    if (!omega_table || !edge_phase) {
        perror("calloc");
        free(omega_table);
        free(edge_phase);
        return 1;
    }
    const double pi = acos(-1.0);
    for (int sign_index = 0; sign_index < 2; ++sign_index) {
        const int sign = sign_index ? 1 : -1;
        for (int coordinate = 0; coordinate < length; ++coordinate) {
            const double angle =
                sign * 2.0 * pi * (double)coordinate / (double)length;
            edge_phase[(size_t)sign_index * (size_t)length
                       + (size_t)coordinate] =
                cos(angle) + I * sin(angle) - 1.0;
        }
    }
    for (size_t index = 0; index < volume; ++index) {
        const momentum value = decode(index);
        double w = 0.0;
        for (int axis = 0; axis < 4; ++axis) {
            const double sine =
                sin(pi * (double)value.x[axis] / (double)length);
            w += 4.0 * sine * sine;
        }
        omega_table[index] = w;
    }

    const momentum p = {{1, 0, 0, 0}};
    const momentum minus_p = neg(p);
    long double totals[7] = {0.0L};
    for (size_t q_index = 0; q_index < volume; ++q_index) {
        const momentum q = decode(q_index);
        const momentum minus_q = neg(q);
        const momentum q_plus_p = add(q, p);
        for (size_t r_index = 0; r_index < volume; ++r_index) {
            const momentum r = decode(r_index);
            const momentum minus_r = neg(r);
            const momentum s = add(q, r);
            const momentum minus_s = neg(s);
            const momentum s_plus_p = add(s, p);
            const momentum minus_s_minus_p = neg(s_plus_p);
            const momentum r_minus_p = add(r, minus_p);
            const momentum minus_r_plus_p = neg(r_minus_p);

            const double gq = propagator(q);
            const double gr = propagator(r);
            const double gs = propagator(s);
            const double gqp = propagator(q_plus_p);
            const double gsp = propagator(s_plus_p);
            const double grm = propagator(r_minus_p);

            const double a0 = kernel3(minus_s, r, q);
            const double ap_s = kernel3(minus_s_minus_p, p, s);
            const double am_s = kernel3(minus_s, minus_p, s_plus_p);
            const double ap_q = kernel3(neg(q_plus_p), p, q);
            const double am_q = kernel3(minus_q, minus_p, q_plus_p);

            totals[0] += 324.0L * ap_s * am_s * a0 * a0
                * gr * gq * gs * gs * gsp;

            totals[1] += 324.0L
                * kernel3(minus_s_minus_p, r, q_plus_p) * am_s
                * ap_q * a0 * gr * gq * gqp * gs * gsp;

            totals[2] += -432.0L * am_s * a0
                * kernel4(minus_s_minus_p, p, r, q)
                * gr * gq * gs * gsp;

            totals[3] += -216.0L * ap_q * am_q
                * kernel4(minus_q, minus_r, r, q)
                * gr * gq * gq * gqp;

            totals[4] += -108.0L * ap_q
                * kernel3(minus_r_plus_p, minus_p, r)
                * kernel4(minus_q, minus_r, r_minus_p, q_plus_p)
                * grm * gr * gq * gqp;

            totals[5] += 180.0L * ap_q
                * kernel5(minus_q, minus_r, minus_p, r, q_plus_p)
                * gr * gq * gqp;

            const double quartic =
                kernel4(minus_s_minus_p, p, r, q);
            totals[6] += 48.0L * quartic * quartic * gr * gq * gsp;
        }
    }
    long double total = 0.0L;
    for (int kernel = 0; kernel < 7; ++kernel) {
        totals[kernel] /= (long double)volume;
        total += totals[kernel];
    }
    const double omega_p = omega(p);
    printf("{\"length\":%d,\"volume\":%zu,\"omega_p\":%.17g,"
           "\"kernels\":[", length, volume, omega_p);
    for (int kernel = 0; kernel < 7; ++kernel) {
        printf("%s%.17Lg", kernel ? "," : "", totals[kernel]);
    }
    printf("],\"sum\":%.17Lg,\"sum_over_N_omega_p\":%.17Lg}\n",
           total, total / ((long double)volume * omega_p));
    free(omega_table);
    free(edge_phase);
    return 0;
}
