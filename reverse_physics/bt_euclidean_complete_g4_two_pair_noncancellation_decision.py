#!/usr/bin/env python3
"""Build the BT complete-g4 two-pair noncancellation certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_NONCANCELLATION_V1.json"
CERT_PATH = os.path.join(ROOT, CERT_REL)
DATA_REL = "reverse_physics/data/bt_euclidean_complete_g4_two_pair_noncancellation_v1.json"
SCHEMA_REL = "reverse_physics/schema/reverse-physics-bt-euclidean-complete-g4-two-pair-noncancellation-v1.schema.json"
REPORT_REL = "reverse_physics/reports/bt-euclidean-complete-g4-two-pair-noncancellation.md"
PRODUCER_REL = "reverse_physics/bt_euclidean_complete_g4_two_pair_noncancellation.py"
VERIFIER_REL = "reverse_physics/verify_bt_euclidean_complete_g4_two_pair_noncancellation.py"
SOURCE_COMMIT = "40d806bdbe7cd73205fed53ac2f2e17503f21ddb"


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
        "producer_checks_all_pass": all(result["checks"].values()),
        "sharp_dispersion_theorem_is_proved": result["method_disposition"]["sharp_lattice_vector_dispersion_inequality"] == "PROVED",
        "pair_seven_has_exact_outward_upper_interval": result["method_disposition"]["pair_7_upper_interval"] == "PROVED_EXACT_OUTWARD",
        "combined_coefficient_is_strictly_negative": result["method_disposition"]["combined_pair_4_pair_7_coefficient"] == "PROVED_STRICTLY_NEGATIVE",
        "complete_M4_remains_open": result["method_disposition"]["complete_M4_large_volume_sign_and_scaling"] == "OPEN",
        "actual_interacting_H_minus_one_remains_open": result["method_disposition"]["actual_interacting_h_minus_one_second_moment"] == "OPEN",
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])
    inputs = [
        result["inputs"]["two_pair_normal_form_certificate"],
        PRODUCER_REL,
        DATA_REL,
    ]
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_NONCANCELLATION_V1",
        "schema_version": "reverse-physics-bt-euclidean-complete-g4-two-pair-noncancellation-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "TWO_PAIR_NONCANCELLATION_PROVED_COMPLETE_M4_OPEN",
        "result_kind": result["result_kind"],
        "question": "Can the positive pair-7 coefficient cancel the negative pair-4 coefficient on their common N*omega(p_L) scale?",
        "answer": "No. A sharp lattice vector-dispersion inequality bounds c_7 by three times a three-Green convolution. Exact outward cubature and Hausdorff-Young give c_7<0.016103194<0.01613, while the upstream rational certificate gives c_4<-0.01613. Therefore c_4+c_7<0. This proves the sign of the leading two-loop power coefficient, not complete M4 or the interacting H^-1 estimate.",
        "data": DATA_REL,
        "data_sha256": sha256(DATA_REL),
        "producer": PRODUCER_REL,
        "producer_sha256": sha256(PRODUCER_REL),
        "dispersion_theorem": result["dispersion_theorem"],
        "pair_seven_bound": result["pair_seven_bound"],
        "comparison": result["comparison"],
        "method_disposition": result["method_disposition"],
        "checks": checks,
        "does_not_establish": result["does_not_establish"],
        "missing_object_ledger": [
            "a volume-uniform tuned bound for the subleading two-loop remainder",
            "lower-loop recombination into the complete order-g^4 coefficient",
            "the complete M4 large-volume sign and scaling",
            "a nonperturbative center or score estimate",
            "the actual interacting H^-1 second moment",
        ],
        "next_gate": result["next_gate"],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": relative, "sha256": sha256(relative)} for relative in inputs],
            "exact_arithmetic": "All pi and sine enclosures, walk returns, monotone box sums, reciprocal bounds, square-root ceilings, singular-origin remainders, and final comparisons use Fraction or integer arithmetic. Binary floating point is used only for the displayed decimal ceiling, never for a claim decision.",
            "assumptions": [
                "The upstream pair-4/pair-7 normal forms and common normalization are imported unchanged by content hash.",
                "The Brillouin-zone measure is normalized by (2*pi)^(-4) in each momentum variable.",
                "The infinite-volume Green function is the zero-mass four-dimensional lattice Green function.",
                "The result is perturbative and EUCLIDEAN-SPECTRAL only.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_two_pair_noncancellation.py --check",
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_two_pair_noncancellation_decision.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_two_pair_noncancellation.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_two_pair_noncancellation",
        ],
    }


def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(build())
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
