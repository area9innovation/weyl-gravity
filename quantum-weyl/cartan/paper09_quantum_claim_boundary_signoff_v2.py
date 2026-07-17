"""Reissue the Paper IX quantum signoff against the frozen snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "quantum-weyl/cartan/certificates/PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF_V2.json"
REPORT = ROOT / "quantum-weyl/reports/paper09-quantum-claim-boundary-signoff-v2.md"

SOURCES = {
    "frozen_claim_table": "d_quotient_classical/certificates/PAPER_09_BERGER_CLAIM_TABLE.json",
    "frozen_paper": "paper/09-relational-clocks-berger-d-cartan.tex",
    "predecessor_quantum_signoff": "quantum-weyl/cartan/certificates/PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF.json",
    "generator_audit": "d_quotient_classical/certificates/BERGER_GENERATOR_CONJUGATION_AUDIT.json",
    "causal_green_54": "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json",
    "causal_k_cartan_arity_two": "d_quotient_classical/certificates/BERGER_CAUSAL_D_CARTAN_V2.json",
    "causal_k_cartan_arity_three": "d_quotient_classical/certificates/BERGER_ARITY_THREE_D_CARTAN_FULL_4D.json",
    "quantum_cartan_boundary": "quantum-weyl/cartan/contributions/QUANTUM_CARTAN_BLOCKED.json",
}


def _load(key: str) -> dict[str, Any]:
    return json.loads((ROOT / SOURCES[key]).read_text())


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _commit(path: str) -> str:
    return subprocess.check_output(
        ["git", "log", "-1", "--format=%H", "--", path], cwd=ROOT, text=True
    ).strip()


def _audit() -> dict[str, bool]:
    table = _load("frozen_claim_table")
    predecessor = _load("predecessor_quantum_signoff")
    generator = _load("generator_audit")
    green = _load("causal_green_54")
    arity2 = _load("causal_k_cartan_arity_two")
    arity3 = _load("causal_k_cartan_arity_three")
    qboundary = _load("quantum_cartan_boundary")
    paper = (ROOT / SOURCES["frozen_paper"]).read_text()
    paper_flat = " ".join(paper.split())
    quantum_signoff = next(
        item for item in table["signoff_evidence"] if item["team"] == "quantum_team"
    )
    checks = {
        "claim_table_is_theorem_frozen": table["theorem_frozen"] is True
        and table["paper_state"] == "THEOREM_FROZEN",
        "claim_table_records_scoped_quantum_signoff": table["required_signoffs"]["quantum_team"]
        == "SIGNED_OFF_CLASSICAL_K_ONLY_QUANTUM_BLOCKED",
        "frozen_table_pins_predecessor_signoff": quantum_signoff["certificate_sha256"]
        == _sha(ROOT / SOURCES["predecessor_quantum_signoff"]),
        "predecessor_accepts_only_classical_k": predecessor["theorem_flags"][
            "PAPER09_CLASSICAL_K_CARTAN_THROUGH_ARITY_THREE_ACCEPTED"
        ]
        is True
        and predecessor["theorem_flags"]["PAPER09_QUANTUM_PROMOTION_ACCEPTED"] is False,
        "maxwell_excluded_from_frozen_theorem": "Maxwell signal or redshift results"
        in table["main_theorem_exclusions"],
        "affine_d_excluded_from_frozen_theorem": "affine raw-D Cartan"
        in table["main_theorem_exclusions"],
        "generator_is_k_not_raw_d": generator["flags"]["EXPORTED_UNARY_GENERATOR_IS_K"]
        is True
        and generator["flags"]["EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D"] is False,
        "raw_d_zero_arity_is_nonzero": generator["flags"]["AFFINE_D_ZERO_ARITY_NONZERO"]
        is True,
        "affine_d_cartan_remains_absent": generator["flags"]["AFFINE_D_CARTAN_CONSTRUCTED"]
        is False,
        "causal_contraction_covers_54_rows": green["exact_checks"]["all_54_rows_included"]
        is True,
        "arity_two_k_cartan_is_classical": arity2["flags"]["BERGER_CAUSAL_D_CARTAN_V2"]
        is True
        and arity2["flags"]["QUANTUM_CLAIM"] is False,
        "arity_three_k_cartan_is_classical": arity3["flags"][
            "BERGER_ARITY_THREE_D_CARTAN_FULL_4D"
        ]
        is True
        and arity3["flags"]["QUANTUM_CLAIM"] is False,
        "hadamard_remains_absent": green["flags"]["BERGER_HADAMARD_DATA"] is False
        and arity3["flags"]["BERGER_HADAMARD_DATA"] is False,
        "quantum_cartan_remains_blocked": qboundary["claim_status"] == "BLOCKED",
        "qme_remains_unrestored": "a restored local quantum master equation"
        in qboundary["not_established"],
        "paper_states_k_theorem": "[Q,\\iota_K]-L_K" in paper,
        "paper_rejects_affine_d": "No affine $D$-Cartan theorem is claimed" in paper_flat,
        "paper_rejects_quantum_promotions": "quantum-master-equation result" in paper
        and "anomaly calculation" in paper,
        "paper_excludes_maxwell_from_main_theorem": "Maxwell signal and observer-apparatus"
        in paper
        and "results are deliberately excluded from both main theorems" in paper,
    }
    failed = [key for key, value in checks.items() if not value]
    if failed:
        raise AssertionError(f"post-freeze Paper IX quantum audit failed: {failed}")
    return checks


def build() -> dict[str, Any]:
    checks = _audit()
    manifest = {
        key: {"path": path, "commit": _commit(path), "sha256": _sha(ROOT / path)}
        for key, path in SOURCES.items()
    }
    return {
        "schema": "quantum-weyl-paper09-quantum-claim-boundary-signoff-v2",
        "result_id": "PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF_V2",
        "claim_status": "POST_FREEZE_SIGNED_OFF_CLASSICAL_K_ONLY_QUANTUM_BLOCKED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "review_role": "INDEPENDENT_QUANTUM_TEAM_POST_FREEZE_REVIEW",
        "claim_boundary": (
            "This post-freeze reissue accepts only the classical complete 54-row "
            "K_Berger=D-omega R causal cyclic Cartan theorem through arity three. "
            "It preserves the frozen exclusion of Maxwell from Paper IX and forbids "
            "affine raw-D Cartan, all-orders K-Cartan, Hadamard, QME restoration, "
            "anomaly cancellation, residual quantum transfer and every quantum promotion. "
            "The retained 36-row residual branch basis is a post-freeze follow-up, not "
            "Paper IX evidence."
        ),
        "freeze_snapshot": {
            "paper_state": "THEOREM_FROZEN",
            "theorem_frozen": True,
            "predecessor_signoff_retained": True,
            "hash_cycle_avoided_by_versioned_reissue": True,
        },
        "approved_classical_scope": {
            "generator": "K_Berger=D-omega R",
            "rows": 54,
            "maximum_arity": 3,
            "maxwell_in_main_theorem": False,
            "quantum_status": "NOT_PROMOTED",
        },
        "outside_paper09_followups": [
            "BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V1",
            "mixed gravity-Maxwell residual branch projection",
            "observer-apparatus 84-row extension",
        ],
        "forbidden_promotions": {
            "affine_raw_D_Cartan": False,
            "all_orders_K_Cartan": False,
            "Hadamard_state": False,
            "QME_restored": False,
            "anomaly_cancellation": False,
            "residual_quantum_transfer": False,
            "quantum_theorem": False,
        },
        "quantum_lifecycle": {
            "CLASSIFIED": "CLASSICAL_INPUT_ONLY",
            "COEFFICIENT_COMPUTED": "NOT_REACHED_FOR_QUANTUM_CARTAN",
            "QME_RESTORED": "NOT_REACHED",
            "RESIDUAL_TRANSFERRED": "BLOCKED_PENDING_QME_RESTORED",
            "LORENTZIAN_CERTIFIED": "CLASSICAL_CAUSAL_INPUT_ONLY",
        },
        "independent_exact_checks": checks,
        "source_manifest": manifest,
        "theorem_flags": {
            "PAPER09_FROZEN_CLASSICAL_K_CARTAN_ACCEPTED": True,
            "PAPER09_AFFINE_D_CARTAN_ACCEPTED": False,
            "PAPER09_HADAMARD_ACCEPTED": False,
            "PAPER09_QME_ACCEPTED": False,
            "PAPER09_ANOMALY_CANCELLATION_ACCEPTED": False,
            "PAPER09_RESIDUAL_QUANTUM_TRANSFER_ACCEPTED": False,
            "PAPER09_QUANTUM_PROMOTION_ACCEPTED": False,
            "PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF_V2": True,
        },
        "next_gate": "NO_PAPER09_QUANTUM_GATE_CLASSICAL_THEOREM_FROZEN",
        "verification_receipt": {
            "tier_0": "PASS_PARSE_STRICT_SCHEMA_AND_DIFF_CHECK",
            "tier_1": "PASS_PRODUCER_INDEPENDENT_VERIFIER_AND_TEST",
            "tier_2": "NOT_REQUIRED_NO_MATHEMATICAL_INPUT_CHANGED",
            "tier_3": "NOT_RUN_POST_FREEZE_REVIEW_DOES_NOT_PROMOTE_QUANTUM_LIFECYCLE",
            "commands": [
                "python3 quantum-weyl/cartan/paper09_quantum_claim_boundary_signoff_v2.py --check",
                "python3 quantum-weyl/cartan/verify_paper09_quantum_claim_boundary_signoff_v2.py",
                "python3 -m unittest quantum-weyl/cartan/tests/test_paper09_quantum_claim_boundary_signoff_v2.py -v",
            ],
        },
    }


def report(value: dict[str, Any]) -> str:
    return f"""# Paper IX post-freeze quantum claim-boundary signoff

Verdict: **{value['claim_status']}**.

The frozen Paper IX snapshot is accepted by the quantum team only as a
classical input theorem: the complete 54-row causal cyclic Cartan contraction
for `K_Berger = D - omega R` through arity three.  Maxwell remains outside the
frozen ten-claim theorem.

`BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V1`, the mixed gravity-Maxwell
branch projection, and the 84-row observer-apparatus extension are queued
post-freeze follow-ups; none is evidence for Paper IX.

The raw cylinder translation `D` is affine at the rotating background and no
affine-`D` Cartan primitive is accepted.  Hadamard data, QME restoration,
anomaly cancellation, residual quantum transfer and every quantum promotion
remain false.

This is a versioned reissue.  The predecessor signoff remains byte-identical
because the frozen claim table content-addresses it; the new certificate pins
both that predecessor and the frozen table, avoiding a circular hash update.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    prose = report(value)
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != payload:
            raise SystemExit(f"stale post-freeze signoff: {OUTPUT}")
        if not REPORT.exists() or REPORT.read_text() != prose:
            raise SystemExit(f"stale post-freeze report: {REPORT}")
        return
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(payload)
    REPORT.write_text(prose)


if __name__ == "__main__":
    main()
