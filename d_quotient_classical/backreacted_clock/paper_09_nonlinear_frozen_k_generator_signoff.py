#!/usr/bin/env python3
"""Build the nonlinear re-signoff for the frozen Paper IX snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/PAPER_09_NONLINEAR_FROZEN_K_GENERATOR_SIGNOFF.json"
SOURCES = {
    "frozen_claim_table": ("d_quotient_classical/certificates/PAPER_09_BERGER_CLAIM_TABLE.json", "PAPER_09_BERGER_CLAIM_TABLE"),
    "prefreeze_nonlinear_signoff": ("d_quotient_classical/certificates/PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF.json", "PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF"),
    "generator_audit": ("d_quotient_classical/certificates/BERGER_GENERATOR_CONJUGATION_AUDIT.json", "BERGER_GENERATOR_CONJUGATION_AUDIT"),
    "paper_source": ("paper/09-relational-clocks-berger-d-cartan.tex", None),
    "paper_supplement": ("paper/09-relational-clocks-berger-d-cartan-computational-supplement.tex", None),
}
COMMANDS = [
    "python3 d_quotient_classical/backreacted_clock/paper_09_nonlinear_frozen_k_generator_signoff.py --check",
    "python3 d_quotient_classical/backreacted_clock/verify_paper_09_nonlinear_frozen_k_generator_signoff.py --check --mutations",
    "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_paper_09_nonlinear_frozen_k_generator_signoff",
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _commit(path: str) -> str:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", path],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()
    if len(result) != 40:
        raise RuntimeError(f"missing committed source: {path}")
    return result


def build_payload() -> dict[str, Any]:
    manifest: dict[str, dict[str, str]] = {}
    for key, (path, result_id) in SOURCES.items():
        entry = {"path": path, "commit": _commit(path), "sha256": _sha(ROOT / path)}
        if result_id:
            entry["result_id"] = result_id
        manifest[key] = entry
    return {
        "schema": "pure-weyl-paper-09-nonlinear-frozen-k-generator-signoff-v1",
        "result_id": "PAPER_09_NONLINEAR_FROZEN_K_GENERATOR_SIGNOFF",
        "reviewer_role": "NONLINEAR_TEAM_INTERNAL_REVIEWER",
        "review_status": "REISSUED_AND_SIGNED_FROZEN_SCOPED_K_THEOREM",
        "setting_id": "compact_positive_berger_clock_q_9_over_40",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "source_manifest": manifest,
        "approved_scope": {
            "generator": "K_Berger=D-omega R",
            "maximum_arity": 3,
            "rows": 54,
            "paper_lifecycle": "THEOREM_FROZEN",
            "theorem": "gravity-clock q2 q3 causal cyclic K-Cartan through arity three",
        },
        "excluded_scope": [
            "affine raw-D Cartan",
            "arity-four or convergent all-orders Cartan",
            "Maxwell signal redshift or coupled 64-row theorem",
            "observer-apparatus or 84-row theorem",
            "Hadamard QME anomaly or quantum theorem",
        ],
        "exact_checks": {
            "frozen_claim_table_hash_pinned": True,
            "paper_source_hash_pinned": True,
            "paper_supplement_hash_pinned": True,
            "prefreeze_nonlinear_signoff_hash_pinned": True,
            "paper_state_theorem_frozen": True,
            "all_required_signoffs_present": True,
            "ten_claim_ledger_unchanged": True,
            "claims_C6_through_C10_are_K_scoped": True,
            "raw_D_remains_affine": True,
            "arity_four_and_all_orders_remain_open": True,
            "Maxwell_excluded_from_main_theorem": True,
            "observer_84_row_excluded_from_main_theorem": True,
            "Hadamard_and_quantum_remain_false": True,
        },
        "flags": {
            "PAPER_09_NONLINEAR_FROZEN_K_GENERATOR_SIGNOFF": True,
            "PAPER_09_THEOREM_FROZEN_ACCEPTED": True,
            "K_BERGER_CARTAN_THROUGH_ARITY_THREE": True,
            "RAW_D_CARTAN_CERTIFIED": False,
            "ARITY_FOUR_CARTAN_CERTIFIED": False,
            "ALL_ORDERS_CARTAN_CERTIFIED": False,
            "MAXWELL_MAIN_THEOREM_INCLUDED": False,
            "OBSERVER_84_ROW_MAIN_THEOREM_INCLUDED": False,
            "HADAMARD_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "verification": {
            "commands": COMMANDS,
            "tier_0": "strict JSON schema and Python parse plus scoped diff check",
            "tier_1": "deterministic producer, independent semantic verifier, mutation rail and unit tests",
            "higher_tiers": "not rerun; this reissue audits the committed frozen lifecycle snapshot without changing mathematical inputs",
        },
        "claim_boundary": "The nonlinear team re-signs the theorem-frozen Paper IX snapshot only for the 54-row gravity-clock K_Berger=D-omega R causal cyclic Cartan result through arity three. Raw affine D, arity four and all orders, Maxwell and observer extensions, Hadamard, QME, anomaly and quantum claims remain excluded.",
        "next_gate": "POST_FREEZE_OBSERVER_AND_MAXWELL_RESULTS_REMAIN_SEPARATE",
    }


def render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    if args.write:
        OUTPUT.write_text(render(payload), encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    if json.loads(OUTPUT.read_text(encoding="utf-8")) != payload:
        raise SystemExit("frozen nonlinear signoff is stale")
    print("PAPER_09_NONLINEAR_FROZEN_K_GENERATOR_SIGNOFF producer check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
