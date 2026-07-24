#!/usr/bin/env python3
"""UNVALIDATED-NUMERIC contour conditioning diagnostic.

Uses the finite-depth Leaver continued fraction only as a local Evans proxy.
It is not a certified Jost normalization and is not an interval computation.
"""
import json

import mpmath as mp


def coeffs(n, w):
    return (
        (n+1)*(n+1+4j*w),
        -2*n*n-2*n-16j*w*n+32*w*w-8j*w-3,
        (n-1)*(n+1+8j*w)-16*w*w+8j*w-3,
    )


def continued_fraction(w, depth=260):
    _, tail, _ = coeffs(depth, w)
    for n in range(depth-1, -1, -1):
        alpha, beta, _ = coeffs(n, w)
        _, _, gamma_next = coeffs(n+1, w)
        tail = beta-alpha*gamma_next/tail
    return tail


def diagnostic(sample_count, center, radius):
    abs_values = []
    abs_log_derivatives = []
    integral = 0j
    arguments = []
    for k in range(sample_count):
        theta = 2*mp.pi*k/sample_count
        w = center+radius*mp.e**(1j*theta)
        value = continued_fraction(w)
        derivative = mp.diff(continued_fraction, w)
        log_derivative = derivative/value
        dw_dtheta = 1j*radius*mp.e**(1j*theta)
        # (1/(2*pi*i))*integral is average(g*dw/dtheta)/i.
        integral += log_derivative*dw_dtheta/sample_count
        abs_values.append(abs(value))
        abs_log_derivatives.append(abs(log_derivative))
        arguments.append(mp.arg(value))
    winding = integral/1j
    unwrapped_total = mp.mpf("0")
    for k in range(sample_count):
        delta = arguments[(k+1) % sample_count]-arguments[k]
        while delta > mp.pi:
            delta -= 2*mp.pi
        while delta <= -mp.pi:
            delta += 2*mp.pi
        unwrapped_total += delta
    return {
        "nsamp": sample_count,
        "min_abs_F": mp.nstr(min(abs_values), 25),
        "max_abs_F": mp.nstr(max(abs_values), 25),
        "min_abs_Fprime_over_F": mp.nstr(
            min(abs_log_derivatives), 25
        ),
        "max_abs_Fprime_over_F": mp.nstr(
            max(abs_log_derivatives), 25
        ),
        "mean_abs_Fprime_over_F": mp.nstr(
            sum(abs_log_derivatives)/sample_count, 25
        ),
        "trapezoid_logderivative_count": [
            mp.nstr(mp.re(winding), 25),
            mp.nstr(mp.im(winding), 25),
        ],
        "sampled_argument_winding": mp.nstr(
            unwrapped_total/(2*mp.pi), 25
        ),
    }


def main():
    mp.mp.dps = 70
    center = mp.mpc(
        "-0.3736716844180418357934920",
        "0.08896231568893569828046093",
    )
    radius = mp.mpf("0.025")
    events = {
        "0": 0,
        "i/4": 0.25j,
        "i/2": 0.5j,
        "i": 1j,
        "positive_Re_partner": mp.mpc(-mp.re(center), mp.im(center)),
    }
    out = {
        "status": "UNVALIDATED-NUMERIC",
        "center": [
            mp.nstr(mp.re(center), 30),
            mp.nstr(mp.im(center), 30),
        ],
        "radius": mp.nstr(radius, 30),
        "imaginary_extent": [
            mp.nstr(mp.im(center)-radius, 30),
            mp.nstr(mp.im(center)+radius, 30),
        ],
        "distance_to_events": {
            key: mp.nstr(abs(center-value), 30)
            for key, value in events.items()
        },
        "clearance_from_event_after_radius": {
            key: mp.nstr(abs(center-value)-radius, 30)
            for key, value in events.items()
        },
        "diagnostics": [
            diagnostic(count, center, radius)
            for count in [32, 64, 128, 256]
        ],
        "b_over_a": {
            "available": False,
            "reason": (
                "No globally normalized intrinsic tangent b has been "
                "implemented; the exact endpoint-normalization and "
                "factor-frame crosswalk remain open."
            ),
            "denominator_only_proxy": (
                "The sampled Leaver F has the reported min |F|, but this "
                "does not bound 1/|a| for a certified Jost normalization."
            ),
        },
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
