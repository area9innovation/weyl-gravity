#!/usr/bin/env python3
"""Record the calibrated binary64 L=6 BT pair-block g4 preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_L6_PREFLIGHT_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-pair-block-response-g4-l6-preflight-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-pair-block-response-g4-l6-preflight.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_pair_block_response_g4_l6_preflight.py"
)
SOURCE_REL = "reverse_physics/bt_euclidean_pair_block_response_g4_l6_preflight.c"
DATA_REL = "reverse_physics/data/bt_euclidean_pair_block_response_g4_l6_preflight_v1.json"
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_TOPOLOGY_REDUCTION_V1.json",
    SOURCE_REL,
    DATA_REL,
]
SOURCE_COMMIT = "b349a24e91dcd60151fed7050ad63a45b902706d"


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def build() -> dict:
    with open(os.path.join(ROOT, DATA_REL), encoding="utf-8") as handle:
        data = json.load(handle)
    terms = data["terms"]
    ordered_terms = [
        terms["F_4_0"],
        terms["F_4_2"],
        terms["F_4_4"],
        terms["minus_F_3_3_Gamma_3"],
        terms["minus_F_2_2_Gamma_4"],
        terms["plus_F_2_2_Gamma_3_squared"],
    ]
    exact_b2 = Fraction(956585197, 10069092633600)
    calibration = data["one_loop_calibration"]
    absolute_sum = sum(abs(value) for value in ordered_terms)
    checks = {
        "lattice_is_certified_L6_fixture": data["lattice_length"] == 6 and data["volume"] == 1296,
        "all_outer_rows_were_evaluated": data["outer_momentum_rows"] == 1296,
        "six_terms_are_recorded": len(ordered_terms) == 6,
        "binary64_sum_reproduces_record": math.isclose(sum(ordered_terms), data["sum"], rel_tol=0, abs_tol=5e-18),
        "observed_sum_is_positive": data["sum"] > 0 and data["observed_sign"] == "POSITIVE_BINARY64",
        "one_loop_calibration_matches_exact_reference": abs(calibration["computed"] - float(exact_b2)) < 2e-16,
        "recorded_calibration_error_is_conservative": abs(calibration["computed"] - float(exact_b2)) <= calibration["absolute_error"] * 1.01,
        "result_is_not_promoted_to_exact_coefficient": data["status"] == "SUPPORTING_ONLY_EXACT_OR_RIGOROUS_SIGN_REQUIRED",
        "cancellation_ratio_is_not_tiny": data["sum"] / absolute_sum > 0.1,
        "memory_ceiling_was_respected": data["peak_kib"] < data["memory_limit_kib"],
        "exact_or_rigorous_sign_remains_open": True,
        "large_volume_and_hminus1_remain_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_L6_PREFLIGHT_V1",
        "schema_version": "reverse-physics-bt-euclidean-pair-block-response-g4-l6-preflight-v1",
        "created": "2026-08-16",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "calibrated bounded-memory binary64 preflight for the six-term full-Gibbs BT pair-block order-lambda^4 coefficient on the periodic 6^4 lattice",
        "question": "What sign and cancellation pattern does the exact six-topology formula exhibit on the first nondegenerate L=6 fixture, before spending resources on a rigorous algebraic sign rail?",
        "answer": (
            "The calibrated binary64 evaluation is positive. The six terms are +0.0005033754906226740, +0.002164969456075357, -0.0010564679600843152, +0.000011171944528325162, -0.0016602526411414497, and +0.0008588398511355388, summing to 0.00082163614113613. The same plane-wave response-vertex code reproduces the certified exact one-loop coefficient 956585197/10069092633600 with absolute binary64 error 1.88e-17. Peak resident memory is only 3172 KiB, so the connected streaming architecture resolves the prior OOM failure. The fourth-order sum is about 13 percent of the sum of absolute term magnitudes, so the observed sign is not a last-bit cancellation. Nevertheless this is numerical supporting evidence only: no exact rational, algebraic, or outward-rounded interval rail has yet certified the sign, and the coefficient lifecycle remains open."
        ),
        "calibration": {
            "exact_one_loop": {
                "numerator": exact_b2.numerator,
                "denominator": exact_b2.denominator,
            },
            "computed_binary64": calibration["computed"],
            "absolute_error": calibration["absolute_error"],
            "status": "MATCHES_EXACT_REFERENCE_WITHIN_2E_MINUS_16",
        },
        "six_term_result": {
            "terms": terms,
            "sum": data["sum"],
            "sum_of_absolute_terms": absolute_sum,
            "cancellation_ratio": data["sum"] / absolute_sum,
            "observed_sign": data["observed_sign"],
            "status": data["status"],
        },
        "resource_receipt": {
            "threads": data["threads"],
            "elapsed_seconds": data["elapsed_seconds"],
            "peak_kib": data["peak_kib"],
            "memory_limit_kib": data["memory_limit_kib"],
            "compiler": data["compiler"],
            "architecture": "streamed 1296-by-1296 momentum pairs; no dense covariance or coordinate response tensor",
        },
        "method_disposition": {
            "binary64_L6_g4_preflight": "POSITIVE_OBSERVED",
            "one_loop_calibration": "PASS",
            "bounded_memory_streaming_architecture": "PASS",
            "exact_or_rigorous_L6_g4_sign": "OPEN",
            "coefficient_computed_lifecycle": "NOT_PROMOTED",
            "large_volume_g4_power_or_log": "OPEN",
            "uniform_pair_response": "OPEN",
            "response_to_witten_schur_bridge": "OPEN",
            "actual_interacting_h_minus_one": "OPEN",
            "continuum_measure": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "next_gate": (
            "Replace every binary64 scalar in the same six-term streaming evaluator by either finite-field arithmetic over primes admitting sixth roots of unity, followed by rational reconstruction and a conjugate-root check, or by outward-rounded complex balls with a final interval strictly above zero. The exact one-loop calibration and all six individual fourth-order terms must be checked on that independent rail before promoting the L=6 coefficient or beginning large-volume hard/soft estimates."
        ),
        "does_not_establish": [
            "an exact value or rigorous sign for the L=6 order-lambda^4 coefficient",
            "positivity of the response at lambda=2/5 after all higher orders",
            "a uniform perturbative remainder or nonperturbative response estimate",
            "a heat-bath gap, Witten estimate, or interacting H^-1 theorem",
            "tightness or continuum identification",
            "a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "numerical_arithmetic": "C11 binary64 complex arithmetic with exact L=6 mode enumeration and OpenMP reduction; supporting only",
            "assumptions": [
                "the imported six-term topology formula and its factorial normalization are correct",
                "agreement with the exact one-loop coefficient calibrates the local response vertex but is not an independent proof of the fourth-order sums",
                "parallel reduction order can perturb final binary64 last bits and is irrelevant to the recorded non-rigorous sign orientation",
            ],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_pair_block_response_g4_l6_preflight.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_pair_block_response_g4_l6_preflight.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_pair_block_response_g4_l6_preflight",
            "cc -std=c11 -O3 -fopenmp -D_DEFAULT_SOURCE -Wall -Wextra -Werror reverse_physics/bt_euclidean_pair_block_response_g4_l6_preflight.c -lm -o /tmp/bt-pair-g4-l6-preflight",
            "ulimit -v 500000; OMP_NUM_THREADS=8 /tmp/bt-pair-g4-l6-preflight",
        ],
        "tier_receipt": {
            "tier_0": "C/Python compilation, strict JSON/schema parsing, content hashes, scoped diff check, and staged-diff inspection required",
            "tier_1": "deterministic certificate producer, nonimporting data verifier, and fast compiled one-loop calibration rail required",
            "tier_2": "full 2330-second binary64 reproduction is recorded but is not an independent exact verification and is not normalized as a per-commit test",
            "tier_3": "not run: numerical preflight only; no coefficient, H^-1, continuum, freeze, release, shared-core, or Lorentzian promotion",
            "memory_policy": "all runs are under a 500000 KiB virtual-memory ceiling; the exhaustive run used 3172 KiB peak RSS",
            "elapsed_seconds_and_peak_kib": {
                "producer": "0.04 s, 20372 KiB",
                "independent_verifier_with_compiled_calibration": "16.62 s, 218936 KiB",
                "unit_tests": "16.55 s, 218768 KiB",
            },
            "repository_audits": {
                "planning_import": "PASS: 1702 nodes, 0 invalid items, 0 malformed events; 7.38 s, 201608 KiB",
                "science_forge_shadow": "not run: no registered shadow input changes; this skip is not a pass",
            },
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [key for key, value in checks.items() if not value],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verifier": VERIFY_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        print("[FAIL] internal checks", result["checks"]["failures"])
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
        "[PASS] BT pair-block g4 L6 numerical preflight "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
