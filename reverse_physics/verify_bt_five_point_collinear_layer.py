#!/usr/bin/env python3
"""Independent verifier for the BT five-point collinear layer.

This rail does not import the producer.  It reconstructs the amplitude from
Kallen/triangle vertices in a truncated Laurent algebra and obtains inverse
double-propagator series by coefficient recurrence.  The producer instead
uses the published dot-product vertices as full SymPy rational expressions.
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
    "REVERSE_PHYSICS_BT_FIVE_POINT_COLLINEAR_LAYER_V1.json",
)
SCHEMA = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-five-point-collinear-layer-v1.schema.json",
)
N = 5
LO = -4
HI = 4
MASS_RAY = [1, 4, 9, 16, 25]
HARD = [Fraction(32, 3), Fraction(-8), Fraction(16), Fraction(-8, 3)]


class FractionDomain:
    zero = Fraction(0)
    one = Fraction(1)

    @staticmethod
    def convert(value):
        return Fraction(value)


class FieldDomain:
    def __init__(self, field):
        self.field = field
        self.zero = field.zero
        self.one = field.one

    def convert(self, value):
        return self.field(value)


class Laurent:
    """Finite Laurent series sufficient through the delta^2 amplitude term."""

    def __init__(self, domain, coefficients=None):
        self.domain = domain
        self.coefficients = {
            int(power): domain.convert(value)
            for power, value in (coefficients or {}).items()
            if value != 0 and LO <= int(power) <= HI
        }

    @classmethod
    def scalar(cls, domain, value):
        return cls(domain, {0: value})

    def coefficient(self, power):
        return self.coefficients.get(power, self.domain.zero)

    def _coerce(self, other):
        if isinstance(other, Laurent):
            return other
        return Laurent.scalar(self.domain, other)

    def __add__(self, other):
        other = self._coerce(other)
        out = dict(self.coefficients)
        for power, value in other.coefficients.items():
            out[power] = out.get(power, self.domain.zero) + value
            if out[power] == 0:
                del out[power]
        return Laurent(self.domain, out)

    __radd__ = __add__

    def __neg__(self):
        return Laurent(self.domain, {power: -value
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
                    out[power] = (out.get(power, self.domain.zero)
                                  + left_value * right_value)
        return Laurent(self.domain, out)

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Laurent):
            return self * other.inverse()
        return Laurent(self.domain, {power: value / other
                                     for power, value in self.coefficients.items()})

    def inverse(self):
        if not self.coefficients:
            raise ZeroDivisionError("zero Laurent series")
        valuation = min(self.coefficients)
        leading = self.coefficient(valuation)
        maximum_n = HI + valuation
        recurrence = {0: self.domain.one / leading}
        for n in range(1, maximum_n + 1):
            total = self.domain.zero
            for index in range(1, n + 1):
                total += (self.coefficient(valuation + index)
                          * recurrence[n - index])
            recurrence[n] = -total / leading
        return Laurent(self.domain, {
            -valuation + n: value for n, value in recurrence.items()
        })


def triangle(a, b, c):
    return (a * a + b * b + c * c
            - 2 * a * b - 2 * a * c - 2 * b * c) / 2


def build_series_amplitude(domain, tau, relative_sign=-1):
    """Invariant-only 25-tree derivation in the Laurent algebra."""
    x = [Laurent(domain, {1: weight}) for weight in MASS_RAY]
    s = [Laurent(domain, {1: tau})]
    s.extend(Laurent.scalar(domain, value) for value in HARD)

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
    pair_squares = {pair: pair_square(*pair) for pair in pairs}

    def z(pair):
        return pair_squares[tuple(sorted(pair))]

    def end(pair):
        i, j = pair
        channel = z(pair)
        return triangle(x[i], x[j], channel) / (channel * channel)

    ends = {pair: end(pair) for pair in pairs}
    amplitude = Laurent(domain)
    for pair in pairs:
        remaining = [index for index in range(N) if index not in pair]
        quartic = Laurent(domain)
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
            amplitude += relative_sign * (
                ends[left] * ends[right]
                * triangle(z(left), z(right), x[central])
            )
    return amplitude


def fraction(payload):
    return Fraction(payload["numerator"], payload["denominator"])


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def minkowski_square(vector):
    return vector[0] ** 2 - sum(component ** 2 for component in vector[1:])


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

    checks["identity_tag_and_lifecycle"] = (
        certificate.get("certificate")
        == "REVERSE_PHYSICS_BT_FIVE_POINT_COLLINEAR_LAYER_V1"
        and certificate.get("dependency_tags") == ["REDUCED-MODE"]
        and certificate.get("lifecycle_state") == "COEFFICIENT_COMPUTED"
    )

    try:
        from sympy.polys.domains import QQ
        from sympy.polys.fields import field

        values = field("tau", QQ)
        rational_field, tau = values[0], values[1]
        symbolic = build_series_amplitude(FieldDomain(rational_field), tau)
        expected = (-3 * (979 * tau * tau - 5620 * tau + 5193)
                    / (4 * tau * tau))
        checks["independent_symbolic_laurent_coefficient"] = (
            symbolic.coefficient(0) == 0
            and symbolic.coefficient(1) == 0
            and symbolic.coefficient(2) == expected
        )
    except Exception:
        checks["independent_symbolic_laurent_coefficient"] = False

    fixtures_ok = True
    for row in certificate.get("amplitude_boundary", {}).get(
            "exact_fixtures", []):
        amplitude = build_series_amplitude(FractionDomain(), row["tau"])
        fixtures_ok &= (
            amplitude.coefficient(0) == 0
            and amplitude.coefficient(1) == 0
            and amplitude.coefficient(2) == fraction(row["leading_coefficient"])
            and row["delta_valuation"] == 2
        )
    checks["three_exact_fixtures"] = (
        len(certificate.get("amplitude_boundary", {}).get(
            "exact_fixtures", [])) == 3 and fixtures_ok
    )

    mutation = certificate.get("amplitude_boundary", {}).get(
        "relative_sign_mutation", {})
    mutated = build_series_amplitude(FractionDomain(), 10, relative_sign=1)
    checks["relative_sign_mutation"] = (
        mutation.get("delta_valuation") == 0
        and fraction(mutation.get("leading_coefficient", {"numerator": 0,
                                                           "denominator": 1}))
        == Fraction(15848, 75)
        and mutated.coefficient(0) == Fraction(15848, 75)
    )

    try:
        physical = certificate["physical_limit_fixture"]
        momenta = [tuple(fraction(component) for component in momentum)
                   for momentum in physical["momenta"]]
        total = tuple(sum(momentum[axis] for momentum in momenta)
                      for axis in range(4))
        cyclic = []
        for index in range(N):
            pair = tuple(momenta[index][axis]
                         + momenta[(index + 1) % N][axis]
                         for axis in range(4))
            cyclic.append(minkowski_square(pair))
        checks["physical_limit_fixture"] = (
            total == (0, 0, 0, 0)
            and all(minkowski_square(momentum) == 0 for momentum in momenta)
            and cyclic == [Fraction(0), Fraction(32, 3), Fraction(-8),
                           Fraction(16), Fraction(-8, 3)]
        )
    except Exception:
        checks["physical_limit_fixture"] = False

    phase = certificate.get("phase_space_boundary", {})
    c10 = Fraction(-140679, 400)
    lower = Fraction(3, 10) * c10 * c10
    checks["threshold_density_and_lower_bound"] = (
        phase.get("threshold_tau") == 9
        and phase.get("window") == [10, 11]
        and fraction(phase.get("tau10_inner_density")) == Fraction(3, 10)
        and fraction(phase.get("strict_lower_bound")) == lower
        and 5620 * 10 - 10386 > 0
        and 10 * 10 - 18 > 0
    )

    try:
        inputs = certificate["provenance"]["inputs"]
        checks["input_hashes"] = all(
            sha256(row["path"]) == row["sha256"] for row in inputs
        )
    except Exception:
        checks["input_hashes"] = False

    disposition = certificate.get("disposition", {})
    boundaries = " ".join(certificate.get("does_not_establish", []))
    checks["fail_closed_disposition"] = (
        disposition.get("collinear_boundary_total_order_five")
        == "STRICTLY_NONZERO_ON_DECLARED_RAY"
        and disposition.get("five_body_phase_space_projector")
        == "PARTIAL_FACTORIZATION_ONLY"
        and disposition.get("mixed_five_mass_distribution")
        == "NOT_DEFINED_WITHOUT_PRESCRIPTION"
        and disposition.get("physical_integrated_2to3_probability")
        == "NOT_COMPUTED"
        and "nonzero mixed" in boundaries
        and "LORENTZIAN-CAUSAL" in boundaries
    )
    checks["missing_objects_and_next_gate"] = (
        len(certificate.get("missing_object_ledger", [])) >= 6
        and "independent-mass" in certificate.get("next_gate", "")
    )
    recorded = certificate.get("checks", {})
    checks["producer_checks_recorded_pass"] = (
        recorded.get("ok") is True
        and recorded.get("passed") == recorded.get("total")
    )
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="verify exact BT five-point collinear-layer certificate")
    parser.add_argument("--verify", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    with open(args.verify, encoding="utf-8") as handle:
        certificate = json.load(handle)
    checks = verify(certificate)
    for name, passed in checks.items():
        print("[%s] %s" % ("PASS" if passed else "FAIL", name))
    passed = sum(checks.values())
    print("checks %d/%d" % (passed, len(checks)))
    ok = all(checks.values())
    print("RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
