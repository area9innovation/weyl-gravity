#!/usr/bin/env python3
"""Independent source, edge, scope and mutation audit."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / "d_quotient_classical/phase1/CLASSICAL_PHASE1_COUNTERFLOW_CLAIM_MAP_V1.json"


def main() -> int:
    d = json.loads(MAP.read_text())
    assert d["result_state"] == "PHASE1_CLASSICAL_COUNTERFLOW_CHAIN_FROZEN_TERMINAL_OBSTRUCTED"
    for ref in d["imports"].values():
        p = ROOT / ref["path"]
        assert hashlib.sha256(p.read_bytes()).hexdigest() == ref["sha256"]
        source = json.loads(p.read_text())
        assert source["result_id"] == ref["result_id"] and source["result_state"] == ref["result_state"]
    rows = d["rows"]; ids = [r["row_id"] for r in rows]
    assert [r["sequence"] for r in rows] == list(range(6)) and len(set(ids)) == 6
    assert [(e["from"], e["to"]) for e in d["edges"]] == list(zip(ids, ids[1:]))
    by_id = {r["row_id"]: r for r in rows}
    assert "SELECTED_FIXTURE" in by_id["two_phase_selected_causal_parent"]["causal_scope"]
    assert "NOT_ESTABLISHED" in by_id["two_phase_selected_causal_parent"]["physical_quotient"]
    assert "FAMILYWIDE_GREEN_NO_CERTIFIED_MAP" in by_id["same_field_retuning_family"]["causal_scope"]
    assert "J_HALF" in by_id["phase1_terminal_disposition"]["spectral_scope"]
    assert all(v.startswith("REJECTED_") for v in d["adversarial_mutations"].values())
    assert d["terminal_summary"] == {
        "familywide_same_field_stable_candidate": False,
        "fixed_Q_rel_retains_physical_clock": False,
        "phase2_candidate_selected": False,
        "selected_fixture_causal_parent": True,
        "selected_fixture_dressed_trace_removed": True,
        "selected_fixture_physically_healthy": False,
    }
    print("PASS: independent Classical Phase-1 hash, edge, scope and mutation audit")
    return 0


if __name__ == "__main__": raise SystemExit(main())
