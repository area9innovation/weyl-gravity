#!/usr/bin/env python3
"""Independent structural and boundary checker for completion Atlas V23."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V23.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V22.json"
Q3_WITNESS = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_PURE_WEYL_Q3_WITNESS_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_q2_green_composition_preflight",
        "strict_recursive_causal_tree_domains", "strict_polarized_formal_coefficients",
        "strict_field_equation_green_quotient_inverse",
        "strict_quadratic_truncation_lambda2_source_obstruction",
        "strict_pure_weyl_q3_witness", "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def cell_map(value: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {(branch["id"], stage["stage"]): stage for branch in value["branches"] for stage in branch["stages"]}


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    previous = json.loads(PREDECESSOR.read_text())
    witness = json.loads(Q3_WITNESS.read_text())
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V23" or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v23":
        return ["result identity/version drift"]
    predecessor = value.get("predecessor", {})
    if predecessor.get("sha256") != sha(PREDECESSOR) or predecessor.get("preserved") is not True:
        errors.append("V22 predecessor binding drift")
    before, after = cell_map(previous), cell_map(value)
    if set(before) != set(after) or len(after) != 77:
        errors.append("77-cell preservation drift")
    changed = {key for key in before.keys() & after.keys() if before[key] != after[key]}
    changed.update(before.keys() ^ after.keys())
    if changed != {("STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")}:
        errors.append("unexpected cell mutation")

    p = value.get("strict_pure_weyl_q3_witness", {})
    expected = {
        "fixture_id": "FLAT_PURE_DIFF_GAUGE_SEED_1",
        "metric_q3_term_count": 41,
        "metric_q3_nonzero_rows": 10,
        "q2_jacobiator_weyl_identity_value": "75760/27",
        "computed_q1_q3_weyl_identity_value": "-75760/9",
        "arity_three_witness_defect": "0",
        "lambda2_witness_source_q1_defect": "0",
        "lambda2_witness_source_closed": True,
        "general_full_weyl_lambda2_source_closed": False,
        "receiver_derived_metric_sector": True,
        "authoritative_arbitrary_input_q3_imported": False,
        "Berger_q3_direct_import_compatible": False,
        "Berger_disposition": "NO_CERTIFIED_SAME_THEORY_CARRIER_MAP",
        "authoritative_export_contract_id": "STRICT_PURE_WEYL_AUTHORITATIVE_Q3_EXPORT_V2",
    }
    for key, wanted in expected.items():
        if p.get(key) != wanted:
            errors.append("q3 witness projection drift: " + key)
    if p.get("result_id") != witness.get("result_id"):
        errors.append("q3 witness result projection drift")

    nonlinear = after.get(("STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN"), {})
    if nonlinear.get("status") != "PARTIAL_CERTIFIED_WITH_EXACT_Q3_WITNESS_CANCELLATION" or witness["result_id"] not in nonlinear.get("evidence", []):
        errors.append("strict nonlinear stage disposition drift")
    if "-75760/9" not in nonlinear.get("statement", "") or "Arbitrary-input" not in nonlinear.get("statement", ""):
        errors.append("witness/general narrative firewall drift")

    routes = value.get("route_selection", [])
    names = [item.get("route") for item in routes]
    expected_front = [
        "STRICT_AUTHORITATIVE_ARBITRARY_FULL_BV_Q2_Q3_EXPORT",
        "STRICT_ARITY_THREE_386_CYCLIC_STABILIZATION",
        "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
    ]
    if len(routes) != 11 or [item.get("rank") for item in routes] != list(range(1, 12)):
        errors.append("route rank/count drift")
    if names[:3] != expected_front:
        errors.append("q3 frontier ordering drift")
    if [item.get("object") for item in value.get("research_queue", [])] != names:
        errors.append("research queue projection drift")

    flags = value.get("claim_flags", {})
    true_flags = (
        "v22_preserved", "strict_pure_weyl_metric_q3_witness_derived",
        "strict_pure_weyl_q3_witness_cancellation_certified",
        "strict_386_lambda2_witness_full_source_closed",
    )
    false_flags = (
        "strict_386_Berger_q3_direct_import_compatible",
        "strict_386_authoritative_q3_imported", "strict_386_arbitrary_input_q3_certified",
        "strict_386_full_bv_arity_three_identity_certified",
        "strict_386_general_full_weyl_lambda2_source_closure_certified",
        "strict_386_authoritative_formal_moller_map_certified",
        "strict_pure_weyl_classical_gate_passed",
        "strict_386_full_bv_hadamard_state_constructed",
        "strict_pure_weyl_qme_restored", "lorentzian_full_theory_certified",
    )
    if any(flags.get(key) is not True for key in true_flags):
        errors.append("positive V23 flag drift")
    if any(flags.get(key) is not False for key in false_flags):
        errors.append("V23 lifecycle/authority firewall drift")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical atlas digest drift")
    if not any(item.get("path") == str(Q3_WITNESS.relative_to(ROOT)) and item.get("sha256") == sha(Q3_WITNESS) for item in value.get("provenance", {}).get("inputs", [])):
        errors.append("q3 witness provenance binding drift")
    return errors


def main() -> int:
    errors = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V23: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
