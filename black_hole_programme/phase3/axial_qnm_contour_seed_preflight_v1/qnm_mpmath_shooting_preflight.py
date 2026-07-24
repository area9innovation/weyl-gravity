#!/usr/bin/env python3
"""UNVALIDATED-NUMERIC arbitrary-precision matched Riccati shooting.

Independent endpoint Frobenius/asymptotic series and mpmath Taylor ODE
transport; no Leaver recurrence is used in the mismatch evaluation.
"""
import json

import mpmath as mp


def conv(a, b):
    out = [mp.mpc(0)]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return out


def polys(kind, w):
    if kind == "horizon":
        a = [0, 1, -4, 6, -4, 1]
        b = [1j*x for x in conv(
            [-1, 3, -3, 1], [-4*w+1j, 4*w-3j]
        )]
        c = [
            16*w*w-4j*w-3,
            -24*w*w+12j*w+3,
            16*w*w-12j*w+3,
            -4*w*w+4j*w-3,
        ]
    else:
        a = [0, 0, 1, -4, 4]
        b = [2j*x for x in conv(
            [-1, 2], [-w, 1j, 4*w-3j]
        )]
        c = [8*w*w-6, -8j*w+18, -16*w*w+16j*w-12]
    return list(map(mp.mpc, a)), list(map(mp.mpc, b)), list(map(mp.mpc, c))


def local_coeffs(kind, w, order):
    poly_a, poly_b, poly_c = polys(kind, w)
    coeff = [mp.mpc(1)]
    for n in range(order):
        target = n+1
        known = mp.mpc(0)
        denom = mp.mpc(0)
        for j, val in enumerate(poly_a):
            k = n-j+2
            if k >= 0:
                fac = k*(k-1)
                if k == target:
                    denom += val*fac
                elif k < len(coeff):
                    known += val*fac*coeff[k]
        for j, val in enumerate(poly_b):
            k = n-j+1
            if k >= 0:
                if k == target:
                    denom += val*k
                elif k < len(coeff):
                    known += val*k*coeff[k]
        for j, val in enumerate(poly_c):
            k = n-j
            if 0 <= k < len(coeff):
                known += val*coeff[k]
        coeff.append(-known/denom)
    return coeff


def horner(coeff, q):
    value = mp.mpc(0)
    derivative = mp.mpc(0)
    for item in reversed(coeff):
        derivative = derivative*q+value
        value = value*q+item
    return value, derivative


def initial(kind, w, endpoint, order):
    coeff = local_coeffs(kind, w, order)
    if kind == "horizon":
        x = 1-2/endpoint
        value, derivative = horner(coeff, x)
        return x*(1-x)**2/2*(2j*w/x+derivative/value)
    z = 1/endpoint
    value, derivative = horner(coeff, z)
    return -z*z*(1-2*z)*(
        1j*w/z**2+2j*w/z+derivative/value
    )


def rhs_r(r, y, w):
    f = 1-2/r
    potential_term = w*w-f*(6/r**2-6/r**3)
    return (-potential_term-y*y)/f


def propagate_forward(start, stop, y0, w, tol):
    solution = mp.odefun(
        lambda r, y: rhs_r(r, y, w),
        start,
        y0,
        tol=tol,
        degree=34,
    )
    return solution(stop)


def propagate_backward(start, stop, y0, w, tol):
    # t=start-r converts backward r integration to forward t integration.
    solution = mp.odefun(
        lambda t, y: -rhs_r(start-t, y, w),
        mp.mpf(0),
        y0,
        tol=tol,
        degree=34,
    )
    return solution(start-stop)


def mismatch(w, eps, outer_radius, horizon_order, infinity_order, match, tol):
    horizon_radius = mp.mpf(2)+eps
    horizon_value = propagate_forward(
        horizon_radius,
        match,
        initial("horizon", w, horizon_radius, horizon_order),
        w,
        tol,
    )
    infinity_value = propagate_backward(
        outer_radius,
        match,
        initial("infinity", w, outer_radius, infinity_order),
        w,
        tol,
    )
    return horizon_value-infinity_value


def main():
    mp.mp.dps = 45
    fixed = {
        "eps": mp.mpf("0.0001"),
        "match": mp.mpf(4),
        "tol": mp.mpf("1e-28"),
    }
    guess_0 = mp.mpc("-0.37367", "0.08896")
    guess_1 = mp.mpc("-0.37368", "0.08897")
    rows = []
    for outer_radius, order in [(30, 24), (40, 34), (45, 38)]:
        config = dict(
            fixed,
            outer_radius=mp.mpf(outer_radius),
            horizon_order=order,
            infinity_order=order,
        )
        root = mp.findroot(
            lambda w: mismatch(w, **config),
            (guess_0, guess_1),
            tol=mp.mpf("1e-20"),
            maxsteps=16,
        )
        rows.append({
            "R": outer_radius,
            "Nh": order,
            "Ni": order,
            "root": mp.nstr(root, 38),
            "mismatch_at_root": mp.nstr(mismatch(root, **config), 20),
        })
        guess_0 = root
        guess_1 = root*(1+mp.mpf("1e-7"))
    print(json.dumps({
        "status": "UNVALIDATED-NUMERIC",
        "method": (
            "45-decimal mpmath Taylor-ODE matched Riccati shooting"
        ),
        "fixed_parameters": {key: str(value) for key, value in fixed.items()},
        "endpoint_convergence_rows": rows,
    }, indent=2))


if __name__ == "__main__":
    main()
