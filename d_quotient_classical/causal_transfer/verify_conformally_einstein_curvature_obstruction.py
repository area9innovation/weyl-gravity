#!/usr/bin/env python3
"""Independent replay of the Nariai tractor-curvature obstruction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/CONFORMALLY_EINSTEIN_TRACTOR_CURVATURE_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/conformally-einstein-tractor-curvature-obstruction-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _coordinate_replay() -> None:
    """Derive the displayed Nariai curvature directly in global coordinates."""
    t, chi, theta, phi = sp.symbols("t chi theta phi", real=True)
    coordinates = (t, chi, theta, phi)
    metric = sp.diag(-1, sp.cosh(t) ** 2, 1, sp.sin(theta) ** 2)
    inverse = metric.inv()
    dimension = 4

    def clean(value: sp.Expr) -> sp.Expr:
        return sp.simplify(sp.expand_trig(value))

    christoffel = [[[
        clean(sum(
            inverse[a, e]
            * (
                sp.diff(metric[e, c], coordinates[b])
                + sp.diff(metric[e, b], coordinates[c])
                - sp.diff(metric[b, c], coordinates[e])
            )
            for e in range(dimension)
        ) / 2)
        for c in range(dimension)] for b in range(dimension)] for a in range(dimension)]

    riemann_up = [[[[(
        clean(
            sp.diff(christoffel[a][b][d], coordinates[c])
            - sp.diff(christoffel[a][b][c], coordinates[d])
            + sum(
                christoffel[a][c][e] * christoffel[e][b][d]
                - christoffel[a][d][e] * christoffel[e][b][c]
                for e in range(dimension)
            )
        )
    ) for d in range(dimension)] for c in range(dimension)] for b in range(dimension)] for a in range(dimension)]
    ricci = sp.Matrix(dimension, dimension, lambda b, d: clean(sum(riemann_up[a][b][a][d] for a in range(dimension))))
    if any(clean(ricci[a, b] - metric[a, b]) != 0 for a in range(dimension) for b in range(dimension)):
        raise ValueError("coordinate Nariai Einstein replay failed")
    scalar = clean(sum(inverse[a, b] * ricci[a, b] for a in range(dimension) for b in range(dimension)))
    if scalar != 4:
        raise ValueError("coordinate scalar-curvature replay failed")

    def riemann(a: int, b: int, c: int, d: int) -> sp.Expr:
        return clean(sum(metric[a, e] * riemann_up[e][b][c][d] for e in range(dimension)))

    def weyl(a: int, b: int, c: int, d: int) -> sp.Expr:
        return clean(
            riemann(a, b, c, d)
            - sp.Rational(1, 2)
            * (
                metric[a, c] * ricci[d, b]
                - metric[a, d] * ricci[c, b]
                - metric[b, c] * ricci[d, a]
                + metric[b, d] * ricci[c, a]
            )
            + scalar
            * sp.Rational(1, 6)
            * (metric[a, c] * metric[d, b] - metric[a, d] * metric[c, b])
        )

    coordinate_expected = {
        (0, 1, 0, 1): -sp.Rational(2, 3) * sp.cosh(t) ** 2,
        (2, 3, 2, 3): sp.Rational(2, 3) * sp.sin(theta) ** 2,
        (0, 2, 0, 2): sp.Rational(1, 3),
    }
    if any(clean(weyl(*indices) - expected) != 0 for indices, expected in coordinate_expected.items()):
        raise ValueError("coordinate Weyl replay failed")


def verify() -> dict:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for relative, digest in value["provenance"]["source_manifest"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"source digest drifted: {relative}")
    dependency = value["dependency_ref"]
    if _sha256(ROOT / dependency["path"]) != dependency["sha256"]:
        raise ValueError("C-G2 dependency drifted")

    _coordinate_replay()

    signs = [Fraction(-1), Fraction(1), Fraction(1), Fraction(1)]

    def g(a: int, b: int) -> Fraction:
        return signs[a] if a == b else Fraction(0)

    def riemann(a: int, b: int, c: int, d: int) -> Fraction:
        in_factor = all(i < 2 for i in (a, b, c, d)) or all(i >= 2 for i in (a, b, c, d))
        return g(a, c) * g(b, d) - g(a, d) * g(b, c) if in_factor else Fraction(0)

    def ricci(b: int, d: int) -> Fraction:
        return sum(signs[a] * riemann(a, b, a, d) for a in range(4))

    scalar = sum(signs[a] * ricci(a, a) for a in range(4))
    if scalar != 4 or any(ricci(a, b) != g(a, b) for a in range(4) for b in range(4)):
        raise ValueError("independent Einstein calculation failed")

    def weyl(a: int, b: int, c: int, d: int) -> Fraction:
        return (
            riemann(a, b, c, d)
            - Fraction(1, 2) * (g(a, c) * ricci(d, b) - g(a, d) * ricci(c, b) - g(b, c) * ricci(d, a) + g(b, d) * ricci(c, a))
            + Fraction(1, 6) * scalar * (g(a, c) * g(d, b) - g(a, d) * g(c, b))
        )

    expected = {"C_0101": "-2/3", "C_2323": "2/3", "C_0202": "1/3"}
    actual = {
        "C_0101": str(weyl(0, 1, 0, 1)),
        "C_2323": str(weyl(2, 3, 2, 3)),
        "C_0202": str(weyl(0, 2, 0, 2)),
    }
    if actual != expected or value["exact_curvature"]["weyl_components"] != expected:
        raise ValueError("independent Weyl witness failed")
    if Fraction(3, 2) * weyl(2, 3, 2, 3) != 1:
        raise ValueError("normalized obstruction failed")
    if value["dependency_tags"] != ["LOCAL-ALGEBRAIC"]:
        raise ValueError("causal scope was overpromoted")
    flags = value["flags"]
    if flags["CURVED_DIFFERENTIAL_HPL_CORRECTION_EXISTS"] is not False or flags["ALL_BACH_FLAT_BACKGROUNDS_OBSTRUCTED"] is not False:
        raise ValueError("claim boundary drifted")
    print("CONFORMALLY_EINSTEIN_TRACTOR_CURVATURE_OBSTRUCTION_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
