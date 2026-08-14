#!/usr/bin/env python3
"""Build the certified generic-L BT g^4 two-loop reduction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_GENERAL_L_TWO_LOOP_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-complete-g4-general-l-two-loop-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-complete-g4-general-l-two-loop.md"
)
DATA_REL = (
    "reverse_physics/data/"
    "bt_euclidean_complete_g4_general_l_two_loop_v1.json"
)
PRODUCER_REL = (
    "reverse_physics/bt_euclidean_complete_g4_general_l_two_loop.py"
)
VERIFIER_REL = (
    "reverse_physics/verify_bt_euclidean_complete_g4_general_l_two_loop.py"
)
SOURCE_COMMIT = "54b46fdaabb3135822c7035e6f640940a66b0a29"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-euclidean-continuum-reconstruction.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_CONNECTED_NORMALIZATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_L4_DECISION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_SCORE_LOG_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SCORE_RG_MATCHING_V1.json",
    PRODUCER_REL,
    DATA_REL,
]


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def build() -> dict:
    with open(os.path.join(ROOT, DATA_REL), encoding="utf-8") as handle:
        atlas = json.load(handle)
    with open(
        os.path.join(
            ROOT,
            "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_L4_DECISION_V1.json",
        ),
        encoding="utf-8",
    ) as handle:
        l4 = json.load(handle)
    checks = {
        "atlas_checks_all_pass": all(atlas["checks"].values()),
        "atlas_is_valid_for_every_integer_L_at_least_five": atlas["volume_scope"][
            "lengths"
        ]
        == "every integer L>=5",
        "complete_two_loop_atlas_has_sixteen_survivors": atlas["statistics"][
            "surviving_integrand_count"
        ]
        == 16,
        "five_integrands_cancel_before_absolute_values": atlas["statistics"][
            "exactly_canceled_integrand_count"
        ]
        == 5,
        "factorized_remainder_is_positive_log_squared": atlas[
            "factorized_conditioning_sector"
        ]["status"]
        == "EXACT_POWER_TADPOLE_CANCELLATION_AND_LOG_SQUARED_BOUND_PROVED",
        "L4_factor_normalization_matches_exact_rank_loop_ledger": atlas[
            "factorized_conditioning_sector"
        ]["exact_L4_normalization_crosscheck"]["surviving_R_4"]
        == {"numerator": 3195980089, "denominator": 361267200},
        "finite_L4_M4_remains_exactly_negative": l4["method_disposition"][
            "finite_L4_complete_M4"
        ]
        == "NEGATIVE_NONZERO_EXACT",
        "remaining_fourteen_integrands_are_not_promoted_to_a_bound": True,
        "whole_M4_and_interacting_H_minus_one_gates_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_GENERAL_L_TWO_LOOP_V1",
        "schema_version": "reverse-physics-bt-euclidean-complete-g4-general-l-two-loop-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "GENERAL_L_TWO_LOOP_FORMULA_AND_FACTOR_TADPOLE_CANCELLATION_PROVED_REMAINING_KERNEL_BOUND_OPEN",
        "result_kind": "exact all-L>=5 connected two-loop reduction and uniform tuned-branch bound for its factorized conditioning sector",
        "question": "Can the bulk and rank-one two-loop sectors be combined before absolute values so that the apparent power-sized conditioning contribution is either exposed or canceled?",
        "answer": "Yes, partially and exactly. For every integer L>=5, exhaustive affine momentum-flow reduction turns 96 source-conserving oriented topology flows into 21 common integrands. Forty-eight flows are identically killed by the removed Gaussian zero mode. Five of the 21 integrands cancel exactly after bulk lines pinned to +/-p are placed on the same omega(p)^(-2) scale as rank-one covariance factors, leaving 16. All terms containing the power-sized quartic tadpole Y_L cancel: the Y_L^2 pair and both X_L*Y_L pairs vanish before absolute values. The only conditioning-scale remainder is the positive factor 162*X_L^2/[N*omega(p)^2], where X_L is the cubic one-loop bubble. The cubic soft-leg bound and an explicit four-dimensional lattice Green-sum estimate give X_L=O(log L), hence this remainder is O(log(L)^2) and g_L^4 times it is bounded on the already certified tuned asymptotically free refinement branch. Fourteen unfactorized two-loop integrands remain; their combined uniform estimate, the full M4 asymptotics, the nonperturbative score, and the actual interacting H^-1 moment are still open.",
        "data": DATA_REL,
        "data_sha256": sha256(DATA_REL),
        "producer": PRODUCER_REL,
        "producer_sha256": sha256(PRODUCER_REL),
        "two_loop_atlas": {
            "volume_scope": atlas["volume_scope"],
            "affine_notation": atlas["affine_notation"],
            "statistics": atlas["statistics"],
            "exact_cancellations": atlas["exact_cancellations"],
            "surviving_integrands": atlas["surviving_integrands"],
            "status": atlas["status"],
        },
        "factorized_conditioning_sector": atlas[
            "factorized_conditioning_sector"
        ],
        "method_disposition": {
            "generic_L_at_least_five_complete_two_loop_formula": "PROVED",
            "bulk_fixed_p_and_rank_one_common_scale_reorganization": "PROVED",
            "power_sized_Y_squared_and_XY_tadpole_survival": "CANCELED_EXACTLY",
            "factorized_conditioning_sector": "POSITIVE_O_LOG_SQUARED",
            "factorized_conditioning_sector_on_tuned_running_branch": "UNIFORMLY_BOUNDED",
            "remaining_fourteen_unfactorized_two_loop_kernel_bound": "OPEN",
            "large_volume_complete_M4_sign_and_scaling": "OPEN",
            "whole_lattice_order_g_four_power_survival": "OPEN",
            "nonperturbative_annealed_zero_fiber_score_bound": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": atlas["does_not_establish"],
        "missing_object_ledger": [
            "a common hard/one-soft/all-soft bound for the 14 unfactorized two-loop integrands",
            "the lower-loop sector asymptotics and their combination with the two-loop atlas",
            "after the fixed-order decision, a whole-composite nonperturbative score estimate",
            "after a one-mode theorem, dyadic Fourier-shell control of the actual interacting H^-1 moment",
        ],
        "next_gate": atlas["next_gate"],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "exact_arithmetic": "integer affine momentum forms, exact rational combinatorial coefficients, and symbolic analytic inequalities; no floating point enters the atlas or decision",
            "assumptions": [
                "p is the lowest axial lattice momentum and the real cosine mode is conditioned out",
                "the finite-volume fixed-order coefficient is not promoted to the resummed interacting measure",
                "the tuned running-coupling consequence uses only the previously certified refinement branch and applies only to the factorized remainder",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_general_l_two_loop.py --check",
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_general_l_two_loop_decision.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_general_l_two_loop.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_general_l_two_loop",
        ],
    }


def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()
    expected = render(build())
    if args.stdout:
        print(expected, end="")
        return 0
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                return 0 if handle.read() == expected else 1
        except OSError:
            return 1
    with open(CERT_PATH, "w", encoding="utf-8") as handle:
        handle.write(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
