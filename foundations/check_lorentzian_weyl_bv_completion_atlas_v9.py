#!/usr/bin/env python3
"""Independent structural and boundary checker for completion atlas V9."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V9.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V8.json"
SIGN_GATE = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1.json"
STAGES = ["S0_CLASSICAL_AUTHORITY", "S1_OFF_SHELL_BV", "S2_CAUSAL_GREEN", "S3_NONLINEAR_CARTAN", "S4_HADAMARD_CCR", "S5_BRST_WARD", "S6_PHYSICAL_POSITIVITY", "S7_RENORMALIZED_PRODUCTS", "S8_QME", "S9_RESIDUAL_TRANSFER", "S10_LORENTZIAN_CERTIFIED"]
BRANCHES = ["STRICT_PURE_WEYL_386", "PURE_WEYL_BACH_FLAT_RANK310", "EINSTEIN_NARIAI_KS", "BERGER_POSITIVE_CLOCK_54", "VACUUM_CYLINDER_REDUCED", "TAU_ADIC_COMPENSATOR", "COMPLEX_COMPENSATOR_CHANGED_ACTION"]
ROUTES = ["STRICT_386_AUXILIARY_Q_SIGN_REPAIR", "STRICT_386_FULL_Q1_JET_TABLE", "STRICT_386_LOCAL_SDR_COMPONENT_MAPS", "STRICT_ENDPOINT_ANALYTIC_GREEN_ACTION", "STRICT_FULL_GREEN_COMPONENT_ACTION_REPLAY", "STRICT_386_LOCAL_D", "STRICT_386_Q2_GREEN_COMPATIBILITY", "DIRECT_SPACETIME_Q26_HADAMARD", "BACH_FLAT_NONLINEAR_CARTAN"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_causal_sign_transport",
        "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge",
        "strict_component_pairing_serialization", "strict_operator_portability",
        "strict_full_q1_split_sign_gate", "berger_h26_c26_decision_chain",
        "route_selection", "research_queue",
    )
    return hashlib.sha256(
        json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    previous = json.loads(PREDECESSOR.read_text())
    source = json.loads(SIGN_GATE.read_text())
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V9" or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v9":
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
    strict = branches.get("STRICT_PURE_WEYL_386", {})
    strict_cells = {item["stage"]: item for item in strict.get("stages", [])}
    old_cells = {item["stage"]: item for item in old["STRICT_PURE_WEYL_386"]["stages"]}
    if strict.get("first_unclosed_gate") != "S0_CLASSICAL_AUTHORITY" or strict_cells.get("S0_CLASSICAL_AUTHORITY", {}).get("status") != "FAIL_CLOSED":
        errors.append("Gate-A firewall")
    for stage_id in STAGES[1:]:
        if strict_cells.get(stage_id) != old_cells.get(stage_id):
            errors.append("unlicensed strict stage mutation " + stage_id)
    s0 = json.dumps(strict_cells.get("S0_CLASSICAL_AUTHORITY", {}))
    if not all(token in s0 for token in ("+I4", "-I4", "eight", "repair")):
        errors.append("S0 sign-gate statement")

    replay = source["exact_replay"]
    expected = {
        "result_id": source["result_id"],
        "status": source["result_state"],
        "carrier_rows": 386,
        "auxiliary_rows": 36,
        "block": "AUX_V_STAR -> AUX_ETA_STAR",
        "executable_sign": "+I_4",
        "declared_sign": "-I_4",
        "executable_cyclicity_defects": 0,
        "declared_cyclicity_defects": 8,
        "both_nilpotent": replay["executable_plus_sign"]["q_squared_defects"] == replay["declared_minus_sign"]["q_squared_defects"] == 0,
        "both_contractible": replay["executable_plus_sign"]["contraction_defects"] == replay["declared_minus_sign"]["contraction_defects"] == 0,
        "repair_applied": False,
        "split_coordinate_classified": True,
        "foundational_upper_bound": "PRA",
        "choice_operation_added": False,
        "next_gate": source["next_gate"],
    }
    if value.get("strict_full_q1_split_sign_gate") != expected:
        errors.append("split-q1 sign-gate projection")
    progress = value.get("strict_gate_a_progress", {})
    if progress.get("status") != "AUXILIARY_Q_TEXT_MATRIX_SIGN_REPAIR_REQUIRED" or progress.get("full_q1_split_sign_control") != expected:
        errors.append("Gate-A progress ledger")
    for key in ("strict_operator_portability", "strict_component_pairing_serialization", "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge", "strict_causal_sign_transport", "berger_h26_c26_decision_chain"):
        if value.get(key) != previous.get(key):
            errors.append("predecessor control mutation " + key)
    if value.get("claim_flags", {}).get("strict_causal_green_homotopy_theorem_preserved") is not True:
        errors.append("causal theorem revocation")
    if [item.get("route") for item in value.get("route_selection", [])] != ROUTES or [item.get("rank") for item in value.get("route_selection", [])] != list(range(1, 10)):
        errors.append("sign-aware route ranking")
    if [item.get("priority") for item in value.get("research_queue", [])] != list(range(1, 10)):
        errors.append("research queue")
    flags = value.get("claim_flags", {})
    for key in ("v8_preserved", "strict_386_auxiliary_q_text_matrix_sign_conflict_certified", "strict_386_executable_auxiliary_q_cyclic_with_serialized_pairing", "strict_386_split_coordinate_location_classified", "strict_causal_green_homotopy_theorem_preserved"):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in ("strict_386_declared_minus_sign_cyclic_with_serialized_pairing", "strict_386_auxiliary_q_sign_repair_applied", "strict_full_386_q1_portable_component_bytes", "strict_pure_weyl_classical_gate_passed", "lorentzian_full_theory_certified"):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)
    expected_predecessor = {
        "result_id": previous["result_id"],
        "path": str(PREDECESSOR.relative_to(ROOT)),
        "sha256": sha(PREDECESSOR),
        "preserved": True,
    }
    if value.get("predecessor") != expected_predecessor:
        errors.append("predecessor")
    expected_inputs = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V8 atlas predecessor"},
        {"path": str(SIGN_GATE.relative_to(ROOT)), "sha256": sha(SIGN_GATE), "role": "exact split-q1 auxiliary text/matrix sign gate"},
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
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V9: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print("  - 77 cells preserved; strict S0 records the exact auxiliary sign conflict")
        print("  - +I4 has zero cyclicity defects; declared -I4 has eight")
        print("  - repair, full q1, Gate A, Hadamard and QME remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
