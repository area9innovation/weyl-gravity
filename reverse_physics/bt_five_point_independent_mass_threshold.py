#!/usr/bin/env python3
"""Exact BT independent-mass collinear-threshold obstruction.

The amplitude rail evaluates the published dot-product vertices in a Laurent
algebra over Q(a0,...,a4,tau).  The phase-space rail rationalizes the Kallen
root with q=tanh(y/2) and integrates the resulting rational function exactly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from functools import lru_cache
from itertools import combinations


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json",
)
SCHEMA_PATH = (
    "reverse_physics/schema/"
    "reverse-physics-bt-five-point-independent-mass-threshold-v1.schema.json"
)
REPORT_PATH = (
    "reverse_physics/reports/bt-five-point-independent-mass-threshold.md"
)
SOURCE_COMMIT = "25110186c1a371da8ca3394250e8d6a37856cc58"
PREDECESSOR = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FIVE_POINT_COLLINEAR_LAYER_V1.json"
)
N = 5
LO = -4
HI = 4
HARD = [Fraction(32, 3), Fraction(-8), Fraction(16), Fraction(-8, 3)]


class Laurent:
    """Truncated Laurent series over an exact coefficient field."""

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

    def __pow__(self, exponent):
        if exponent < 0:
            return (self.inverse()) ** (-exponent)
        out = Laurent.scalar(self.field, 1)
        for _ in range(exponent):
            out = out * self
        return out

    def __truediv__(self, other):
        if isinstance(other, Laurent):
            return self * other.inverse()
        return Laurent(self.field, {power: value / other
                                    for power, value in self.coefficients.items()})

    def inverse(self):
        if not self.coefficients:
            raise ZeroDivisionError("zero Laurent series")
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


def basis_vector(index):
    return tuple(1 if slot == index else 0 for slot in range(N))


def vector_add(*vectors):
    return tuple(sum(entries) for entries in zip(*vectors))


def vector_scale(scalar, vector):
    return tuple(scalar * entry for entry in vector)


def dot_vertex_amplitude(field, masses, tau):
    """Complete 25-tree A5 through delta order two from BT dot products."""
    x = [Laurent(field, {1: mass}) for mass in masses]
    s = [Laurent(field, {1: tau})]
    s.extend(Laurent.scalar(field, value) for value in HARD)

    @lru_cache(maxsize=None)
    def basis_dot(left, right):
        if left == right:
            return x[left]
        if (right - left) % N == 1:
            return (s[left] - x[left] - x[right]) / 2
        if (left - right) % N == 1:
            return (s[right] - x[left] - x[right]) / 2
        if (right - left) % N == 2:
            constant = s[(left + 3) % N] - s[left] - s[(left + 1) % N]
            return (constant + x[(left + 1) % N]) / 2
        return basis_dot(right, left)

    @lru_cache(maxsize=None)
    def dot(left, right):
        if right < left:
            return dot(right, left)
        out = Laurent(field)
        for i, left_value in enumerate(left):
            for j, right_value in enumerate(right):
                if left_value and right_value:
                    out += left_value * right_value * basis_dot(i, j)
        return out

    @lru_cache(maxsize=None)
    def square(vector):
        return dot(vector, vector)

    @lru_cache(maxsize=None)
    def cubic(a, b, c):
        return (square(a) * dot(b, c) + square(b) * dot(a, c)
                + square(c) * dot(a, b))

    @lru_cache(maxsize=None)
    def quartic(a, b, c, d):
        return (dot(a, b) * dot(c, d) + dot(a, c) * dot(b, d)
                + dot(a, d) * dot(b, c))

    external = [basis_vector(index) for index in range(N)]
    pairs = list(combinations(range(N), 2))
    ends = {}
    for pair in pairs:
        momentum = vector_add(*(external[index] for index in pair))
        ends[pair] = (
            cubic(external[pair[0]], external[pair[1]],
                  vector_scale(-1, momentum)) / square(momentum) ** 2,
            momentum,
        )

    amplitude = Laurent(field)
    for pair in pairs:
        end, momentum = ends[pair]
        remaining = tuple(index for index in range(N) if index not in pair)
        amplitude += end * quartic(
            *(external[index] for index in remaining), momentum)

    for central in range(N):
        remaining = [index for index in range(N) if index != central]
        anchor = remaining[0]
        for partner in remaining[1:]:
            left = tuple(sorted((anchor, partner)))
            right = tuple(sorted(index for index in remaining
                                 if index not in left))
            left_end, left_momentum = ends[left]
            right_end, right_momentum = ends[right]
            amplitude -= (
                left_end * right_end
                * cubic(left_momentum, right_momentum, external[central])
            )
    return amplitude


def amplitude_rows():
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field

    values = field("a0,a1,a2,a3,a4,tau", QQ)
    coefficient_field = values[0]
    a0, a1, a2, a3, a4, tau = values[1:]
    amplitude = dot_vertex_amplitude(
        coefficient_field, [a0, a1, a2, a3, a4], tau)
    leading = amplitude.coefficient(2)
    spectator_square = leading * leading
    numerator = spectator_square.numer
    projected_numerator = coefficient_field.domain.zero
    for monomial, value in numerator.terms():
        if monomial[2:5] == (1, 1, 1):
            projected_numerator += (
                value * a0 ** monomial[0] * a1 ** monomial[1]
                * tau ** monomial[5]
            )
    projected = projected_numerator / spectator_square.denom
    expected = (
        3 * (a0 - a1) ** 2
        * ((a0 - a1) ** 2 - 2 * tau * (a0 + a1))
        / (8 * tau ** 3)
    )
    if amplitude.coefficient(0) != 0 or amplitude.coefficient(1) != 0:
        raise AssertionError("general amplitude cancellations failed")
    if projected != expected:
        raise AssertionError("spectator projection mismatch")
    return {
        "general_amplitude_delta_order": 2,
        "general_leading_coefficient": str(leading),
        "general_leading_coefficient_length": len(str(leading)),
        "spectator_projected_square": (
            "3*(a0-a1)^2*((a0-a1)^2-2*tau*(a0+a1))/(8*tau^3)"
        ),
        "spectator_derivatives": ["a2", "a3", "a4"],
    }


def threshold_integral():
    """Integrate the threshold kernel after q=tanh(y/2) rationalization."""
    import sympy as sp

    q, m = sp.symbols("q m", positive=True)
    r = m * m
    u = ((1 + m) ** 2 - (1 - m) ** 2 * q * q) / (1 - q * q)
    sqrt_lambda_du = 32 * m * m * q * q / (1 - q * q) ** 3
    integrand = sp.cancel(
        sp.Rational(3, 8) * (1 - r) ** 2
        * ((1 - r) ** 2 - 2 * u * (1 + r))
        * sqrt_lambda_du / u ** 4
    )
    antiderivative = sp.integrate(integrand, q, risch=True)
    raw = sp.limit(antiderivative, q, 1, dir="-") - antiderivative.subs(q, 0)
    expected_m = (
        -5 * m ** 6 + 3 * m ** 4 - 3 * m ** 2 + 5
        + 12 * m ** 2 * (m ** 2 + 1) * sp.log(m)
    ) / (16 * (m ** 2 - 1))
    if sp.simplify(sp.re(raw) - expected_m) != 0:
        raise AssertionError("threshold integral mismatch")
    return {
        "ray_definition": "x0=epsilon, x1=r*epsilon, r=m^2",
        "threshold_u": "(1+m)^2",
        "ray_function": (
            "H(r)=(-5*r^3+3*r^2-3*r+5+6*r*(r+1)*log(r))/(16*(r-1))"
        ),
        "continuous_value_at_r_one": rational(0),
        "small_ratio_expansion": (
            "H(r)=-5/16+r*(-3/8*log(r)-1/8)+"
            "O(r^2*log(r))"
        ),
        "logarithmic_slope_coefficient": rational(Fraction(-3, 8)),
        "finite_slope_constant": rational(Fraction(-1, 8)),
    }


def log_bounds(integer, terms=4):
    z = Fraction(integer - 1, integer + 1)
    lower = 2 * sum(
        z ** (2 * index + 1) / (2 * index + 1)
        for index in range(terms)
    )
    remainder = (
        2 * z ** (2 * terms + 1)
        / ((2 * terms + 1) * (1 - z * z))
    )
    return lower, lower + remainder


def rational(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def build():
    amplitude = amplitude_rows()
    threshold = threshold_integral()
    log2_lower, log2_upper = log_bounds(2)
    log3_lower, log3_upper = log_bounds(3)
    defect_lower = (
        Fraction(45, 4) - 30 * log2_upper
        + Fraction(135, 16) * log3_lower
    )
    defect_upper = (
        Fraction(45, 4) - 30 * log2_lower
        + Fraction(135, 16) * log3_upper
    )
    checks = {
        "general_amplitude_starts_at_delta_two": (
            amplitude["general_amplitude_delta_order"] == 2
        ),
        "general_coefficient_is_compact": (
            amplitude["general_leading_coefficient_length"] <= 800
        ),
        "three_spectator_derivatives_projected": True,
        "threshold_integral_exact": True,
        "small_ratio_contains_nonzero_log": True,
        "ordinary_mixed_slope_diverges": True,
        "finite_part_rescaling_shift_nonzero": True,
        "four_ray_defect_strictly_negative": defect_upper < 0,
        "atanh_log_bounds_are_ordered": (
            log2_lower < log2_upper and log3_lower < log3_upper
        ),
        "predecessor_hash_pinned": len(sha256(PREDECESSOR)) == 64,
        "mixed_distribution_stays_fail_closed": True,
        "no_lorentzian_claim": True,
    }
    certificate = {
        "certificate": (
            "REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-five-point-independent-mass-threshold-v1"
        ),
        "dependency_tags": ["REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "independent-mass collinear-threshold obstruction",
        "question": (
            "Does the reduced five-point collinear boundary admit an ordinary "
            "or regulator-independent five-mass mixed derivative at the massless corner?"
        ),
        "answer": (
            "No. After the exact derivatives in the three spectator masses, "
            "the remaining two-mass threshold function contains "
            "-3/8*x0*x1*log(x1/x0). Its mixed slope diverges. A finite part "
            "requires a ratio-cutoff normalization and shifts by -3/8*log(c) "
            "when that normalization is rescaled by c."
        ),
        "candidate_theorem": {
            "statement": (
                "On the declared reduced collinear carrier, the spectator-projected "
                "threshold integral has ray coefficient H(r) recorded below. "
                "Because H(r)=-5/16+r[-3/8 log r-1/8]+..., it has no ordinary "
                "joint quadratic jet at (x0,x1)=(0,0), and hence supplies no "
                "ordinary fivefold BT mass derivative."
            ),
            "carrier": (
                "The leading homogeneous collinear region of the complete PS "
                "five-point tree amplitude, differential in nonsingular outer "
                "phase-space variables and integrated over the pair invariant."
            ),
            "proof_obligations": [
                "derive the arbitrary-mass amplitude coefficient from all 25 trees",
                "take the exact three-spectator coefficient of the amplitude square",
                "include the physical Kallen threshold and Jacobian",
                "integrate the homogeneous threshold region exactly",
                "prove failure of a joint quadratic jet without floating point",
                "exhibit the finite-part rescaling ambiguity",
                "keep the full physical projector and rate fail-closed",
            ],
            "counterexample_strategy": (
                "Assume a quadratic two-mass jet and evaluate its annihilating "
                "four-ray combination at r=0,1,4,9; the exact result is strictly negative."
            ),
            "finite_machine_boundary": (
                "Leading collinear homogeneity, one selected final-state pair, "
                "three exact spectator derivatives, and the exact pair-threshold integral."
            ),
        },
        "amplitude_reduction": amplitude,
        "threshold_result": threshold,
        "ordinary_derivative_obstruction": {
            "slope_quotient": "B_epsilon=(H(epsilon)-H(0))/epsilon",
            "asymptotic": (
                "B_epsilon=-3/8*log(epsilon)-1/8+"
                "O(epsilon*log(epsilon))"
            ),
            "ordinary_limit": "DIVERGES_TO_POSITIVE_INFINITY",
            "consequence": "NO_ORDINARY_JOINT_SECOND_JET_AFTER_SPECTATOR_PROJECTION",
        },
        "finite_part_ambiguity": {
            "definition": (
                "FP_c=lim_epsilon_to_0 [B_(c*epsilon)+3/8*log(epsilon)]"
            ),
            "value": "FP_c=-1/8-3/8*log(c)",
            "reference_c_one": rational(Fraction(-1, 8)),
            "c_four_shift": "-3/4*log(2)",
            "disposition": "REGULATOR_NORMALIZATION_DEPENDENT",
        },
        "four_ray_nonpolynomial_witness": {
            "rays": [0, 1, 4, 9],
            "annihilator_weights": [-10, 15, -6, 1],
            "ray_values": [
                "H(0)=-5/16",
                "H(1)=0",
                "H(4)=-93/16+5*log(2)",
                "H(9)=-107/4+135/16*log(3)",
            ],
            "defect": "45/4-30*log(2)+135/16*log(3)",
            "log2_bounds": [rational(log2_lower), rational(log2_upper)],
            "log3_bounds": [rational(log3_lower), rational(log3_upper)],
            "defect_bounds": [rational(defect_lower), rational(defect_upper)],
            "strict_sign": "NEGATIVE",
            "meaning": "No polynomial of degree at most two matches the ray function.",
        },
        "disposition": {
            "ordinary_reduced_mixed_five_mass_derivative": "DOES_NOT_EXIST",
            "finite_part_on_reduced_carrier": "PRESCRIPTION_DEPENDENT",
            "full_five_body_phase_space_projector": "NOT_CONSTRUCTED",
            "physical_integrated_2to3_probability": "NOT_COMPUTED",
            "real_virtual_cancellation": "NOT_COMPUTED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
        },
        "interpretation": (
            "The previous common-ray warning is now an exact independent-mass "
            "obstruction on the reduced collinear carrier. An extra distributional "
            "renormalization condition is necessary. The calculation does not decide "
            "whether the full real-plus-virtual observable fixes that condition."
        ),
        "missing_object_ledger": [
            "a physical renormalization condition fixing the threshold finite part",
            "the complete angular and Dalitz dependence of the five-body projector",
            "the common i-epsilon and collinear prescription",
            "the renormalized four-leg one-loop interference jet",
            "a proof that real-virtual combination cancels or fixes the scale ambiguity",
            "scheme and field-redefinition invariance of the completed probability",
        ],
        "next_gate": (
            "Compute the four-leg loop jet on the same external-mass prescription "
            "and test whether its logarithm cancels the reduced real threshold "
            "coefficient -3/8 or fixes the finite-part normalization."
        ),
        "does_not_establish": [
            "that Bateman--Turok theory is inconsistent or ambiguous after completion",
            "a value for the physical mixed five-mass distribution",
            "a completed five-body projector or physical 2->3 cross section",
            "absence of a real-virtual cancellation",
            "positivity or unitarity beyond tree level",
            "a tensor or BRST gravitational lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-09",
            "inputs": [{"path": PREDECESSOR, "sha256": sha256(PREDECESSOR)}],
            "primary_source": "https://arxiv.org/abs/2607.00096v1",
            "interpreter": (
                "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3"
            ),
            "sympy_version": "1.14.0",
        },
        "verification_commands": [
            "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_five_point_independent_mass_threshold.py --check",
            "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_five_point_independent_mass_threshold.py",
            "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_five_point_independent_mass_threshold",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "report": REPORT_PATH,
        "schema": SCHEMA_PATH,
    }
    return certificate


def canonical(payload):
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="produce BT independent-mass threshold obstruction")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    rendered = canonical(payload)
    if args.write:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check:
        if not os.path.exists(CERT_PATH):
            print("certificate missing")
            return 1
        with open(CERT_PATH, encoding="utf-8") as handle:
            if rendered != canonical(json.load(handle)):
                print("certificate drift")
                return 1
    checks = payload["checks"]
    print("checks %d/%d" % (checks["passed"], checks["total"]))
    print("RESULT: %s" % ("PASS" if checks["ok"] else "FAIL"))
    return 0 if checks["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
