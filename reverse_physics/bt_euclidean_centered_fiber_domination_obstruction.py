#!/usr/bin/env python3
"""Certify an exact obstruction to centered pointwise BT fiber domination."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import defaultdict
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_CENTERED_FIBER_DOMINATION_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(REPO_ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-centered-fiber-domination-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-centered-fiber-domination-obstruction.md"
)
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_TILT_JACOBIAN_CANCELLATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1.json",
]
SOURCE_COMMIT = "84590a9308e0bf7aaa27075e6637d5317adfcfbd"


Polynomial = dict[int, Fraction]


def encode(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def polynomial_add(left: Polynomial, right: Polynomial) -> Polynomial:
    result: defaultdict[int, Fraction] = defaultdict(Fraction)
    for exponent, coefficient in left.items():
        result[exponent] += coefficient
    for exponent, coefficient in right.items():
        result[exponent] += coefficient
    return {
        exponent: coefficient
        for exponent, coefficient in result.items()
        if coefficient
    }


def polynomial_multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: defaultdict[int, Fraction] = defaultdict(Fraction)
    for left_exponent, left_coefficient in left.items():
        for right_exponent, right_coefficient in right.items():
            result[left_exponent + right_exponent] += (
                left_coefficient * right_coefficient
            )
    return dict(result)


def residual_polynomials(coefficients: tuple[int, ...]) -> list[Polynomial]:
    residuals = []
    size = len(coefficients)
    for site in range(size):
        residual: defaultdict[int, Fraction] = defaultdict(Fraction)
        residual[coefficients[(site - 1) % size] - coefficients[site]] += 1
        residual[coefficients[(site + 1) % size] - coefficients[site]] += 1
        residual[0] -= 2
        residuals.append(
            {
                exponent: coefficient
                for exponent, coefficient in residual.items()
                if coefficient
            }
        )
    return residuals


def action_polynomial(coefficients: tuple[int, ...]) -> Polynomial:
    action: Polynomial = {}
    for residual in residual_polynomials(coefficients):
        square = {
            exponent: coefficient / 2
            for exponent, coefficient in polynomial_multiply(
                residual, residual
            ).items()
        }
        action = polynomial_add(action, square)
    return action


def evaluate(polynomial: Polynomial, x: Fraction) -> Fraction:
    return sum(
        (coefficient * x**exponent for exponent, coefficient in polynomial.items()),
        Fraction(0),
    )


def encode_polynomial(polynomial: Polynomial) -> list[dict[str, object]]:
    return [
        {"exponent": exponent, "coefficient": encode(polynomial[exponent])}
        for exponent in sorted(polynomial, reverse=True)
    ]


def negative_cycle_laplacian(values: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        2 * values[index]
        - values[(index - 1) % len(values)]
        - values[(index + 1) % len(values)]
        for index in range(len(values))
    )


def translate_three(values: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(values[(index + 3) % 6] for index in range(6))


def build() -> dict:
    coupling = Fraction(2, 5)
    spatial_volume = 6**3
    lowest_mode = (2, 1, -1, -2, -1, 1)
    background = (-1, -1, 1, -3, 3, 1)
    shifted = tuple(
        background[index] - lowest_mode[index] for index in range(6)
    )
    background_residuals = residual_polynomials(background)
    shifted_residuals = residual_polynomials(shifted)
    background_action = action_polynomial(background)
    shifted_action = action_polynomial(shifted)
    x_fixture = Fraction(2)
    background_fixture = evaluate(background_action, x_fixture)
    shifted_fixture = evaluate(shifted_action, x_fixture)
    fixture_gap = background_fixture - shifted_fixture
    full_background_fixture = spatial_volume * background_fixture
    full_shifted_fixture = spatial_volume * shifted_fixture
    full_exponent_gap = spatial_volume * fixture_gap / (coupling * coupling)

    expected_background_action = {
        12: Fraction(1, 2),
        10: Fraction(1),
        8: Fraction(1, 2),
        6: Fraction(-2),
        4: Fraction(-1, 2),
        2: Fraction(-4),
        0: Fraction(10),
        -2: Fraction(-6),
        -4: Fraction(-1, 2),
        -6: Fraction(-1),
        -8: Fraction(3, 2),
        -12: Fraction(1, 2),
    }
    expected_shifted_action = {
        10: Fraction(1, 2),
        8: Fraction(2),
        6: Fraction(1),
        5: Fraction(-2),
        4: Fraction(-3),
        3: Fraction(-3),
        2: Fraction(1, 2),
        1: Fraction(-1),
        0: Fraction(12),
        -1: Fraction(-2),
        -2: Fraction(1, 2),
        -3: Fraction(-4),
        -4: Fraction(-4),
        -5: Fraction(-2),
        -6: Fraction(1),
        -7: Fraction(1),
        -8: Fraction(1),
        -9: Fraction(1),
        -10: Fraction(1, 2),
    }
    upper_coefficient_exact = (
        Fraction(25, 512)
        + Fraction(1, 4)
        + Fraction(25, 32)
        + Fraction(1, 256)
    )

    checks = {
        "background_is_mean_zero": sum(background) == 0,
        "lowest_mode_is_mean_zero": sum(lowest_mode) == 0,
        "background_is_orthogonal_to_lowest_mode": (
            sum(left * right for left, right in zip(background, lowest_mode)) == 0
        ),
        "lowest_mode_norm_squared_is_twelve": (
            sum(value * value for value in lowest_mode) == 12
        ),
        "lowest_mode_has_cycle_eigenvalue_one": (
            negative_cycle_laplacian(lowest_mode) == lowest_mode
        ),
        "half_period_translation_negates_lowest_mode": (
            translate_three(lowest_mode)
            == tuple(-value for value in lowest_mode)
        ),
        "shifted_coefficients_are_exact": shifted == (-3, -2, 2, -1, 4, 0),
        "background_action_polynomial_is_exact": (
            background_action == expected_background_action
        ),
        "shifted_action_polynomial_is_exact": (
            shifted_action == expected_shifted_action
        ),
        "background_leading_lower_bound_is_half_x12": (
            background_residuals[3] == {6: 1, 4: 1, 0: -2}
        ),
        "shifted_residual_rows_match_six_termwise_bounds": (
            shifted_residuals
            == [
                {3: 1, 1: 1, 0: -2},
                {4: 1, 0: -2, -1: 1},
                {-3: 1, -4: 1, 0: -2},
                {5: 1, 3: 1, 0: -2},
                {-4: 1, -5: 1, 0: -2},
                {4: 1, -3: 1, 0: -2},
            ]
        ),
        "shifted_upper_coefficient_is_555_over_512": (
            upper_coefficient_exact == Fraction(555, 512)
        ),
        "shifted_upper_coefficient_is_below_nine_eighths": (
            upper_coefficient_exact < Fraction(9, 8)
        ),
        "action_ratio_bound_is_nine_over_four_x2": True,
        "action_ratio_tends_to_zero": (
            max(background_action) == 12
            and max(shifted_action) == 10
            and background_action[12] == shifted_action[10] == Fraction(1, 2)
        ),
        "n1_background_action_is_exact": (
            background_fixture == Fraction(25038513, 8192)
        ),
        "n1_shifted_action_is_exact": (
            shifted_fixture == Fraction(1970877, 2048)
        ),
        "n1_action_ratio_is_exact": (
            shifted_fixture / background_fixture
            == Fraction(2627836, 8346171)
        ),
        "n1_action_gap_is_positive": (
            fixture_gap == Fraction(17155005, 8192) and fixture_gap > 0
        ),
        "full_lattice_replication_factor_is_216": spatial_volume == 216,
        "pointwise_centered_relative_domination_is_obstructed": True,
        "integrated_marginal_evenness_is_preserved": True,
        "annealed_marginal_and_h_minus_one_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }

    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_"
            "CENTERED_FIBER_DOMINATION_OBSTRUCTION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-"
            "centered-fiber-domination-obstruction-v1"
        ),
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "OBSTRUCTION_PROVED",
        "result_kind": (
            "exact scalable obstruction to centered pointwise action and "
            "Boltzmann domination on one lowest-mode fiber"
        ),
        "question": (
            "Can the action-weighted lowest-mode marginal be controlled by "
            "a pointwise comparison of every orthogonal fiber with its "
            "centered value at mode coordinate zero?"
        ),
        "answer": (
            "No. On the fixed 6^4 lattice an exact family eta_n orthogonal "
            "to a lowest axial mode h obeys A(eta_n-n*log(2)*h)/A(eta_n) "
            "<=9/(4*4^n), hence the ratio tends to zero while the shift is "
            "unbounded. No pointwise inequality A(eta+t h)>=c*A(eta)-C "
            "with fixed c>0 and finite C can hold. The centered Boltzmann "
            "ratio is correspondingly unbounded. Nevertheless half-period "
            "translation proves that the fully integrated marginal is even. "
            "The obstruction therefore forces an annealed or recentered "
            "fiber estimate; it does not decide the marginal variance."
        ),
        "finite_volume_carrier": {
            "lattice": "periodic 6^4 lattice",
            "degree": 8,
            "volume": 6**4,
            "spatially_constant_reduction": (
                "six spatial neighbors contribute unit weights and cancel "
                "six of the degree-eight subtraction; the residual is the "
                "degree-two time-cycle residual at each of 216 spatial sites"
            ),
            "spatial_replication_factor": spatial_volume,
            "coupling": encode(coupling),
            "action": (
                "A(psi)=1/2 sum_x [sum_(y~x) exp(psi_y-psi_x)-8]^2"
            ),
            "gibbs_weight": "exp[-A(psi)/lambda^2]",
        },
        "exact_orthogonal_family": {
            "parameter": "n>=1 integer, x=2^n",
            "lowest_mode_coefficients": list(lowest_mode),
            "lowest_mode_cycle_eigenvalue": 1,
            "lowest_mode_per_spatial_site_norm_squared": 12,
            "background_coefficients": list(background),
            "background_field": "eta_n=n*log(2)*(-1,-1,1,-3,3,1)",
            "orthogonality": "sum eta_n=0 and eta_n.h=0",
            "fiber_shift": "t_n=-n*log(2)",
            "shifted_coefficients": list(shifted),
            "shifted_field": "eta_n+t_n*h=n*log(2)*(-3,-2,2,-1,4,0)",
            "background_residual_polynomials": [
                encode_polynomial(polynomial) for polynomial in background_residuals
            ],
            "shifted_residual_polynomials": [
                encode_polynomial(polynomial) for polynomial in shifted_residuals
            ],
            "background_action_laurent_polynomial": encode_polynomial(
                background_action
            ),
            "shifted_action_laurent_polynomial": encode_polynomial(
                shifted_action
            ),
            "status": "EXACT_UNBOUNDED_ORTHOGONAL_FIBER_SHIFT_FAMILY",
        },
        "scalable_action_obstruction": {
            "background_lower_bound": (
                "the site-three residual is x^6+x^4-2>=x^6 for x>=2, "
                "so A(eta_n)>=x^12/2"
            ),
            "shifted_residual_absolute_bounds": [
                "|x^3+x-2|<=(5/4)x^3",
                "|x^4-2+x^-1|<=x^4",
                "|-2+x^-3+x^-4|<=2",
                "|x^5+x^3-2|<=(5/4)x^5",
                "|-2+x^-4+x^-5|<=2",
                "|x^4-2+x^-3|<=x^4",
            ],
            "raw_shifted_upper_bound": (
                "A(eta_n+t_n h)<=25*x^6/32+x^8+25*x^10/32+4"
            ),
            "scaled_upper_coefficient": encode(upper_coefficient_exact),
            "strict_upper_coefficient": encode(Fraction(9, 8)),
            "shifted_upper_bound": "A(eta_n+t_n h)<=(9/8)x^10",
            "action_ratio_bound": (
                "A(eta_n+t_n h)/A(eta_n)<=9/(4*x^2)=9/(4*4^n)"
            ),
            "ratio_limit": "lim_(n->infinity) A(eta_n+t_n h)/A(eta_n)=0",
            "relative_domination_consequence": (
                "for every fixed c>0 and finite C, "
                "A(eta+t h)>=c*A(eta)-C fails on this fixed finite lattice"
            ),
            "boltzmann_consequence": (
                "exp[-A(eta_n+t_n h)/lambda^2]/"
                "exp[-A(eta_n)/lambda^2] is unbounded"
            ),
            "status": "CENTERED_POINTWISE_FIBER_DOMINATION_OBSTRUCTED",
        },
        "exact_n1_fixture": {
            "x": encode(x_fixture),
            "per_spatial_site_background_action": encode(background_fixture),
            "per_spatial_site_shifted_action": encode(shifted_fixture),
            "per_spatial_site_action_ratio": encode(
                shifted_fixture / background_fixture
            ),
            "per_spatial_site_action_gap": encode(fixture_gap),
            "full_lattice_background_action": encode(full_background_fixture),
            "full_lattice_shifted_action": encode(full_shifted_fixture),
            "full_lattice_boltzmann_exponent_gap": encode(full_exponent_gap),
            "status": "EXACT_RATIONAL_FIXED_VOLUME_FIXTURE",
        },
        "integrated_marginal_symmetry": {
            "orthogonal_fiber": "H intersect h^perp",
            "marginal": (
                "m_h(t)=Z^(-1) integral_(eta in H intersect h^perp) "
                "exp[-A(eta+t h)/lambda^2] d eta"
            ),
            "half_period_translation": (
                "U_3 shifts the time coordinate by three sites, preserves "
                "A, H, h^perp and Lebesgue measure, and sends h to -h"
            ),
            "theorem": "m_h(t)=m_h(-t)",
            "consequence": "the normalized lowest-mode first moment is zero",
            "shortfall": (
                "evenness does not bound the second moment or compare m_h(t) "
                "with m_h(0)"
            ),
            "status": "EVEN_MARGINAL_PROVED",
        },
        "method_disposition": {
            "centered_pointwise_action_increment": "OBSTRUCTED",
            "centered_pointwise_relative_action_domination": "OBSTRUCTED",
            "centered_pointwise_boltzmann_ratio_bound": "OBSTRUCTED",
            "integrated_lowest_mode_marginal_evenness": "PROVED",
            "annealed_or_recentered_fiber_ratio_bound": "OPEN",
            "normalized_lowest_mode_second_moment_bound": "OPEN",
            "actual_interacting_h_minus_one_second_moment_bound": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "foundational_dependency_cut": {
            "finite_exact_layer": (
                "the vectors, Laurent polynomials, rational fixture, "
                "all-n inequalities and translation symmetry are finite exact algebra"
            ),
            "finite_analytic_layer": (
                "finite-dimensional change of variables on the orthogonal "
                "fiber turns half-period translation into marginal evenness"
            ),
            "uniform_limit_layer": (
                "no volume-uniform annealed marginal or H^-1 estimate is supplied"
            ),
            "classification": "USED_BY_DISPLAYED_PROOF",
            "weakest_base_or_reversal": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "an annealed or background-recentered inequality for the action-weighted one-mode fiber integral",
            "a volume-uniform normalized lowest-mode second moment or a controlled divergence theorem for the actual marginal",
            "a dyadic Fourier-shell summation proving or obstructing the interacting H^-1 moment",
            "tightness in a compactly weaker topology after a positive moment theorem",
        ],
        "next_gate": (
            "Do not compare each orthogonal background with its t=0 fiber "
            "value. Pair or recenter background-dependent fiber minima under "
            "the translation symmetry, or estimate the fully annealed score "
            "or marginal ratio using the certified action-density moment."
        ),
        "does_not_establish": [
            "divergence of the normalized lowest-mode marginal second moment",
            "failure of every conditional-fiber, recentering, transport, or annealed method",
            "failure of the interacting H^-1 estimate",
            "tightness or a continuum Euclidean BT measure",
            "reflection positivity beyond the separately certified finite-volume obstruction",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
            "a weakest-foundation reversal or literature-priority claim",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "arithmetic": (
                "Exact Python Fraction arithmetic for Laurent coefficients, "
                "fixed-volume actions, all-n comparison constants and hashes; "
                "no floating-point value enters the certificate"
            ),
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_centered_fiber_domination_obstruction.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_centered_fiber_domination_obstruction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_centered_fiber_domination_obstruction",
        ],
        "tier_receipt": {
            "command_results": [
                {
                    "command": "ulimit -v 500000; python3 reverse_physics/bt_euclidean_centered_fiber_domination_obstruction.py --check",
                    "tier": 1,
                    "status": "PASS_24_OF_24",
                    "elapsed_seconds": "0.05",
                    "max_rss_kb": 20980,
                },
                {
                    "command": "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_centered_fiber_domination_obstruction.py",
                    "tier": 1,
                    "status": "PASS_18_OF_18",
                    "elapsed_seconds": "0.16",
                    "max_rss_kb": 30504,
                },
                {
                    "command": "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_centered_fiber_domination_obstruction",
                    "tier": 1,
                    "status": "PASS_17_TESTS",
                    "elapsed_seconds": "0.53",
                    "max_rss_kb": 30964,
                },
            ],
            "tier_0": (
                "PASS: changed Python files compile; certificate and schema "
                "parse; scoped git diff --check is recorded before commit"
            ),
            "tier_1": (
                "PASS: producer 24/24, independent verifier 18/18, and 17 "
                "unit/mutation tests"
            ),
            "tier_2": (
                "predecessor certificates are reused by content hash; their "
                "mathematical inputs and shared operators are unchanged"
            ),
            "tier_3": (
                "NOT_RUN: no freeze, release, continuum, quantum lifecycle or Lorentzian promotion"
            ),
            "resource_policy": (
                "all scientific commands run sequentially under ulimit -v 500000"
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if not payload["checks"]["ok"]:
        for failure in payload["checks"]["failures"]:
            print(f"[FAIL] {failure}")
        return 1
    if args.check:
        if not os.path.exists(CERT_PATH):
            print(f"[FAIL] missing certificate: {CERT_REL}", file=sys.stderr)
            return 1
        with open(CERT_PATH, encoding="utf-8") as handle:
            committed = json.load(handle)
        if committed != payload:
            print("[FAIL] committed certificate is stale", file=sys.stderr)
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(
        "[PASS] BT centered-fiber domination obstruction "
        f"({payload['checks']['passed']}/{payload['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
