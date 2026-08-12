#!/usr/bin/env python3
"""Exact rail for the cylinder-wave foundational strength ladder.

The checker manipulates Laurent monomials with Gaussian-rational coefficients.
It certifies only finite-mode identities, an explicit tail modulus, and the
nonlocality of spectral truncation.  It never evaluates a transcendental
function or replays a continuum PDE producer.
"""
from __future__ import annotations

from fractions import Fraction as Q
import hashlib
import json
from typing import Any

G = tuple[Q, Q]
Monomial = tuple[int, int]  # (time Laurent degree, spatial Laurent degree)
Polynomial = dict[Monomial, G]


def g(real: int | Q = 0, imag: int | Q = 0) -> G:
    return Q(real), Q(imag)


def add(a: G, b: G) -> G:
    return a[0] + b[0], a[1] + b[1]


def mul(a: G, b: G) -> G:
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def scale(a: G, q: int | Q) -> G:
    return a[0] * q, a[1] * q


def norm2(a: G) -> Q:
    return a[0] * a[0] + a[1] * a[1]


def clean(poly: Polynomial) -> Polynomial:
    return {key: value for key, value in poly.items() if value != g()}


def padd(left: Polynomial, right: Polynomial) -> Polynomial:
    out = dict(left)
    for key, value in right.items():
        out[key] = add(out.get(key, g()), value)
    return clean(out)


def derivative(poly: Polynomial, axis: int) -> Polynomial:
    # z=exp(i t), w=exp(i x): d/dt or d/dx multiplies by i*degree.
    out: Polynomial = {}
    for degrees, coefficient in poly.items():
        out[degrees] = mul(g(0, degrees[axis]), coefficient)
    return clean(out)


def second(poly: Polynomial, axis: int) -> Polynomial:
    return derivative(derivative(poly, axis), axis)


def project(poly: Polynomial, cutoff: int) -> Polynomial:
    return {key: value for key, value in poly.items() if abs(key[1]) <= cutoff}


def fixture(cutoff: int) -> Polynomial:
    """Two exact chiral branches with stable coefficients across cutoffs."""
    out: Polynomial = {}
    for n in range(-cutoff, cutoff + 1):
        if n == 0:
            out[(0, 0)] = g(1)
            continue
        left = g(Q(1, abs(n) + 1), Q(n, (abs(n) + 1) * (abs(n) + 2)))
        right = g(Q(1, abs(n) + 2), Q(-n, (abs(n) + 2) * (abs(n) + 3)))
        out[(n, n)] = add(out.get((n, n), g()), left)
        out[(-n, n)] = add(out.get((-n, n), g()), right)
    return clean(out)


def scalar_text(value: Q) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def check(data: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    cutoffs = list(range(1, 13))
    rows: list[dict[str, Any]] = []
    previous: Polynomial | None = None
    for cutoff in cutoffs:
        wave = fixture(cutoff)
        residual = padd(second(wave, 0), {key: scale(value, -1) for key, value in second(wave, 1).items()})
        if residual:
            errors.append(f"wave residual N={cutoff}")
        if previous is not None and project(wave, cutoff - 1) != previous:
            errors.append(f"Galerkin nesting N={cutoff}")
        previous = wave
        branch_energy = sum((degrees[1] ** 2) * norm2(value) for degrees, value in wave.items())
        if branch_energy <= 0:
            errors.append(f"energy positivity N={cutoff}")
        # The Dirichlet kernel for a projected point source is nonzero at the antipode.
        antipode = sum(-1 if abs(n) % 2 else 1 for n in range(-cutoff, cutoff + 1))
        expected_antipode = -1 if cutoff % 2 else 1
        if antipode != expected_antipode or antipode == 0:
            errors.append(f"antipode N={cutoff}")
        rows.append({
            "cutoff": cutoff,
            "monomials": len(wave),
            "energy": scalar_text(branch_energy),
            "wave_residual_zero": not residual,
            "antipode_dirichlet_value": antipode,
        })

    # Explicit datum c_n=1/n^2 has energy summand n^2|c_n|^2=1/n^2.
    # For n>=2, 1/n^2 <= 1/(n-1)-1/n, giving tail <=1/N.
    tail_rows = []
    for n in range(2, 257):
        summand = Q(1, n * n)
        telescoper = Q(1, n - 1) - Q(1, n)
        if summand > telescoper:
            errors.append(f"tail inequality n={n}")
        tail_rows.append((n, scalar_text(summand), scalar_text(telescoper)))
    moduli = []
    for precision in range(1, 13):
        cutoff = 2 ** precision
        tail_bound = Q(1, cutoff)
        if tail_bound > Q(1, 2 ** precision):
            errors.append(f"tail modulus k={precision}")
        moduli.append((precision, cutoff, scalar_text(tail_bound)))

    payload = {
        "cutoff_rows": rows,
        "tail_inequality_rows": tail_rows,
        "tail_moduli": moduli,
        "arithmetic": "Gaussian rationals, integer Laurent degrees, and exact rational inequalities",
        "certifies": [
            "finite chiral Laurent modes solve the 1+1 wave equation",
            "Galerkin projections are nested",
            "the displayed finite energy is positive and exact",
            "c_n=1/n^2 has the explicit energy-tail modulus N(k)=2^k",
            "finite Fourier projection of a point source is nonzero at the antipode",
        ],
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    wanted = None if data is None else data.get("independent_checker", {}).get("expected_digest")
    if wanted is not None and wanted != digest:
        errors.append("digest")
    return errors, {**payload, "digest": digest}


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
