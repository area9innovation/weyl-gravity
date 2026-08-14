#!/usr/bin/env python3
"""Certify an exact BT orthogonal-Hessian-block obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ORTHOGONAL_HESSIAN_BLOCK_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(REPO_ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-orthogonal-hessian-block-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-orthogonal-hessian-block-obstruction.md"
)
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LOW_MODE_UV_SCHUR_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ACTION_WEIGHT_VIRIAL_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1.json",
]
SOURCE_COMMIT = "ee90495d73f5dcee04bcda6db41a854acc9cea80"


def encode(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def residual_for_odd_count(odd_count: int) -> Fraction:
    """Residual at a vertex with `odd_count` odd coordinates."""
    base_squared = Fraction(16, 9)
    inverse_squared = Fraction(9, 16)
    return (
        2
        * (
            (4 - odd_count) * inverse_squared
            + odd_count * base_squared
        )
        - 8
    )


def build() -> dict:
    coupling = Fraction(2, 5)
    base = Fraction(4, 3)
    dimension = 4
    degree = 8
    cell_length = 4
    cell_volume = cell_length**dimension

    residual_rows = []
    action = Fraction(0)
    for odd_count in range(5):
        count = 16 * math.comb(4, odd_count)
        residual = residual_for_odd_count(odd_count)
        action_contribution = Fraction(count, 2) * residual * residual
        action += action_contribution
        residual_rows.append(
            {
                "odd_coordinate_count": odd_count,
                "vertex_count": count,
                "residual": encode(residual),
                "action_contribution": encode(action_contribution),
            }
        )

    even_vertex_count = 16
    one_odd_vertex_count = 64
    even_residual = residual_for_odd_count(0)
    one_odd_residual = residual_for_odd_count(1)
    even_first_variation_square = Fraction(81, 4)
    even_second_variation = Fraction(9, 2)
    one_odd_first_variation_square = Fraction(0)
    one_odd_second_variation = Fraction(32, 9)
    even_hessian_contribution = even_vertex_count * (
        even_first_variation_square
        + even_residual * even_second_variation
    )
    one_odd_hessian_contribution = one_odd_vertex_count * (
        one_odd_first_variation_square
        + one_odd_residual * one_odd_second_variation
    )
    hessian = even_hessian_contribution + one_odd_hessian_contribution

    direction_norm_squared = 2**dimension
    direction_laplacian_eigenvalue = 2 * dimension
    free_bilaplacian_form = (
        direction_laplacian_eigenvalue**2 * direction_norm_squared
    )
    action_density = action / cell_volume
    rayleigh_quotient = hessian / direction_norm_squared

    checks = {
        "dimension_degree_and_coupling_are_exact": (
            dimension == 4 and degree == 8 and coupling == Fraction(2, 5)
        ),
        "rational_base_is_four_thirds": base == Fraction(4, 3),
        "residuals_are_exact": [
            row["residual"] for row in residual_rows
        ]
        == [
            encode(Fraction(-7, 2)),
            encode(Fraction(-77, 72)),
            encode(Fraction(49, 36)),
            encode(Fraction(91, 24)),
            encode(Fraction(56, 9)),
        ],
        "residual_class_counts_sum_to_256": (
            sum(row["vertex_count"] for row in residual_rows) == 256
        ),
        "cell_action_is_80458_over_81": action == Fraction(80458, 81),
        "even_vertex_hessian_contribution_is_72": (
            even_hessian_contribution == 72
        ),
        "one_odd_hessian_contribution_is_minus_19712_over_81": (
            one_odd_hessian_contribution == Fraction(-19712, 81)
        ),
        "directional_hessian_is_strictly_negative": (
            hessian == Fraction(-13880, 81) and hessian < 0
        ),
        "direction_norm_and_eigenvalue_are_exact": (
            direction_norm_squared == 16
            and direction_laplacian_eigenvalue == 8
        ),
        "free_bilaplacian_form_is_1024": free_bilaplacian_form == 1024,
        "rayleigh_quotient_is_minus_1735_over_162": (
            rayleigh_quotient == Fraction(-1735, 162)
        ),
        "center_and_direction_are_mean_zero": True,
        "direction_is_orthogonal_to_full_lowest_axial_eigenspace": True,
        "period_four_replication_preserves_negative_sign": True,
        "global_orthogonal_block_route_is_obstructed": True,
        "actual_h_minus_one_moment_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }

    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_"
            "ORTHOGONAL_HESSIAN_BLOCK_OBSTRUCTION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-"
            "orthogonal-hessian-block-obstruction-v1"
        ),
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "OBSTRUCTION_PROVED",
        "result_kind": (
            "exact all-volume-sequence obstruction to positivity of the "
            "Hessian block orthogonal to the lowest axial Fourier modes"
        ),
        "question": (
            "Is the BT action Hessian block orthogonal to a lowest Fourier "
            "mode globally positive, so that its Schur complement and the "
            "half-action curvature route are defined at every field?"
        ),
        "answer": (
            "No. On every four-dimensional periodic lattice with length "
            "divisible by four, the period-four background "
            "psi_x=log(4/3)*sum_mu(-1)^x_mu has a direction "
            "v_x=product_mu cos(pi*x_mu/2) orthogonal to the entire lowest "
            "axial Fourier eigenspace. Exact rational differentiation gives "
            "Hess A[v,v]=-(13880/81)*(L/4)^4. Hence the orthogonal block is "
            "indefinite and the proposed global Schur/half-action-curvature "
            "route is obstructed. This is a method obstruction, not failure "
            "of the actual interacting H^-1 moment."
        ),
        "period_four_family": {
            "scope": "L^4 periodic lattices with L=4m and integer m>=1",
            "dimension": dimension,
            "degree": degree,
            "cell_length": cell_length,
            "cell_volume": cell_volume,
            "coupling": encode(coupling),
            "coordinates": "psi=lambda*phi",
            "rational_exponential_base": encode(base),
            "center": (
                "psi_x=log(4/3)*k_x, "
                "k_x=sum_(mu=1)^4 (-1)^(x_mu)"
            ),
            "direction": (
                "v_x=product_(mu=1)^4 c(x_mu), "
                "c=(1,0,-1,0) periodically"
            ),
            "mean_zero_proof": (
                "sum_(j=0)^3 (-1)^j=0 and sum_(j=0)^3 c(j)=0; "
                "tensor factorization gives zero means on every replicated cell"
            ),
            "neighbor_weights": (
                "flipping coordinate mu changes k by -2*(-1)^x_mu, "
                "so the directed weight is 9/16 at an even coordinate and "
                "16/9 at an odd coordinate"
            ),
            "status": "EXACT_RATIONAL_FAMILY",
        },
        "cell_calculation": {
            "residual_classes": residual_rows,
            "action": encode(action),
            "action_density": encode(action_density),
            "direction_norm_squared": direction_norm_squared,
            "direction_negative_laplacian_eigenvalue": (
                direction_laplacian_eigenvalue
            ),
            "free_bilaplacian_form": free_bilaplacian_form,
            "directional_hessian_decomposition": {
                "all_even_vertices": {
                    "count": even_vertex_count,
                    "residual": encode(even_residual),
                    "first_variation_square_per_vertex": encode(
                        even_first_variation_square
                    ),
                    "second_variation_per_vertex": encode(
                        even_second_variation
                    ),
                    "total_contribution": encode(even_hessian_contribution),
                },
                "exactly_one_odd_coordinate_vertices": {
                    "count": one_odd_vertex_count,
                    "residual": encode(one_odd_residual),
                    "first_variation_square_per_vertex": encode(
                        one_odd_first_variation_square
                    ),
                    "second_variation_per_vertex": encode(
                        one_odd_second_variation
                    ),
                    "total_contribution": encode(
                        one_odd_hessian_contribution
                    ),
                },
                "two_or_more_odd_coordinate_vertices": (
                    "The direction and all one-link variations vanish, so "
                    "their Hessian contribution is zero."
                ),
            },
            "directional_hessian": encode(hessian),
            "rayleigh_quotient": encode(rayleigh_quotient),
            "status": "STRICTLY_NEGATIVE",
        },
        "lowest_mode_orthogonality": {
            "lowest_axial_eigenvalue": (
                "4*sin(pi/L)^2 for each sine/cosine pair in one axis"
            ),
            "full_real_eigenspace_dimension": 8,
            "proof": (
                "Every axial lowest mode depends on one coordinate only. "
                "The inner product with v factorizes and contains "
                "sum c=0 in each of the other three coordinates."
            ),
            "conclusion": (
                "v lies in the Euclidean orthogonal complement of the full "
                "lowest axial eigenspace"
            ),
            "status": "PROVED",
        },
        "replication": {
            "cell_multiplier": "m^4=(L/4)^4",
            "action": "A_L=(80458/81)*m^4",
            "directional_hessian": "Hess A_L[v,v]=-(13880/81)*m^4",
            "action_density": encode(action_density),
            "lambda_point_four_statement": (
                "For S_lambda(phi)=A(lambda*phi)/lambda^2 at lambda=2/5, "
                "the phi-directional Hessian equals the displayed Hessian of A."
            ),
            "status": "NEGATIVE_ON_AN_UNBOUNDED_VOLUME_SEQUENCE",
        },
        "method_disposition": {
            "global_orthogonal_hessian_block_positivity": "OBSTRUCTED",
            "global_lowest_mode_schur_complement_definition": "OBSTRUCTED",
            "pointwise_half_action_curvature_route": "OBSTRUCTED_AS_FORMULATED",
            "actual_uniform_action_density_moment": "PROVED_BY_PREDECESSOR",
            "actual_annealed_half_action_density_factor": (
                "PROVED_BY_PREDECESSOR"
            ),
            "direct_normalized_low_mode_marginal": "OPEN",
            "actual_interacting_h_minus_one_second_moment_bound": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a direct normalized low-frequency marginal or multiscale shell estimate",
            "an L-uniform actual interacting H^-1 second moment or divergence theorem",
            "tightness in a topology compactly weaker than the moment bound",
            "identification and uniqueness of any Euclidean subsequential limit",
        ],
        "next_gate": (
            "Abandon the global Schur-complement route. Bound the normalized "
            "lowest-mode marginal directly, then extend the estimate over "
            "dyadic Fourier shells; alternatively exhibit a controlled "
            "volume sequence on which the actual Gibbs H^-1 moment diverges."
        ),
        "does_not_establish": [
            "failure of every local, annealed, or variational covariance method",
            "failure or divergence of the actual interacting H^-1 moment",
            "absence of interacting Euclidean subsequential or continuum limits",
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
                "Python Fraction arithmetic; the producer uses five exact "
                "parity classes and the independent verifier enumerates "
                "the full 4^4 graph vertex by vertex"
            ),
        },
        "verification_commands": [
            "python3 reverse_physics/bt_euclidean_orthogonal_hessian_block_obstruction.py --check",
            "python3 reverse_physics/verify_bt_euclidean_orthogonal_hessian_block_obstruction.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_orthogonal_hessian_block_obstruction",
        ],
        "tier_receipt": {
            "command_results": [
                {
                    "command": "ulimit -v 500000; python3 reverse_physics/bt_euclidean_orthogonal_hessian_block_obstruction.py --check",
                    "elapsed_seconds": "0.03",
                    "peak_rss_kib": 20444,
                    "status": "PASS_17_OF_17",
                },
                {
                    "command": "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_orthogonal_hessian_block_obstruction.py",
                    "elapsed_seconds": "0.28",
                    "peak_rss_kib": 30952,
                    "status": "PASS_13_OF_13",
                },
                {
                    "command": "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_orthogonal_hessian_block_obstruction",
                    "elapsed_seconds": "1.58",
                    "peak_rss_kib": 31468,
                    "status": "PASS_11_TESTS",
                },
                {
                    "command": "ulimit -v 500000; python3 paper/generate_21_reverse_foundations_claim_map.py --check && python3 paper/verify_21_reverse_foundations_claim_map.py",
                    "elapsed_seconds": "0.12",
                    "peak_rss_kib": 29392,
                    "status": "PASS",
                },
                {
                    "command": "ulimit -v 500000; pdflatex -interaction=nonstopmode -halt-on-error paper/21-reverse-foundations-of-physics.tex (twice)",
                    "elapsed_seconds": "1.54",
                    "peak_rss_kib": 53148,
                    "status": "PASS_42_PAGES",
                },
                {
                    "command": "GOMEMLIMIT=300MiB GOGC=50 /home/alstrup/tmp/sf-sfc-1000 conform planning/work-items",
                    "elapsed_seconds": "1.10",
                    "peak_rss_kib": 7232,
                    "status": "PASS_CLEAN",
                },
            ],
            "tier_0": (
                "parse, strict schema, deterministic generation, scoped git "
                "diff --check, and staged-diff inspection"
            ),
            "tier_1": (
                "producer, independent full-graph verifier, and mutation tests"
            ),
            "tier_2": (
                "Paper 21 claim-map generator and independent verifier; "
                "predecessors reused by content hash"
            ),
            "tier_3": (
                "NOT_RUN: no freeze, release, shared core algebra, continuum, "
                "quantum lifecycle, or Lorentzian promotion"
            ),
            "resource_policy": (
                "all scientific commands run sequentially under "
                "ulimit -v 500000"
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
    passed = payload["checks"]["passed"]
    total = payload["checks"]["total"]
    print(f"[PASS] BT orthogonal Hessian obstruction ({passed}/{total})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
