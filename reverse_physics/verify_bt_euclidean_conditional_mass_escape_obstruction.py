#!/usr/bin/env python3
"""Independent verifier for the BT conditional-mass escape obstruction."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_CONDITIONAL_MASS_ESCAPE_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "schema",
    "reverse-physics-bt-euclidean-conditional-mass-escape-obstruction-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def dyadic(exponent: int) -> Fraction:
    if exponent >= 0:
        return Fraction(2**exponent)
    return Fraction(1, 2 ** (-exponent))


def direct_cycle_action(coefficients: tuple[int, ...]) -> Fraction:
    result = Fraction(0)
    for site in range(6):
        left = dyadic(coefficients[(site - 1) % 6] - coefficients[site])
        right = dyadic(coefficients[(site + 1) % 6] - coefficients[site])
        residual = left + right - 2
        result += residual * residual / 2
    return result


def verify(path: str = DEFAULT_CERT) -> bool:
    checks: dict[str, bool] = {}
    schema_errors = []
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        schema_errors = sorted(
            Draft202012Validator(schema).iter_errors(certificate),
            key=lambda error: list(error.path),
        )
        checks["strict_schema"] = not schema_errors

        family = certificate["exact_orthogonal_family"]
        a = tuple(family["background_coefficients"])
        h = tuple(family["lowest_mode_coefficients"])
        shifted = tuple(family["shifted_coefficients_at_candidate"])
        shifted_edges = tuple(family["shifted_adjacent_differences"])
        mode_edges = tuple(family["mode_adjacent_differences"])
        checks["vectors_and_edges_rederived"] = (
            a == (-1, -1, 1, -3, 3, 1)
            and h == (2, 1, -1, -2, -1, 1)
            and sum(a) == sum(h) == 0
            and sum(x * y for x, y in zip(a, h)) == 0
            and shifted == tuple(x - y for x, y in zip(a, h))
            and shifted_edges
            == tuple(shifted[(i + 1) % 6] - shifted[i] for i in range(6))
            and mode_edges
            == tuple(h[(i + 1) % 6] - h[i] for i in range(6))
            and max(map(abs, shifted_edges)) == 5
            and max(map(abs, mode_edges)) == 2
        )

        carrier = certificate["finite_volume_carrier"]
        coupling = decode(carrier["coupling"])
        checks["conditional_inverse_temperature_rederived"] = (
            coupling == Fraction(2, 5)
            and carrier["spatial_replication_factor"] == 216
            and Fraction(216, 1) / (coupling * coupling) == 1350
            and carrier["conditional_inverse_temperature"] == 1350
        )

        fixture = certificate["exact_m2_fixture"]
        m = fixture["m"]
        candidate = tuple(4 * m * x - 4 * m * y for x, y in zip(a, h))
        threshold = tuple(4 * m * x - m * y for x, y in zip(a, h))
        candidate_action = direct_cycle_action(candidate)
        threshold_action = direct_cycle_action(threshold)
        C = 2 ** (46 * m - 3)
        M = 243 * 2 ** (40 * m)
        D = 1350 * (C - M)
        binary_exponent = 50 * m - 1 - D
        checks["m2_fixture_rederived_by_direct_action"] = (
            m == 2
            and tuple(fixture["candidate_coefficients"]) == candidate
            and tuple(fixture["threshold_coefficients"]) == threshold
            and decode(fixture["candidate_cycle_action"]) == candidate_action
            and decode(fixture["threshold_cycle_action"]) == threshold_action
            and fixture["C_m"] == C
            and fixture["M_m"] == M
            and fixture["D_m"] == D
            and fixture["binary_tail_exponent"] == binary_exponent
            and candidate_action <= M < C <= threshold_action
        )

        checks["right_tail_residual_formula_rederived"] = all(
            4 * m_value * (a[2] - a[3]) + (-m_value + v) * (h[2] - h[3])
            == 15 * m_value + v
            and 4 * m_value * (a[4] - a[3])
            + (-m_value + v) * (h[4] - h[3])
            == 23 * m_value + v
            for m_value in range(2, 9)
            for v in range(0, 5)
        )
        checks["right_tail_action_samples_rederived"] = all(
            direct_cycle_action(
                tuple(
                    4 * m_value * x + (-m_value + v) * y
                    for x, y in zip(a, h)
                )
            )
            >= 2 ** (46 * m_value + 2 * v - 3)
            for m_value in range(2, 7)
            for v in range(0, 4)
        )

        checks["all_m_integer_comparison_rederived"] = all(
            (C_m := 2 ** (46 * m_value - 3))
            > (M_m := 243 * 2 ** (40 * m_value))
            and (D_m := 1350 * (C_m - M_m)) >= 51 * m_value
            and 50 * m_value - 1 - D_m <= -m_value
            for m_value in range(2, 17)
        )
        comparison = certificate["all_m_comparison"]
        checks["all_m_proof_structure_retained"] = (
            "512/243>1" in comparison["C_exceeds_M_proof"]
            and "2^(40m)>=m" in comparison["D_lower_bound"]
            and "2^(-m)" in comparison["tail_probability_bound"]
            and "u_m^*<-m" in comparison["global_minimizer_consequence"]
            and "m^2*(1-2^(-m))" in comparison["raw_second_moment_bound"]
            and comparison["status"]
            == "UNIFORM_BACKGROUNDWISE_RAW_CONDITIONAL_MOMENT_OBSTRUCTED"
        )

        tail = certificate["right_tail_lower_bound"]
        well = certificate["candidate_well_lower_normalization"]
        checks["analytic_normalization_comparison_is_explicit"] = (
            tail["analytic_lemma"] == "4^v>=1+v for v>=0"
            and "exp[-1350*C_m]/(1350*C_m)"
            in tail["tail_integral_inequality"]
            and well["delta_m"] == "2^(-50m)"
            and "exp[-1350*M_m]" in well["normalization_lower_bound"]
        )

        provenance = certificate["provenance"]
        checks["input_hashes_match"] = (
            len(provenance["inputs"]) == 2
            and all(
                record["sha256"] == file_hash(record["path"])
                for record in provenance["inputs"]
            )
            and "Fraction and integer arithmetic" in provenance["arithmetic"]
        )
        affine_path = provenance["inputs"][1]["path"]
        with open(os.path.join(REPO_ROOT, affine_path), encoding="utf-8") as handle:
            affine = json.load(handle)
        log_lower = decode(
            affine["pointwise_affine_virial_theorem"]["q8_log_certificate"][
                "log_two_lower_bound"
            ]
        )
        checks["real_calculus_lemma_has_rational_log_input"] = (
            log_lower > Fraction(2, 3)
        )

        disposition = certificate["method_disposition"]
        checks["method_boundary_is_fail_closed"] = (
            disposition["uniform_backgroundwise_raw_conditional_second_moment"]
            == "OBSTRUCTED"
            and disposition["conditional_mass_escape_on_exact_family"] == "PROVED"
            and disposition["uniform_recentered_conditional_variance"] == "OPEN"
            and disposition["annealed_center_second_moment"] == "OPEN"
            and disposition["normalized_lowest_mode_second_moment"] == "OPEN"
            and disposition["actual_interacting_h_minus_one_second_moment"]
            == "OPEN"
            and disposition["interacting_tightness"] == "NOT_ESTABLISHED"
            and disposition["continuum_limit"] == "NOT_ESTABLISHED"
            and disposition["born_rule"] == "NOT_ESTABLISHED"
            and disposition["krein_reconstruction"] == "NOT_ASSESSED"
            and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED"
        )
        foundation = certificate["foundational_dependency_cut"]
        checks["foundational_boundary_is_fail_closed"] = (
            foundation["classification"] == "USED_BY_DISPLAYED_PROOF"
            and foundation["weakest_base_or_reversal"] == "NOT_ESTABLISHED"
            and "no volume-uniform" in foundation["uniform_limit_layer"]
        )
        nonclaims = certificate["does_not_establish"]
        checks["required_nonclaims_are_explicit"] = all(
            any(token in item for item in nonclaims)
            for token in (
                "fully integrated",
                "H^-1",
                "recentered",
                "annealed",
                "continuum",
                "Born",
                "Krein",
                "LORENTZIAN-CAUSAL",
                "weakest-foundation",
            )
        )
        checks["dependency_tags_are_exact"] = certificate["dependency_tags"] == [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
        ]
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"[FAIL] verifier exception: {exc}")
        return False

    if not all(checks.values()):
        for error in schema_errors[:3]:
            print(f"[FAIL] schema: {error.message}")
        for name, passed in checks.items():
            if not passed:
                print(f"[FAIL] {name}")
        return False
    print(
        "[PASS] independent BT conditional-mass escape verifier "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
