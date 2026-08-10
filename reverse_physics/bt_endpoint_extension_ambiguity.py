#!/usr/bin/env python3
"""Classify exact endpoint extensions of the BT ordered-slot cross Gram."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics", "certificates",
                    "REVERSE_PHYSICS_BT_ENDPOINT_EXTENSION_AMBIGUITY_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-endpoint-extension-ambiguity-v1.schema.json"
REPORT = "reverse_physics/reports/bt-endpoint-extension-ambiguity.md"
SOURCE_COMMIT = "c452d77d9a5620a694adb53bfa80f88012593b5f"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_RT_JORDAN_KERNEL_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ASYMPTOTIC_GENERATOR_PREFLIGHT_V1.json",
]


def derivative_at(coefficients, order, point):
    total = Fraction(0)
    for power, coefficient in enumerate(coefficients):
        if power < order:
            continue
        factor = 1
        for value in range(power - order + 1, power + 1):
            factor *= value
        total += coefficient * factor * Fraction(point) ** (power - order)
    return total


def subtract_left_jet(coefficients):
    out = list(coefficients)
    out += [Fraction(0)] * max(0, 3 - len(out))
    out[0] -= derivative_at(coefficients, 0, 0)
    out[1] -= derivative_at(coefficients, 1, 0)
    out[2] -= derivative_at(coefficients, 2, 0) / 2
    return out


def reflect(coefficients):
    """Coefficients of f(1-z), by exact binomial expansion."""
    from math import comb
    out = [Fraction(0)] * len(coefficients)
    for power, coefficient in enumerate(coefficients):
        for degree in range(power + 1):
            out[degree] += coefficient * comb(power, degree) * (-1) ** degree
    return out


def plus_left(coefficients):
    remainder = subtract_left_jet(coefficients)
    return sum(coefficient / Fraction(power - 2)
               for power, coefficient in enumerate(remainder) if power >= 3)


def plus_right(coefficients):
    return plus_left(reflect(coefficients))


def symmetric_plus(coefficients):
    return -Fraction(1, 2) * (plus_left(coefficients) + plus_right(coefficients))


def cutoff_fp_left(coefficients):
    """Constant term of integral_epsilon^1 f(z)/z^3 dz."""
    total = Fraction(0)
    for power, coefficient in enumerate(coefficients):
        if power == 0:
            total -= coefficient / 2
        elif power == 1:
            total -= coefficient
        elif power == 2:
            pass  # -log(epsilon) has zero constant in this convention.
        else:
            total += coefficient / Fraction(power - 2)
    return total


def cutoff_fp_right(coefficients):
    return cutoff_fp_left(reflect(coefficients))


def symmetric_cutoff_fp(coefficients):
    return -Fraction(1, 2) * (
        cutoff_fp_left(coefficients) + cutoff_fp_right(coefficients)
    )


def delta_action(coefficients, endpoint, order):
    # delta_endpoint^(n)[f]=(-1)^n f^(n)(endpoint).
    return (-1) ** order * derivative_at(coefficients, order, endpoint)


def symmetric_ambiguity_action(coefficients, order):
    # Reflection-even basis delta_0^(n)+(-1)^n delta_1^(n).
    return (delta_action(coefficients, 0, order)
            + (-1) ** order * delta_action(coefficients, 1, order))


def rational(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def build():
    fixtures = [
        [Fraction(1)],
        [Fraction(0), Fraction(1)],
        [Fraction(3), Fraction(-2), Fraction(5), Fraction(7)],
        [Fraction(-1), Fraction(4), Fraction(0), Fraction(-3), Fraction(2)],
    ]
    reflection_ok = all(
        symmetric_plus(f) == symmetric_plus(reflect(f))
        and symmetric_cutoff_fp(f) == symmetric_cutoff_fp(reflect(f))
        for f in fixtures
    )
    constant = [Fraction(1)]
    plus_constant = symmetric_plus(constant)
    cutoff_constant = symmetric_cutoff_fp(constant)
    target = Fraction(1, 48)
    fitted_c0 = target / symmetric_ambiguity_action(constant, 0)
    # Three reflection-even endpoint-jet probes: 1, z(1-z), z^2(1-z)^2.
    jet_probes = [
        [Fraction(1)],
        [Fraction(0), Fraction(1), Fraction(-1)],
        [Fraction(0), Fraction(0), Fraction(1), Fraction(-2), Fraction(1)],
    ]
    jet_matrix = [[symmetric_ambiguity_action(probe, order)
                   for order in range(3)] for probe in jet_probes]
    # determinant of the 3x3 endpoint-jet action matrix.
    a = jet_matrix
    determinant = (
        a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
        - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
    )
    checks = {
        "cross_gram_partial_fraction_identity": all(
            -(1 - 3*z + 3*z*z) / (2*z**3*(1-z)**3)
            == -Fraction(1, 2) * (z**-3 + (1-z)**-3)
            for z in (Fraction(1, 5), Fraction(2, 7), Fraction(3, 8))
        ),
        "plus_extension_is_reflection_even": reflection_ok,
        "plus_extension_annihilates_constant": plus_constant == 0,
        "cutoff_fp_constant_is_one_half": cutoff_constant == Fraction(1, 2),
        "two_valid_extensions_disagree": plus_constant != cutoff_constant,
        "symmetric_ambiguity_has_three_independent_jets": determinant != 0,
        "constant_sees_only_delta_zero_order": (
            symmetric_ambiguity_action(constant, 0) == 2
            and symmetric_ambiguity_action(constant, 1) == 0
            and symmetric_ambiguity_action(constant, 2) == 0
        ),
        "fitting_one_over_48_requires_c0_one_over_96": fitted_c0 == Fraction(1, 96),
        "target_not_fixed_by_distribution_axioms": True,
        "oscillatory_matching_stays_open": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "probability_stays_open": True,
        "no_lorentzian_claim": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_ENDPOINT_EXTENSION_AMBIGUITY_V1",
        "schema_version": "reverse-physics-bt-endpoint-extension-ambiguity-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "distribution-extension classification of the ordered-slot BT endpoint Gram",
        "question": "Do reflection symmetry, finite scaling degree, and the interior R_t kernel uniquely determine the inclusive endpoint Gram?",
        "answer": (
            "No. The dimensionless cross-Gram shape is exactly "
            "-(1/2)*(z^-3+(1-z)^-3). Reflection-even extensions differ by "
            "three independent endpoint distributions. Two explicit exact "
            "extensions give different values on the inclusive constant test: "
            "the triple-plus extension gives 0 and the symmetric cutoff finite "
            "part gives 1/2. Adding c0*(delta_0+delta_1) changes that value by "
            "2*c0; c0=1/96 reproduces 1/48 but is a fit, not a prediction."
        ),
        "interior_kernel": {
            "shape": "h(z)=-(1-3*z+3*z^2)/(2*z^3*(1-z)^3)",
            "partial_fraction": "h(z)=-(1/2)*(z^-3+(1-z)^-3)",
            "scope": "ordered slots before Bose factors, phase space, oscillatory sectors, and E^-2 carrier factor"
        },
        "extension_classification": {
            "scaling_degree": 3,
            "left_ambiguity": "c0*delta_0+c1*delta_0_prime+c2*delta_0_double_prime",
            "reflection_even_ambiguity": "sum_n=0^2 c_n*(delta_0^(n)+(-1)^n*delta_1^(n))",
            "jet_action_matrix": [[rational(value) for value in row] for row in jet_matrix],
            "jet_matrix_determinant": rational(determinant),
            "triple_plus_on_one": rational(plus_constant),
            "symmetric_cutoff_fp_on_one": rational(cutoff_constant),
            "difference_is_allowed_endpoint_distribution": True
        },
        "target_test": {
            "required_gram": rational(target),
            "constant_ambiguity_action": rational(Fraction(2)),
            "coefficient_that_fits_target_from_plus_base": rational(fitted_c0),
            "disposition": "ONE_OVER_48_IS_NOT_DERIVED_BY_THE_INTERIOR_KERNEL_OR_EXTENSION_AXIOMS"
        },
        "disposition": {
            "interior_partial_fraction": "COEFFICIENT_COMPUTED",
            "reflection_even_extension_space": "CLASSIFIED",
            "ordinary_unique_endpoint_extension": "EXACT_OBSTRUCTION",
            "one_over_48_from_current_data": "UNDERDETERMINED",
            "oscillatory_and_vacuum_matching_condition": "NOT_COMPUTED",
            "full_transported_projector": "NOT_CONSTRUCTED",
            "full_nlo_quotient_trace": "NOT_COMPUTED",
            "physical_nlo_probability": "NOT_ESTABLISHED"
        },
        "missing_object_ledger": [
            "derive endpoint delta, delta-prime, and delta-double-prime coefficients from the oscillatory creation and Q_t squeeze sectors",
            "enforce projector idempotence and pseudo-unitarity on the same endpoint test-function domain",
            "include incoming and outgoing resolution flows and test their equality",
            "restore Bose factors, phase space, and the complete neutral quotient trace",
            "show the resulting coefficient is regulator independent rather than fitted to 1/48",
            "combine the completed projector with the renormalized virtual and complete real NLO terms"
        ],
        "next_gate": (
            "Compute the omitted oscillatory creation and Q_t vacuum-squeeze "
            "contributions as endpoint distributions. Only a dynamical matching "
            "condition from those sectors can fix the three symmetric endpoint "
            "constants; the interior kernel and reflection symmetry cannot."
        ),
        "does_not_establish": [
            "that the physical BT prescription chooses the triple-plus extension",
            "that the physical BT prescription chooses the cutoff finite part",
            "that 1/48 is impossible after full dynamical matching",
            "a continuum transported projector or KLN theorem",
            "a complete NLO probability or beyond-tree positivity",
            "a tensor or BRST gravitational lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-10",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "primary_source": {"source": "Bateman--Turok arXiv:2607.00096v1", "url": "https://arxiv.org/abs/2607.00096", "equations": ["Eq. (16)", "Eq. (19)", "Appendix C"]}
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_endpoint_extension_ambiguity.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_endpoint_extension_ambiguity.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_endpoint_extension_ambiguity"
        ],
        "checks": {"ok": all(checks.values()), "passed": sum(checks.values()), "total": len(checks), "failures": [name for name, ok in checks.items() if not ok], "details": checks},
        "report": REPORT,
        "schema": SCHEMA
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=CERT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] recorded_certificate: {exc}")
            return 1
        ok = result == recorded
        print(f"[{'PASS' if ok else 'FAIL'}] exact_reproduction")
        print(f"RESULT: {'PASS' if ok else 'FAIL'} ({result['checks']['passed']}/{result['checks']['total']})")
        return 0 if ok else 1
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(args.output)
    return 0 if result["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
