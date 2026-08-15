#!/usr/bin/env python3
"""Independent verifier for the BT annealed-response Watson bound."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction
from functools import lru_cache

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_RESPONSE_WATSON_BOUND_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-annealed-response-watson-bound-v1.schema.json",
)
W_TRUNCATION = 2500
POTENTIAL_TRUNCATION = 10


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction_hash(value: Fraction) -> str:
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    canonical = f"{value.numerator}/{value.denominator}".encode("ascii")
    return hashlib.sha256(canonical).hexdigest()


@lru_cache(maxsize=1)
def multinomial_origin_counts(limit: int) -> tuple[int, ...]:
    """Independent closed-walk formula, without the producer recurrence."""

    counts = []
    for n in range(limit + 1):
        if n == 0:
            counts.append(1)
            continue
        central = math.comb(2 * n, n)
        term = central
        inner = term
        for k in range(n):
            remaining = n - k
            numerator = term * remaining**3 * (2 * k + 1)
            denominator = (k + 1) ** 3 * (2 * remaining - 1)
            term, remainder = divmod(numerator, denominator)
            if remainder:
                raise ArithmeticError(f"nonintegral multinomial ratio n={n}, k={k}")
            inner += term
        counts.append(central * inner)
    return tuple(counts)


@lru_cache(maxsize=None)
def direct_diagonal_endpoint_count(n: int) -> int:
    """Direct four-coordinate composition for endpoint (1,1,0,0)."""

    if n == 0:
        return 0
    factorial = math.factorial
    total = Fraction()
    for first in range(n):
        for second in range(n - first):
            for third in range(n - first - second):
                fourth = n - 1 - first - second - third
                total += Fraction(
                    factorial(2 * n),
                    factorial(first)
                    * factorial(first + 1)
                    * factorial(second)
                    * factorial(second + 1)
                    * factorial(third) ** 2
                    * factorial(fourth) ** 2,
                )
    if total.denominator != 1:
        raise ArithmeticError(f"nonintegral direct endpoint count n={n}")
    return total.numerator


def scaled_partial(counts: tuple[int, ...]) -> Fraction:
    numerator = 0
    for count in counts:
        numerator = 64 * numerator + count
    return Fraction(numerator, 8 * 64 ** (len(counts) - 1))


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
        set(certificate) == set(schema["required"])
        and not list(Draft202012Validator(schema).iter_errors(certificate))
    )
    inputs = certificate["provenance"]["inputs"]
    checks["provenance_hashes_current"] = len(inputs) == 1 and all(
        file_hash(row["path"]) == row["sha256"] for row in inputs
    )

    counts = multinomial_origin_counts(W_TRUNCATION)
    partial = scaled_partial(counts)
    watson = certificate["watson_return_series"]
    tail = Fraction(121, 784 * W_TRUNCATION)
    checks["independent_multinomial_reconstruction"] = (
        list(counts[:6]) == watson["initial_values"]
        and fraction_hash(partial) == watson["partial_fraction_sha256"]
        and len(str(partial.numerator))
        == watson["partial_numerator_decimal_digits"]
        and len(str(partial.denominator))
        == watson["partial_denominator_decimal_digits"]
    )
    checks["watson_tail_and_strict_bound"] = (
        decode(watson["tail_upper"]) == tail
        and partial + tail < decode(watson["computed_upper_below"])
        and decode(watson["computed_upper_below"]) == Fraction(15499, 100000)
        and partial + tail < decode(watson["certified_upper"])
        and decode(watson["certified_upper"]) == Fraction(31, 200)
        and watson["certified_bound"] == "W4<31/200"
    )

    endpoints = [
        direct_diagonal_endpoint_count(n)
        for n in range(POTENTIAL_TRUNCATION + 1)
    ]
    potential = sum(
        (
            Fraction(counts[n] - endpoints[n], 8 * 64**n)
            for n in range(POTENTIAL_TRUNCATION + 1)
        ),
        Fraction(),
    )
    derivative = certificate["derivative_moment_potential_kernel"]
    checks["independent_endpoint_reconstruction"] = (
        endpoints == derivative["endpoint_counts"]
        and list(counts[: POTENTIAL_TRUNCATION + 1]) == derivative["origin_counts"]
        and all(counts[n] >= endpoints[n] for n in range(POTENTIAL_TRUNCATION + 1))
        and decode(derivative["partial_potential"]) == potential
        and potential == Fraction(2558322539133673, 18014398509481984)
    )
    i_upper = 1 - 4 * potential
    checks["potential_and_i_strict_bound"] = (
        potential > decode(derivative["partial_exceeds"])
        and decode(derivative["partial_exceeds"]) == Fraction(71, 500)
        and decode(derivative["exact_i_upper_from_partial"]) == i_upper
        and i_upper < decode(derivative["certified_upper"])
        and decode(derivative["certified_upper"]) == Fraction(54, 125)
        and derivative["certified_bound"] == "I4<54/125"
    )

    beta_upper = (
        Fraction(-85, 5184)
        + Fraction(31, 200 * 18)
        + Fraction(5, 288) * Fraction(54, 125)
    )
    decision = certificate["large_volume_decision"]
    checks["exact_negative_limit_decision"] = (
        beta_upper == Fraction(-37, 129600)
        and decode(decision["upper"]) == beta_upper
        and decision["sign"] == "STRICTLY_NEGATIVE"
        and decision["status"] == "LARGE_VOLUME_ONE_LOOP_SIGN_CERTIFIED"
    )

    with open(os.path.join(ROOT, inputs[0]["path"]), encoding="utf-8") as handle:
        predecessor = json.load(handle)
    checks["imported_formula_matches_predecessor"] = (
        predecessor["large_volume_reduction"]["limit_formula"]
        == decision["imported_formula"]
        == "b_(2,infinity)=-85/5184+W4/18+5*I4/288"
    )

    consequence = certificate["method_consequence"]
    disposition = certificate["method_disposition"]
    checks["perturbative_method_boundary"] = (
        consequence["single_site_annealed_beta_nonnegative"]
        == "OBSTRUCTED_AT_LARGE_VOLUME_ONE_LOOP"
        and "coefficientwise" in consequence["scope"]
        and "resummed nonperturbative beta" in consequence["does_not_extend_to"]
        and disposition["annealed_single_site_signed_response_one_loop"]
        == "OBSTRUCTED_AT_LARGE_VOLUME"
        and disposition["nonperturbative_annealed_response"] == "OPEN"
        and disposition["interacting_h_minus_one_bound"] == "OPEN"
        and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED"
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
        "REDUCED-MODE",
    ]
    required_nonclaims = {
        "a negative nonperturbative beta_L at lambda=0.4 or any fixed coupling",
        "instability or a negative spectral gap for continuous-time heat-bath dynamics",
        "failure of block conditioning, direct score estimates, or every Witten method",
        "failure of the normalized lowest-mode or interacting Gibbs H^-1 bound",
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
