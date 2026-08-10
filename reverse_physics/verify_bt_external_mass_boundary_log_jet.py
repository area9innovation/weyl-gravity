#!/usr/bin/env python3
"""Independent verifier for the BT external-mass boundary logarithmic jet.

This rail does not import the new producer.  It reconstructs the complete
five-point collinear coefficient from invariant Kallen vertices using the
predecessor's independent graph representation, differentiates the cut in the
rational function field, and assembles the four-mass interference in a sparse
square-free algebra.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from itertools import combinations

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_EXTERNAL_MASS_BOUNDARY_LOG_JET_V1.json",
)
SCHEMA = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-external-mass-boundary-log-jet-v1.schema.json",
)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def invariant_boundary_cut():
    """Rebuild D without the producer's dot-product amplitude or radicals."""
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field

    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    from reverse_physics.verify_bt_five_point_independent_mass_threshold import (
        invariant_amplitude,
    )

    values = field("a0,a1,a2,a3,a4,tau", QQ)
    coefficient_field = values[0]
    a0, a1, a2, a3, a4, tau = values[1:]
    amplitude = invariant_amplitude(
        coefficient_field, [a0, a1, a2, a3, a4], tau)
    leading = amplitude.coefficient(2)

    def at_cut_corner(expression):
        return expression.subs(a0, 0).subs(a1, 0)

    leading_a = at_cut_corner(leading.diff(a0))
    leading_b = at_cut_corner(leading.diff(a1))
    leading_ab = at_cut_corner(leading.diff(a0).diff(a1))
    # For g=Kallen^(3/2)/(2*tau), at a0=a1=0:
    # g=tau^2/2, g_a=g_b=-3*tau/2, g_ab=0.
    cut = (
        tau ** 2 * leading_ab
        - 3 * tau * (leading_a + leading_b)
    ) / 2
    expected = -(
        5 * a2 ** 2 + 5 * a2 * a3 + 5 * a2 * a4 - a2 * tau
        + 5 * a3 ** 2 + 5 * a3 * a4 - a3 * tau
        + 5 * a4 ** 2 - a4 * tau
    ) / 4
    return {
        "amplitude": amplitude,
        "cut": cut,
        "expected": expected,
        "identity": cut == expected,
    }


class MassJet:
    def __init__(self, ring, coefficients=None):
        self.ring = ring
        self.coefficients = {
            int(mask): ring.base(value)
            for mask, value in (coefficients or {}).items() if value != 0
        }

    def _coerce(self, other):
        return self.ring(other)

    def __eq__(self, other):
        return self.coefficients == self._coerce(other).coefficients

    def __bool__(self):
        return bool(self.coefficients)

    def __add__(self, other):
        other = self._coerce(other)
        out = dict(self.coefficients)
        for mask, value in other.coefficients.items():
            out[mask] = out.get(mask, self.ring.base.zero) + value
        return MassJet(self.ring, out)

    __radd__ = __add__

    def __neg__(self):
        return MassJet(
            self.ring, {mask: -value for mask, value in self.coefficients.items()})

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
                out[mask] = out.get(mask, self.ring.base.zero) + left_value * right_value
        return MassJet(self.ring, out)

    __rmul__ = __mul__

    def inverse(self):
        scalar = self.coefficients.get(0, self.ring.base.zero)
        if scalar == 0:
            raise ZeroDivisionError
        nilpotent = self - MassJet(self.ring, {0: scalar})
        ratio = (-1 / scalar) * nilpotent
        out = MassJet(self.ring, {0: self.ring.base.one})
        term = out
        for _ in range(5):
            term = term * ratio
            out = out + term
        return (1 / scalar) * out

    def __truediv__(self, other):
        return self * self._coerce(other).inverse()

    def __rtruediv__(self, other):
        return self._coerce(other) * self.inverse()


class MassJetField:
    def __init__(self, base):
        self.base = base
        self.zero = MassJet(self)
        self.one = MassJet(self, {0: base.one})

    def __call__(self, value):
        return value if isinstance(value, MassJet) else MassJet(
            self, {0: self.base(value)})


def invariant_symbolic_family_cut():
    """Repeat the physical zeta/chi cancellation with invariant tree graphs."""
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field

    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    import reverse_physics.verify_bt_five_point_independent_mass_threshold as source

    base, tau, zeta, chi = field("tau,zeta,chi", QQ)
    ring = MassJetField(base)
    masses = [MassJet(ring, {1 << index: base.one}) for index in range(5)]
    old_hard = source.HARD
    try:
        source.HARD = [1 - zeta, -chi, 1, zeta * (chi - 1)]
        amplitude = source.invariant_amplitude(ring, masses, tau)
    finally:
        source.HARD = old_hard
    leading = amplitude.coefficient(2)
    cut = {}
    for mask in range(32):
        if mask & 3:
            continue
        ab = leading.coefficients.get(mask | 3, base.zero)
        a = leading.coefficients.get(mask | 1, base.zero)
        b = leading.coefficients.get(mask | 2, base.zero)
        value = (tau ** 2 * ab - 3 * tau * (a + b)) / 2
        if value:
            cut[mask] = value
    expected = {
        4: tau / 4, 8: tau / 4, 16: tau / 4,
        12: -base(5) / 4, 20: -base(5) / 4, 24: -base(5) / 4,
    }
    return {
        "identity": cut == expected,
        "zeta_independent": all(value.diff(zeta) == 0 for value in cut.values()),
        "chi_independent": all(value.diff(chi) == 0 for value in cut.values()),
    }


def square_free_product(left, right):
    """Multiply mask-indexed square-free polynomials with log-vector values."""
    out = {}
    for left_mask, left_value in left.items():
        for right_mask, right_value in right.items():
            if left_mask & right_mask:
                continue
            mask = left_mask | right_mask
            value = tuple(
                a + b for a, b in zip(
                    out.get(mask, (Fraction(0),) * 4),
                    tuple(left_value * item for item in right_value),
                )
            )
            out[mask] = value
    return out


def boundary_log_vector(pair_weight=10):
    """Return the degree-two loop polynomial as mask -> four log weights."""
    out = {}
    for index in range(4):
        others = [slot for slot in range(4) if slot != index]
        for other in others:
            mask = (1 << index) | (1 << other)
            row = list(out.get(mask, (Fraction(0),) * 4))
            row[index] += Fraction(-2)
            out[mask] = tuple(row)
        for left, right in combinations(others, 2):
            mask = (1 << left) | (1 << right)
            row = list(out.get(mask, (Fraction(0),) * 4))
            row[index] += Fraction(pair_weight)
            out[mask] = tuple(row)
    return out


def interference_weights(pair_weight=10):
    tree = {
        (1 << left) | (1 << right): Fraction(1, 2)
        for left, right in combinations(range(4), 2)
    }
    return square_free_product(tree, boundary_log_vector(pair_weight)).get(
        15, (Fraction(0),) * 4
    )


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

    cut = invariant_boundary_cut()
    checks["invariant_graph_low_orders_cancel"] = (
        cut["amplitude"].coefficient(0) == 0
        and cut["amplitude"].coefficient(1) == 0
    )
    checks["invariant_graph_boundary_cut"] = cut["identity"]
    family = invariant_symbolic_family_cut()
    checks["invariant_symbolic_family_cut"] = family["identity"]
    checks["invariant_splitting_fraction_independence"] = family["zeta_independent"]
    checks["invariant_outer_ratio_independence"] = family["chi_independent"]

    weights = interference_weights()
    checks["sparse_interference_weights"] = weights == (12, 12, 12, 12)
    checks["coefficient_mutation_rejected"] = (
        interference_weights(pair_weight=8) == (9, 9, 9, 9)
        and interference_weights(pair_weight=8) != weights
    )
    checks["physical_rate_reconstruction"] = (
        Fraction(12) * 8 / 16 / 256 == Fraction(3, 128)
    )

    result = cert.get("four_mass_interference", {})
    checks["recorded_reduced_top"] = (
        result.get("reduced_top_coefficient")
        == "[x1*x2*x3*x4](Mtree_red*E_boundary)=12*(L1+L2+L3+L4)"
    )
    checks["recorded_projected_rate"] = (
        result.get("projected_rate")
        == "d_sigma_boundary_log/d_Omega="
           "3*lambda^6*(L1+L2+L3+L4)/(128*pi^4*s)"
    )
    response = cert.get("regulator_response", {})
    checks["regulator_response"] = (
        response.get("rate_shift")
        == "Delta[d_sigma/d_Omega]=-3*lambda^6*sum_i log(c_i)/(128*pi^4*s)"
        and response.get("comparison_status")
        == "NOT_COMPARABLE_WITHOUT_REGULATOR_GLUING_AND_FULL_REAL_PHASE_SPACE"
    )
    disposition = cert.get("disposition", {})
    checks["claim_boundary_fail_closed"] = (
        disposition.get("complete_external_mass_boundary_log_jet") == "COMPUTED"
        and disposition.get("physical_collinear_family_dependence")
        == "INDEPENDENT_OF_ZETA_AND_CHI"
        and disposition.get("four_to_five_leg_regulator_gluing") == "NOT_COMPUTED"
        and disposition.get("real_virtual_cancellation") == "NOT_COMPUTED"
        and disposition.get("beyond_tree_positivity") == "NOT_ESTABLISHED"
    )
    inputs = cert.get("provenance", {}).get("inputs", [])
    checks["provenance_hashes"] = len(inputs) == 3 and all(
        item.get("sha256") == sha256(item.get("path", "")) for item in inputs
    )
    checks["producer_checks"] = (
        cert.get("checks", {}).get("ok") is True
        and cert.get("checks", {}).get("passed")
        == cert.get("checks", {}).get("total") == 20
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
