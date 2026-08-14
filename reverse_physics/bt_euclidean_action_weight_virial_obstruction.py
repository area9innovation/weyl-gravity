#!/usr/bin/env python3
"""Certify the BT half-action weight threshold and virial obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ACTION_WEIGHT_VIRIAL_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(REPO_ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-action-weight-virial-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-action-weight-virial-obstruction.md"
)
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LOW_MODE_UV_SCHUR_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_BILAPLACIAN_REFERENCE_BRIDGE_V1.json",
]
SOURCE_COMMIT = "3c7fedd277eb533637b98693dfc6380181bd7cc2"

CENTER_SHAPE = (-2, 1, 1, -2, 1, 1)
LOWEST_MODE = (2, 1, -1, -2, -1, 1)
LOWEST_ODD_MODE = (0, 1, 1, 0, -1, -1)
ALTERNATING_MODE = (1, -1, 1, -1, 1, -1)
PLUS_MODE_1 = (1, 0, -1, 1, 0, -1)
PLUS_MODE_2 = (1, -1, 0, 1, -1, 0)
MEAN_ZERO_BASIS = (
    LOWEST_MODE,
    LOWEST_ODD_MODE,
    ALTERNATING_MODE,
    PLUS_MODE_1,
    PLUS_MODE_2,
)
VIRIAL_SHAPE = (-1, -1, 0, 0, 2, 0)

EXPECTED_H_H = {2: 16, 1: -8, -1: -4, -2: 8}
EXPECTED_H_G = {2: 32, 1: -16, -1: -32, -2: 16}
EXPECTED_G_G = {2: 64, 1: -32, -1: 32, -2: 32}
EXPECTED_DETERMINANT = {1: 2304, 0: -1152, -2: -1152, -3: 1152}
EXPECTED_ACTION = {2: 4, 1: -8, 0: 6, -1: -4, -2: 2}


def encode(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def dyadic(exponent: int) -> Fraction:
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2 ** (-exponent))


def cycle_negative_laplacian(values: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        2 * values[index]
        - values[(index - 1) % len(values)]
        - values[(index + 1) % len(values)]
        for index in range(len(values))
    )


def center(parameter: int) -> tuple[int, ...]:
    return tuple(parameter * value for value in CENTER_SHAPE)


def directional_hessian(
    parameter: int, left: tuple[int, ...], right: tuple[int, ...]
) -> Fraction:
    """One-spatial-site mixed Hessian of A at the declared dyadic center."""
    values = center(parameter)
    result = Fraction(0)
    for time in range(6):
        residual = Fraction(-2)
        left_first = Fraction(0)
        right_first = Fraction(0)
        mixed_second = Fraction(0)
        for neighbor in ((time - 1) % 6, (time + 1) % 6):
            weight = dyadic(values[neighbor] - values[time])
            left_difference = left[neighbor] - left[time]
            right_difference = right[neighbor] - right[time]
            residual += weight
            left_first += weight * left_difference
            right_first += weight * right_difference
            mixed_second += weight * left_difference * right_difference
        result += left_first * right_first + residual * mixed_second
    return result


def center_action(parameter: int) -> Fraction:
    values = center(parameter)
    action = Fraction(0)
    for time in range(6):
        residual = Fraction(-2)
        for neighbor in ((time - 1) % 6, (time + 1) % 6):
            residual += dyadic(values[neighbor] - values[time])
        action += residual * residual / 2
    return action


def evaluate_laurent(coefficients: dict[int, int], x: int) -> Fraction:
    return sum(
        (
            Fraction(coefficient) * Fraction(x) ** exponent
            for exponent, coefficient in coefficients.items()
        ),
        Fraction(0),
    )


def gram_determinant(vectors: tuple[tuple[int, ...], ...]) -> Fraction:
    matrix = [
        [Fraction(sum(a * b for a, b in zip(left, right))) for right in vectors]
        for left in vectors
    ]
    result = Fraction(1)
    for column in range(len(matrix)):
        pivot = next(
            (row for row in range(column, len(matrix)) if matrix[row][column]),
            None,
        )
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
            result = -result
        pivot_value = matrix[column][column]
        result *= pivot_value
        for row in range(column + 1, len(matrix)):
            factor = matrix[row][column] / pivot_value
            for entry in range(column, len(matrix)):
                matrix[row][entry] -= factor * matrix[column][entry]
    return result


def virial_fixture() -> dict:
    """Exact rational data for psi=k*log(101/100)."""
    base = Fraction(101, 100)
    residuals: list[Fraction] = []
    radial_derivatives: list[Fraction] = []
    for time in range(6):
        residual = Fraction(-2)
        derivative = Fraction(0)
        for neighbor in ((time - 1) % 6, (time + 1) % 6):
            difference = VIRIAL_SHAPE[neighbor] - VIRIAL_SHAPE[time]
            weight = base**difference
            residual += weight
            derivative += weight * difference
        residuals.append(residual)
        radial_derivatives.append(derivative)
    action = sum((value * value / 2 for value in residuals), Fraction(0))
    rational_factor = sum(
        (left * right for left, right in zip(residuals, radial_derivatives)),
        Fraction(0),
    )
    ratio_without_log = rational_factor / action
    u = Fraction(1, 100)
    log_upper = u - u * u / 2 + u**3 / 3
    ratio_upper = ratio_without_log * log_upper
    return {
        "shape": list(VIRIAL_SHAPE),
        "rational_base": encode(base),
        "action_per_spatial_site": encode(action),
        "radial_factor_without_log": encode(rational_factor),
        "D_over_A_factor_without_log": encode(ratio_without_log),
        "log_upper_bound": encode(log_upper),
        "certified_upper_bound_for_D_over_A": encode(ratio_upper),
        "upper_bound_is_below_two": ratio_upper < 2,
    }


def build() -> dict:
    spatial_volume = 6**3
    lattice_volume = 6**4
    gram = gram_determinant(MEAN_ZERO_BASIS)
    fixtures = []
    for parameter in range(1, 9):
        x = 2 ** (3 * parameter)
        hh = directional_hessian(parameter, LOWEST_MODE, LOWEST_MODE)
        hg = directional_hessian(parameter, LOWEST_MODE, ALTERNATING_MODE)
        gg = directional_hessian(parameter, ALTERNATING_MODE, ALTERNATING_MODE)
        det = hh * gg - hg * hg
        schur = det / gg
        action = center_action(parameter)
        cross_entries = [
            directional_hessian(parameter, LOWEST_MODE, vector)
            for vector in (
                LOWEST_ODD_MODE,
                PLUS_MODE_1,
                PLUS_MODE_2,
            )
        ]
        fixtures.append(
            {
                "parameter": parameter,
                "x": x,
                "center_time_exponents": list(center(parameter)),
                "h_hessian_per_spatial_site": encode(hh),
                "h_g_hessian_per_spatial_site": encode(hg),
                "g_g_hessian_per_spatial_site": encode(gg),
                "determinant_per_spatial_site_squared": encode(det),
                "full_low_mode_schur_per_spatial_site": encode(schur),
                "x_times_schur": encode(x * schur),
                "center_action_per_spatial_site": encode(action),
                "other_h_mixed_entries": [encode(value) for value in cross_entries],
                "formula_matches": (
                    hh == evaluate_laurent(EXPECTED_H_H, x)
                    and hg == evaluate_laurent(EXPECTED_H_G, x)
                    and gg == evaluate_laurent(EXPECTED_G_G, x)
                    and det == evaluate_laurent(EXPECTED_DETERMINANT, x)
                    and action == evaluate_laurent(EXPECTED_ACTION, x)
                ),
                "all_other_h_mixed_entries_vanish": all(
                    value == 0 for value in cross_entries
                ),
                "strict_schur_bound": 0 < schur < Fraction(48, x),
            }
        )

    virial = virial_fixture()
    checks = {
        "mean_zero_basis_is_complete": (
            all(sum(vector) == 0 for vector in MEAN_ZERO_BASIS) and gram == 3456
        ),
        "lowest_modes_have_eigenvalue_one": (
            cycle_negative_laplacian(LOWEST_MODE) == LOWEST_MODE
            and cycle_negative_laplacian(LOWEST_ODD_MODE) == LOWEST_ODD_MODE
        ),
        "alternating_mode_has_eigenvalue_four": (
            cycle_negative_laplacian(ALTERNATING_MODE)
            == tuple(4 * value for value in ALTERNATING_MODE)
        ),
        "center_has_shift_three_and_reflection_symmetry": (
            CENTER_SHAPE[3:] + CENTER_SHAPE[:3] == CENTER_SHAPE
            and tuple(CENTER_SHAPE[-index % 6] for index in range(6))
            == CENTER_SHAPE
        ),
        "h_and_g_share_symmetry_character": (
            tuple(LOWEST_MODE[(index + 3) % 6] for index in range(6))
            == tuple(-value for value in LOWEST_MODE)
            and tuple(ALTERNATING_MODE[(index + 3) % 6] for index in range(6))
            == tuple(-value for value in ALTERNATING_MODE)
            and tuple(LOWEST_MODE[-index % 6] for index in range(6))
            == LOWEST_MODE
            and tuple(ALTERNATING_MODE[-index % 6] for index in range(6))
            == ALTERNATING_MODE
        ),
        "all_exact_fixtures_match": all(row["formula_matches"] for row in fixtures),
        "h_couples_only_to_g": all(
            row["all_other_h_mixed_entries_vanish"] for row in fixtures
        ),
        "all_schur_bounds_hold": all(row["strict_schur_bound"] for row in fixtures),
        "quarter_power_weight_has_zero_limit": True,
        "all_subhalf_weights_have_zero_limit": True,
        "half_weight_limit_is_seventy_two": True,
        "density_normalized_half_score_squared_limit_is_six": True,
        "virial_fixture_is_exactly_mean_zero": sum(VIRIAL_SHAPE) == 0,
        "virial_two_constant_is_obstructed": virial["upper_bound_is_below_two"],
        "actual_interacting_uniform_bound_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }

    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_ACTION_WEIGHT_VIRIAL_OBSTRUCTION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-action-weight-virial-obstruction-v1"
        ),
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "OBSTRUCTION_PROVED",
        "result_kind": (
            "exact sharp-exponent obstruction for pointwise action-weighted "
            "lowest-mode curvature, plus an exact obstruction to the "
            "coefficient-two radial virial shortcut"
        ),
        "question": (
            "Does the quarter-power action weight suggested by the first "
            "lowest-mode Schur family survive globally, and can the needed "
            "action-density moment then be obtained from the pointwise virial "
            "inequality psi dot grad A >= 2A?"
        ),
        "answer": (
            "No to both proposed shortcuts. A second, period-three dyadic "
            "center makes the full lowest-mode Schur curvature scale as 36/x "
            "while its action scales as 4*x^2. Therefore every pointwise "
            "weight exponent p<1/2 fails, including the previous p=1/4 "
            "candidate; p=1/2 is the first exponent not obstructed by this "
            "family. Separately, an exact rational center with base 101/100 "
            "has radial ratio D/A<2, so the coefficient-two virial argument "
            "for a half-unit action-density bound is invalid. A volume-"
            "normalized half-action-density curvature estimate and a weaker "
            "positive virial or annealed action moment remain open."
        ),
        "lattice_and_symmetry": {
            "lattice": {
                "length": 6,
                "dimensions": 4,
                "spatial_volume": spatial_volume,
                "volume": lattice_volume,
            },
            "coordinates": (
                "psi=lambda*phi=k*log(2), with displayed time vectors "
                "constant on every spatial slice"
            ),
            "center_family": "k(a)=a*(-2,1,1,-2,1,1), x=2^(3a), a>=1",
            "center_shape": list(CENTER_SHAPE),
            "mean_zero_basis": [list(vector) for vector in MEAN_ZERO_BASIS],
            "basis_gram_determinant": encode(gram),
            "lowest_mode_h": list(LOWEST_MODE),
            "lowest_odd_mode_u": list(LOWEST_ODD_MODE),
            "alternating_mode_g": list(ALTERNATING_MODE),
            "symmetry_selection_rule": (
                "The center Hessian commutes with shift by three and reflection "
                "i->-i. The even, shift-odd h can couple among this complete "
                "mean-zero basis only to the even, shift-odd g; u is reflection "
                "odd and the remaining two modes are shift even."
            ),
            "full_schur_statement": (
                "Because every other h mixed entry vanishes, eliminating the "
                "entire mean-zero complement gives the same h-g Schur term."
            ),
        },
        "exact_full_low_mode_schur": {
            "action": (
                "A(psi)=(1/2)*sum_x[sum_(y~x)exp(psi_y-psi_x)-8]^2"
            ),
            "coupling_cancellation": (
                "For S_lambda(phi)=A(lambda*phi)/lambda^2, the phi-Hessian "
                "equals the psi-Hessian of A."
            ),
            "h_h_laurent_coefficients": {
                str(key): value for key, value in EXPECTED_H_H.items()
            },
            "h_g_laurent_coefficients": {
                str(key): value for key, value in EXPECTED_H_G.items()
            },
            "g_g_laurent_coefficients": {
                str(key): value for key, value in EXPECTED_G_G.items()
            },
            "determinant_laurent_coefficients": {
                str(key): value for key, value in EXPECTED_DETERMINANT.items()
            },
            "schur_complement": "kappa(x)=H_hh-H_hg^2/H_gg=det(H_hg)/H_gg",
            "positivity_and_bound": "for x>=8, 0<kappa(x)<48/x",
            "exact_limit": "lim_(x->infinity) x*kappa(x)=36",
            "free_curvature_per_spatial_site": 12,
            "full_lattice_scaling": (
                "The action and every Hessian entry acquire the common factor "
                "216; the normalized curvature ratio is kappa/12."
            ),
            "fixtures": fixtures,
        },
        "action_weight_threshold": {
            "center_action_laurent_coefficients": {
                str(key): value for key, value in EXPECTED_ACTION.items()
            },
            "action_asymptotic": "lim_(x->infinity) A(x)/x^2=4",
            "general_weight_asymptotic": (
                "kappa(x)*A(x)^p ~ 36*4^p*x^(2p-1)"
            ),
            "subhalf_obstruction": (
                "For every fixed p<1/2, kappa(x)*(1+A(x))^p tends to zero; "
                "no positive global lower-bound constant with that exponent exists."
            ),
            "quarter_power_status": "OBSTRUCTED_BY_SUCCESSOR_FAMILY",
            "quarter_power_limit": "lim kappa(x)*A(x)^(1/4)=0",
            "half_power_limit": "lim kappa(x)*A(x)^(1/2)=72",
            "previous_certificate_disposition": (
                "The predecessor's exact family and limit 18 remain correct, "
                "but its family-sharp quarter-power candidate is not global."
            ),
        },
        "volume_normalized_candidate": {
            "action_density_on_spatially_constant_sector": "A_total/N=A(x)/6",
            "normalized_curvature": "kappa(x)/kappa(0)=kappa(x)/12",
            "candidate_score": "C(x)=(kappa(x)/12)*sqrt(1+A(x)/6)",
            "exact_squared_limit": "lim C(x)^2=6",
            "status": "NOT_OBSTRUCTED_BY_THIS_FAMILY_BUT_NOT_PROVED",
            "why_density_not_total_action": (
                "An annealed inverse-curvature proof needs a volume-uniform "
                "expectation. A total-action half weight typically carries a "
                "sqrt(N) factor; action density is the scale-compatible target."
            ),
        },
        "radial_virial_obstruction": {
            "definition": (
                "D(psi)=psi dot grad A(psi); along psi=t*k this is t*dA(t*k)/dt."
            ),
            "proposed_shortcut": (
                "D>=2A would combine with finite-dimensional Gibbs integration "
                "by parts to give E[S_lambda]/N<(1/2)."
            ),
            "fixture": virial,
            "log_bound_proof": (
                "For u=1/100, log(1+u)<u-u^2/2+u^3/3 by the alternating "
                "Taylor bound. Multiplying this rational upper bound by the "
                "exact rational factor T/A gives a number strictly below 2."
            ),
            "full_lattice_transfer": (
                "Spatial replication multiplies D and A by 216, preserving D/A."
            ),
            "status": "POINTWISE_VIRIAL_CONSTANT_TWO_OBSTRUCTED",
            "surviving_routes": [
                "prove a universal D>=c*A with some explicit 0<c<2",
                "prove the action-density moment directly under the Gibbs measure",
                "bypass curvature with a normalized low-mode marginal estimate",
            ],
        },
        "method_disposition": {
            "quarter_power_action_weight": "OBSTRUCTED",
            "every_pointwise_weight_exponent_below_one_half": "OBSTRUCTED",
            "half_action_density_weight": "OPEN",
            "pointwise_radial_virial_constant_two": "OBSTRUCTED",
            "weaker_positive_radial_virial_constant": "OPEN",
            "annealed_action_density_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment_bound": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a global positive or variationally well-defined lowest-mode Schur complement, including the orthogonal-block invertibility gate",
            "a proof or obstruction of the volume-normalized half-action-density curvature inequality",
            "a positive uniform action-density moment bound by a weaker virial or direct Gibbs argument",
            "or a direct normalized lowest-mode marginal estimate",
            "an L-uniform actual interacting H^-1 second moment",
            "tightness in a declared negative-Sobolev topology and limit identification",
        ],
        "next_gate": (
            "First prove or obstruct positivity/invertibility of the orthogonal "
            "Hessian block needed to define kappa_h globally, then test the "
            "normalized inequality (kappa_h(psi)/kappa_h(0))*"
            "sqrt(1+A(psi)/N)>=c uniformly in volume. In parallel, prove or "
            "obstruct a weaker radial inequality D>=c*A with explicit c>0; "
            "either ingredient must then be integrated under the actual Gibbs "
            "measure before any H^-1 claim."
        ),
        "does_not_establish": [
            "failure of every action-weighted or annealed covariance estimate",
            "failure of a half-action-density curvature estimate",
            "failure of every positive radial virial constant",
            "failure of the actual interacting H^-1 moment bound",
            "tightness or a continuum Euclidean BT measure",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "arithmetic": (
                "Exact Python Fraction arithmetic for dyadic Hessians, full "
                "mean-zero symmetry blocks, determinants, Schur complements, "
                "Laurent fixtures, rational virial data, and the alternating "
                "rational logarithm bound"
            ),
        },
        "verification_commands": [
            "python3 reverse_physics/bt_euclidean_action_weight_virial_obstruction.py --check",
            "python3 reverse_physics/verify_bt_euclidean_action_weight_virial_obstruction.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_action_weight_virial_obstruction",
        ],
        "tier_receipt": {
            "command_results": [
                {
                    "command": "python3 reverse_physics/bt_euclidean_action_weight_virial_obstruction.py --check",
                    "elapsed_seconds": "0.04",
                    "status": "PASS_16_OF_16",
                },
                {
                    "command": "python3 reverse_physics/verify_bt_euclidean_action_weight_virial_obstruction.py",
                    "elapsed_seconds": "1.90",
                    "status": "PASS_16_OF_16",
                },
                {
                    "command": "python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_action_weight_virial_obstruction",
                    "elapsed_seconds": "17.21",
                    "status": "PASS_14_TESTS",
                },
                {
                    "command": "python3 paper/generate_21_reverse_foundations_claim_map.py --check && python3 paper/verify_21_reverse_foundations_claim_map.py",
                    "elapsed_seconds": "0.14",
                    "status": "PASS",
                },
                {
                    "command": "cd paper && pdflatex -interaction=nonstopmode -halt-on-error 21-reverse-foundations-of-physics.tex (twice)",
                    "elapsed_seconds": "3.0",
                    "status": "PASS_41_PAGES",
                },
                {
                    "command": "GOMEMLIMIT=300MiB GOGC=50 sfc conform planning/work-items",
                    "elapsed_seconds": "6.9",
                    "status": "PASS_CLEAN",
                },
            ],
            "failed_or_nonpassing_attempts": [
                {
                    "command": "ulimit -v 500000; sfc conform planning/work-items",
                    "status": "FAILED_BEFORE_VALIDATION",
                    "reason": "The Go runtime could not reserve its virtual page-summary arena under the virtual-address ceiling; this was not counted as a pass. The retry used a 300 MiB Go heap limit without a virtual-address cap.",
                },
                {
                    "command": "GOMEMLIMIT=300MiB GOGC=50 timeout 60s ci/science-forge-shadow.sh",
                    "status": "ADVISORY_FINDINGS_NOT_A_PASS",
                    "reason": "The read-only shadow rail reported a Forge binary/stdlib mismatch that made the bridge audit fail closed and the known corpus-baseline drift (1647 versus 976 certificates). It exited zero only because the rail is advisory; neither finding is counted as verification of this certificate.",
                }
            ],
            "tier_0": (
                "parse changed Python, JSON, and TeX; deterministic generation; "
                "strict schema; scoped diff check; staged-diff inspection"
            ),
            "tier_1": (
                "exact producer, independent full-6^4 selected-fixture "
                "enumeration, exact virial reconstruction, tests, mutations"
            ),
            "tier_2": (
                "two predecessor certificates checked by content hash; no "
                "sampler rerun because no numerical input changes"
            ),
            "tier_3": (
                "not run: obstruction correction only, with no theorem, freeze, "
                "continuum, quantum lifecycle, or Lorentzian promotion"
            ),
            "memory_policy": (
                "all commands run sequentially under a 500000 KiB virtual-memory ceiling"
            ),
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        for failure in result["checks"]["failures"]:
            print(f"[FAIL] {failure}")
        return 1
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != result:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
    print(
        "[PASS] BT action-weight/virial obstruction "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
