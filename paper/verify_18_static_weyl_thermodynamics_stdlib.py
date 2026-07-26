#!/usr/bin/env python3
"""Independent exact algebra rail for Paper 18.

This verifier deliberately uses only the Python standard library.  It
implements a tiny sparse Laurent-polynomial ring over ``fractions.Fraction``
and checks the load-bearing charge, quotient, discriminant, and horizon
identities coefficientwise.  It does not import SymPy or any programme
producer.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_RECEIPT = ROOT / "reports" / "PAPER18_STDLIB_ALGEBRA_RECEIPT.json"
VARS = ("beta", "gamma", "k", "r")
NVAR = len(VARS)


def _exp(i: int, power: int = 1) -> tuple[int, ...]:
    row = [0] * NVAR
    row[i] = power
    return tuple(row)


@dataclass(frozen=True)
class Laurent:
    """Sparse Laurent polynomial with exact rational coefficients."""

    terms: dict[tuple[int, ...], Fraction]

    def __post_init__(self) -> None:
        clean = {
            tuple(e): Fraction(c)
            for e, c in self.terms.items()
            if Fraction(c) != 0
        }
        if any(len(e) != NVAR for e in clean):
            raise ValueError("wrong exponent-vector length")
        object.__setattr__(self, "terms", clean)

    @staticmethod
    def coerce(value: int | Fraction | "Laurent") -> "Laurent":
        if isinstance(value, Laurent):
            return value
        value = Fraction(value)
        return Laurent({(0,) * NVAR: value}) if value else Laurent({})

    def __add__(self, other: int | Fraction | "Laurent") -> "Laurent":
        other = Laurent.coerce(other)
        out = dict(self.terms)
        for e, c in other.terms.items():
            out[e] = out.get(e, Fraction(0)) + c
        return Laurent(out)

    __radd__ = __add__

    def __neg__(self) -> "Laurent":
        return Laurent({e: -c for e, c in self.terms.items()})

    def __sub__(self, other: int | Fraction | "Laurent") -> "Laurent":
        return self + (-Laurent.coerce(other))

    def __rsub__(self, other: int | Fraction | "Laurent") -> "Laurent":
        return Laurent.coerce(other) - self

    def __mul__(self, other: int | Fraction | "Laurent") -> "Laurent":
        other = Laurent.coerce(other)
        out: dict[tuple[int, ...], Fraction] = {}
        for e1, c1 in self.terms.items():
            for e2, c2 in other.terms.items():
                e = tuple(a + b for a, b in zip(e1, e2))
                out[e] = out.get(e, Fraction(0)) + c1 * c2
        return Laurent(out)

    __rmul__ = __mul__

    def __pow__(self, power: int) -> "Laurent":
        if power < 0:
            if len(self.terms) != 1:
                raise ValueError("negative powers require a monomial")
            (e, c), = self.terms.items()
            return Laurent({tuple(power * x for x in e): c**power})
        out = Laurent.coerce(1)
        base = self
        n = power
        while n:
            if n & 1:
                out = out * base
            base = base * base
            n >>= 1
        return out

    def diff(self, variable: int) -> "Laurent":
        out: dict[tuple[int, ...], Fraction] = {}
        for e, c in self.terms.items():
            if e[variable] == 0:
                continue
            ee = list(e)
            factor = ee[variable]
            ee[variable] -= 1
            key = tuple(ee)
            out[key] = out.get(key, Fraction(0)) + c * factor
        return Laurent(out)

    def is_zero(self) -> bool:
        return not self.terms


ONE = Laurent.coerce(1)
BETA = Laurent({_exp(0): Fraction(1)})
GAMMA = Laurent({_exp(1): Fraction(1)})
K = Laurent({_exp(2): Fraction(1)})
R = Laurent({_exp(3): Fraction(1)})


def require_zero(expr: Laurent, label: str, checks: list[str]) -> None:
    if not expr.is_zero():
        terms = sorted(expr.terms.items())
        raise AssertionError(f"{label}: nonzero Laurent coefficients {terms[:8]}")
    checks.append(label)


def directional(expr: Laurent, vector: Iterable[Laurent]) -> Laurent:
    return sum((component * expr.diff(i) for i, component in enumerate(vector)), Laurent.coerce(0))


def discriminant_cubic(a: Laurent, b: Laurent, c: Laurent, d: Laurent) -> Laurent:
    return (
        b**2 * c**2
        - 4 * a * c**3
        - 4 * b**3 * d
        - 27 * a**2 * d**2
        + 18 * a * b * c * d
    )


def verify() -> list[str]:
    checks: list[str] = []
    beta, gamma, k, r = BETA, GAMMA, K, R
    u = beta * (2 - 3 * beta * gamma)
    w = 1 - 3 * beta * gamma
    d1 = 27 * beta**2 * k - 3 * beta * gamma - 1
    d2 = (
        9 * beta**2 * gamma**2 * k
        - beta * gamma**3
        - 12 * beta * gamma * k
        + gamma**2
        + 4 * k
    )
    h = -beta**2 * d2
    f = (
        12 * beta * gamma * k - gamma**2 - 4 * k,
        beta * (6 * beta * k - gamma),
        -beta * (2 - 3 * beta * gamma),
    )

    for i, name in enumerate(("beta", "gamma", "k")):
        require_zero(h.diff(i) - u * f[i], f"dH=uF ({name})", checks)
    for i, j, name in ((0, 1, "beta,gamma"), (0, 2, "beta,k"), (1, 2, "gamma,k")):
        require_zero(
            (u * f[j]).diff(i) - (u * f[i]).diff(j),
            f"d(uF)=0 ({name})",
            checks,
        )

    xc = (-3 * beta**2, 6 * beta * gamma - 2, gamma, Laurent.coerce(0))
    xl = (-beta, gamma, 2 * k, Laurent.coerce(0))
    require_zero(directional(u, xc), "X_c(u)=0", checks)
    require_zero(directional(u, xl) + u, "X_lambda(u)=-u", checks)
    require_zero(sum((u * f[i] * xc[i] for i in range(3)), Laurent.coerce(0)), "uF horizontal under X_c", checks)
    require_zero(sum((u * f[i] * xl[i] for i in range(3)), Laurent.coerce(0)), "uF horizontal under X_lambda", checks)

    disc = discriminant_cubic(-u, w, gamma, -k)
    jinv = u**2 * disc
    require_zero(jinv + u**2 * d1 * d2, "J=-u^2 D1 D2", checks)
    require_zero(directional(jinv, xc), "X_c(J)=0", checks)
    require_zero(directional(jinv, xl), "X_lambda(J)=0", checks)
    for i, j, name in ((0, 1, "beta,gamma"), (0, 2, "beta,k"), (1, 2, "gamma,k")):
        require_zero(
            h.diff(i) * jinv.diff(j) - h.diff(j) * jinv.diff(i),
            f"dH wedge dJ=0 ({name})",
            checks,
        )

    metric_b = w - u * r**-1 + gamma * r - k * r**2
    metric_br = metric_b.diff(3)
    entropy = beta * (2 - 3 * beta * gamma + gamma * r) * r**-1
    expected = (
        metric_b * 2 * beta * gamma * (3 * beta * gamma - 2) * r**-1,
        metric_b * 2 * beta**2 * (3 * beta * gamma - 2) * r**-1,
        Laurent.coerce(0),
    )
    for i, name in enumerate(("beta", "gamma", "k")):
        remainder = h.diff(i) - u * (
            metric_br * entropy.diff(i) - entropy.diff(3) * metric_b.diff(i)
        )
        require_zero(remainder - expected[i], f"first-law quotient ({name})", checks)

    # Exact three-horizon fixture: 19*r*B = -(r-1)(r-3)(r-8).
    substitutions = (
        (0, Fraction(3, 2)),
        (1, Fraction(12, 19)),
        (2, Fraction(1, 19)),
    )

    def evaluate_parameters(expr: Laurent) -> Laurent:
        out = Laurent.coerce(0)
        for exponents, coefficient in expr.terms.items():
            scalar = coefficient
            for index, value in substitutions:
                scalar *= value ** exponents[index]
            new_exp = (0, 0, 0, exponents[3])
            out += Laurent({new_exp: scalar})
        return out

    fixture_poly = 19 * r * evaluate_parameters(metric_b)
    target = -(r - 1) * (r - 3) * (r - 8)
    require_zero(fixture_poly - target, "three-horizon fixture factorization", checks)

    # Mutation control: changing the Hamiltonian by beta must be rejected.
    mutated = h + beta
    if (mutated.diff(0) - u * f[0]).is_zero():
        raise AssertionError("mutation control unexpectedly passed")
    checks.append("mutation control rejects H+beta")
    return checks


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=None, help="write a deterministic JSON receipt")
    args = parser.parse_args()
    checks = verify()
    receipt = {
        "schema": "paper18-stdlib-algebra-receipt-v1",
        "result_token": "PAPER18_STDLIB_EXACT_ALGEBRA_PASS",
        "backend": "Python standard library fractions.Fraction sparse Laurent polynomials",
        "sympy_imported": False,
        "checks": checks,
        "verifier": str(Path(__file__).resolve().relative_to(ROOT)),
        "verifier_sha256": sha256(Path(__file__).resolve()),
    }
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    print(f"PASS {len(checks)} independent exact Paper 18 algebra checks")


if __name__ == "__main__":
    main()
