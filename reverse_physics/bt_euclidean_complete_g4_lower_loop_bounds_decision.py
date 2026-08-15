#!/usr/bin/env python3
"""Build the certified BT complete-g4 lower-loop decision."""

from __future__ import annotations

import argparse
import hashlib
import json
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_LOWER_LOOP_BOUNDS_V1.json"
CERT_PATH = os.path.join(ROOT, CERT_REL)
ATLAS_PRODUCER_REL = "reverse_physics/bt_euclidean_complete_g4_lower_loop_atlas.py"
ATLAS_REL = "reverse_physics/data/bt_euclidean_complete_g4_lower_loop_atlas_v1.json"
PRODUCER_REL = "reverse_physics/bt_euclidean_complete_g4_lower_loop_bounds.py"
DATA_REL = "reverse_physics/data/bt_euclidean_complete_g4_lower_loop_bounds_v1.json"
UPSTREAM_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_NONCANCELLATION_V1.json"
SCHEMA_REL = "reverse_physics/schema/reverse-physics-bt-euclidean-complete-g4-lower-loop-bounds-v1.schema.json"
REPORT_REL = "reverse_physics/reports/bt-euclidean-complete-g4-lower-loop-bounds.md"
VERIFIER_REL = "reverse_physics/verify_bt_euclidean_complete_g4_lower_loop_bounds.py"
SOURCE_COMMIT = "0dc53a6ba452b0da8ad5a98b13b3d11871906778"


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def build() -> dict:
    with open(os.path.join(ROOT, DATA_REL), encoding="utf-8") as handle:
        result = json.load(handle)
    with open(os.path.join(ROOT, UPSTREAM_REL), encoding="utf-8") as handle:
        upstream = json.load(handle)
    checks = {
        "producer_checks_all_pass": all(result["checks"].values()),
        "upstream_two_loop_coefficient_is_strictly_negative": upstream["comparison"]["combined"] == "c_4+c_7<0",
        "zero_loop_has_exact_positive_finite_limit": result["zero_loop"]["status"] == "EXACT_POSITIVE_BOUNDED_NONZERO_LIMIT",
        "one_loop_is_at_most_logarithmic": result["one_loop_summary"]["asymptotic_status"] == "O_LOG_L_AND_little_o_N_omega_p",
        "complete_M4_leading_power_is_strictly_negative": result["complete_leading_power"]["status"] == "COMPLETE_M4_LEADING_POWER_COEFFICIENT_STRICTLY_NEGATIVE",
        "perturbative_uniformity_is_not_promoted": any("perturbative expansion" in item for item in result["does_not_establish"]),
        "actual_interacting_H_minus_one_remains_open": any("actual interacting H^-1" in item for item in result["does_not_establish"]),
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])
    inputs = [ATLAS_PRODUCER_REL, ATLAS_REL, PRODUCER_REL, DATA_REL, UPSTREAM_REL]
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_LOWER_LOOP_BOUNDS_V1",
        "schema_version": "reverse-physics-bt-euclidean-complete-g4-lower-loop-bounds-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "COMPLETE_M4_LEADING_POWER_DECIDED_INTERACTING_H_MINUS_ONE_OPEN",
        "result_kind": result["result_kind"],
        "question": "Can the omitted zero- and one-loop conditioned sectors cancel the certified negative two-loop N*omega(p) coefficient in complete BT M4?",
        "answer": "No. Exact affine enumeration leaves ten zero-loop and twenty-seven one-loop rows for every L>=7. The ten zero-loop rows combine to a rational function with positive limit 111/(32*pi^4). Selectable cubic bounds, all-leg quartic/quintic bounds, a five-center torus shell estimate, and the exact collinear cubic identity prove the full one-loop sector is O(log L). Both are little-o of N*omega(p), which is order L^2. Therefore complete perturbative M4 inherits the strictly negative leading coefficient c4+c7 from the two-loop sector. This is a coefficient theorem, not a uniform interacting or nonperturbative H^-1 theorem.",
        "data": DATA_REL,
        "data_sha256": sha256(DATA_REL),
        "atlas": ATLAS_REL,
        "atlas_sha256": sha256(ATLAS_REL),
        "producer": PRODUCER_REL,
        "producer_sha256": sha256(PRODUCER_REL),
        "zero_loop": result["zero_loop"],
        "collinear_cubic_identity": result["collinear_cubic_identity"],
        "one_loop_shell_lemma": result["one_loop_shell_lemma"],
        "one_loop_summary": result["one_loop_summary"],
        "complete_leading_power": result["complete_leading_power"],
        "checks": checks,
        "does_not_establish": result["does_not_establish"],
        "missing_object_ledger": [
            "a uniform remainder theorem for the perturbative expansion on the tuned coupling branch",
            "a nonperturbative centered conditional-score or convexity estimate",
            "the actual interacting H^-1 second moment",
            "a tight continuum measure or identification theorem",
            "any Born/Krein reconstruction or Lorentzian causal transfer",
        ],
        "next_gate": result["next_gate"],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in inputs],
            "exact_arithmetic": "The affine atlas, all coefficients, Laurent-polynomial cross multiplication, exponent allocations, shell counts, and bound constants use integers or Fraction arithmetic. The displayed pi factors enter only through analytic sine inequalities; no floating-point value decides a claim.",
            "assumptions": [
                "The certified connected-M4 normalization and two-loop affine atlas are imported unchanged through their downstream certificate hashes.",
                "The external momentum is p=(1,0,0,0) on the four-dimensional periodic lattice.",
                "The generic affine lower-loop atlas is restricted to L>=7 because its maximum absolute component source is six.",
                "This is a perturbative LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL coefficient result only.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_lower_loop_atlas.py --check",
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_lower_loop_bounds.py --check",
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_lower_loop_bounds_decision.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_lower_loop_bounds.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_lower_loop_bounds",
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
