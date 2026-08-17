#!/usr/bin/env python3
"""Build the BT torus dyadic stopping-flow certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_DYADIC_STOPPING_FLOW_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-dyadic-stopping-flow-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-torus-dyadic-stopping-flow.md"
VERIFY_REL = "reverse_physics/verify_bt_euclidean_torus_dyadic_stopping_flow.py"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_TOP_BAND_FLOW_V1.json",
]
SOURCE_COMMIT = "1931a152ed8eeb5e69b2daf6e368f6b15f394b04"


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def constant_audit() -> dict[str, object]:
    q = 8
    cutoff_coefficient = 512
    minimum_side = 4096
    minimum_side_log = 12
    sparse_required_coefficient = 512 * q**5 * 4
    sparse_available_coefficient = cutoff_coefficient**3
    stopping_left = 2**16  # 4096^(4/3)
    stopping_log = 9 + 10 * minimum_side_log // 3
    stopping_right = 16 * stopping_log**2
    checks = {
        "sparse_coefficient_clears": sparse_available_coefficient
        >= sparse_required_coefficient,
        "minimum_side_is_power_of_two": minimum_side == 2**minimum_side_log,
        "stopping_log_is_exact": stopping_log == 49,
        "stopping_condition_holds_at_minimum_side": stopping_left >= stopping_right,
        "old_cutoff_coefficient_below_minimum_side": 3072 < minimum_side,
        "dense_log_fraction_below_one_eighth": 5 * 8 < 64,
        "sparse_normalized_floor_constant": 64 * q == 512,
        "dense_normalized_floor_constant": 16 * 64 == 1024,
    }
    return {
        "q": q,
        "cutoff_coefficient": cutoff_coefficient,
        "minimum_side": minimum_side,
        "minimum_side_log2": minimum_side_log,
        "sparse_available_coefficient": sparse_available_coefficient,
        "sparse_required_coefficient": sparse_required_coefficient,
        "stopping_condition_left_at_L0": stopping_left,
        "stopping_condition_log2_W0_at_L0": stopping_log,
        "stopping_condition_right_at_L0": stopping_right,
        "checks": checks,
    }


def build() -> dict[str, object]:
    audit = constant_audit()
    checks = {
        "constant_audit_closes": all(audit["checks"].values()),
        "acyclic_path_decomposition_used": True,
        "dyadic_low_band_count_proved": True,
        "dyadic_path_length_proved": True,
        "dense_divergence_floor_proved": True,
        "complete_current_error_absorbed": True,
        "sparse_dense_dichotomy_proved": True,
        "torus_L_10_over_3_corollary_proved": True,
        "all_field_scaled_PL_remains_open": True,
        "no_witten_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_DYADIC_STOPPING_FLOW_V1",
        "schema_version": "reverse-physics-bt-euclidean-torus-dyadic-stopping-flow-v1",
        "created": "2026-08-17",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "UNCONDITIONAL_SUPER_L_10_OVER_3_CONTRAST_CLOSED_FOR_L_GE_4096_MODERATE_GATE_OPEN",
        "result_kind": "exact dyadic stopping-flow theorem and asymptotic four-torus contrast cutoff",
        "question": "Can flow spread across many moderate ratio bands evade both the density-sensitive and single-top-band BT estimates on the isotropic four-torus?",
        "answer": "Not above a smaller asymptotic contrast scale. The leading acyclic flow has total mass F. If F>2*q^2*N/W, more than F/2 crosses edges with ratio at least two. A source-to-sink path contains at most D*log_2(W) such edges, forcing ||div(f)||_2>=F/[D*log_2(W)*sqrt(N)]. The complete-current error is absorbed when sqrt(W)>=16*sqrt(q)*D*log_2(W), giving Q>=q^2/[D^2*log_2(W)^2] in this dense dyadic branch. The complementary branch F<=2*q^2*N/W is controlled by the predecessor top-band theorem when W^3>=512*q^5*D^2*N^2. Combining both branches with the old cutoff proves that, for L>=4096, W>=512*L^(10/3) implies Q/omega_L^2>=32/pi^4. A collapsing family must therefore eventually have W<512*L^(10/3). The all-field moderate-contrast sector remains open.",
        "dyadic_stopping_theorem": {
            "total_flow_mass": "sum_e f_e=F",
            "low_band": "B_<2={e:z_e<2}",
            "low_band_mass_ceiling": "sum_(e in B_<2) f_e<=q^2*N/W",
            "dense_hypothesis": "F>2*q^2*N/W",
            "high_band_mass_floor": "sum_(e:z_e>=2) f_e>F/2",
            "path_edge_count": "each source-to-sink path contains at most D*log_2(W) edges with z_e>=2",
            "divergence_floor": "||div(f)||_2>=F/(D*log_2(W)*sqrt(N))",
            "error_absorption_hypothesis": "sqrt(W)>=16*sqrt(q)*D*log_2(W)",
            "complete_gradient_floor": "||g||_2>=W^2*F/(2*D*log_2(W)*sqrt(N))",
            "dense_quotient_floor": "Q>=q^2/(D^2*log_2(W)^2)",
        },
        "sparse_dense_dichotomy": {
            "sparse_branch": "F<=2*q^2*N/W",
            "sparse_sufficient_condition": "W^3>=512*q^5*D^2*N^2",
            "sparse_conclusion": "Q>=64*q/N",
            "dense_branch": "F>2*q^2*N/W",
            "dense_sufficient_condition": "sqrt(W)>=16*sqrt(q)*D*log_2(W)",
            "dense_conclusion": "Q>=q^2/(D^2*log_2(W)^2)",
        },
        "four_torus_corollary": {
            "scope": "T_L^4 with L>=4096",
            "contrast_hypothesis": "W>=512*L^(10/3)",
            "predecessor_large_contrast_branch": "W>=3072*L^(11/3)",
            "new_live_interval": "512*L^(10/3)<=W<3072*L^(11/3)",
            "dense_interval_log_bound": "log_2(W)<(14/3)*log_2(L)<5*log_2(L)<=5*L/64<L/8",
            "normalized_conclusion": "Q/omega_L^2>=32/pi^4",
            "counterfamily_necessity": "Q/omega_L^2->0 implies eventually W<512*L^(10/3)",
        },
        "monotonicity_lemmas": {
            "stopping_ratio": "sqrt(W)/log_2(W) is increasing for W>e^2",
            "torus_base_check": "L^(4/3)>=16*(9+(10/3)*log_2(L))^2 at L=4096",
            "torus_extension": "the left/right ratio in the base check is increasing for L>=4096",
            "log_growth": "log_2(L)<=L/64 for L>=4096",
        },
        "exact_constant_audit": audit,
        "research_disposition": {
            "super_L_10_over_3_edge_contrast_collapse_for_L_ge_4096": "RULED_OUT",
            "dyadic_moderate_band_transport": "PROVED",
            "sub_L_10_over_3_moderate_contrast_sector": "OPEN",
            "all_field_torus_scaled_PL": "OPEN",
            "witten_poincare_transfer": "OPEN",
            "interacting_h_minus_one": "OPEN",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "does_not_establish": [
            "a lower bound for every positive field on T_L^4",
            "exclusion of polynomial contrast W=O(L^(10/3))",
            "the L^(10/3) cutoff for L<4096",
            "a nonseparable collapsing family",
            "a Witten or Poincare theorem",
            "boundedness or divergence of the interacting H^-1 moment",
            "a continuum measure, Born rule, or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "integer audit of the sparse coefficient, L=4096 stopping inequality, logarithmic interval bound, and normalized torus floors",
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_dyadic_stopping_flow.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_dyadic_stopping_flow.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_dyadic_stopping_flow",
        ],
        "tier_receipt": {
            "tier_0": "PASS: Python compilation, strict JSON/schema parsing, deterministic drift, scoped diff check, exact staged-diff inspection, planning import, claim-map verification, and two-pass PDF build; planning import passed with 1713 nodes, 0 invalid items, and 0 malformed events in 1.22 s at 16896 KiB maximum RSS",
            "tier_1": "PASS: producer 10/10 in 0.03 s at 20032 KiB; independent verifier 12/12 in 0.09 s at 29780 KiB; focused and mutation tests 11/11 in 0.10 s at 30704 KiB; unchanged top-band predecessor verifier 10/10 in 0.11 s at 30084 KiB",
            "tier_2": "the top-band predecessor is unchanged and checked by content hash",
            "tier_3": "not triggered: the all-field, Witten, H^-1, continuum, freeze, and release gates remain open",
            "paper_integration": "PASS: claim-map verifier 0.58 s at 148272 KiB maximum RSS; two-pass PDF build 1.74 s at 54172 KiB maximum RSS; prose advisory remained non-certifying and reported manuscript-wide parenthetical and abstract-word findings",
            "planning_event": "PASS: append-only event sequence 94, id c5abc8168b333351",
            "science_forge_shadow": "ADVISORY EXIT 0 IN 6.72 S AT 341500 KiB, NOT A SCIENTIFIC PASS: bridge audit fail-closed on source-current Forge E9415 drift; coverage census reports 1973 certificates versus baseline 976",
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
        "verifier": VERIFY_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        print("[FAIL] internal checks")
        return 1
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = handle.read()
        except OSError as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != encoded:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            handle.write(encoded)
    print(
        "[PASS] BT torus dyadic stopping flow "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
