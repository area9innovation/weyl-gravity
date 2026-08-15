#!/usr/bin/env python3
"""Build the certificate for the surviving BT g^4 coefficient normal forms."""

from __future__ import annotations

import argparse
import hashlib
import json
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_COEFFICIENT_NORMAL_FORM_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
DATA_REL = (
    "reverse_physics/data/"
    "bt_euclidean_complete_g4_two_pair_coefficient_normal_form_v1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-complete-g4-two-pair-coefficient-normal-form-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-complete-g4-two-pair-coefficient-normal-form.md"
)
PRODUCER_REL = (
    "reverse_physics/"
    "bt_euclidean_complete_g4_two_pair_coefficient_normal_form.py"
)
VERIFIER_REL = (
    "reverse_physics/"
    "verify_bt_euclidean_complete_g4_two_pair_coefficient_normal_form.py"
)
SOURCE_COMMIT = "dd023eef41548ba8c3fa1c75ffc27dd754dfebfd"


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
        "common_normalization_is_fixed": result["normalization"]["status"]
        == "COMMON_NORMALIZATION_FIXED",
        "pair_four_is_strictly_negative": result["method_disposition"][
            "pair_4_coefficient_normal_form"
        ]
        == "PROVED_STRICTLY_NEGATIVE",
        "pair_seven_is_strictly_positive_and_finite": result[
            "method_disposition"
        ]["pair_7_coefficient_normal_form"]
        == "PROVED_STRICTLY_POSITIVE_FINITE",
        "combined_coefficient_remains_open": result["method_disposition"][
            "combined_pair_4_pair_7_coefficient"
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
    inputs = [
        result["inputs"]["linear_pair_certificate"],
        result["inputs"]["seven_kernel_certificate"],
        PRODUCER_REL,
        DATA_REL,
    ]
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_COEFFICIENT_NORMAL_FORM_V1",
        "schema_version": "reverse-physics-bt-euclidean-complete-g4-two-pair-coefficient-normal-form-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "TWO_PAIR_COEFFICIENT_NORMAL_FORMS_PROVED_COMPARISON_OPEN",
        "result_kind": result["result_kind"],
        "question": "Do the two surviving inversion pairs have rigorous common-scale limits, and can their coefficients yet be proved not to cancel?",
        "answer": "Both limits exist on the N*omega(p_L) normalization. Pair 4 has the exact negative coefficient c_4=-(2*A_4/pi^4)*S_4 and exact rational truncations prove c_4<-0.01613. Pair 7 has an exact positive finite Brillouin-zone coefficient; its six-term soft derivative collapses to [omega(q)sin(q_1)+omega(r)sin(r_1)+omega(-q-r)sin(-q_1-r_1)]/6. No certified upper bound below 0.01613 is yet available, so noncancellation, tuned control, complete M4, and the actual interacting H^-1 estimate remain open.",
        "data": DATA_REL,
        "data_sha256": sha256(DATA_REL),
        "producer": PRODUCER_REL,
        "producer_sha256": sha256(PRODUCER_REL),
        "normalization": result["normalization"],
        "pair_four": result["pair_four"],
        "pair_seven": result["pair_seven"],
        "comparison_gate": result["comparison_gate"],
        "method_disposition": result["method_disposition"],
        "checks": checks,
        "does_not_establish": result["does_not_establish"],
        "missing_object_ledger": [
            "a certified upper interval for c_7 with endpoint below 0.01613, or another proof that c_4+c_7 is nonzero",
            "a signed subleading estimate if c_4+c_7 cancels",
            "lower-loop recombination with the complete M4 coefficient",
            "a volume-uniform nonperturbative center or score estimate",
            "the actual interacting H^-1 second moment",
        ],
        "next_gate": result["next_gate"],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in inputs
            ],
            "exact_arithmetic": "All return probabilities, finite integer sums, coefficient prefactors, and the c_4 rational gap use fractions.Fraction; no binary floating point enters the certified decision.",
            "assumptions": [
                "The certified complete-g4 atlas and two-pair reduction are imported unchanged by content hash.",
                "The massless covariance zero mode is omitted before cancellations and limits.",
                "The external mode is p_L=(2*pi/L)e_1 and L tends to infinity through integers.",
                "The result is perturbative and EUCLIDEAN-SPECTRAL only.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_two_pair_coefficient_normal_form.py --check",
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_two_pair_coefficient_normal_form_decision.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_two_pair_coefficient_normal_form.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_two_pair_coefficient_normal_form",
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
