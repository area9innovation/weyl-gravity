#!/usr/bin/env python3
"""Independent verifier for the BT centered-fiber domination obstruction."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
from collections import defaultdict
from fractions import Fraction

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "certificates",
    "REVERSE_PHYSICS_BT_EUCLIDEAN_CENTERED_FIBER_DOMINATION_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "schema",
    "reverse-physics-bt-euclidean-centered-fiber-domination-obstruction-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def decode_polynomial(terms: list[dict[str, object]]) -> dict[int, Fraction]:
    return {
        int(term["exponent"]): decode(term["coefficient"])
        for term in terms
    }


def evaluate(terms: list[dict[str, object]], x: Fraction) -> Fraction:
    return sum(
        (
            decode(term["coefficient"]) * x ** int(term["exponent"])
            for term in terms
        ),
        Fraction(0),
    )


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def direct_cycle_action(coefficients: tuple[int, ...], x: Fraction) -> Fraction:
    omega = [x**coefficient for coefficient in coefficients]
    action = Fraction(0)
    for site in range(6):
        residual = (
            omega[(site - 1) % 6] / omega[site]
            + omega[(site + 1) % 6] / omega[site]
            - 2
        )
        action += residual * residual / 2
    return action


def direct_full_action(coefficients: tuple[int, ...], x: Fraction) -> Fraction:
    """Enumerate all 6^4 sites and all eight neighbors directly."""
    action = Fraction(0)
    for point in itertools.product(range(6), repeat=4):
        omega_here = x ** coefficients[point[0]]
        residual = Fraction(-8)
        for axis in range(4):
            for step in (-1, 1):
                neighbor = list(point)
                neighbor[axis] = (neighbor[axis] + step) % 6
                omega_neighbor = x ** coefficients[neighbor[0]]
                residual += omega_neighbor / omega_here
        action += residual * residual / 2
    return action


def residual_exponents(coefficients: tuple[int, ...]) -> list[dict[int, Fraction]]:
    rows = []
    for site in range(6):
        row: defaultdict[int, Fraction] = defaultdict(Fraction)
        row[coefficients[(site - 1) % 6] - coefficients[site]] += 1
        row[coefficients[(site + 1) % 6] - coefficients[site]] += 1
        row[0] -= 2
        rows.append({exponent: value for exponent, value in row.items() if value})
    return rows


def cycle_laplacian(values: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        2 * values[index]
        - values[(index - 1) % 6]
        - values[(index + 1) % 6]
        for index in range(6)
    )


def verify(path: str = DEFAULT_CERT) -> bool:
    checks: dict[str, bool] = {}
    errors = []
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        errors = sorted(
            Draft202012Validator(schema).iter_errors(certificate),
            key=lambda error: list(error.path),
        )
        checks["strict_schema"] = not errors

        family = certificate["exact_orthogonal_family"]
        h = tuple(family["lowest_mode_coefficients"])
        eta = tuple(family["background_coefficients"])
        shifted = tuple(family["shifted_coefficients"])
        checks["vectors_and_orthogonality_rederived"] = (
            h == (2, 1, -1, -2, -1, 1)
            and eta == (-1, -1, 1, -3, 3, 1)
            and shifted == tuple(left - right for left, right in zip(eta, h))
            and sum(h) == sum(eta) == 0
            and sum(left * right for left, right in zip(eta, h)) == 0
            and sum(value * value for value in h) == 12
        )
        checks["lowest_mode_and_half_translation_rederived"] = (
            cycle_laplacian(h) == h
            and tuple(h[(index + 3) % 6] for index in range(6))
            == tuple(-value for value in h)
        )

        public_background_residuals = [
            decode_polynomial(row)
            for row in family["background_residual_polynomials"]
        ]
        public_shifted_residuals = [
            decode_polynomial(row)
            for row in family["shifted_residual_polynomials"]
        ]
        checks["residual_laurent_rows_rederived"] = (
            public_background_residuals == residual_exponents(eta)
            and public_shifted_residuals == residual_exponents(shifted)
        )

        background_polynomial = decode_polynomial(
            family["background_action_laurent_polynomial"]
        )
        shifted_polynomial = decode_polynomial(
            family["shifted_action_laurent_polynomial"]
        )
        checks["leading_action_terms_rederived"] = (
            max(background_polynomial) == 12
            and background_polynomial[12] == Fraction(1, 2)
            and max(shifted_polynomial) == 10
            and shifted_polynomial[10] == Fraction(1, 2)
        )
        checks["polynomial_values_match_direct_cycle_actions"] = all(
            evaluate(family["background_action_laurent_polynomial"], x)
            == direct_cycle_action(eta, x)
            and evaluate(family["shifted_action_laurent_polynomial"], x)
            == direct_cycle_action(shifted, x)
            for x in (Fraction(2), Fraction(4), Fraction(8))
        )

        obstruction = certificate["scalable_action_obstruction"]
        coefficient = decode(obstruction["scaled_upper_coefficient"])
        checks["all_n_comparison_constant_rederived"] = (
            coefficient
            == Fraction(25, 512)
            + Fraction(1, 4)
            + Fraction(25, 32)
            + Fraction(1, 256)
            == Fraction(555, 512)
            and coefficient < decode(obstruction["strict_upper_coefficient"])
            == Fraction(9, 8)
        )
        checks["ratio_bound_samples_rederived_exactly"] = all(
            direct_cycle_action(shifted, Fraction(2**n))
            / direct_cycle_action(eta, Fraction(2**n))
            <= Fraction(9, 4 * 4**n)
            for n in range(1, 6)
        )
        checks["all_n_proof_is_retained"] = (
            "x^12/2" in obstruction["background_lower_bound"]
            and "(9/8)x^10" in obstruction["shifted_upper_bound"]
            and "9/(4*x^2)" in obstruction["action_ratio_bound"]
            and "c>0" in obstruction["relative_domination_consequence"]
            and obstruction["status"]
            == "CENTERED_POINTWISE_FIBER_DOMINATION_OBSTRUCTED"
        )

        fixture = certificate["exact_n1_fixture"]
        background_n1 = direct_cycle_action(eta, Fraction(2))
        shifted_n1 = direct_cycle_action(shifted, Fraction(2))
        full_background = direct_full_action(eta, Fraction(2))
        full_shifted = direct_full_action(shifted, Fraction(2))
        coupling = decode(certificate["finite_volume_carrier"]["coupling"])
        checks["n1_cycle_fixture_rederived"] = (
            background_n1
            == decode(fixture["per_spatial_site_background_action"])
            == Fraction(25038513, 8192)
            and shifted_n1
            == decode(fixture["per_spatial_site_shifted_action"])
            == Fraction(1970877, 2048)
            and shifted_n1 / background_n1
            == decode(fixture["per_spatial_site_action_ratio"])
            == Fraction(2627836, 8346171)
            and background_n1 - shifted_n1
            == decode(fixture["per_spatial_site_action_gap"])
            == Fraction(17155005, 8192)
        )
        checks["full_6_to_the_4_fixture_enumerated"] = (
            full_background == 216 * background_n1
            and full_shifted == 216 * shifted_n1
            and full_background == decode(fixture["full_lattice_background_action"])
            and full_shifted == decode(fixture["full_lattice_shifted_action"])
            and (full_background - full_shifted) / (coupling * coupling)
            == decode(fixture["full_lattice_boltzmann_exponent_gap"])
        )

        symmetry = certificate["integrated_marginal_symmetry"]
        checks["integrated_evenness_is_typed_without_variance_promotion"] = (
            symmetry["theorem"] == "m_h(t)=m_h(-t)"
            and symmetry["status"] == "EVEN_MARGINAL_PROVED"
            and "preserves A" in symmetry["half_period_translation"]
            and "does not bound the second moment" in symmetry["shortfall"]
        )
        disposition = certificate["method_disposition"]
        checks["method_boundary_is_fail_closed"] = (
            disposition["centered_pointwise_action_increment"] == "OBSTRUCTED"
            and disposition["centered_pointwise_relative_action_domination"]
            == "OBSTRUCTED"
            and disposition["centered_pointwise_boltzmann_ratio_bound"]
            == "OBSTRUCTED"
            and disposition["integrated_lowest_mode_marginal_evenness"] == "PROVED"
            and disposition["annealed_or_recentered_fiber_ratio_bound"] == "OPEN"
            and disposition["normalized_lowest_mode_second_moment_bound"] == "OPEN"
            and disposition["actual_interacting_h_minus_one_second_moment_bound"]
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
        checks["missing_objects_name_annealed_gate"] = all(
            any(token in item for item in certificate["missing_object_ledger"])
            for token in ("annealed", "second moment", "Fourier-shell", "tightness")
        )
        nonclaims = certificate["does_not_establish"]
        checks["required_nonclaims_are_explicit"] = all(
            any(token in statement for statement in nonclaims)
            for token in (
                "divergence",
                "conditional-fiber",
                "H^-1",
                "continuum",
                "reflection positivity",
                "Born",
                "Krein",
                "LORENTZIAN-CAUSAL",
                "weakest-foundation",
            )
        )
        provenance = certificate["provenance"]
        checks["input_hashes_match"] = (
            len(provenance["inputs"]) == 2
            and all(
                record["sha256"] == file_hash(record["path"])
                for record in provenance["inputs"]
            )
            and "Exact Python Fraction arithmetic" in provenance["arithmetic"]
        )
        checks["dependency_tags_are_exact"] = certificate["dependency_tags"] == [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
        ]
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"[FAIL] verifier exception: {exc}")
        return False

    if not all(checks.values()):
        for error in errors[:3]:
            print(f"[FAIL] schema: {error.message}")
        for name, ok in checks.items():
            if not ok:
                print(f"[FAIL] {name}")
        return False
    print(
        "[PASS] independent BT centered-fiber domination obstruction verifier "
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
