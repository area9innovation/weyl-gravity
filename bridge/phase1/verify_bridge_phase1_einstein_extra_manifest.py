#!/usr/bin/env python3
"""Independent hash, branch, charge and correction-class audit."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / "bridge/phase1/BRIDGE_PHASE1_EINSTEIN_EXTRA_CONTRIBUTION_V1.json"


def verify(path: Path) -> None:
    d = json.loads(path.read_text())
    assert d["result_state"] == "PHASE1_EINSTEIN_EXTRA_STRUCTURAL_CONTRIBUTION_FROZEN"
    for ref in d["imports"].values():
        p = ROOT / ref["path"]
        assert hashlib.sha256(p.read_bytes()).hexdigest() == ref["sha256"]
        src = json.loads(p.read_text())
        assert src["result_id"] == ref["result_id"]
        assert src["lifecycle_state"] == ref["lifecycle_state"]
        assert src.get("result_state", "NOT_APPLICABLE_RECEIPT_OR_THEOREM_FREEZE") == ref["result_state"]
    rows = d["rows"]
    assert [r["sequence"] for r in rows] == list(range(8))
    ids = {r["row_id"] for r in rows}; assert len(ids) == 8
    traces = {r["branch_id"]: r for r in d["branch_traces"]}
    assert set(traces) == {"einstein_image_axial", "extra_axial", "einstein_image_polar", "extra_polar"}
    assert traces["extra_axial"]["pairing"] == "CERTIFIED_NONRADICAL_INERTIA_2_0"
    assert traces["extra_polar"]["third_order"] == "NO_CERTIFIED_MAP"
    mixed = next(r for r in rows if r["row_id"] == "mixed_charge_derived_correspondence")
    assert "anti-diagonal" in mixed["scope"]["charge_fibre"]
    third = next(r for r in rows if r["row_id"] == "balanced_axial_third_order")
    assert third["representative_dependence"] == "GLOBAL_K3_CORRECTION_INDEPENDENT_SHELL_VERDICT_REPRESENTATIVE_SCOPED"
    assert "NO_CERTIFIED_MAP" in third["correction_class"]
    assert "SMOOTH_SECULAR_CERTIFIED" in third["disposition"]
    assert "BOUNDED_REPRESENTATIVE_OBSTRUCTED" in third["disposition"]
    assert all(v.startswith("REJECTED_") for v in d["adversarial_mutations"].values())
    assert d["terminal_summary"]["einstein_inclusion_symplectic_equivalence"] is False
    assert d["terminal_summary"]["separate_neutral_branch_projection"] is False


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--manifest", type=Path, default=MAP); args = ap.parse_args()
    verify(args.manifest)
    print("PASS: independent Bridge Phase-1 hashes, branches, charge fibres and correction classes")
    return 0


if __name__ == "__main__": raise SystemExit(main())
