#!/usr/bin/env python3
"""Independent verifier for the BT local-potential regulator trilemma.

This verifier does not import the producer.  It evaluates the recorded sparse
polynomials at exact rational fixtures and derives the gradient, Hessian, and
determinant directly from F(s)=a0+a1*s+a2*s^2+a3*s^3.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "certificates",
    "REVERSE_PHYSICS_BT_IR_REGULATOR_TRILEMMA_V1.json",
)
SCHEMA = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-ir-regulator-trilemma-v1.schema.json",
)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def evaluate_terms(terms, values):
    total = Fraction(0)
    for term in terms:
        coefficient = term["coefficient"]
        value = Fraction(coefficient["numerator"], coefficient["denominator"])
        for name, exponent in term["powers"].items():
            value *= Fraction(values[name]) ** int(exponent)
        total += value
    return total


def f_prime(coefficients, s):
    return sum(
        Fraction(power) * coefficient * s ** (power - 1)
        for power, coefficient in enumerate(coefficients)
        if power
    )


def f_double_prime(coefficients, s):
    return sum(
        Fraction(power * (power - 1)) * coefficient * s ** (power - 2)
        for power, coefficient in enumerate(coefficients)
        if power >= 2
    )


def det2(matrix):
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def derived_at_point(coefficients, omega, upsilon, z):
    s = omega * upsilon
    fp = f_prime(coefficients, s)
    fpp = f_double_prime(coefficients, s)
    gradient = (upsilon * fp, omega * fp)
    hessian = (
        (upsilon * upsilon * fpp, fp + s * fpp),
        (fp + s * fpp, omega * omega * fpp),
    )
    kinetic = (
        (hessian[0][0], hessian[0][1] - z),
        (hessian[1][0] - z, hessian[1][1]),
    )
    return gradient, hessian, det2(kinetic)


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
    checks["identity"] = (
        certificate.get("certificate")
        == "REVERSE_PHYSICS_BT_IR_REGULATOR_TRILEMMA_V1"
        and certificate.get("schema_version")
        == "reverse-physics-bt-ir-regulator-trilemma-v1"
    )
    checks["boundary"] = (
        certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC"]
        and certificate.get("lifecycle_state") == "CLASSIFIED"
        and any(
            "LORENTZIAN-CAUSAL" in item
            for item in certificate.get("does_not_establish", [])
        )
    )
    checks["producer_checks_recorded"] = (
        certificate.get("checks", {}).get("ok") is True
        and certificate.get("checks", {}).get("passed")
        == certificate.get("checks", {}).get("total")
        and not certificate.get("checks", {}).get("failures")
    )
    checks["four_independence_witnesses"] = (
        len(certificate.get("independence_witnesses", [])) == 4
        and all(row.get("drop") and row.get("witness")
                for row in certificate.get("independence_witnesses", []))
    )
    inputs = certificate.get("provenance", {}).get("inputs", [])
    try:
        checks["input_hashes"] = bool(inputs) and all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        )
    except (KeyError, OSError):
        checks["input_hashes"] = False

    identities = certificate.get("polynomial_identities", {})
    required = {
        "BT_branch_gradient", "BT_branch_hessian",
        "BT_branch_pole_polynomial",
        "stationary_nonzero_branch_pole_polynomial",
        "mass_deformation_held_background",
        "mass_deformation_true_vacuum",
    }
    checks["identity_set"] = required <= set(identities)
    if not checks["identity_set"]:
        return checks

    # A cubic term probes that the verifier has not silently assumed the
    # producer's two-jet before restricting to s=0.
    fixtures = [
        (Fraction(2), Fraction(3), Fraction(5), Fraction(7), Fraction(11)),
        (Fraction(-3, 2), Fraction(4, 3), Fraction(-2), Fraction(5, 2), Fraction(-7, 3)),
        (Fraction(5, 4), Fraction(-8, 5), Fraction(9, 7), Fraction(-3, 2), Fraction(13, 6)),
    ]
    bt_ok = shifted_ok = mass_ok = True
    for v, a1, a2, mu2, z in fixtures:
        coefficients = (Fraction(17, 5), a1, a2 / 2, Fraction(19, 11))
        gradient, hessian, pole = derived_at_point(coefficients, v, Fraction(0), z)
        values = {"v": v, "f1": a1, "f2": a2, "z": z}
        recorded_gradient = tuple(
            evaluate_terms(component, values)
            for component in identities["BT_branch_gradient"]["components"]
        )
        recorded_hessian = tuple(tuple(evaluate_terms(component, values)
                                       for component in row)
                                   for row in identities["BT_branch_hessian"]["components"])
        recorded_pole = evaluate_terms(
            identities["BT_branch_pole_polynomial"]["terms"], values)
        bt_ok = bt_ok and (
            gradient == recorded_gradient
            and hessian == recorded_hessian
            and pole == recorded_pole
            and ((gradient == (0, 0)) == (a1 == 0))
        )

        # Construct a polynomial whose first two derivatives at s0 have the
        # declared values, then independently evaluate at (v,s0/v).
        s0 = Fraction(3, 7)
        shifted_coefficients = (a2 * s0 * s0 / 2, -a2 * s0, a2 / 2)
        shifted_gradient, _, shifted_pole = derived_at_point(
            shifted_coefficients, v, s0 / v, z)
        shifted_values = {"s0": s0, "f2": a2, "z": z}
        shifted_recorded = evaluate_terms(
            identities["stationary_nonzero_branch_pole_polynomial"]["terms"],
            shifted_values,
        )
        shifted_ok = shifted_ok and shifted_gradient == (0, 0) and (
            shifted_pole == shifted_recorded
        )

        lambda2 = a2 if a2 else Fraction(1)
        mass_coefficients = (Fraction(0), mu2, lambda2 / 2)
        held_gradient, _, held_pole = derived_at_point(
            mass_coefficients, v, Fraction(0), z)
        mass_values = {"v": v, "mu2": mu2, "z": z}
        held_gradient_recorded = tuple(
            evaluate_terms(component, mass_values)
            for component in identities["mass_deformation_held_background"]["gradient"]
        )
        held_pole_recorded = evaluate_terms(
            identities["mass_deformation_held_background"]["pole_terms"],
            mass_values,
        )
        true_s = -mu2 / lambda2
        true_gradient, _, true_pole = derived_at_point(
            mass_coefficients, v, true_s / v, z)
        true_pole_recorded = evaluate_terms(
            identities["mass_deformation_true_vacuum"]["pole_terms"],
            mass_values,
        )
        mass_ok = mass_ok and (
            held_gradient == held_gradient_recorded
            and held_gradient[1] == v * mu2
            and held_pole == held_pole_recorded
            and true_gradient == (0, 0)
            and true_pole == true_pole_recorded
            and evaluate_terms(
                identities["mass_deformation_true_vacuum"]["pole_terms"],
                {"mu2": mu2, "z": Fraction(0)},
            ) == 0
            and evaluate_terms(
                identities["mass_deformation_true_vacuum"]["pole_terms"],
                {"mu2": mu2, "z": -2 * mu2},
            ) == 0
        )

    checks["independent_BT_branch_derivation"] = bt_ok
    checks["independent_stationary_branch_derivation"] = shifted_ok
    checks["independent_mass_deformation_derivation"] = mass_ok
    checks["fixed_v_source_charge"] = (
        "charge -1" in certificate["independence_witnesses"][1]["witness"]
        and "spurion" in certificate["independence_witnesses"][1]["witness"]
    )
    checks["predecessor_correction_is_fail_closed"] = (
        certificate.get("correction_to_predecessor", {}).get("predecessor")
        == "REVERSE_PHYSICS_CHARGE_GRADING_LOOP_STABILITY_V1"
        and bool(certificate.get("correction_to_predecessor", {}).get("withdrawn"))
        and bool(certificate.get("correction_to_predecessor", {}).get("retained"))
    )
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description="independent BT trilemma verifier")
    parser.add_argument("--verify", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    with open(args.verify, encoding="utf-8") as handle:
        certificate = json.load(handle)
    checks = verify(certificate)
    for name, passed in checks.items():
        print(("[OK ] " if passed else "[FAIL] ") + name)
    failures = [name for name, passed in checks.items() if not passed]
    print("checks %d/%d" % (len(checks) - len(failures), len(checks)))
    print("RESULT: %s" % ("PASS" if not failures else "FAIL"))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
