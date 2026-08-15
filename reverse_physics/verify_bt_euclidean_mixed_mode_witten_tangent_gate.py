#!/usr/bin/env python3
"""Independent verifier for the BT mixed-mode Witten tangent gate."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_"
    "MIXED_MODE_WITTEN_TANGENT_GATE_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-"
    "mixed-mode-witten-tangent-gate-v1.schema.json",
)
PRODUCER_NAME = "bt_euclidean_mixed_mode_witten_tangent_gate"


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def producer_not_imported() -> bool:
    with open(__file__, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(PRODUCER_NAME in alias.name for alias in node.names):
                return False
        elif isinstance(node, ast.ImportFrom) and node.module:
            if PRODUCER_NAME in node.module:
                return False
    return True


Polynomial = dict[tuple[int, int], Fraction]


def pclean(value: Polynomial) -> Polynomial:
    return {monomial: coefficient for monomial, coefficient in value.items() if coefficient}


def padd(*values: Polynomial) -> Polynomial:
    out: Polynomial = {}
    for value in values:
        for monomial, coefficient in value.items():
            out[monomial] = out.get(monomial, Fraction(0)) + coefficient
    return pclean(out)


def pscale(value: Polynomial, scalar: Fraction | int) -> Polynomial:
    scalar = Fraction(scalar)
    return pclean({monomial: scalar * coefficient for monomial, coefficient in value.items()})


def pmul(left: Polynomial, right: Polynomial) -> Polynomial:
    out: Polynomial = {}
    for (left_a, left_d), left_coefficient in left.items():
        for (right_a, right_d), right_coefficient in right.items():
            monomial = left_a + right_a, left_d + right_d
            out[monomial] = out.get(monomial, Fraction(0)) + left_coefficient * right_coefficient
    return pclean(out)


def pderivative(value: Polynomial, axis: int) -> Polynomial:
    out: Polynomial = {}
    for monomial, coefficient in value.items():
        power = monomial[axis]
        if power:
            lowered = list(monomial)
            lowered[axis] -= 1
            out[tuple(lowered)] = coefficient * power
    return pclean(out)


def gaussian_moment(power: int) -> Fraction:
    if power % 2:
        return Fraction(0)
    value = Fraction(1)
    for factor in range(power - 1, 0, -2):
        value *= factor
    return value


def gaussian_expectation(value: Polynomial) -> Fraction:
    return sum(
        (
            coefficient * gaussian_moment(a_power) * gaussian_moment(d_power)
            for (a_power, d_power), coefficient in value.items()
        ),
        Fraction(0),
    )


def reduced_action() -> Polynomial:
    return {
        (2, 0): Fraction(1, 2),
        (0, 2): Fraction(1, 2),
        (2, 1): Fraction(-1),
        (4, 0): Fraction(5, 8),
        (2, 2): Fraction(5, 4),
        (0, 4): Fraction(5, 32),
    }


def homogeneous(value: Polynomial, degree: int) -> Polynomial:
    return {
        monomial: coefficient
        for monomial, coefficient in value.items()
        if sum(monomial) == degree
    }


def reduced_relative_coefficient(mixed_b: Fraction) -> Fraction:
    """Rebuild the normalized lambda^2 Rayleigh coefficient."""
    b = Fraction(mixed_b)
    action = reduced_action()
    h_aa = pderivative(pderivative(action, 0), 0)
    h_ad = pderivative(pderivative(action, 0), 1)
    h_dd = pderivative(pderivative(action, 1), 1)
    tangent_d = {(1, 0): 2 * b}
    hessian_form = padd(
        h_aa,
        pscale(pmul(tangent_d, h_ad), 2),
        pmul(pmul(tangent_d, tangent_d), h_dd),
    )

    h0 = homogeneous(hessian_form, 0)
    h1 = homogeneous(hessian_form, 1)
    h2 = homogeneous(hessian_form, 2)
    action3 = homogeneous(action, 3)
    action4 = homogeneous(action, 4)
    weight1 = pscale(action3, -1)
    weight2 = padd(pscale(pmul(action3, action3), Fraction(1, 2)), pscale(action4, -1))
    z2 = gaussian_expectation(weight2)
    expected_h2 = (
        gaussian_expectation(h2)
        + gaussian_expectation(pmul(h1, weight1))
        + gaussian_expectation(pmul(h0, weight2))
        - gaussian_expectation(h0) * z2
    )
    # The derivative cost b^2 and the order-lambda^2 norm correction b^2
    # cancel in lambda^2*Q/||v||^2, leaving expected_h2.
    return expected_h2


def free_fixture_reconstruction() -> dict[str, Fraction]:
    volume = Fraction(4**4)
    omega = Fraction(2)
    coupling = Fraction(2, 5)
    b = Fraction(5, 3)
    q = 2 * b
    amplitude_variance = coupling**2 / (volume * omega**2)
    derivative_cost = q**2 / 4
    transverse_hessian_cost = q**2
    norm = volume + q**2 * amplitude_variance * volume / 4
    form = volume * omega**2 / coupling**2 + derivative_cost + transverse_hessian_cost
    rayleigh = form / norm
    free_rayleigh = omega**2 / coupling**2
    return {
        "x": q**2 * coupling**2 / (4 * volume * omega**2),
        "norm": norm,
        "form": form,
        "rayleigh": rayleigh,
        "free_rayleigh": free_rayleigh,
        "relative": rayleigh / free_rayleigh,
        "increase": rayleigh - free_rayleigh,
    }


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    checks["strict_schema"] = not list(Draft202012Validator(schema).iter_errors(certificate))
    checks["producer_not_imported"] = producer_not_imported()
    inputs = certificate["provenance"]["inputs"]
    checks["provenance_hashes_current"] = len(inputs) == 2 and all(
        file_hash(item["path"]) == item["sha256"] for item in inputs
    )

    rebuilt_free = free_fixture_reconstruction()
    stored_free = certificate["exact_free_fixture"]
    checks["free_fixture_reconstructed"] = (
        rebuilt_free["x"] == decode(stored_free["x"])
        and rebuilt_free["norm"] == decode(stored_free["one_form_norm_squared"])
        and rebuilt_free["form"] == decode(stored_free["witten_form"])
        and rebuilt_free["rayleigh"] == decode(stored_free["rayleigh_quotient"])
        and rebuilt_free["relative"] == decode(stored_free["relative_factor"])
        and rebuilt_free["increase"] == decode(stored_free["strict_increase"])
    )
    checks["free_strict_increase"] = rebuilt_free["relative"] == Fraction(2309, 2305) > 1

    tested_b = (Fraction(0), Fraction(1), Fraction(2), Fraction(5, 3))
    checks["reduced_coefficients_reconstructed"] = all(
        reduced_relative_coefficient(b) == 4 * (b * b - 2 * b + 2)
        for b in tested_b
    )
    reduced = certificate["exact_reduced_fixture"]
    checks["reduced_positive_completion"] = (
        reduced_relative_coefficient(Fraction(1)) == decode(reduced["minimum_coefficient"]) == 4
        and reduced_relative_coefficient(Fraction(5, 3))
        == decode(reduced["coefficient_at_deterministic_resonance"])
        == Fraction(52, 9)
    )

    free_theorem = certificate["free_lattice_theorem"]
    reduced_theorem = certificate["reduced_interacting_theorem"]
    checks["theorem_formulas_recorded"] = (
        free_theorem["derivative_cost"] == "||D v_q||_HS^2=q^2/4"
        and free_theorem["form"] == "Q_1(v_q)=N omega_L^2/lambda^2+5q^2/4"
        and free_theorem["conclusion"]
        == "R_q>=omega_L^2/lambda^2, with equality iff q=0"
        and reduced_theorem["weak_expansion"]
        == "lambda^2 R_b(lambda)=1+4((b-1)^2+1)lambda^2+O(lambda^4)"
        and reduced_theorem["deterministic_resonance"]
        == "at b=5/3 the coefficient is 52/9>0"
    )
    checks["method_boundary"] = certificate["method_disposition"] == {
        "mixed_deterministic_coefficient_one": "OBSTRUCTED_BY_PREDECESSOR",
        "canonical_mixed_tangent_free_low_rayleigh": "RULED_OUT",
        "canonical_mixed_tangent_reduced_weak_low_rayleigh": "RULED_OUT_TO_FIRST_INTERACTING_ORDER",
        "arbitrary_full_witten_low_rayleigh_sequence": "OPEN",
        "volume_uniform_witten_coercivity": "OPEN",
        "normalized_lowest_mode_bound": "OPEN",
        "interacting_h_minus_one_bound": "OPEN",
        "continuum_reconstruction": "NOT_ESTABLISHED",
        "born_rule": "NOT_ESTABLISHED",
        "krein_reconstruction": "NOT_ASSESSED",
        "lorentzian_transfer": "NOT_ESTABLISHED",
    }
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"
    ]
    checks["required_nonclaims"] = {
        "a lower bound for every one-form in the full interacting Witten cyclic sector",
        "boundedness or divergence of the actual interacting H^-1 moment",
        "a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
    }.issubset(set(certificate["does_not_establish"]))
    checks["certificate_checks_closed"] = (
        certificate["checks"]["ok"]
        and certificate["checks"]["passed"] == certificate["checks"]["total"]
        and not certificate["checks"]["failures"]
        and all(certificate["checks"]["details"].values())
    )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    passed = sum(checks.values())
    print(f"RESULT: {'PASS' if passed == len(checks) else 'FAIL'} ({passed}/{len(checks)})")
    return passed == len(checks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
