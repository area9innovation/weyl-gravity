#!/usr/bin/env python3
"""Independent fail-closed audit of the Phase-1 closure join."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-07-22"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ledger = json.loads((ROOT / f"reports/phase1-closure-claims-ledger-{STAMP}.json").read_text())
    snapshot = json.loads((ROOT / f"reports/phase1-closure-dependency-snapshot-{STAMP}.json").read_text())
    audit = json.loads((ROOT / f"planning/paper-coverage/phase1-closure-paper-audit-{STAMP}.json").read_text())
    atlas = json.loads((ROOT / "residual_atlas/programme-phase1-classification-ending-fragment-v1.json").read_text())
    receipt = json.loads((ROOT / "reports/PHASE1_CLOSURE_V1_TIER_RECEIPT.json").read_text())

    assert ledger["result_state"] == "PHASE1_CLOSED_CLASSIFICATION_ENDING_NO_PHASE2_CANDIDATE"
    decision = ledger["decision"]
    assert decision["status"] == "CLOSED" and decision["ending"] == "CLASSIFICATION_ENDING"
    assert decision["selected_counterflow_causal_parent"] is True
    assert decision["selected_counterflow_physically_healthy"] is False
    assert decision["fixed_Q_rel_retains_clock"] is False
    assert decision["robust_phase2_candidate_selected"] is False
    assert decision["invariant_interaction_class_decided"] is False
    assert decision["operational_frequency_ratio_activated"] is False
    assert decision["quantum_phase2_candidate_selected"] is False

    required_type_fields = {"theory", "action", "background", "carrier", "charge_fibre", "correction_class", "lifecycle"}
    assert len(ledger["claims"]) == 10
    assert len({row["claim_id"] for row in ledger["claims"]}) == 10
    assert all(required_type_fields <= row.keys() for row in ledger["claims"])
    assert all(row["source"] in snapshot["dependencies"] for row in ledger["claims"])

    for role, ref in snapshot["dependencies"].items():
        path = ROOT / ref["path"]
        assert path.is_file(), (role, "missing")
        assert digest(path) == ref["sha256"], (role, "hash drift")
        doc = json.loads(path.read_text())
        assert (doc.get("result_id") or doc.get("paper_id")) == ref["result_id"]
        if ref["result_state"] is not None:
            assert doc.get("result_state") == ref["result_state"]
        assert ref["effective_work_state"] == "DONE"

    counts = audit["counts"]
    assert counts["papers_audited"] == 12
    assert counts["human_classified_results"] == 8
    assert counts["typed_reverse_paper_claims"] == 11
    assert counts["uncovered_material"] == 0
    assert counts["claim_no_evidence"] == 0
    assert counts["review_queue"] == 1400
    assert counts["scoped_followup_papers"] == 3
    for row in audit["papers"]:
        path = ROOT / row["path"]
        assert digest(path) == row["sha256"]
        if "FOLLOWUP" in row["audit_status"] or "REPAIR" in row["audit_status"]:
            assert row["scoped_followup_work_items"]
            for work_id in row["scoped_followup_work_items"]:
                slug = work_id.rsplit("/", 1)[-1]
                assert (ROOT / f"planning/work-items/{slug}.json").is_file()

    assert atlas["entries"][0]["id"] == "programme.phase1.classification_ending.no_candidate_selected"
    assert atlas["entries"][0]["descriptions"]["causal"] == "CERTIFIED"
    assert atlas["entries"][0]["descriptions"]["symplectic"] == "OBSTRUCTED"
    for path_text, record in receipt["outputs"].items():
        assert digest(ROOT / path_text) == record["sha256"], (path_text, "closure-output hash drift")
    assert receipt["tiers"]["tier_3"].startswith("NOT_RUN")
    print("PASS: independent Phase-1 dependency, typing, paper, and boundary audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
