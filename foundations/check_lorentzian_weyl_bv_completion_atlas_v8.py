#!/usr/bin/env python3
"""Independent structural and boundary checker for completion atlas V8."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V8.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V7.json"
PORTABILITY = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1.json"
STAGES = ["S0_CLASSICAL_AUTHORITY", "S1_OFF_SHELL_BV", "S2_CAUSAL_GREEN", "S3_NONLINEAR_CARTAN", "S4_HADAMARD_CCR", "S5_BRST_WARD", "S6_PHYSICAL_POSITIVITY", "S7_RENORMALIZED_PRODUCTS", "S8_QME", "S9_RESIDUAL_TRANSFER", "S10_LORENTZIAN_CERTIFIED"]
BRANCHES = ["STRICT_PURE_WEYL_386", "PURE_WEYL_BACH_FLAT_RANK310", "EINSTEIN_NARIAI_KS", "BERGER_POSITIVE_CLOCK_54", "VACUUM_CYLINDER_REDUCED", "TAU_ADIC_COMPENSATOR", "COMPLEX_COMPENSATOR_CHANGED_ACTION"]
ROUTES = ["STRICT_386_FULL_Q1_JET_TABLE", "STRICT_386_LOCAL_SDR_COMPONENT_MAPS", "STRICT_ENDPOINT_ANALYTIC_GREEN_ACTION", "STRICT_FULL_GREEN_COMPONENT_ACTION_REPLAY", "STRICT_386_LOCAL_D", "STRICT_386_Q2_GREEN_COMPATIBILITY", "DIRECT_SPACETIME_Q26_HADAMARD", "BACH_FLAT_NONLINEAR_CARTAN"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_causal_sign_transport",
        "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge",
        "strict_component_pairing_serialization", "strict_operator_portability",
        "berger_h26_c26_decision_chain", "route_selection", "research_queue",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    previous = json.loads(PREDECESSOR.read_text())
    source = json.loads(PORTABILITY.read_text())
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V8" or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v8":
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
    strict_cells = {item["stage"]: item for item in branches.get("STRICT_PURE_WEYL_386", {}).get("stages", [])}
    old_cells = {item["stage"]: item for item in old["STRICT_PURE_WEYL_386"]["stages"]}
    if branches.get("STRICT_PURE_WEYL_386", {}).get("first_unclosed_gate") != "S0_CLASSICAL_AUTHORITY" or strict_cells.get("S0_CLASSICAL_AUTHORITY", {}).get("status") != "FAIL_CLOSED":
        errors.append("Gate-A firewall")
    for stage_id in STAGES:
        if stage_id not in {"S0_CLASSICAL_AUTHORITY", "S2_CAUSAL_GREEN"} and strict_cells.get(stage_id) != old_cells.get(stage_id):
            errors.append("unlicensed strict stage mutation " + stage_id)
    causal_text = json.dumps(strict_cells.get("S2_CAUSAL_GREEN", {}))
    if not all(token in causal_text for token in ("nonlocal", "not a finite jet table", "receiver-executable")):
        errors.append("local/nonlocal causal statement")

    projected = value.get("strict_operator_portability", {})
    expected = {
        "result_id": source["result_id"], "status": source["result_state"],
        "contracts": ["FINITE_COMPONENT_JET_TABLE", "FINITE_SPARSE_COMPONENT_MAP", "ANALYTIC_GREEN_ACTION"],
        "operator_families_classified": 6, "status_counts": source["status_counts"],
        "endpoint_q1_arrow_tables": 80, "endpoint_q1_nonzero_coefficients": 619,
        "endpoint_q1_bach_columns": 700, "full_q1_portable": False,
        "local_sdr_portable": False, "endpoint_green_action_portable": False,
        "full_green_action_portable": False, "causal_green_theorem_preserved": True,
        "finite_local_upper_bound": "PRA", "analytic_green_weakest_base": "NOT_ESTABLISHED",
        "next_gate": source["next_gate"],
    }
    if projected != expected:
        errors.append("operator portability projection")
    progress = value.get("strict_gate_a_progress", {})
    if progress.get("status") != "ENDPOINT_Q1_PORTABLE_FULL_LOCAL_AND_ANALYTIC_ACTION_ARTIFACTS_OPEN" or progress.get("operator_portability_control") != expected:
        errors.append("Gate-A progress ledger")
    if value.get("strict_component_pairing_serialization") != previous.get("strict_component_pairing_serialization") or value.get("strict_endpoint_q1_content_bridge") != previous.get("strict_endpoint_q1_content_bridge") or value.get("berger_h26_c26_decision_chain") != previous.get("berger_h26_c26_decision_chain"):
        errors.append("predecessor control mutation")
    if [item.get("route") for item in value.get("route_selection", [])] != ROUTES or [item.get("rank") for item in value.get("route_selection", [])] != list(range(1, 9)):
        errors.append("typed route ranking")
    if [item.get("priority") for item in value.get("research_queue", [])] != list(range(1, 9)):
        errors.append("research queue")
    flags = value.get("claim_flags", {})
    for key in ("v7_preserved", "strict_386_operator_portability_types_classified", "strict_endpoint_q1_portable_component_bytes", "strict_causal_green_homotopy_theorem_preserved", "strict_386_component_pairing_serialized"):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in ("strict_full_386_q1_portable_component_bytes", "strict_full_386_local_sdr_portable_component_bytes", "strict_endpoint_green_portable_action_serialized", "strict_full_green_portable_action_serialized", "strict_386_all_operator_component_adjoints_replayed", "strict_386_local_d_certified", "strict_386_q2_green_compatibility_certified", "strict_pure_weyl_classical_gate_passed", "lorentzian_full_theory_certified"):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)
    predecessor = value.get("predecessor")
    expected_predecessor = {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True}
    if predecessor != expected_predecessor:
        errors.append("predecessor")
    expected_inputs = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V7 atlas predecessor"},
        {"path": str(PORTABILITY.relative_to(ROOT)), "sha256": sha(PORTABILITY), "role": "typed local/nonlocal strict-operator portability audit"},
    ]
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
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V8: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print("  - 77 cells preserved; six operator families split across three contracts")
        print("  - endpoint q1 portable; full local tables and nonlocal Green actions open")
        print("  - causal theorem preserved; Gate A, D, q2, Hadamard and QME fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
