#!/usr/bin/env python3
"""Build the certified BT complete-g4 subpower-pair decision."""

from __future__ import annotations

import argparse
import hashlib
import json
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SUBPOWER_PAIR_BOUNDS_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-complete-g4-subpower-pair-bounds-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-complete-g4-subpower-pair-bounds.md"
)
DATA_REL = (
    "reverse_physics/data/"
    "bt_euclidean_complete_g4_subpower_pair_bounds_v1.json"
)
PRODUCER_REL = (
    "reverse_physics/bt_euclidean_complete_g4_subpower_pair_bounds.py"
)
VERIFIER_REL = (
    "reverse_physics/verify_bt_euclidean_complete_g4_subpower_pair_bounds.py"
)
SOURCE_COMMIT = "1ffc17e215f5a5e55ce7c095bccd25210af0698c"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-euclidean-continuum-reconstruction.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_GENERAL_L_TWO_LOOP_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SEVEN_KERNEL_REDUCTION_V1.json",
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
        "three_pairs_have_exact_log_squared_bounds": [
            row["asymptotic_status"] for row in result["pair_bounds"]
        ]
        == ["O_LOG_SQUARED_AND_little_o_N_omega_p"] * 3,
        "subpower_pair_set_is_exactly_one_two_five": result[
            "power_sector_reduction"
        ]["subpower_pairs"]
        == [1, 2, 5],
        "tuned_g_four_uniformity_is_proved_for_three_pairs": result[
            "method_disposition"
        ]["pairs_1_2_5_tuned_g_four_uniformity"]
        == "PROVED",
        "three_pairs_have_zero_power_coefficient": result["method_disposition"][
            "pairs_1_2_5_contribution_to_N_omega_p_coefficient"
        ]
        == "ZERO",
        "power_gate_is_exactly_pairs_three_four_six_seven": result[
            "power_sector_reduction"
        ]["pairs_still_capable_of_N_omega_p_scale"]
        == [3, 4, 6, 7],
        "pair_three_and_six_scales_remain_open": result["method_disposition"][
            "pair_3_scale"
        ]
        == "OPEN"
        and result["method_disposition"]["pair_6_scale"] == "OPEN",
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
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SUBPOWER_PAIR_BOUNDS_V1",
        "schema_version": "reverse-physics-bt-euclidean-complete-g4-subpower-pair-bounds-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "THREE_SUBPOWER_PAIR_BOUNDS_PROVED_FOUR_PAIR_POWER_GATE_OPEN",
        "result_kind": result["result_kind"],
        "question": "Which of the seven exact inversion-paired kernels can contribute to the N*omega(p) power coefficient, and which admit explicit tuned-branch uniform bounds?",
        "answer": "Pairs 1, 2, and 5 are rigorously sub-power. Cubic soft-factor allocation reduces pairs 1 and 2 to at most 64*omega(p)^2*G2(L)^2/N. An all-leg quartic bound and a new two-centre shifted convolution estimate reduce pair 5 to at most 896*omega(p)^2*J_L^2/N, with J_L<=N*[11/16+(1/2)*log floor(L/2)]. Since 256<=N*omega(p)^2<=16*pi^4, all three pairs are O(log(L)^2), are little-o of N*omega(p), and become uniformly bounded after multiplication by tuned g_L^4. They cannot cancel a nonzero power coefficient. The power decision is therefore confined to pairs 3, 4, 6, and 7. The parity-sensitive scales of pairs 3 and 6, their combination with the proved negative pair 4 and positive power-capable pair 7, complete M4, the nonperturbative score, and the actual interacting H^-1 moment remain open.",
        "data": DATA_REL,
        "data_sha256": sha256(DATA_REL),
        "producer": PRODUCER_REL,
        "producer_sha256": sha256(PRODUCER_REL),
        "vertex_bounds": result["vertex_bounds"],
        "convolution_bounds": result["convolution_bounds"],
        "pair_bounds": result["pair_bounds"],
        "power_sector_reduction": result["power_sector_reduction"],
        "method_disposition": result["method_disposition"],
        "checks": checks,
        "does_not_establish": result["does_not_establish"],
        "missing_object_ledger": [
            "a p-reflection-symmetrized hard/one-soft/all-soft bound for pair 3",
            "a p-reflection-symmetrized hard/one-soft/all-soft bound for pair 6",
            "the common N*omega(p) coefficient of pairs 3, 4, 6, and 7",
            "factorized and lower-loop recombination needed to decide complete M4",
            "a whole-composite nonperturbative score estimate and dyadic H^-1 shell sum",
        ],
        "next_gate": result["next_gate"],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "exact_arithmetic": "integer affine forms, Fraction vertex constants, exact shell cardinalities, and symbolic inequalities; no floating point enters the decision",
            "assumptions": [
                "L is an integer at least five and p is the lowest axial momentum",
                "the tuned consequence imports only the previously certified g_L^2*log(L) asymptotic",
                "sub-power fixed-order bounds are not promoted to the combined coefficient or actual Gibbs measure",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_subpower_pair_bounds.py --check",
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_subpower_pair_bounds_decision.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_subpower_pair_bounds.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_subpower_pair_bounds",
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
