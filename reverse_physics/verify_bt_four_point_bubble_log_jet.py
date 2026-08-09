#!/usr/bin/env python3
"""Independent verifier for the BT two-quartic bubble logarithmic jet.

The cut rail uses explicit rational center-of-mass four-vectors and exact
spherical monomial averages.  The jet rail uses a square-free subset algebra,
not the producer's sequential symbolic differentiation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_FOUR_POINT_BUBBLE_LOG_JET_V1.json",
)
SCHEMA = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-four-point-bubble-log-jet-v1.schema.json",
)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def minkowski_dot(left, right):
    return left[0] * right[0] - sum(
        left[index] * right[index] for index in range(1, 4)
    )


def quartic(left_a, left_b, right_a, right_b):
    return (
        minkowski_dot(left_a, left_b) * minkowski_dot(right_a, right_b)
        + minkowski_dot(left_a, right_a) * minkowski_dot(left_b, right_b)
        + minkowski_dot(left_a, right_b) * minkowski_dot(left_b, right_a)
    )


def sphere_average(polynomial, directions):
    import sympy as sp

    expanded = sp.Poly(sp.expand(polynomial), *directions)
    result = 0
    for powers, coefficient in expanded.terms():
        if any(power % 2 for power in powers):
            continue
        total = sum(powers)
        numerator = sp.prod(
            sp.factorial2(power - 1) if power else 1 for power in powers
        )
        result += coefficient * numerator / sp.factorial2(total + 1)
    return sp.factor(result)


def coordinate_cut_fixture(H, a_values, c_values):
    """Direct CM-frame double-pole cut for one rational external fixture."""
    import sympy as sp

    y, z = sp.symbols("y z")
    nx, ny, nz = sp.symbols("nx ny nz")
    H = sp.Integer(H)
    S = H ** 2
    total = (H, 0, 0, 0)
    a = tuple(map(sp.Integer, a_values))
    c = tuple(map(sp.Integer, c_values))
    b = tuple(total[index] - a[index] for index in range(4))
    d = tuple(-total[index] - c[index] for index in range(4))

    internal_kallen = (
        S ** 2 + y ** 2 + z ** 2 - 2 * S * y - 2 * S * z - 2 * y * z
    )
    energy = (S + y - z) / (2 * H)
    radius = sp.sqrt(internal_kallen) / (2 * H)
    r = (energy, radius * nx, radius * ny, radius * nz)
    w = (H - energy, -radius * nx, -radius * ny, -radius * nz)
    angular = sphere_average(
        quartic(a, b, r, w) * quartic(c, d, r, w), (nx, ny, nz)
    )
    ordinary_cut = sp.sqrt(internal_kallen) * angular / S
    cut = sp.factor(sp.diff(ordinary_cut, y, z).subs({y: 0, z: 0}))

    xa, xb, xc, xd = (
        minkowski_dot(vector, vector) for vector in (a, b, c, d)
    )
    a_plus_c = tuple(a[index] + c[index] for index in range(4))
    T = minkowski_dot(a_plus_c, a_plus_c)
    polynomial = (
        7 * S ** 2 + S * T + T ** 2
        - (7 * S + T) * (xa + xb + xc + xd)
        + xa * xb + xc * xd
        + 7 * (xa * xc + xa * xd + xb * xc + xb * xd)
    )
    return {
        "S": int(S),
        "T": int(T),
        "masses": tuple(map(int, (xa, xb, xc, xd))),
        "cut": cut,
        "expected": sp.Rational(polynomial, 12),
    }


class Jet:
    """Square-free four-variable jet with symbolic coefficient field."""

    def __init__(self, coefficients=None):
        self.coefficients = {
            int(mask): value for mask, value in (coefficients or {}).items()
            if value != 0
        }

    @classmethod
    def scalar(cls, value):
        return cls({0: value})

    @classmethod
    def variable(cls, index):
        return cls({1 << index: 1})

    def _coerce(self, other):
        return other if isinstance(other, Jet) else Jet.scalar(other)

    def __add__(self, other):
        other = self._coerce(other)
        out = dict(self.coefficients)
        for mask, value in other.coefficients.items():
            out[mask] = out.get(mask, 0) + value
        return Jet(out)

    __radd__ = __add__

    def __neg__(self):
        return Jet({mask: -value for mask, value in self.coefficients.items()})

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __rsub__(self, other):
        return self._coerce(other) - self

    def __mul__(self, other):
        other = self._coerce(other)
        out = {}
        for left_mask, left_value in self.coefficients.items():
            for right_mask, right_value in other.coefficients.items():
                if left_mask & right_mask:
                    continue
                mask = left_mask | right_mask
                out[mask] = out.get(mask, 0) + left_value * right_value
        return Jet(out)

    __rmul__ = __mul__

    def __pow__(self, exponent):
        out = Jet.scalar(1)
        for _ in range(exponent):
            out = out * self
        return out

    def inverse(self):
        scalar = self.coefficients.get(0, 0)
        if scalar == 0:
            raise ZeroDivisionError("jet has zero scalar coefficient")
        nilpotent = self - scalar
        ratio = nilpotent * (-1 / scalar)
        return sum((ratio ** degree for degree in range(5)), Jet()) * (1 / scalar)

    def __truediv__(self, other):
        return self * (other.inverse() if isinstance(other, Jet) else 1 / other)

    def coefficient(self, mask):
        return self.coefficients.get(mask, 0)


def subset_jet_result():
    import sympy as sp

    s, t, ls, lt, lu = sp.symbols("s t Ls Lt Lu", nonzero=True)
    x1, x2, x3, x4 = [Jet.variable(index) for index in range(4)]
    total = x1 + x2 + x3 + x4
    u = total - s - t

    def kallen(a, b, c):
        return a * a + b * b + c * c - 2 * a * b - 2 * a * c - 2 * b * c

    def end(channel, a, b):
        return kallen(channel, a, b) / 2

    quartic_jet = (
        (s - x1 - x2) * (s - x3 - x4)
        + (t - x1 - x3) * (t - x2 - x4)
        + (u - x1 - x4) * (u - x2 - x3)
    ) / 4
    tree = (
        end(s, x1, x2) * end(s, x3, x4) / s ** 2
        + end(t, x1, x3) * end(t, x2, x4) / t ** 2
        + end(u, x1, x4) * end(u, x2, x3) / (u ** 2)
        - quartic_jet
    )

    def channel(S, T, a, b, c, d):
        return (
            7 * S * S + S * T + T * T
            - (7 * S + T) * (a + b + c + d)
            + a * b + c * d + 7 * (a * c + a * d + b * c + b * d)
        )

    ps = channel(s, t, x1, x2, x3, x4)
    pt = channel(t, s, x1, x3, x2, x4)
    pu = channel(u, s, x1, x4, x2, x3)
    logu = Jet.scalar(lu) - sum(
        (total ** degree) / (sp.Integer(degree) * (s + t) ** degree)
        for degree in range(1, 5)
    )
    bubble = ps * ls + pt * lt + pu * logu
    top = sp.factor((tree * bubble).coefficient(15))
    denominator = s ** 2 * t ** 2 * (s + t) ** 2
    rows = {}
    expression = sp.expand(sp.cancel(top * denominator))
    for name, symbol in (("Ls", ls), ("Lt", lt), ("Lu", lu)):
        polynomial = sp.Poly(sp.diff(expression, symbol), s, t)
        rows[name] = [
            int(polynomial.coeff_monomial(s ** (6 - k) * t ** k))
            for k in range(7)
        ]
    rational = sp.Poly(expression.subs({ls: 0, lt: 0, lu: 0}), s, t)
    rows["rational"] = [
        int(rational.coeff_monomial(s ** (6 - k) * t ** k))
        for k in range(7)
    ]
    return top, rows


def verify(path):
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    errors = list(Draft202012Validator(schema).iter_errors(cert))
    checks = {"strict_schema": not errors}
    fixtures = [
        coordinate_cut_fixture(5, (3, 1, 0, 1), (-2, 0, 1, 1)),
        coordinate_cut_fixture(7, (4, 1, 2, 0), (-3, 2, -1, 1)),
        coordinate_cut_fixture(6, (2, -1, 1, 1), (-4, 1, 0, -2)),
    ]
    checks["coordinate_cut_fixtures"] = all(
        row["cut"] == row["expected"] for row in fixtures
    )
    checks["fixtures_are_distinct"] = len({
        (row["S"], row["T"], row["masses"]) for row in fixtures
    }) == len(fixtures)

    _, rows = subset_jet_result()
    recorded_rows = cert.get("bubble_log_interference_jet", {}).get(
        "numerator_coefficients", {}
    )
    checks["subset_jet_rows"] = rows == recorded_rows
    checks["nonzero_top_jet"] = any(rows.get("rational", []))
    checks["crossing_controls"] = (
        rows.get("Ls") == list(reversed(rows.get("Lt", [])))
        and rows.get("Lu") == list(reversed(rows.get("Lu", [])))
    )
    disposition = cert.get("disposition", {})
    checks["sector_boundary"] = (
        disposition.get("triangle_sector") == "NOT_COMPUTED"
        and disposition.get("box_sector") == "NOT_COMPUTED"
        and disposition.get("external_phase_space_projector") == "NOT_APPLIED"
    )
    checks["physical_boundary"] = (
        disposition.get("real_virtual_collinear_cancellation") == "NOT_COMPUTED"
        and disposition.get("beyond_tree_positivity") == "NOT_ESTABLISHED"
    )
    checks["provenance_hashes"] = all(
        item.get("sha256") == sha256(item.get("path", ""))
        for item in cert.get("provenance", {}).get("inputs", [])
    )
    checks["producer_checks"] = (
        cert.get("checks", {}).get("ok") is True
        and cert.get("checks", {}).get("passed")
        == cert.get("checks", {}).get("total") == 16
    )

    for name, ok in checks.items():
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    passed = sum(checks.values())
    print(f"RESULT: {'PASS' if passed == len(checks) else 'FAIL'} "
          f"({passed}/{len(checks)})")
    return passed == len(checks)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.verify) else 1


if __name__ == "__main__":
    sys.exit(main())
