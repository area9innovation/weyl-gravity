#!/usr/bin/env python3
"""Independent verifier for the BT independent-mass threshold obstruction.

The amplitude is rebuilt from invariant triangle vertices rather than the
producer's dot products.  The threshold root is rationalized with z=exp(-y),
not q=tanh(y/2).
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
    "REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json",
)
SCHEMA = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-five-point-independent-mass-threshold-v1.schema.json",
)
N = 5
LO = -4
HI = 4
HARD = [Fraction(32, 3), Fraction(-8), Fraction(16), Fraction(-8, 3)]


class Laurent:
    def __init__(self, field, coefficients=None):
        self.field = field
        self.coefficients = {
            int(power): field(value)
            for power, value in (coefficients or {}).items()
            if value != 0 and LO <= int(power) <= HI
        }

    @classmethod
    def scalar(cls, field, value):
        return cls(field, {0: value})

    def coefficient(self, power):
        return self.coefficients.get(power, self.field.zero)

    def _coerce(self, other):
        return other if isinstance(other, Laurent) else Laurent.scalar(
            self.field, other)

    def __add__(self, other):
        other = self._coerce(other)
        out = dict(self.coefficients)
        for power, value in other.coefficients.items():
            out[power] = out.get(power, self.field.zero) + value
            if out[power] == 0:
                del out[power]
        return Laurent(self.field, out)

    __radd__ = __add__

    def __neg__(self):
        return Laurent(self.field, {power: -value
                                    for power, value in self.coefficients.items()})

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __rsub__(self, other):
        return self._coerce(other) - self

    def __mul__(self, other):
        other = self._coerce(other)
        out = {}
        for left_power, left_value in self.coefficients.items():
            for right_power, right_value in other.coefficients.items():
                power = left_power + right_power
                if LO <= power <= HI:
                    out[power] = (out.get(power, self.field.zero)
                                  + left_value * right_value)
        return Laurent(self.field, out)

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Laurent):
            return self * other.inverse()
        return Laurent(self.field, {power: value / other
                                    for power, value in self.coefficients.items()})

    def inverse(self):
        valuation = min(self.coefficients)
        leading = self.coefficient(valuation)
        recurrence = {0: self.field.one / leading}
        for order in range(1, HI + valuation + 1):
            total = self.field.zero
            for index in range(1, order + 1):
                total += (self.coefficient(valuation + index)
                          * recurrence[order - index])
            recurrence[order] = -total / leading
        return Laurent(self.field, {
            -valuation + order: value
            for order, value in recurrence.items()
        })


def triangle(a, b, c):
    return (a * a + b * b + c * c
            - 2 * a * b - 2 * a * c - 2 * b * c) / 2


def invariant_amplitude(field, masses, tau):
    x = [Laurent(field, {1: mass}) for mass in masses]
    s = [Laurent(field, {1: tau})]
    s.extend(Laurent.scalar(field, value) for value in HARD)

    def pair_square(i, j):
        i, j = sorted((i, j))
        if j == i + 1:
            return s[i]
        if (i, j) == (0, 4):
            return s[4]
        anchor = i if (j - i) % N == 2 else j
        return (s[(anchor + 3) % N] - s[anchor] - s[(anchor + 1) % N]
                + x[anchor] + x[(anchor + 1) % N]
                + x[(anchor + 2) % N])

    pairs = list(combinations(range(N), 2))
    squares = {pair: pair_square(*pair) for pair in pairs}

    def z(pair):
        return squares[tuple(sorted(pair))]

    ends = {
        pair: triangle(x[pair[0]], x[pair[1]], z(pair))
        / (z(pair) * z(pair))
        for pair in pairs
    }
    amplitude = Laurent(field)
    for pair in pairs:
        remaining = [index for index in range(N) if index not in pair]
        quartic = Laurent(field)
        for left, right in combinations(remaining, 2):
            other = next(index for index in remaining
                         if index not in (left, right))
            channel = z((left, right))
            quartic += ((channel - x[left] - x[right])
                        * (channel - x[other] - z(pair))) / 4
        amplitude += ends[pair] * quartic
    for central in range(N):
        remaining = [index for index in range(N) if index != central]
        anchor = remaining[0]
        for partner in remaining[1:]:
            left = tuple(sorted((anchor, partner)))
            right = tuple(sorted(index for index in remaining
                                 if index not in left))
            amplitude -= (ends[left] * ends[right]
                          * triangle(z(left), z(right), x[central]))
    return amplitude


def independent_amplitude_projection():
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field

    values = field("a0,a1,a2,a3,a4,tau", QQ)
    coefficient_field = values[0]
    a0, a1, a2, a3, a4, tau = values[1:]
    amplitude = invariant_amplitude(
        coefficient_field, [a0, a1, a2, a3, a4], tau)
    leading = amplitude.coefficient(2)
    squared = leading * leading
    numerator = coefficient_field.domain.zero
    for monomial, value in squared.numer.terms():
        if monomial[2:5] == (1, 1, 1):
            numerator += (value * a0 ** monomial[0] * a1 ** monomial[1]
                          * tau ** monomial[5])
    projected = numerator / squared.denom
    expected = (
        3 * (a0 - a1) ** 2
        * ((a0 - a1) ** 2 - 2 * tau * (a0 + a1))
        / (8 * tau ** 3)
    )
    return (
        amplitude.coefficient(0) == 0
        and amplitude.coefficient(1) == 0
        and projected == expected
    )


def independent_threshold_integral():
    import sympy as sp

    z, m = sp.symbols("z m", positive=True)
    r = m * m
    u = 1 + m * m + m * (z + 1 / z)
    sqrt_lambda_du = m * m * (1 - z * z) ** 2 / z ** 3
    integrand = sp.cancel(
        sp.Rational(3, 8) * (1 - r) ** 2
        * ((1 - r) ** 2 - 2 * u * (1 + r))
        * sqrt_lambda_du / u ** 4
    )
    antiderivative = sp.integrate(integrand, z, risch=True)
    raw = (sp.limit(antiderivative, z, 1, dir="-")
           - sp.limit(antiderivative, z, 0, dir="+"))
    expected = (
        -5 * m ** 6 + 3 * m ** 4 - 3 * m ** 2 + 5
        + 12 * m ** 2 * (m ** 2 + 1) * sp.log(m)
    ) / (16 * (m ** 2 - 1))
    return sp.simplify(sp.re(raw) - expected) == 0


def fraction(payload):
    return Fraction(payload["numerator"], payload["denominator"])


def log_bounds(integer, terms=4):
    z = Fraction(integer - 1, integer + 1)
    lower = 2 * sum(
        z ** (2 * index + 1) / (2 * index + 1)
        for index in range(terms)
    )
    upper = lower + (
        2 * z ** (2 * terms + 1)
        / ((2 * terms + 1) * (1 - z * z))
    )
    return lower, upper


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate):
    checks = {}
    try:
        with open(SCHEMA, encoding="utf-8") as handle:
            schema = json.load(handle)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(certificate)
        checks["strict_schema"] = True
    except Exception:
        checks["strict_schema"] = False

    checks["identity_tag_lifecycle"] = (
        certificate.get("certificate")
        == "REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1"
        and certificate.get("dependency_tags") == ["REDUCED-MODE"]
        and certificate.get("lifecycle_state") == "COEFFICIENT_COMPUTED"
    )
    try:
        checks["independent_invariant_amplitude"] = (
            independent_amplitude_projection())
    except Exception:
        checks["independent_invariant_amplitude"] = False
    try:
        checks["independent_z_threshold_integral"] = (
            independent_threshold_integral())
    except Exception:
        checks["independent_z_threshold_integral"] = False

    threshold = certificate.get("threshold_result", {})
    checks["ray_function_and_log_slope"] = (
        "6*r*(r+1)*log(r)" in threshold.get("ray_function", "")
        and fraction(threshold.get("logarithmic_slope_coefficient"))
        == Fraction(-3, 8)
        and fraction(threshold.get("finite_slope_constant"))
        == Fraction(-1, 8)
    )
    obstruction = certificate.get("ordinary_derivative_obstruction", {})
    finite_part = certificate.get("finite_part_ambiguity", {})
    checks["derivative_and_finite_part_disposition"] = (
        obstruction.get("ordinary_limit") == "DIVERGES_TO_POSITIVE_INFINITY"
        and obstruction.get("consequence")
        == "NO_ORDINARY_JOINT_SECOND_JET_AFTER_SPECTATOR_PROJECTION"
        and finite_part.get("value") == "FP_c=-1/8-3/8*log(c)"
        and finite_part.get("c_four_shift") == "-3/4*log(2)"
    )

    witness = certificate.get("four_ray_nonpolynomial_witness", {})
    l2, u2 = log_bounds(2)
    l3, u3 = log_bounds(3)
    defect_lower = Fraction(45, 4) - 30 * u2 + Fraction(135, 16) * l3
    defect_upper = Fraction(45, 4) - 30 * l2 + Fraction(135, 16) * u3
    checks["exact_four_ray_witness"] = (
        witness.get("annihilator_weights") == [-10, 15, -6, 1]
        and [fraction(value) for value in witness.get("log2_bounds", [])]
        == [l2, u2]
        and [fraction(value) for value in witness.get("log3_bounds", [])]
        == [l3, u3]
        and [fraction(value) for value in witness.get("defect_bounds", [])]
        == [defect_lower, defect_upper]
        and defect_upper < 0
    )
    try:
        checks["input_hashes"] = all(
            sha256(row["path"]) == row["sha256"]
            for row in certificate["provenance"]["inputs"]
        )
    except Exception:
        checks["input_hashes"] = False

    disposition = certificate.get("disposition", {})
    boundaries = " ".join(certificate.get("does_not_establish", []))
    checks["fail_closed_claim_boundary"] = (
        disposition.get("ordinary_reduced_mixed_five_mass_derivative")
        == "DOES_NOT_EXIST"
        and disposition.get("finite_part_on_reduced_carrier")
        == "PRESCRIPTION_DEPENDENT"
        and disposition.get("full_five_body_phase_space_projector")
        == "NOT_CONSTRUCTED"
        and disposition.get("physical_integrated_2to3_probability")
        == "NOT_COMPUTED"
        and "theory is inconsistent" in boundaries
        and "LORENTZIAN-CAUSAL" in boundaries
    )
    checks["missing_objects_and_next_gate"] = (
        len(certificate.get("missing_object_ledger", [])) >= 6
        and "four-leg loop jet" in certificate.get("next_gate", "")
    )
    recorded = certificate.get("checks", {})
    checks["producer_checks_recorded_pass"] = (
        recorded.get("ok") is True
        and recorded.get("passed") == recorded.get("total")
    )
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="verify BT independent-mass threshold obstruction")
    parser.add_argument("--verify", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    with open(args.verify, encoding="utf-8") as handle:
        certificate = json.load(handle)
    checks = verify(certificate)
    for name, passed in checks.items():
        print("[%s] %s" % ("PASS" if passed else "FAIL", name))
    print("checks %d/%d" % (sum(checks.values()), len(checks)))
    ok = all(checks.values())
    print("RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
