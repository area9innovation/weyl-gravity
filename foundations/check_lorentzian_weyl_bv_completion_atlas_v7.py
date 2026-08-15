#!/usr/bin/env python3
"""Independent structural and boundary checker for completion atlas V7."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V7.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V6.json"
PAIRING = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
STAGES = ["S0_CLASSICAL_AUTHORITY", "S1_OFF_SHELL_BV", "S2_CAUSAL_GREEN", "S3_NONLINEAR_CARTAN", "S4_HADAMARD_CCR", "S5_BRST_WARD", "S6_PHYSICAL_POSITIVITY", "S7_RENORMALIZED_PRODUCTS", "S8_QME", "S9_RESIDUAL_TRANSFER", "S10_LORENTZIAN_CERTIFIED"]
BRANCHES = ["STRICT_PURE_WEYL_386", "PURE_WEYL_BACH_FLAT_RANK310", "EINSTEIN_NARIAI_KS", "BERGER_POSITIVE_CLOCK_54", "VACUUM_CYLINDER_REDUCED", "TAU_ADIC_COMPENSATOR", "COMPLEX_COMPENSATOR_CHANGED_ACTION"]
ROUTES = ["STRICT_386_OPERATOR_COMPONENT_SERIALIZATION", "STRICT_386_LOCAL_D", "STRICT_386_Q2_GREEN_COMPATIBILITY", "DIRECT_SPACETIME_Q26_HADAMARD", "BACH_FLAT_NONLINEAR_CARTAN"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = ("stages", "branches", "frontier_summary", "classical_import_reconciliation", "strict_gate_a_progress", "strict_causal_sign_transport", "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge", "strict_component_pairing_serialization", "berger_h26_c26_decision_chain", "route_selection", "research_queue")
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    previous = json.loads(PREDECESSOR.read_text())
    source = json.loads(PAIRING.read_text())
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V7" or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v7":
        errors.append("identity")
    if [item.get("id") for item in value.get("stages", [])] != STAGES or [item.get("id") for item in value.get("branches", [])] != BRANCHES:
        errors.append("axis identity/order")
    branches = {item.get("id"): item for item in value.get("branches", [])}
    old = {item.get("id"): item for item in previous.get("branches", [])}
    for branch_id, item in branches.items():
        if [cell.get("stage") for cell in item.get("stages", [])] != STAGES:
            errors.append("stage closure " + str(branch_id))
        if branch_id != "STRICT_PURE_WEYL_386" and item != old.get(branch_id):
            errors.append("unlicensed branch mutation " + str(branch_id))
    strict_cells = {item["stage"]: item for item in branches["STRICT_PURE_WEYL_386"]["stages"]}
    old_cells = {item["stage"]: item for item in old["STRICT_PURE_WEYL_386"]["stages"]}
    if branches["STRICT_PURE_WEYL_386"].get("first_unclosed_gate") != "S0_CLASSICAL_AUTHORITY" or strict_cells["S0_CLASSICAL_AUTHORITY"]["status"] != "FAIL_CLOSED":
        errors.append("Gate-A firewall")
    for stage_id in STAGES:
        if stage_id not in {"S0_CLASSICAL_AUTHORITY", "S2_CAUSAL_GREEN"} and strict_cells[stage_id] != old_cells[stage_id]:
            errors.append("unlicensed strict stage mutation " + stage_id)
    if not all(token in json.dumps(strict_cells["S2_CAUSAL_GREEN"]) for token in ("410", "component", "not component coefficient")):
        errors.append("component causal statement")

    basis = source["component_basis"]
    omega = source["pairing_serialization"]
    signs = source["suspension_serialization"]
    projected = value.get("strict_component_pairing_serialization", {})
    expected_projection = {
        "result_id": source["result_id"], "status": source["result_state"],
        "full_rows": 386, "endpoint_rows": 30, "algebraic_complement_rows": 356,
        "algebraic_complement_split": "356=36+320", "pairing_entries": 410, "pairing_rank": 386,
        "endpoint_pairing_entries_gate_coordinates": 30, "endpoint_pairing_entries_pre_pullback": 54,
        "componentwise_T_adjoint_replayed": True, "all_operator_component_adjoints_replayed": False,
        "finite_serialization_base": "PRA", "next_gate": source["next_gate"],
    }
    if projected != expected_projection:
        errors.append("component pairing projection")
    if basis["dimension"] != 386 or basis["algebraic_complement_split"] != "356=36+320" or omega["rank"] != 386 or omega["nonzero_ordered_entry_count"] != 410:
        errors.append("source basis/pairing arithmetic")
    if signs["T_negative"] != 5 or signs["R_negative"] != 10 or not signs["componentwise_T_adjoint_relation_replayed"]:
        errors.append("source suspension replay")

    progress = value.get("strict_gate_a_progress", {})
    if progress.get("status") != "FULL_COMPONENT_BASIS_PAIRING_AND_SUSPENSION_SERIALIZED_OPERATOR_TABLES_D_Q2_OPEN" or progress.get("component_pairing_control") != {"rows": 386, "complement_split": "356=36+320", "pairing_entries": 410, "pairing_rank": 386, "T_negative": 5, "R_negative": 10}:
        errors.append("progress ledger")
    if progress.get("endpoint_q1_control", {}).get("full_pairing_open") is not False or progress.get("endpoint_q1_control", {}).get("full_operator_snapshot_open") is not True:
        errors.append("endpoint progress boundary")
    suspended = progress.get("suspended_adjoint_control", {})
    if suspended.get("endpoint_pairing_entries") != 30 or suspended.get("endpoint_pairing_entries_pre_pullback") != 54 or suspended.get("full_component_pairing_serialized") is not True or suspended.get("all_operator_component_adjoints_replayed") is not False:
        errors.append("suspension progress reconciliation")
    if value.get("classical_import_reconciliation") != previous.get("classical_import_reconciliation") or value.get("strict_endpoint_q1_content_bridge") != previous.get("strict_endpoint_q1_content_bridge") or value.get("berger_h26_c26_decision_chain") != previous.get("berger_h26_c26_decision_chain"):
        errors.append("predecessor control mutation")
    if [item.get("route") for item in value.get("route_selection", [])] != ROUTES or [item.get("rank") for item in value.get("route_selection", [])] != [1, 2, 3, 4, 5]:
        errors.append("route ranking")
    flags = value.get("claim_flags", {})
    for key in ("v6_preserved", "strict_386_pairing_suspension_bridge_certified", "strict_386_full_suspended_green_adjoint_replayed", "strict_386_component_basis_serialized", "strict_386_component_pairing_serialized", "strict_full_386_pairing_serialized", "strict_386_componentwise_t_adjoint_replayed"):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in ("strict_386_all_operator_component_adjoints_replayed", "strict_386_common_bytes_identified", "strict_386_local_d_certified", "strict_386_q2_green_compatibility_certified", "strict_pure_weyl_classical_gate_passed", "lorentzian_full_theory_certified"):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)
    predecessor = value.get("predecessor")
    if predecessor != {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True}:
        errors.append("predecessor")
    expected_inputs = [*previous["provenance"]["inputs"], {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V6 atlas predecessor"}, {"path": str(PAIRING.relative_to(ROOT)), "sha256": sha(PAIRING), "role": "exact 386-row component basis and pairing serialization"}]
    if value.get("provenance", {}).get("inputs") != expected_inputs:
        errors.append("append-only provenance")
    for item in expected_inputs:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            errors.append("provenance " + item["path"])
    if digest(value) != value.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V7: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors: print("  - " + error)
    else:
        print("  - 77 cells preserved; 386 rows split as 30+36+320")
        print("  - exact rank-386 odd pairing has 410 ordered entries")
        print("  - operator bytes, D, q2, Hadamard and QME remain fail closed")
    return bool(errors)


if __name__ == "__main__": raise SystemExit(main())
