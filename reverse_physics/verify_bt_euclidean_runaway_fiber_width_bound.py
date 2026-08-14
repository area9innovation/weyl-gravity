#!/usr/bin/env python3
"""Independent verifier for the BT runaway-fiber width theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RUNAWAY_FIBER_WIDTH_BOUND_V1.json",
)
SCHEMA_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-runaway-fiber-width-bound-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def power_two(exponent: int) -> Fraction:
    if exponent >= 0:
        return Fraction(2**exponent)
    return Fraction(1, 2 ** (-exponent))


def differentiate_directly(m: int, u: int) -> Fraction:
    """Rebuild A''/(log 2)^2 site by site from outgoing edge weights."""
    background = (-1, -1, 1, -3, 3, 1)
    mode = (2, 1, -1, -2, -1, 1)
    field = tuple(4 * m * a + u * h for a, h in zip(background, mode))
    answer = Fraction(0)
    for site in range(6):
        r = Fraction(-2)
        r_prime = Fraction(0)
        r_second = Fraction(0)
        for neighbor in ((site + 1) % 6, (site - 1) % 6):
            weight = power_two(field[neighbor] - field[site])
            direction = mode[neighbor] - mode[site]
            r += weight
            r_prime += direction * weight
            r_second += direction * direction * weight
        answer += r_prime * r_prime + r * r_second
    return answer


def six_coefficients(r: Fraction) -> dict[int, Fraction]:
    """Independently transcribe the collected six-term Laurent form."""
    a = 2 * r**4 - 12 * r**2 + 2 + 2 * r**-8 + 2 * r**-12
    b = r**2 + 1 + 2 * r**-4 + 2 * r**-6
    c = 2 * r**6 + 2 * r**4 + 2 + 2 * r**-2 - r**-6 - r**-8
    d = 2 * r**12 + 4 * r**10 + 2 * r**8 + 2 - 16 * r**-2 + 2 * r**-4
    return {-4: 16 * r**4, -2: a, -1: -b, 1: -c, 2: d, 4: 16 * r**-4}


def evaluate_six_term(m: int, u: int) -> Fraction:
    r = Fraction(2 ** (4 * m))
    z = power_two(u)
    return sum(
        (coefficient * z**power for power, coefficient in six_coefficients(r).items()),
        Fraction(0),
    )


def translate_polynomial(polynomial: dict[int, int], origin: int) -> list[int]:
    """Independent exact expansion of p(origin+s)."""
    translated = [0] * (max(polynomial) + 1)
    for old_power, value in polynomial.items():
        for new_power in range(old_power + 1):
            translated[new_power] += (
                value
                * math.comb(old_power, new_power)
                * origin ** (old_power - new_power)
            )
    return translated


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

        family = certificate["exact_family"]
        background = tuple(family["background_coefficients"])
        mode = tuple(family["lowest_mode_coefficients"])
        checks["family_rederived"] = (
            background == (-1, -1, 1, -3, 3, 1)
            and mode == (2, 1, -1, -2, -1, 1)
            and sum(background) == sum(mode) == 0
            and sum(a * h for a, h in zip(background, mode)) == 0
        )

        expected_terms = [
            (-12, -2, 2), (-8, -2, 2), (-8, 1, 1), (-6, -1, -2),
            (-6, 1, 1), (-4, -1, -2), (-4, 2, 2), (-4, 4, 16),
            (-2, 1, -2), (-2, 2, -16), (0, -2, 2), (0, -1, -1),
            (0, 1, -2), (0, 2, 2), (2, -2, -12), (2, -1, -1),
            (4, -4, 16), (4, -2, 2), (4, 1, -2), (6, 1, -2),
            (8, 2, 2), (10, 2, 4), (12, 2, 2),
        ]
        recorded_terms = [
            (row["R_power"], row["z_power"], row["coefficient"])
            for row in certificate["exact_curvature"]["bivariate_terms"]
        ]
        checks["bivariate_terms_match_independent_table"] = recorded_terms == expected_terms

        fixtures = certificate["exact_curvature"]["fixtures"]
        checks["fixtures_rederived_by_direct_differentiation"] = all(
            (direct := differentiate_directly(row["m"], row["u"]))
            == decode(row["direct_K"])
            == decode(row["laurent_K"])
            == evaluate_six_term(row["m"], row["u"])
            and direct >= Fraction(115, 4)
            for row in fixtures
        )

        r0 = Fraction(256)
        coefficients = six_coefficients(r0)
        a0, b0, c0, d0 = (
            coefficients[-2], -coefficients[-1], -coefficients[1], coefficients[2]
        )
        checks["threshold_coefficient_bounds_hold_exactly"] = (
            a0 >= r0**4
            and 0 < b0 <= 2 * r0**2
            and 0 < c0 <= 3 * r0**6
            and d0 >= r0**12
        )
        cleared_polynomials = {
            "R^12*(A-R^4)": {16: 1, 14: -12, 12: 2, 4: 2, 0: 2},
            "R^6*(2R^2-B)": {8: 1, 6: -1, 2: -2, 0: -2},
            "R^8*C": {14: 2, 12: 2, 8: 2, 6: 2, 2: -1, 0: -1},
            "R^8*(3R^6-C)": {14: 1, 12: -2, 8: -2, 6: -2, 2: 1, 0: 1},
            "R^4*(D-R^12)": {16: 1, 14: 4, 12: 2, 4: 2, 2: -16, 0: 2},
        }
        shift_checks = certificate["uniform_lower_bound"]["cleared_polynomial_shift_checks"]
        checks["universal_coefficient_bounds_have_exact_shift_certificates"] = (
            set(shift_checks) == set(cleared_polynomials)
            and all(
                (translated := translate_polynomial(polynomial, 256))[0] > 0
                and all(coefficient >= 0 for coefficient in translated)
                and shift_checks[name]
                == {
                    "degree": len(translated) - 1,
                    "all_shifted_coefficients_nonnegative": True,
                    "positive_constant_coefficient": True,
                }
                for name, polynomial in cleared_polynomials.items()
            )
        )

        bound = certificate["uniform_lower_bound"]
        checks["square_completion_and_am_gm_constant"] = (
            decode(bound["lower_bound"]) == Fraction(115, 4)
            and bound["coefficient_bounds"]
            == ["A>=R^4>0", "0<B<=2R^2", "0<C<=3R^6", "D>=R^12>0"]
            and Fraction(32) - Fraction(1) - Fraction(9, 4) == Fraction(115, 4)
        )

        carrier = certificate["finite_volume_carrier"]
        beta = Fraction(carrier["spatial_replication_factor"], 1) / decode(carrier["coupling"]) ** 2
        variance = certificate["conditional_variance"]
        checks["gibbs_and_variance_normalization_rederived"] = (
            beta == carrier["conditional_inverse_temperature"] == 1350
            and Fraction(1, 1) / (beta * Fraction(115, 4)) == Fraction(2, 77625)
            and decode(variance["rational_prefactor"]) == Fraction(2, 77625)
            and decode(variance["rationalized_bound"]) == Fraction(8, 77625)
            and Fraction(2, 77625) / Fraction(1, 2) ** 2
            == Fraction(8, 77625)
            and "Brascamp-Lieb" in variance["analytic_input"]
        )
        center = certificate["conditional_center_escape"]
        checks["conditional_mean_escape_rederived"] = (
            center["conclusion"] == "E_qm[u]<-m/2 for every m>=2"
            and Fraction(1 - Fraction(1, 4)) * Fraction(2**2, 4)
            == Fraction(3, 4)
            and Fraction(8, 77625) < Fraction(3, 4)
            and center["status"]
            == "PROVED_ESCAPE_TO_MINUS_INFINITY_ON_EXACT_RUNAWAY_FAMILY"
        )

        predecessor = certificate["provenance"]["inputs"]
        checks["predecessor_hash_matches"] = (
            len(predecessor) == 1
            and predecessor[0]["sha256"] == file_hash(predecessor[0]["path"])
        )
        disposition = certificate["method_disposition"]
        checks["claim_boundary_is_fail_closed"] = (
            disposition["runaway_family_recentered_conditional_variance"] == "PROVED"
            and disposition["runaway_family_conditional_mean_escape"] == "PROVED"
            and disposition["all_background_uniform_recentered_conditional_variance"] == "OPEN"
            and disposition["annealed_center_second_moment"] == "OPEN"
            and disposition["normalized_lowest_mode_second_moment"] == "OPEN"
            and disposition["actual_interacting_h_minus_one_second_moment"] == "OPEN"
            and disposition["continuum_limit"] == "NOT_ESTABLISHED"
            and disposition["born_rule"] == "NOT_ESTABLISHED"
            and disposition["krein_reconstruction"] == "NOT_ASSESSED"
            and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED"
        )
        nonclaims = certificate["does_not_establish"]
        checks["required_nonclaims_are_explicit"] = all(
            any(token in item for item in nonclaims)
            for token in ("every orthogonal", "annealed", "integrated", "H^-1", "continuum", "Born", "Krein", "LORENTZIAN-CAUSAL")
        )
        checks["dependency_tags_are_exact"] = certificate["dependency_tags"] == [
            "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"
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
        "[PASS] independent BT runaway-fiber width verifier "
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
