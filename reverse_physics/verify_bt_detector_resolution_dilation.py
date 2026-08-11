#!/usr/bin/env python3
"""Independent verifier for the BT detector-resolution dilation theorem."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_DETECTOR_RESOLUTION_DILATION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-detector-resolution-dilation-v1.schema.json",
)
PHYSICAL = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_SHELL_PSEUDOUNITARY_COMPLETION_V1.json",
)
LOG_SHELL = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_LOG_SHELL_MOLLER_LIMIT_V1.json",
)


def load(path):
    with open(path) as handle:
        return json.load(handle)


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def polynomial_integral(coefficients, left, right):
    coefficients = [frac(value) for value in coefficients]

    def primitive(x):
        x = Fraction(x)
        return sum(
            coefficient * x ** (power + 1) / (power + 1)
            for power, coefficient in enumerate(coefficients)
        )

    return primitive(right) - primitive(left)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate):
    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    profiles = certificate.get("profile_fixtures", {})
    sharp = profiles.get("sharp", {}).get("unit_shift_density", [])
    cubic = profiles.get("cubic_smoothstep", {}).get("unit_shift_density", [])
    response = certificate.get("physical_response", {})
    algebra = certificate.get("detector_algebra", {})
    cocycle = certificate.get("dilation_cocycle", {})
    disposition = certificate.get("disposition", {})

    def integrate_pieces(pieces):
        answer = Fraction(0)
        for piece in pieces:
            left, right = (frac(value) for value in piece["interval"])
            answer += polynomial_integral(
                piece["density_coefficients_ascending"], left, right
            )
        return answer

    try:
        sharp_trace = integrate_pieces(sharp)
        cubic_trace = integrate_pieces(cubic)
        cubic_coefficients = [
            [frac(value) for value in piece["density_coefficients_ascending"]]
            for piece in cubic
        ]
        cubic_intervals = [
            tuple(frac(value) for value in piece["interval"]) for piece in cubic
        ]
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        sharp_trace = cubic_trace = Fraction(-1)
        cubic_coefficients = []
        cubic_intervals = []

    physical_source = load(PHYSICAL).get("response_ledger", {})
    log_source = load(LOG_SHELL)
    gamma = frac(response.get("real_per_pair_born_normalized_per_unit_a", {"numerator": 0, "denominator": 1}))
    pair_count = response.get("pair_count", 0)
    real = pair_count * gamma
    hard_amplitude = frac(response.get("hard_amplitude_real_part_per_unit_a", {"numerator": 0, "denominator": 1}))
    hard_probability = 2 * hard_amplitude
    born = frac(response.get("born_coefficient", {"numerator": 0, "denominator": 1}))
    checks = {
        "schema": not errors,
        "sharp_unit_response": (
            len(sharp) == 1
            and sharp_trace == 1
            and frac(sharp[0].get("integral", {})) == 1
        ),
        "smooth_exact_polynomials": (
            cubic_coefficients
            == [
                [Fraction(0), Fraction(0), Fraction(3), Fraction(-2)],
                [Fraction(-4), Fraction(12), Fraction(-9), Fraction(2)],
            ]
            and cubic_intervals == [(Fraction(0), Fraction(1)), (Fraction(1), Fraction(2))]
        ),
        "smooth_unit_response": (
            len(cubic) == 2
            and cubic_trace == 1
            and [frac(piece["integral"]) for piece in cubic]
            == [Fraction(1, 2), Fraction(1, 2)]
        ),
        "smooth_positivity_witnesses": (
            len(cubic) == 2
            and cubic[0].get("positivity_witness") == "y^2*(3-2*y)"
            and cubic[1].get("positivity_witness") == "(2-y)^2*(2*y-1)"
        ),
        "general_trace_identity": (
            algebra.get("positivity") == "d_(R,a)>=0"
            and algebra.get("trace_theorem") == "integral_R d_(R,a)(y) dy=a"
            and "endpoint jump" in algebra.get("trace_proof", "")
        ),
        "dilation_covariance": (
            cocycle.get("translation") == "(T_b f)(y)=f(y-b)"
            and cocycle.get("cutoff_covariance") == "d_(R+b,a)=T_b d_(R,a)"
            and cocycle.get("shell_covariance") == "u_(R+b,a)=T_b u_(R,a)"
            and cocycle.get("unit_norm") == "integral |u_(R,a)|^2 dy=1"
        ),
        "source_real_and_hard_coefficients": (
            frac(physical_source.get("real_per_pair_Born_normalized", {})) == Fraction(1, 48)
            and frac(physical_source.get("real_total_Born_normalized", {})) == Fraction(1, 16)
            and frac(physical_source.get("forced_hard_survival_Born_normalized", {})) == Fraction(-1, 16)
            and frac(physical_source.get("forced_hard_absolute", {})) == Fraction(-3, 512)
        ),
        "independent_response_arithmetic": (
            gamma == Fraction(1, 48)
            and pair_count == 3
            and real == Fraction(1, 16)
            and hard_amplitude == Fraction(-1, 32)
            and hard_probability == Fraction(-1, 16)
            and real + hard_probability == 0
            and born * real == Fraction(3, 512)
            and born * hard_probability == Fraction(-3, 512)
        ),
        "physical_state_is_scoped": (
            response.get("state")
            == "PHYSICAL_NLO_LEADING_LOG_RESOLUTION_RESPONSE_COMPUTED_ON_DECLARED_FINAL_PAIR_CYLINDER"
            and response.get("profile_disposition")
            == "SHARP_SMOOTH_AND_ALL_ADMISSIBLE_MONOTONE_PROFILES_AGREE"
        ),
        "predecessor_obstruction_retained": (
            log_source.get("disposition", {}).get("ordinary_L2_strong_Moller_limit")
            == "EXACT_OBSTRUCTION"
            and disposition.get("ordinary_strong_Moller_limit")
            == "EXACT_OBSTRUCTION_RETAINED"
        ),
        "affiliation_boundary": (
            disposition.get("abstract_boundary_fibre_affiliation")
            == "AFFILIATED_TO_ASYMPTOTIC_MOMENTUM_RESOLUTION_ALGEBRA"
            and disposition.get("spacetime_local_LSZ_or_AQFT_affiliation")
            == "NOT_ESTABLISHED"
            and disposition.get("time_asymptotic_Hamiltonian") == "NOT_CONSTRUCTED"
            and disposition.get("incoming_degenerate_sector_completion")
            == "NOT_CONSTRUCTED"
        ),
        "no_claim_promotion": (
            disposition.get("finite_complete_NLO_probability") == "NOT_ESTABLISHED"
            and disposition.get("beyond_tree_positivity") == "NOT_ESTABLISHED"
            and disposition.get("Eq19_all_orders") == "NOT_PROVED"
            and "anything LORENTZIAN-CAUSAL"
            in certificate.get("does_not_establish", [])
        ),
        "hashes": (
            len(certificate.get("provenance", {}).get("inputs", [])) == 5
            and all(
                row["sha256"] == sha256(row["path"])
                for row in certificate.get("provenance", {}).get("inputs", [])
            )
        ),
        "producer_ledger": (
            certificate.get("checks", {}).get("passed")
            == certificate.get("checks", {}).get("total")
            == 24
            and certificate.get("checks", {}).get("failures") == []
            and all(certificate.get("checks", {}).get("details", {}).values())
        ),
    }
    for error in errors:
        print("schema", list(error.path), error.message)
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        print("BT DETECTOR RESOLUTION DILATION VERIFY: FAIL", *failures, sep="\n  ")
        return False, checks
    return True, checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args()
    ok, checks = verify(load(args.verify))
    if not ok:
        return 1
    print(
        "BT DETECTOR RESOLUTION DILATION VERIFY: ALL PASS "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
