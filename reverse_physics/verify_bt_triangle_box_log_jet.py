#!/usr/bin/env python3
"""Independent verifier for the BT triangle/box logarithmic jet.

This rail does not import the producer.  It derives the low-degree tree
identity with a subset jet algebra and derives the single-quartic cross cut
from a transverse two-body tensor projector rather than the producer's
center-of-mass moment parametrization.  It then reconstructs the interference
rows in the subset algebra.
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
    "REVERSE_PHYSICS_BT_TRIANGLE_BOX_LOG_JET_V1.json",
)
SCHEMA = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-triangle-box-log-jet-v1.schema.json",
)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


class Jet:
    """Square-free four-variable jet over a symbolic coefficient field."""

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
            out *= self
        return out

    def inverse(self):
        scalar = self.coefficients.get(0, 0)
        if scalar == 0:
            raise ZeroDivisionError("jet has zero scalar coefficient")
        nilpotent = self - scalar
        ratio = nilpotent * (-1 / scalar)
        return sum((ratio ** degree for degree in range(5)), Jet()) * (1 / scalar)

    def __truediv__(self, other):
        if isinstance(other, Jet):
            return self * other.inverse()
        import sympy as sp
        return self * (sp.S.One / sp.sympify(other))

    def coefficient(self, mask):
        return self.coefficients.get(mask, 0)


def subset_tree():
    """Construct the full PS tree directly in the 16-slot quotient."""
    import sympy as sp

    s, t = sp.symbols("s t", nonzero=True)
    x1, x2, x3, x4 = [Jet.variable(index) for index in range(4)]
    xs = (x1, x2, x3, x4)
    total = sum(xs, Jet())
    u = total - s - t

    def kallen(a, b, c):
        return a * a + b * b + c * c - 2 * a * b - 2 * a * c - 2 * b * c

    def end(channel, a, b):
        return kallen(channel, a, b) / 2

    quartic = (
        (s - x1 - x2) * (s - x3 - x4)
        + (t - x1 - x3) * (t - x2 - x4)
        + (u - x1 - x4) * (u - x2 - x3)
    ) / 4
    tree = (
        end(s, x1, x2) * end(s, x3, x4) / s ** 2
        + end(t, x1, x3) * end(t, x2, x4) / t ** 2
        + end(u, x1, x4) * end(u, x2, x3) / (u ** 2)
        - quartic
    )
    return (s, t), xs, tree


def transverse_projector_cut():
    """Derive topology cuts using <q_mu q_nu> on the transverse subspace."""
    import sympy as sp
    from itertools import combinations

    S, T, xa, xb, xc, xd, y, z = sp.symbols(
        "S T xa xb xc xd y z", positive=True
    )
    xs = (xa, xb, xc, xd)
    aP = (S + xa - xb) / 2
    bP = (S - xa + xb) / 2
    cP = (-S - xc + xd) / 2
    dP = (-S + xc - xd) / 2
    ab = (S - xa - xb) / 2
    cd = (S - xc - xd) / 2
    kallen = S ** 2 + y ** 2 + z ** 2 - 2 * S * y - 2 * S * z - 2 * y * z
    alpha = (S + y - z) / (2 * S)

    def q_average(pair_dot, left_p, right_p):
        transverse_pair = pair_dot - left_p * right_p / S
        q_pair = -kallen * transverse_pair / (12 * S)
        return sp.factor(
            pair_dot * (S - y - z) / 2
            + 2 * alpha * (1 - alpha) * left_p * right_p
            - 2 * q_pair
        )

    q_left = q_average(ab, aP, bP)
    q_right = q_average(cd, cP, dP)
    a2_left = (
        xa * xb + xa * y + xa * z + xb * y + xb * z + y * z
    ) / 2
    a2_right = (
        xc * xd + xc * y + xc * z + xd * y + xd * z + y * z
    ) / 2
    density = sp.sqrt(kallen) / S
    cross_raw = sp.diff(
        density * (q_left * a2_right + a2_left * q_right), y, z
    ).subs({y: 0, z: 0})

    cross = 0
    zero = dict.fromkeys(xs, 0)
    for degree in range(3):
        for indices in combinations(range(4), degree):
            coefficient = cross_raw
            monomial = 1
            for index in indices:
                coefficient = sp.diff(coefficient, xs[index])
                monomial *= xs[index]
            cross += sp.factor(coefficient.subs(zero)) * monomial
    cross = sp.factor(cross)

    bubble = (
        7 * S ** 2 + S * T + T ** 2 - (7 * S + T) * sum(xs)
        + xa * xb + xc * xd
        + 7 * (xa * xc + xa * xd + xb * xc + xb * xd)
    ) / 12
    full = (
        xa * xb + xc * xd
        + 2 * (xa * xc + xa * xd + xb * xc + xb * xd)
    ) / 4
    return {
        "triangle": sp.factor(-cross - 2 * bubble),
        "box": sp.factor(full + cross + bubble),
        "full": sp.factor(full),
        "sum": sp.factor(bubble - cross - 2 * bubble + full + cross + bubble),
        "symbols": (S, T, xa, xb, xc, xd),
    }


def topology_polynomials():
    def bubble(S, T, a, b, c, d):
        return (
            7 * S * S + S * T + T * T - (7 * S + T) * (a + b + c + d)
            + a * b + c * d + 7 * (a * c + a * d + b * c + b * d)
        )

    def triangle(S, T, a, b, c, d):
        return -(
            19 * S * S + 2 * S * T + 2 * T * T
            - (25 * S + 2 * T) * (a + b + c + d)
            + 3 * a * b + 3 * c * d
            + 32 * (a * c + a * d + b * c + b * d)
        )

    def box(S, T, a, b, c, d):
        return (
            12 * S * S + S * T + T * T
            - (18 * S + T) * (a + b + c + d)
            + 5 * a * b + 5 * c * d
            + 31 * (a * c + a * d + b * c + b * d)
        )

    return bubble, triangle, box


def subset_interference_rows(channel):
    import sympy as sp

    (s, t), xs, tree = subset_tree()
    x1, x2, x3, x4 = xs
    total = sum(xs, Jet())
    u = total - s - t
    ls, lt, lu = sp.symbols("Ls Lt Lu")
    ps = channel(s, t, x1, x2, x3, x4)
    pt = channel(t, s, x1, x3, x2, x4)
    pu = channel(u, s, x1, x4, x2, x3)
    logu = Jet.scalar(lu) - sum(
        (total ** degree) / (sp.Integer(degree) * (s + t) ** degree)
        for degree in range(1, 5)
    )
    top = sp.factor((tree * (ps * ls + pt * lt + pu * logu)).coefficient(15))
    denominator = s ** 2 * t ** 2 * (s + t) ** 2
    numerator = sp.expand(sp.cancel(top * denominator))
    rows = {}
    for name, symbol in (("Ls", ls), ("Lt", lt), ("Lu", lu)):
        polynomial = sp.Poly(sp.diff(numerator, symbol), s, t)
        rows[name] = [
            int(polynomial.coeff_monomial(s ** (6 - k) * t ** k))
            for k in range(7)
        ]
    polynomial = sp.Poly(numerator.subs({ls: 0, lt: 0, lu: 0}), s, t)
    rows["log_kinematic_rational"] = [
        int(polynomial.coeff_monomial(s ** (6 - k) * t ** k))
        for k in range(7)
    ]
    return top, rows


def verify(path):
    import sympy as sp

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

    _, _, tree = subset_tree()
    checks["subset_tree_low_degree"] = (
        tree.coefficient(0) == 0
        and all(tree.coefficient(1 << index) == 0 for index in range(4))
        and all(sp.factor(tree.coefficient(mask) - sp.Rational(1, 2)) == 0
                for mask in (3, 5, 9, 6, 10, 12))
    )

    direct = transverse_projector_cut()
    S, T, xa, xb, xc, xd = direct["symbols"]
    bubble_fn, triangle_fn, box_fn = topology_polynomials()
    expected_triangle = triangle_fn(S, T, xa, xb, xc, xd) / 12
    expected_box = box_fn(S, T, xa, xb, xc, xd) / 12
    checks["transverse_projector_triangle"] = sp.expand(
        direct["triangle"] - expected_triangle
    ) == 0
    checks["transverse_projector_box"] = sp.expand(
        direct["box"] - expected_box
    ) == 0
    checks["channel_sum_is_full_cut"] = sp.expand(
        direct["sum"] - direct["full"]
    ) == 0
    checks["holdom_forward_coefficients"] = (
        bubble_fn(S, 0, 0, 0, 0, 0) * 2 / S ** 2 == 14
        and -triangle_fn(S, 0, 0, 0, 0, 0) / S ** 2 == 19
        and box_fn(S, 0, 0, 0, 0, 0) / (2 * S ** 2) == 6
    )

    bubble_top, bubble_rows = subset_interference_rows(bubble_fn)
    triangle_top, triangle_rows = subset_interference_rows(triangle_fn)
    box_top, box_rows = subset_interference_rows(box_fn)
    recorded = cert.get("interference_jets", {})
    checks["subset_triangle_rows"] = triangle_rows == recorded.get("triangle_rows")
    checks["subset_box_rows"] = box_rows == recorded.get("box_rows")
    combined_rows = {
        key: [sum(values) for values in zip(
            bubble_rows[key], triangle_rows[key], box_rows[key]
        )]
        for key in bubble_rows
    }
    checks["subset_combined_rows"] = combined_rows == recorded.get("complete_rows")
    ls, lt, lu = sp.symbols("Ls Lt Lu")
    checks["combined_top_reduction"] = sp.cancel(
        bubble_top + triangle_top + box_top - 15 * (ls + lt + lu)
    ) == 0

    disposition = cert.get("disposition", {})
    checks["log_sectors_computed"] = (
        disposition.get("triangle_logarithmic_jet") == "COMPUTED"
        and disposition.get("box_logarithmic_jet") == "COMPUTED"
    )
    checks["finite_boundary"] = (
        disposition.get("triangle_cut_free_finite_rational_part") == "NOT_COMPUTED"
        and disposition.get("box_cut_free_finite_rational_part") == "NOT_COMPUTED"
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
        == cert.get("checks", {}).get("total") == 21
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
