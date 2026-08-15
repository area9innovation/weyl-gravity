#!/usr/bin/env python3
"""Independent structural and boundary checker for completion Atlas V22."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V22.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V21.json"
OBSTRUCTION = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1.json"


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
        "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def cell_map(value: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {(branch["id"], stage["stage"]): stage for branch in value["branches"] for stage in branch["stages"]}


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    previous = json.loads(PREDECESSOR.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V22" or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v22":
        return ["result identity/version drift"]
    if value.get("predecessor", {}).get("sha256") != sha(PREDECESSOR) or value.get("predecessor", {}).get("preserved") is not True:
        errors.append("V21 predecessor binding drift")
    before, after = cell_map(previous), cell_map(value)
    if set(before) != set(after) or len(after) != 77:
        errors.append("77-cell preservation drift")
    changed = {key for key in before.keys() & after.keys() if before[key] != after[key]}
    changed.update(before.keys() ^ after.keys())
    if changed != {("STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")}:
        errors.append("unexpected cell mutation")

    p = value.get("strict_quadratic_truncation_lambda2_source_obstruction", {})
    source = obstruction["quadratic_truncation_disposition"]
    expected = {
        "fixture_id": "FLAT_PURE_DIFF_GAUGE_SEED_1",
        "q1_closed_fixture": True,
        "q2_jacobiator_nonzero": True,
        "q2_jacobiator_weyl_identity_value": source["witness_jacobiator_weyl_identity"],
        "q2_only_lambda2_source_closed": False,
        "q2_only_lambda2_source_defect": source["witness_source_closure_defect"],
        "authoritative_q3_required": True,
        "required_q3_q1_image": source["required_q3_q1_image_on_witness"],
        "authoritative_q3_imported": False,
        "full_weyl_lambda2_source_closure": False,
        "not_a_full_weyl_no_go": True,
        "analytic_green_action_needed_for_obstruction": False,
    }
    for key, wanted in expected.items():
        if p.get(key) != wanted:
            errors.append("lambda2 projection drift: " + key)
    if p.get("export_contract_id") != "STRICT_PURE_WEYL_AUTHORITATIVE_Q3_SOURCE_CLOSURE_EXPORT_V1":
        errors.append("q3 export contract projection drift")

    nonlinear = after[("STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")]
    if nonlinear.get("status") != "PARTIAL_CERTIFIED_WITH_SCOPED_OBSTRUCTION" or obstruction["result_id"] not in nonlinear.get("evidence", []):
        errors.append("strict nonlinear stage disposition drift")
    if "37880/27" not in nonlinear.get("statement", "") or "full Weyl" not in nonlinear.get("statement", ""):
        errors.append("scoped obstruction narrative drift")

    routes = value.get("route_selection", [])
    route_names = [item.get("route") for item in routes]
    if len(routes) != 11 or [item.get("rank") for item in routes] != list(range(1, 12)):
        errors.append("route rank/count drift")
    if route_names[:2] != ["STRICT_AUTHORITATIVE_Q2_Q3_ARITY_THREE_EXPORT", "STRICT_LAMBDA2_FULL_SOURCE_COCYCLE_CLOSURE"]:
        errors.append("nonlinear frontier ordering drift")
    if "STRICT_Q2_Q3_SOURCE_COCYCLE_CLOSURE" in route_names:
        errors.append("vague V21 source route not retired")
    if [item.get("object") for item in value.get("research_queue", [])] != route_names:
        errors.append("research queue projection drift")

    flags = value.get("claim_flags", {})
    for key in ("v21_preserved", "strict_386_q2_only_lambda2_source_obstructed", "strict_386_q2_jacobiator_nonzero_witness_certified", "strict_386_authoritative_q3_required"):
        if flags.get(key) is not True:
            errors.append("positive flag missing: " + key)
    for key in ("strict_386_authoritative_q3_imported", "strict_386_full_weyl_lambda2_source_closure_certified", "strict_386_quadratic_truncation_moller_map_certified", "strict_386_authoritative_formal_moller_map_certified", "strict_pure_weyl_classical_gate_passed", "strict_386_full_bv_hadamard_state_constructed", "strict_pure_weyl_qme_restored", "lorentzian_full_theory_certified"):
        if flags.get(key) is not False:
            errors.append("firewall flag missing: " + key)
    if not any("a no-go theorem for full Weyl gravity" in item for item in value.get("does_not_establish", [])):
        errors.append("full-Weyl no-go boundary missing")

    inputs = value.get("provenance", {}).get("inputs", [])
    if not any(item.get("path") == str(OBSTRUCTION.relative_to(ROOT)) and item.get("sha256") == sha(OBSTRUCTION) for item in inputs):
        errors.append("obstruction provenance missing")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical atlas digest drift")
    return errors


def main() -> int:
    errors = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V22: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    if not errors:
        print("  - all 77 cells preserved and the q2-only lambda2 obstruction projects")
        print("  - exact q3 cancellation target and authoritative export contract exposed")
        print("  - full Weyl source closure, Gate A, Hadamard and QME remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
