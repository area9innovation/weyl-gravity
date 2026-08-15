#!/usr/bin/env python3
"""Independent verifier for the BT annealed-response one-loop certificate."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_RESPONSE_ONE_LOOP_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-annealed-response-one-loop-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def compact_symbol(values: tuple[Fraction, ...]) -> Fraction:
    e1 = sum(values, Fraction())
    e2 = sum(
        (
            values[left] * values[right]
            for left in range(4)
            for right in range(left + 1, 4)
        ),
        Fraction(),
    )
    return (
        e1 / 24
        - Fraction(5, 288) * e1**2
        + e2 / 144
        + Fraction(5, 1296) * e1**3
        + Fraction(5, 1728) * e1 * e2
        - Fraction(5, 31104) * e1**4
        - Fraction(13, 31104) * e1**2 * e2
    )


PARTITION_COEFFICIENTS = {
    (1,): Fraction(1, 24),
    (2,): Fraction(-5, 288),
    (1, 1): Fraction(-1, 36),
    (3,): Fraction(5, 1296),
    (2, 1): Fraction(25, 1728),
    (1, 1, 1): Fraction(55, 1728),
    (4,): Fraction(-5, 31104),
    (3, 1): Fraction(-11, 10368),
    (2, 2): Fraction(-7, 3888),
    (2, 1, 1): Fraction(-125, 31104),
    (1, 1, 1, 1): Fraction(-23, 2592),
}


def partition_symbol(values: tuple[Fraction, ...]) -> Fraction:
    total = Fraction()
    for powers, coefficient in PARTITION_COEFFICIENTS.items():
        padded = powers + (0,) * (4 - len(powers))
        orbit = set(itertools.permutations(padded))
        total += coefficient * sum(
            (
                values[0] ** row[0]
                * values[1] ** row[1]
                * values[2] ** row[2]
                * values[3] ** row[3]
                for row in orbit
            ),
            Fraction(),
        )
    return total


def independent_l6() -> Fraction:
    one_axis = (
        Fraction(0),
        Fraction(1),
        Fraction(3),
        Fraction(4),
        Fraction(3),
        Fraction(1),
    )
    total = Fraction()
    for momentum in itertools.product(range(6), repeat=4):
        values = tuple(one_axis[index] for index in momentum)
        omega = sum(values, Fraction())
        if omega:
            total += partition_symbol(values) / omega**2
    return Fraction(-43, 5184) + total / 6**4


def strict_top_level(certificate: dict, schema: dict) -> bool:
    required = set(schema["required"])
    return set(certificate) == required


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

    checks["strict_schema"] = (
        strict_top_level(certificate, schema)
        and not list(Draft202012Validator(schema).iter_errors(certificate))
    )
    inputs = certificate["provenance"]["inputs"]
    checks["provenance_hashes_current"] = len(inputs) == 1 and all(
        file_hash(row["path"]) == row["sha256"] for row in inputs
    )

    fixtures = (
        (Fraction(1), Fraction(2), Fraction(3), Fraction(4)),
        (Fraction(0), Fraction(1), Fraction(3), Fraction(4)),
        (Fraction(2, 3), Fraction(5, 7), Fraction(11, 13), Fraction(17, 19)),
    )
    checks["independent_partition_symbol"] = all(
        compact_symbol(values) == partition_symbol(values) for values in fixtures
    )
    exact_l6 = independent_l6()
    decision = certificate["exact_l6_decision"]
    checks["independent_exact_l6_sum"] = (
        exact_l6 == Fraction(-849547889, 1849425177600)
        and decode(decision["coefficient"]) == exact_l6
        and exact_l6 < 0
        and decision["sign"] == "STRICTLY_NEGATIVE"
    )

    symbol = certificate["one_loop_symbol"]
    checks["symbol_and_kernel_invariants"] = (
        symbol["vacuum_term"] == {"numerator": -43, "denominator": 5184}
        and symbol["covariance_kernel_terms"] == 161
        and decode(symbol["covariance_kernel_sum"]) == 0
        and symbol["derived_x_monomials"] == 69
        and symbol["P"]
        == "e1/24-5*e1^2/288+e2/144+5*e1^3/1296+5*e1*e2/1728-5*e1^4/31104-13*e1^2*e2/31104"
    )

    expansion = certificate["conditional_expansion"]
    checks["conditional_and_marginal_terms_retained"] = (
        expansion["free_conditional_precision"] == 72
        and decode(expansion["free_conditional_variance"]) == Fraction(1, 72)
        and expansion["free_center_terms"] == 40
        and expansion["surviving_component_term_counts"]
        == {"p1": 820, "p2": 40, "p3": 1, "q1": 11480, "q3": 40}
        and "translation" in expansion["annealed_reweighting_cancellation"]
        and "constant-shift" in expansion["annealed_reweighting_cancellation"]
        and "O_L(lambda^4)" in expansion["evenness"]
    )

    corrected = certificate["corrected_distance_two_response"]
    checks["corrected_path_prefactor"] = (
        "exp(psi_y-2*psi_v)" in corrected["axial_path"]
        and "two intermediate sites" in corrected["mixed_path"]
        and "strictly positive" in corrected["sign"]
    )

    limit = certificate["large_volume_reduction"]
    checks["large_volume_reduction_is_fail_closed"] = (
        limit["limit_formula"]
        == "b_(2,infinity)=-85/5184+W4/18+5*I4/288"
        and limit["sign_status"]
        == "OPEN_PENDING_RIGOROUS_WATSON_BESSEL_INTERVAL"
        and "O(|k|^-2)" in limit["convergence"]
    )

    disposition = certificate["method_disposition"]
    checks["method_boundary"] = (
        disposition["annealed_beta_nonnegative_at_all_finite_volumes"]
        == "REFUTED_AT_ONE_LOOP_ON_L6"
        and disposition["large_volume_annealed_beta_sign"]
        == "EXACT_INTEGRAL_REDUCTION_SIGN_OPEN"
        and disposition["interacting_h_minus_one_bound"] == "OPEN"
        and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED"
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
        "REDUCED-MODE",
    ]
    required_nonclaims = {
        "a negative beta_L at lambda=0.4 or at arbitrary coupling",
        "a negative large-volume one-loop coefficient before the Watson/Bessel interval is certified",
        "instability or a negative spectral gap for continuous-time heat-bath dynamics",
        "the normalized lowest-mode or interacting Gibbs H^-1 bound or its failure",
        "a new physical dimension, Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
    }
    checks["required_nonclaims"] = required_nonclaims.issubset(
        set(certificate["does_not_establish"])
    )
    checks["certificate_checks_closed"] = (
        certificate["checks"]["ok"]
        and certificate["checks"]["passed"] == certificate["checks"]["total"]
        and not certificate["checks"]["failures"]
        and all(certificate["checks"]["details"].values())
    )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return all(checks.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
