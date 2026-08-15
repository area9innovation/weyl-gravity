#!/usr/bin/env python3
"""Independent structural checker for completion Atlas V26."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V26.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V25.json"
OBSTRUCTION = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1.json"
GATE_V8 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V8_RECONCILIATION.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_gate_v8_reconciliation",
        "strict_q2_green_composition_preflight",
        "strict_recursive_causal_tree_domains", "strict_polarized_formal_coefficients",
        "strict_field_equation_green_quotient_inverse", "strict_quadratic_truncation_lambda2_source_obstruction",
        "strict_pure_weyl_q3_witness", "strict_minimal_q3_completion", "strict_386_stabilized_q3_preflight",
        "strict_nonminimal_theory_identity_obstruction", "route_selection", "research_queue",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def cells(value: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {(branch["id"], stage["stage"]): stage for branch in value["branches"] for stage in branch["stages"]}


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    previous = json.loads(PREDECESSOR.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    gate_v8 = json.loads(GATE_V8.read_text())
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V26" or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v26":
        return ["result identity/version drift"]
    predecessor = value.get("predecessor", {})
    if predecessor.get("sha256") != sha(PREDECESSOR) or predecessor.get("preserved") is not True:
        errors.append("V25 predecessor binding drift")
    before, after = cells(previous), cells(value)
    if set(before) != set(after) or len(after) != 77:
        errors.append("77-cell preservation drift")
    if {key for key in before if before[key] != after[key]} != {("STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")}:
        errors.append("unexpected completion-cell mutation")
    comparison = obstruction["exact_channel_comparison"]
    disposition = obstruction["theory_identity_disposition"]
    expected = {
        "result_id": obstruction["result_id"], "carrier_rows": 386,
        "cyclic_form_channel": "Omega(f_hat,q2(v,v))", "block_channel": ["AUX_F_HAT", "AUX_V", "AUX_V"],
        "source_value": "-1", "candidate_value": "0", "source_minus_candidate_defect": "-1",
        "literal_identity_refuted": True, "linear_shear_only_identity_refuted": True,
        "candidate_internal_identities_preserved": True, "nonlinear_equivalence_may_exist": True,
        "nonlinear_equivalence_constructed": False, "nonlinear_equivalence_obstructed": False,
        "first_required_correction": disposition["first_required_correction"], "classical_import_gate_a_passed": False,
        "foundational_classification": "FINITE_EXACT_LOCAL_ACTION_POLARIZATION", "next_gate": obstruction["next_gate"],
    }
    if value.get("strict_nonminimal_theory_identity_obstruction") != expected:
        errors.append("theory-identity obstruction projection drift")
    if comparison.get("source_minus_candidate_defect") != "-1" or comparison.get("literal_identity") is not False:
        errors.append("source obstruction semantic drift")
    gate_m2 = gate_v8["m2_theory_identity_obstruction"]
    gate_disposition = gate_v8["gate_disposition"]
    expected_gate = {
        "result_id": gate_v8["result_id"], "status": gate_v8["result_state"],
        "exports_total": 20, "exports_receiver_verified_scoped": gate_disposition["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": 10, "freeze_checks_receiver_verified_scoped": gate_disposition["freeze_checks_receiver_verified_scoped"],
        "freeze_checks_supporting_evidence_only": gate_disposition["freeze_checks_supporting_evidence_only"],
        "freeze_checks_blocked": gate_disposition["freeze_checks_blocked"],
        "accepted_top_level_hashes": 0, "gate_a_status": "FAIL_CLOSED", "candidate_q2_hash_accepted": False,
        "cyclic_form_channel": "Omega(f_hat,q2(v,v))", "source_value": "-1", "candidate_value": "0", "defect": "-1",
        "literal_and_linear_identity_refuted": True, "candidate_internal_identities_preserved": True,
        "nonlinear_equivalence_may_exist": True, "nonlinear_equivalence_constructed": False,
        "nonlinear_equivalence_obstructed": False,
        "missing_bundle_ids": [item["id"] for item in gate_v8["minimal_missing_bundle"]],
        "next_gate": gate_v8["next_gate"],
    }
    if value.get("strict_gate_v8_reconciliation") != expected_gate or gate_m2.get("defect") != "-1":
        errors.append("Gate V8 projection drift")
    nonlinear = after.get(("STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN"), {})
    if nonlinear.get("status") != "PARTIAL_CERTIFIED_WITH_LINEAR_THEORY_IDENTITY_OBSTRUCTED_NONLINEAR_EQUIVALENCE_OPEN" or obstruction["result_id"] not in nonlinear.get("evidence", []):
        errors.append("strict nonlinear stage projection drift")
    if "does not refute nonlinear equivalence" not in nonlinear.get("boundary", ""):
        errors.append("nonlinear-equivalence narrative firewall drift")
    names = [item.get("route") for item in value.get("route_selection", [])]
    if len(names) != 11 or [item.get("rank") for item in value["route_selection"]] != list(range(1, 12)):
        errors.append("route count/rank drift")
    if names[:4] != ["STRICT_NONLINEAR_AUXILIARY_ELIMINATION_MAP_Q2", "STRICT_SOURCE_Q2_Q3_PULLBACK_IDENTITY", "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE", "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE"]:
        errors.append("post-obstruction route ordering drift")
    if [item.get("object") for item in value.get("research_queue", [])] != names:
        errors.append("research queue drift")
    flags = value.get("claim_flags", {})
    true_flags = ("v25_preserved", "strict_386_literal_trivial_stabilization_identity_refuted", "strict_386_linear_shear_theory_identity_refuted", "strict_386_candidate_internal_identities_preserved", "strict_386_nonlinear_equivalence_may_exist")
    false_flags = ("strict_386_nonlinear_equivalence_constructed", "strict_386_nonlinear_equivalence_obstructed", "strict_386_authoritative_q2_imported", "strict_386_authoritative_q3_imported", "strict_386_candidate_causal_lambda2_source_closure_certified", "strict_pure_weyl_classical_gate_passed", "strict_386_full_bv_hadamard_state_constructed", "strict_pure_weyl_qme_restored", "lorentzian_full_theory_certified")
    if any(flags.get(key) is not True for key in true_flags) or any(flags.get(key) is not False for key in false_flags):
        errors.append("V26 claim firewall drift")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical atlas digest drift")
    if not any(item.get("path") == str(OBSTRUCTION.relative_to(ROOT)) and item.get("sha256") == sha(OBSTRUCTION) for item in value.get("provenance", {}).get("inputs", [])):
        errors.append("obstruction provenance drift")
    if not any(item.get("path") == str(GATE_V8.relative_to(ROOT)) and item.get("sha256") == sha(GATE_V8) for item in value.get("provenance", {}).get("inputs", [])):
        errors.append("Gate V8 provenance drift")
    return errors


def main() -> int:
    errors = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V26: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
