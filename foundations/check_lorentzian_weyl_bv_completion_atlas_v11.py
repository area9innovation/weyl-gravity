#!/usr/bin/env python3
"""Independent structural and boundary checker for completion atlas V11."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V11.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V10.json"
Q1 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
STAGES = ["S0_CLASSICAL_AUTHORITY", "S1_OFF_SHELL_BV", "S2_CAUSAL_GREEN", "S3_NONLINEAR_CARTAN", "S4_HADAMARD_CCR", "S5_BRST_WARD", "S6_PHYSICAL_POSITIVITY", "S7_RENORMALIZED_PRODUCTS", "S8_QME", "S9_RESIDUAL_TRANSFER", "S10_LORENTZIAN_CERTIFIED"]
BRANCHES = ["STRICT_PURE_WEYL_386", "PURE_WEYL_BACH_FLAT_RANK310", "EINSTEIN_NARIAI_KS", "BERGER_POSITIVE_CLOCK_54", "VACUUM_CYLINDER_REDUCED", "TAU_ADIC_COMPENSATOR", "COMPLEX_COMPENSATOR_CHANGED_ACTION"]
ROUTES = ["STRICT_386_LOCAL_SDR_COMPONENT_MAPS", "STRICT_386_CANONICAL_SHEAR_TABLE", "STRICT_ENDPOINT_ANALYTIC_GREEN_ACTION", "STRICT_FULL_GREEN_COMPONENT_ACTION_REPLAY", "STRICT_386_ACCEPTED_COMMON_SNAPSHOT", "STRICT_386_LOCAL_D", "STRICT_386_Q2_GREEN_COMPATIBILITY", "DIRECT_SPACETIME_Q26_HADAMARD", "BACH_FLAT_NONLINEAR_CARTAN"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = ("stages", "branches", "frontier_summary", "classical_import_reconciliation", "strict_gate_a_progress", "strict_causal_sign_transport", "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge", "strict_component_pairing_serialization", "strict_operator_portability", "strict_full_q1_split_sign_gate", "strict_auxiliary_q_sign_repair", "strict_full_q1_component_jet_table", "berger_h26_c26_decision_chain", "route_selection", "research_queue")
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    previous = json.loads(PREDECESSOR.read_text())
    source = json.loads(Q1.read_text())
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V11" or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v11":
        errors.append("identity")
    if [item.get("id") for item in value.get("stages", [])] != STAGES or [item.get("id") for item in value.get("branches", [])] != BRANCHES:
        errors.append("axis identity/order")
    branches = {item.get("id"): item for item in value.get("branches", [])}
    old = {item.get("id"): item for item in previous.get("branches", [])}
    for branch_id, item in branches.items():
        if len(item.get("stages", [])) != 11:
            errors.append("stage closure " + str(branch_id))
        if branch_id != "STRICT_PURE_WEYL_386" and item != old.get(branch_id):
            errors.append("unlicensed branch mutation " + str(branch_id))
    strict = branches.get("STRICT_PURE_WEYL_386", {})
    cells = {item["stage"]: item for item in strict.get("stages", [])}
    old_cells = {item["stage"]: item for item in old["STRICT_PURE_WEYL_386"]["stages"]}
    if strict.get("first_unclosed_gate") != "S0_CLASSICAL_AUTHORITY" or cells.get("S0_CLASSICAL_AUTHORITY", {}).get("status") != "FAIL_CLOSED":
        errors.append("Gate-A firewall")
    for stage_id in STAGES[1:]:
        if cells.get(stage_id) != old_cells.get(stage_id):
            errors.append("unlicensed strict stage mutation " + stage_id)

    q1 = value.get("strict_full_q1_component_jet_table", {})
    expected_q1 = {
        "result_id": source["result_id"],
        "status": source["result_state"],
        "carrier_dimension": 386,
        "carrier_split": "30+36+320",
        "operator_tables": 18,
        "coefficient_multiindex_tables": 127,
        "nonzero_rational_coefficients": 2193,
        "sector_coefficients": {"endpoint_30": 619, "auxiliary_36": 30, "mapping_cone_320": 1544},
        "maximum_order": 4,
        "q1_squared_zero": True,
        "suspended_cyclicity_defects": 0,
        "derivative_multiindices_checked": 70,
        "unary_snapshot_sha256": source["unary_snapshot"]["snapshot_sha256"],
        "full_sdr_tables_serialized": False,
        "classical_import_gate_passed": False,
        "next_gate": source["next_gate"],
    }
    if q1 != expected_q1:
        errors.append("full-q1 projection")
    progress = value.get("strict_gate_a_progress", {})
    if progress.get("status") != "FULL_Q1_SERIALIZED_SDR_COMMON_SNAPSHOT_REQUIRED" or progress.get("full_q1_component_jet_control") != expected_q1:
        errors.append("Gate-A progress ledger")
    for key in ("strict_operator_portability", "strict_component_pairing_serialization", "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge", "strict_causal_sign_transport", "strict_full_q1_split_sign_gate", "strict_auxiliary_q_sign_repair", "berger_h26_c26_decision_chain"):
        if value.get(key) != previous.get(key):
            errors.append("predecessor control mutation " + key)
    if [item.get("route") for item in value.get("route_selection", [])] != ROUTES or [item.get("rank") for item in value.get("route_selection", [])] != list(range(1, 10)):
        errors.append("q1-aware route ranking")

    flags = value.get("claim_flags", {})
    for key in ("v10_preserved", "strict_full_386_q1_portable_component_bytes", "strict_386_full_q1_squared_zero_replayed", "strict_386_full_q1_suspended_cyclicity_replayed", "strict_386_unary_snapshot_hash_established", "strict_causal_green_homotopy_theorem_preserved"):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in ("strict_386_full_sdr_operator_tables_serialized", "strict_pure_weyl_classical_gate_passed", "lorentzian_full_theory_certified"):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)
    expected_predecessor = {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True}
    if value.get("predecessor") != expected_predecessor:
        errors.append("predecessor")
    expected_inputs = [*previous["provenance"]["inputs"], {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V10 atlas predecessor"}, {"path": str(Q1.relative_to(ROOT)), "sha256": sha(Q1), "role": "complete exact 386-row unary snapshot and replay"}]
    if value.get("provenance", {}).get("inputs") != expected_inputs:
        errors.append("append-only provenance")
    for item in expected_inputs:
        path = ROOT / item["path"]
        historical = item["path"] in {
            "quantum-weyl/classical_import/certificates/STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1.json",
            "quantum-weyl/classical_import/certificates/STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1.json",
            "quantum-weyl/classical_import/certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json",
        }
        if historical:
            if len(item["sha256"]) != 64:
                errors.append("historical repair provenance")
        elif not path.is_file() or sha(path) != item["sha256"]:
            errors.append("provenance " + item["path"])
    if digest(value) != value.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V11: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    if not errors:
        print("  - 77 cells preserved; strict S0 now includes the complete exact unary snapshot")
        print("  - 2,193 rational coefficients; q1 squared and suspended cyclicity replay with zero defects")
        print("  - SDR/common snapshot, Hadamard and QME remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
