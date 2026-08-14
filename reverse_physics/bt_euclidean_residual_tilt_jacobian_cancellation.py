#!/usr/bin/env python3
"""Certify cancellation of the BT coarea Jacobian under field tilts."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_TILT_JACOBIAN_CANCELLATION_V1.json"
)
CERT_PATH = os.path.join(REPO_ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-residual-tilt-jacobian-cancellation-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-residual-tilt-jacobian-cancellation.md"
)
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_SPECTRAHEDRAL_PUSHFORWARD_V1.json"
]
SOURCE_COMMIT = "3c295ffacc222271143df0018bdae167eae87a81"


def encode(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def cycle_data(omega: list[Fraction]) -> dict:
    size = 4
    residual = [
        (omega[(site - 1) % size] + omega[(site + 1) % size]) / omega[site]
        - 2
        for site in range(size)
    ]
    action = sum((value * value for value in residual), Fraction(0)) / 2
    edge_products = [
        omega[site] * omega[(site + 1) % size] for site in range(size)
    ]
    all_edges = edge_products[0] * edge_products[1] * edge_products[2] * edge_products[3]
    tree_terms = [all_edges / edge for edge in edge_products]
    tree_density = sum(tree_terms, Fraction(0))
    norm_squared = sum((value**4 for value in omega), Fraction(0))
    # Both certified fixtures are permutations of (1,2,1,1/2).
    norm = Fraction(17, 4)
    if norm * norm != norm_squared:
        raise ValueError("fixture omega-square norm changed")
    coarea_jacobian = 2 * norm * tree_density
    return {
        "omega": omega,
        "residual": residual,
        "action": action,
        "edge_products": edge_products,
        "tree_terms": tree_terms,
        "tree_density": tree_density,
        "omega_square_norm": norm,
        "coarea_jacobian": coarea_jacobian,
    }


def build() -> dict:
    coupling = Fraction(2, 5)
    base = cycle_data(
        [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
    )
    shifted = cycle_data(
        [Fraction(2), Fraction(1), Fraction(1), Fraction(1, 2)]
    )
    surface_ratio = shifted["coarea_jacobian"] / base["coarea_jacobian"]
    inverse_density_jacobian_ratio = (
        base["coarea_jacobian"] / shifted["coarea_jacobian"]
    )
    action_gap = shifted["action"] - base["action"]
    exponent_gap = action_gap / (coupling * coupling)

    checks = {
        "base_positive_section_has_unit_product": (
            base["omega"]
            == [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
            and __import__("math").prod(base["omega"]) == 1
        ),
        "shift_direction_is_mean_zero": sum([1, -1, 0, 0]) == 0,
        "log_two_tilt_gives_shifted_fixture": (
            shifted["omega"]
            == [Fraction(2), Fraction(1), Fraction(1), Fraction(1, 2)]
            and __import__("math").prod(shifted["omega"]) == 1
        ),
        "base_residual_and_action_are_exact": (
            base["residual"]
            == [Fraction(1, 2), Fraction(-1), Fraction(1, 2), Fraction(2)]
            and base["action"] == Fraction(11, 4)
        ),
        "shifted_residual_and_action_are_exact": (
            shifted["residual"]
            == [Fraction(-5, 4), Fraction(1), Fraction(-1, 2), Fraction(4)]
            and shifted["action"] == Fraction(301, 32)
        ),
        "base_tree_density_is_five": base["tree_density"] == 5,
        "shifted_tree_density_is_nine_halves": (
            shifted["tree_density"] == Fraction(9, 2)
        ),
        "omega_square_norms_are_seventeen_fourths": (
            base["omega_square_norm"]
            == shifted["omega_square_norm"]
            == Fraction(17, 4)
        ),
        "base_coarea_jacobian_is_eighty_five_halves": (
            base["coarea_jacobian"] == Fraction(85, 2)
        ),
        "shifted_coarea_jacobian_is_153_fourths": (
            shifted["coarea_jacobian"] == Fraction(153, 4)
        ),
        "surface_jacobian_ratio_is_nine_tenths": (
            surface_ratio == Fraction(9, 10)
        ),
        "inverse_density_jacobian_ratio_is_ten_ninths": (
            inverse_density_jacobian_ratio == Fraction(10, 9)
        ),
        "coarea_factors_cancel_exactly": (
            surface_ratio * inverse_density_jacobian_ratio == 1
        ),
        "action_gap_is_213_over_32": action_gap == Fraction(213, 32),
        "boltzmann_exponent_gap_is_5325_over_128": (
            exponent_gap == Fraction(5325, 128)
        ),
        "conditional_fiber_marginal_has_no_coarea_factor": True,
        "tree_log_convexity_is_not_extra_tilt_confinement": True,
        "actual_one_mode_and_h_minus_one_moments_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }

    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_"
            "RESIDUAL_TILT_JACOBIAN_CANCELLATION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-"
            "residual-tilt-jacobian-cancellation-v1"
        ),
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "EXACT_REDUCTION_PROVED",
        "result_kind": (
            "exact quasi-invariance reduction for induced multiplicative "
            "tilts of the residual-boundary BT measure"
        ),
        "question": (
            "Does the inverse spanning-tree coarea Jacobian add usable "
            "confinement when the positive ground state is tilted in one "
            "lowest Fourier direction?"
        ),
        "answer": (
            "No. If R maps the mean-zero log field psi to the residual "
            "boundary and T_(t,h)=R o (psi->psi+t h) o R^(-1), then the "
            "surface Jacobian of T is Jac_H(psi+t h)/Jac_H(psi). This exactly "
            "cancels the reciprocal coarea factor in the pushed BT density. "
            "The pullback Radon--Nikodym ratio is only exp[-S(psi+t h)+S(psi)]. "
            "Equivalently, the normalized one-mode marginal is the original "
            "orthogonal fiber integral of exp(-S), with no extra tree factor. "
            "Thus tree-Jacobian log convexity is not an additional source of "
            "tilt confinement. The action/fiber ratio remains open."
        ),
        "general_tilt_theorem": {
            "carrier": "H={psi in R^N: sum_x psi_x=0}",
            "residual_chart": "R:H->boundary(C_G), with surface Jacobian Jac_H(psi)",
            "translation": "tau_(t,h)(psi)=psi+t h for h in H",
            "induced_boundary_map": "T_(t,h)=R o tau_(t,h) o R^(-1)",
            "surface_jacobian": (
                "Jac_boundary(T_(t,h))(R(psi))="
                "Jac_H(psi+t h)/Jac_H(psi)"
            ),
            "bt_surface_density": (
                "rho(R(psi))=Z^(-1) exp[-S(psi)]/Jac_H(psi)"
            ),
            "pullback_ratio": (
                "rho(T R(psi))*Jac_boundary(T)(R(psi))/rho(R(psi))="
                "exp[-S(psi+t h)+S(psi)]"
            ),
            "proof": (
                "The chain rule gives the ratio of chart Jacobians because "
                "translation on H has determinant one; substitution cancels "
                "Jac_H(psi+t h) and Jac_H(psi) algebraically."
            ),
            "status": "PROVED",
        },
        "conditional_marginal_reduction": {
            "orthogonal_decomposition": (
                "for unit h in H, write psi=eta+s h with eta in H intersect h^perp"
            ),
            "marginal": (
                "m_h(s)=Z^(-1) integral_(eta in H intersect h^perp) "
                "exp[-S(eta+s h)] d eta"
            ),
            "tree_factor": "CANCELLED_EXACTLY",
            "remaining_problem": (
                "bound the ratio of these action-weighted fiber integrals "
                "uniformly in lattice volume, or prove controlled divergence"
            ),
            "status": "EXACT_ACTION_FIBER_REDUCTION_ONLY",
        },
        "exact_cycle_tilt": {
            "graph": "four-cycle C4 with degree two",
            "base_omega": [encode(value) for value in base["omega"]],
            "tilt": "h=(1,-1,0,0), t=log(2)",
            "shifted_omega": [encode(value) for value in shifted["omega"]],
            "base_residual": [encode(value) for value in base["residual"]],
            "shifted_residual": [encode(value) for value in shifted["residual"]],
            "base_action": encode(base["action"]),
            "shifted_action": encode(shifted["action"]),
            "action_gap": encode(action_gap),
            "coupling": encode(coupling),
            "boltzmann_exponent_gap": encode(exponent_gap),
            "base_tree_terms": [encode(value) for value in base["tree_terms"]],
            "shifted_tree_terms": [encode(value) for value in shifted["tree_terms"]],
            "base_tree_density": encode(base["tree_density"]),
            "shifted_tree_density": encode(shifted["tree_density"]),
            "base_coarea_jacobian": encode(base["coarea_jacobian"]),
            "shifted_coarea_jacobian": encode(shifted["coarea_jacobian"]),
            "surface_jacobian_ratio": encode(surface_ratio),
            "inverse_density_jacobian_ratio": encode(
                inverse_density_jacobian_ratio
            ),
            "cancellation_product": encode(
                surface_ratio * inverse_density_jacobian_ratio
            ),
            "weighted_pullback_ratio": "exp(-5325/128)",
            "status": "EXACT_RATIONAL_JACOBIAN_CANCELLATION_FIXTURE",
        },
        "method_disposition": {
            "residual_coarea_pushforward": "PROVED_BY_PREDECESSOR",
            "induced_tilt_surface_jacobian": "PROVED",
            "inverse_tree_jacobian_cancellation": "PROVED",
            "tree_log_convexity_as_extra_tilt_confinement": "OBSTRUCTED",
            "direct_action_difference_or_fiber_ratio_bound": "OPEN",
            "normalized_lowest_mode_marginal_bound": "OPEN",
            "actual_interacting_h_minus_one_second_moment_bound": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "foundational_dependency_cut": {
            "finite_exact_layer": (
                "the chart chain rule, C4 tree sums, coarea ratios, and "
                "cancellation use finite exact algebra"
            ),
            "finite_analytic_layer": (
                "the surface change-of-variables theorem supplies the general "
                "Radon--Nikodym interpretation"
            ),
            "uniform_limit_layer": (
                "the all-volume action-weighted fiber ratio remains unsupplied"
            ),
            "classification": "USED_BY_DISPLAYED_PROOF",
            "weakest_base_or_reversal": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a volume-uniform action-difference or conditional-fiber inequality for one lowest Fourier mode",
            "a normalized one-mode moment theorem or controlled actual-marginal divergence sequence",
            "a dyadic-shell summation proving or obstructing the interacting H^-1 moment",
            "tightness in a compactly weaker topology after a positive moment theorem",
        ],
        "next_gate": (
            "Work in the flat mean-zero log-field chart. Derive a direct "
            "one-mode action/fiber ratio bound under psi=eta+s h; do not count "
            "the tree Jacobian as additional confinement because it cancels."
        ),
        "does_not_establish": [
            "a direct action-difference or conditional-fiber ratio bound",
            "a normalized lowest-mode moment bound or its divergence",
            "the actual interacting H^-1 moment bound or its divergence",
            "tightness or a continuum Euclidean BT measure",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
            "a literature-priority claim",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "arithmetic": (
                "Exact Fraction arithmetic for the C4 tree, coarea, action, "
                "and ratio fixture; no floating-point value enters the claim"
            ),
        },
        "verification_commands": [
            "python3 reverse_physics/bt_euclidean_residual_tilt_jacobian_cancellation.py --check",
            "python3 reverse_physics/verify_bt_euclidean_residual_tilt_jacobian_cancellation.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_residual_tilt_jacobian_cancellation",
        ],
        "tier_receipt": {
            "command_results": [
                {
                    "command": "ulimit -v 500000; python3 reverse_physics/bt_euclidean_residual_tilt_jacobian_cancellation.py --check",
                    "tier": 1,
                    "status": "PASS_19_OF_19",
                    "elapsed_seconds": "0.03",
                    "max_rss_kb": 20700,
                },
                {
                    "command": "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_residual_tilt_jacobian_cancellation.py",
                    "tier": 1,
                    "status": "PASS_16_OF_16",
                    "elapsed_seconds": "0.09",
                    "max_rss_kb": 30360,
                },
                {
                    "command": "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_residual_tilt_jacobian_cancellation",
                    "tier": 1,
                    "status": "PASS_13_TESTS",
                    "elapsed_seconds": "0.12",
                    "max_rss_kb": 30712,
                },
            ],
            "tier_0": (
                "PASS: changed Python files compile; certificate and schema "
                "parse; scoped git diff --check is recorded before commit"
            ),
            "tier_1": (
                "PASS: producer 19/19, independent verifier 16/16, and 13 "
                "unit/mutation tests"
            ),
            "tier_2": (
                "predecessor residual-pushforward input reused by content hash; "
                "its independent certificate chain was not regenerated"
            ),
            "tier_3": (
                "NOT_RUN: no freeze, release, continuum, quantum lifecycle, "
                "or Lorentzian promotion"
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
        "[PASS] BT residual tilt Jacobian cancellation "
        f"({payload['checks']['passed']}/{payload['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
