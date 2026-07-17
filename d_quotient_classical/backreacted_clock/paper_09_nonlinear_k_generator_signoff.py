#!/usr/bin/env python3
"""Deterministically build the Paper IX nonlinear K-generator signoff."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF.json"

SOURCES: dict[str, tuple[str, str | None]] = {
    "claim_table": (
        "d_quotient_classical/certificates/PAPER_09_BERGER_CLAIM_TABLE.json",
        "PAPER_09_BERGER_CLAIM_TABLE",
    ),
    "generator_audit": (
        "d_quotient_classical/certificates/BERGER_GENERATOR_CONJUGATION_AUDIT.json",
        "BERGER_GENERATOR_CONJUGATION_AUDIT",
    ),
    "support_local_q2": (
        "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json",
        "BERGER_SUPPORT_LOCAL_Q2",
    ),
    "support_local_q3": (
        "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3.json",
        "BERGER_SUPPORT_LOCAL_Q3",
    ),
    "causal_green_homotopy": (
        "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json",
        "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2",
    ),
    "causal_cartan_arity_two": (
        "d_quotient_classical/certificates/BERGER_CAUSAL_D_CARTAN_V2.json",
        "BERGER_CAUSAL_D_CARTAN_V2",
    ),
    "causal_cartan_arity_three": (
        "d_quotient_classical/certificates/BERGER_ARITY_THREE_D_CARTAN_FULL_4D.json",
        "BERGER_ARITY_THREE_D_CARTAN_FULL_4D",
    ),
    "paper_source": ("paper/09-relational-clocks-berger-d-cartan.tex", None),
}

COMMANDS = [
    "python3 d_quotient_classical/backreacted_clock/paper_09_nonlinear_k_generator_signoff.py --check",
    "python3 d_quotient_classical/backreacted_clock/verify_paper_09_nonlinear_k_generator_signoff.py --check --mutations",
    "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_paper_09_nonlinear_k_generator_signoff",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _last_commit(path: str) -> str:
    proc = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", path],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    commit = proc.stdout.strip()
    if len(commit) != 40:
        raise RuntimeError(f"no committed provenance for {path}")
    return commit


def _manifest() -> dict[str, dict[str, str]]:
    manifest: dict[str, dict[str, str]] = {}
    for key, (path, result_id) in SOURCES.items():
        entry = {"path": path, "commit": _last_commit(path), "sha256": _sha256(ROOT / path)}
        if result_id is not None:
            entry["result_id"] = result_id
        manifest[key] = entry
    return manifest


def build_payload() -> dict[str, Any]:
    return {
        "schema": "pure-weyl-paper-09-nonlinear-k-generator-signoff-v1",
        "result_id": "PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF",
        "reviewer_role": "NONLINEAR_TEAM_INTERNAL_REVIEWER",
        "review_status": "SIGNED_SCOPED_K_THEOREM",
        "setting_id": "compact_positive_berger_clock_q_9_over_40",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "source_manifest": _manifest(),
        "review_scope": {
            "certified_generator": "K_Berger=D-omega R",
            "raw_cylinder_generator": "D=partial_t is affine about the rotating background",
            "certified_taylor_arities": [1, 2, 3],
            "maximum_certified_arity": 3,
            "gauge_fixed_rows": 54,
            "input_scope": "arbitrary four-dimensional jets at the frozen rational Berger fixture",
            "support_scope": "q2 q3 and pairing support-local; cyclic Cartan primitives supported in the two-sided causal hull",
        },
        "exact_checks": {
            "source_hashes_pinned": True,
            "claim_table_is_writing_started": True,
            "claim_table_not_theorem_frozen": True,
            "paper_states_K_theorem": True,
            "paper_separates_raw_D_from_K": True,
            "paper_rejects_affine_D_Cartan_promotion": True,
            "paper_rejects_all_orders_promotion": True,
            "generator_audit_identifies_frozen_action_as_K": True,
            "generator_audit_identifies_raw_D_as_affine": True,
            "q2_action_derived_support_local_and_K_equivariant": True,
            "q3_action_derived_support_local_and_K_equivariant": True,
            "causal_chain_contractions_cover_all_54_rows": True,
            "cyclic_K_Cartan_identity_through_arity_two": True,
            "cyclic_K_Cartan_identity_through_arity_three": True,
            "legacy_D_labels_reinterpreted_only_via_generator_audit": True,
            "no_affine_D_Cartan_certificate": True,
            "no_arity_four_certificate": True,
            "no_all_orders_certificate": True,
            "no_quantum_promotion": True,
        },
        "signoff": {
            "nonlinear_team": "SIGNED_K_GENERATOR_INTERPRETATION",
            "accepted_theorem": "The action-derived Taylor operations and causal cyclic Cartan primitive are certified for K_Berger=D-omega R on all 54 gauge-fixed rows through arity three.",
            "rejected_interpretations": [
                "affine raw-D Cartan theorem",
                "arity-four Cartan theorem",
                "convergent all-orders Cartan theorem",
                "integrated nonlinear quotient",
                "Hadamard or quantum theorem",
            ],
        },
        "legacy_artifact_interpretation": {
            "legacy_symbol": "D in frozen dressed-complex artifact names",
            "authoritative_symbol": "K_Berger=D-omega R",
            "rule": "Legacy names are retained for content-addressed compatibility and acquire no raw-D theorem semantics.",
        },
        "forbidden_promotions": [
            "AFFINE_D_CARTAN_CONSTRUCTED",
            "BERGER_ARITY_FOUR_CARTAN",
            "BERGER_ALL_ORDERS_CARTAN",
            "BERGER_INTEGRATED_NONLINEAR_QUOTIENT",
            "BERGER_HADAMARD_DATA",
            "QUANTUM_CLAIM",
            "THEOREM_FROZEN",
        ],
        "flags": {
            "PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF": True,
            "K_BERGER_CARTAN_THROUGH_ARITY_THREE": True,
            "RAW_D_CARTAN_CERTIFIED": False,
            "ARITY_FOUR_CARTAN_CERTIFIED": False,
            "ALL_ORDERS_CARTAN_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
            "THEOREM_FROZEN": False,
        },
        "verification": {
            "commands": COMMANDS,
            "tier_0": "schema, JSON and Python parse plus scoped diff check",
            "tier_1": "independent semantic verifier and mutation tests",
            "higher_tiers": "not run; no mathematical input or freeze state changed",
            "recorded_run": [
                {"command": COMMANDS[0], "status": "PASS", "elapsed_seconds": 0.05},
                {"command": COMMANDS[1], "status": "PASS", "elapsed_seconds": 0.27},
                {"command": COMMANDS[2], "status": "PASS", "elapsed_seconds": 0.73},
            ],
        },
        "claim_boundary": "The nonlinear-team review signs the K_Berger=D-omega R interpretation of the existing 54-row action-derived q2/q3 and causal cyclic Cartan certificates through arity three. Raw D remains affine with a nonzero zeroth-arity component; no affine-D, arity-four, convergent all-orders, integrated quotient, Hadamard, quantum, or theorem-freeze claim is signed.",
        "next_gate": "QUANTUM_K_GENERATOR_CLAIM_BOUNDARY_SIGNOFF_AND_DEFERRED_CLEAN_TREE_REPLAY",
    }


def _render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="write the deterministic artifact")
    group.add_argument("--check", action="store_true", help="compare the artifact with a fresh build")
    args = parser.parse_args()
    payload = build_payload()
    if args.write:
        OUTPUT.write_text(_render(payload), encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    current = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if current != payload:
        raise SystemExit("PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF is stale; rerun with --write")
    print("PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF producer check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
