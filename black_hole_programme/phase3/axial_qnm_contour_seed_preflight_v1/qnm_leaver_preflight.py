#!/usr/bin/env python3
"""UNVALIDATED-NUMERIC Leaver preflight for Schwarzschild axial l=2, M=1.

Convention: exp(+i omega t), horizon exp(+i omega r_*),
outgoing infinity exp(-i omega r_*).
"""
import json

import mpmath as mp


def coeffs(n, w):
    alpha = (n + 1) * (n + 1 + 4j * w)
    beta = -2*n*n - 2*n - 16j*w*n + 32*w*w - 8j*w - 3
    gamma = (n - 1) * (n + 1 + 8j*w) - 16*w*w + 8j*w - 3
    return alpha, beta, gamma


def cf(w, depth):
    """Finite backward approximant beta_0-alpha_0 gamma_1/(beta_1-...)."""
    _, tail, _ = coeffs(depth, w)
    for n in range(depth - 1, -1, -1):
        a, b, _ = coeffs(n, w)
        _, _, gnext = coeffs(n + 1, w)
        tail = b - a * gnext / tail
    return tail


def main():
    mp.mp.dps = 90
    guesses = [
        mp.mpc("-0.37367", "0.08896"),
        mp.mpc("0.37367", "0.08896"),
    ]
    rows = []
    for depth in [40, 60, 80, 120, 180, 260, 400]:
        found = []
        for g in guesses:
            try:
                root = mp.findroot(
                    lambda z: cf(z, depth),
                    (g, g*(1+mp.mpf("1e-5"))),
                )
                found.append(mp.nstr(root, 75))
            except Exception as exc:
                found.append(f"FAIL:{type(exc).__name__}:{exc}")
        rows.append({"depth": depth, "roots": found})
    out = {
        "status": "UNVALIDATED-NUMERIC",
        "method": "finite backward Leaver continued fraction",
        "ansatz": (
            "y=exp(-i*w*r)*r^(-2*i*w)*x^(2*i*w)*sum(a_n*x^n), "
            "x=1-2/r"
        ),
        "recurrence": {
            "alpha_n": "(n+1)*(n+1+4*i*w)",
            "beta_n": "-2*n^2-2*n-16*i*w*n+32*w^2-8*i*w-3",
            "gamma_n": (
                "(n-1)*(n+1+8*i*w)-16*w^2+8*i*w-3"
            ),
        },
        "rows": rows,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
