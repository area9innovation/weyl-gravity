#!/usr/bin/env python3
"""Build the certified BT complete-g4 linear-pair power reduction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_LINEAR_PAIR_BOUNDS_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-complete-g4-linear-pair-bounds-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-complete-g4-linear-pair-bounds.md"
)
DATA_REL = (
    "reverse_physics/data/"
    "bt_euclidean_complete_g4_linear_pair_bounds_v1.json"
)
PRODUCER_REL = "reverse_physics/bt_euclidean_complete_g4_linear_pair_bounds.py"
VERIFIER_REL = (
    "reverse_physics/verify_bt_euclidean_complete_g4_linear_pair_bounds.py"
)
SOURCE_COMMIT = "88dcdd26fc53b46db7ebe0300fe54e19e8365858"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-euclidean-continuum-reconstruction.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SEVEN_KERNEL_REDUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SUBPOWER_PAIR_BOUNDS_V1.json",
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
        result = json.load(handle)
    checks = {
        "result_checks_all_pass": all(result["checks"].values()),
        "pair_three_is_exactly_O_L": result["method_disposition"][
            "pair_3_scale"
        ]
        == "O_L",
        "pair_six_is_exactly_O_L_log_L": result["method_disposition"][
            "pair_6_scale"
        ]
        == "O_L_LOG_L",
        "five_pair_subpower_set_is_exact": result["power_sector_reduction"][
            "subpower_pairs"
        ]
        == [1, 2, 3, 5, 6],
        "power_gate_is_exactly_pairs_four_and_seven": result[
            "power_sector_reduction"
        ]["pairs_still_capable_of_N_omega_p_scale"]
        == [4, 7],
        "pair_four_seven_coefficient_remains_open": result["method_disposition"][
            "combined_pairs_4_7_power_coefficient"
        ]
        == "OPEN",
        "tuned_uniformity_is_not_promoted": result["method_disposition"][
            "pairs_3_6_tuned_g_four_uniformity"
        ]
        == "NOT_ESTABLISHED_BY_THESE_BOUNDS",
        "complete_M4_remains_open": result["method_disposition"][
            "complete_M4_large_volume_sign_and_scaling"
        ]
        == "OPEN",
        "actual_interacting_H_minus_one_remains_open": result[
            "method_disposition"
        ]["actual_interacting_h_minus_one_second_moment"]
        == "OPEN",
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_LINEAR_PAIR_BOUNDS_V1",
        "schema_version": "reverse-physics-bt-euclidean-complete-g4-linear-pair-bounds-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "TWO_LINEAR_PAIR_BOUNDS_PROVED_TWO_PAIR_POWER_GATE_OPEN",
        "result_kind": result["result_kind"],
        "question": "Can inversion pairs 3 and 6 contribute to the N*omega(p) coefficient, and what remains of the complete-g4 leading-power gate?",
        "answer": "No. Pair 3 admits an exact all-volume O(L) bound after cubic and quartic soft-factor allocation reduces it to a three-weight torus convolution. Pair 6 admits an O(L log L) bound after the new all-leg quintic estimate abs(K5)<=8*product sqrt(omega) factorizes it into G1(L)*J_L. Both are little-o of N*omega(p), so pairs 1, 2, 3, 5, and 6 have zero leading-power coefficient. Only negative pair 4 and positive pair 7 remain power-capable. Their common coefficient, tuned-g_L^4 control of the subleading sector, the complete seven-kernel sum, complete M4, the nonperturbative score, and the actual interacting H^-1 moment remain open.",
        "data": DATA_REL,
        "data_sha256": sha256(DATA_REL),
        "producer": PRODUCER_REL,
        "producer_sha256": sha256(PRODUCER_REL),
        "vertex_bounds": result["vertex_bounds"],
        "torus_convolution": result["torus_convolution"],
        "pair_bounds": result["pair_bounds"],
        "power_sector_reduction": result["power_sector_reduction"],
        "method_disposition": result["method_disposition"],
        "checks": checks,
        "does_not_establish": result["does_not_establish"],
        "missing_object_ledger": [
            "the common N*omega(p) coefficient of pairs 4 and 7",
            "a signed subleading bound if the pair-4/pair-7 power coefficient cancels",
            "factorized and lower-loop recombination needed to decide complete M4",
            "a whole-composite nonperturbative score estimate",
            "the dyadic shell estimate for the actual interacting H^-1 moment",
        ],
        "next_gate": result["next_gate"],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "exact_arithmetic": "integer affine momentum forms, Fraction vertex constants, exact max-norm shell polynomials, rational inequalities, and symbolic asymptotic comparison; no floating point enters the decision",
            "assumptions": [
                "L is an integer at least five and p is the lowest axial momentum",
                "zero covariance modes are omitted before canceled soft factors are bounded",
                "the tuned-branch statement imports only g_L^4=O(log(L)^(-2)) and is retained as a nonuniform upper-bound boundary",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_linear_pair_bounds.py --check",
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_linear_pair_bounds_decision.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_linear_pair_bounds.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_linear_pair_bounds",
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
