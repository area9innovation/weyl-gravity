#!/usr/bin/env python3
"""Independent structural and boundary checker for completion atlas V6."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V6.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V5.json"
SUSPENSION = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1.json"
STAGES = ["S0_CLASSICAL_AUTHORITY", "S1_OFF_SHELL_BV", "S2_CAUSAL_GREEN", "S3_NONLINEAR_CARTAN", "S4_HADAMARD_CCR", "S5_BRST_WARD", "S6_PHYSICAL_POSITIVITY", "S7_RENORMALIZED_PRODUCTS", "S8_QME", "S9_RESIDUAL_TRANSFER", "S10_LORENTZIAN_CERTIFIED"]
BRANCHES = ["STRICT_PURE_WEYL_386", "PURE_WEYL_BACH_FLAT_RANK310", "EINSTEIN_NARIAI_KS", "BERGER_POSITIVE_CLOCK_54", "VACUUM_CYLINDER_REDUCED", "TAU_ADIC_COMPENSATOR", "COMPLEX_COMPENSATOR_CHANGED_ACTION"]
ROUTES = ["STRICT_386_COMPONENT_PAIRING_SERIALIZATION", "STRICT_386_LOCAL_D", "STRICT_386_Q2_GREEN_COMPATIBILITY", "DIRECT_SPACETIME_Q26_HADAMARD", "BACH_FLAT_NONLINEAR_CARTAN"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = ("stages", "branches", "frontier_summary", "classical_import_reconciliation", "strict_gate_a_progress", "strict_causal_sign_transport", "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge", "berger_h26_c26_decision_chain", "route_selection", "research_queue")
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    previous = json.loads(PREDECESSOR.read_text())
    source = json.loads(SUSPENSION.read_text())
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V6" or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v6":
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
    if not all(token in json.dumps(strict_cells["S2_CAUSAL_GREEN"]) for token in ("A^ddagger", "Lambda'_+", "projector-level")):
        errors.append("suspended causal statement")
    endpoint = source["endpoint_exact_algebra"]
    full = source["full_carrier_extension"]
    projected = value.get("strict_suspended_adjoint_bridge", {})
    expected = {"result_id": source["result_id"], "status": source["result_state"], "endpoint_pairing_entries": 54, "endpoint_T_negative": 5, "endpoint_T_sharp_negative": 5, "endpoint_R_negative": 10, "full_R_positive": 376, "full_R_negative": 10, "full_suspended_green_adjoint_replayed": True, "full_component_pairing_serialized": False, "finite_bridge_base": "PRA", "analytic_causal_weakest_base": "NOT_ESTABLISHED", "next_gate": source["next_gate"]}
    if projected != expected:
        errors.append("suspension projection")
    if endpoint["T_diagonal"].count(-1) != 5 or endpoint["T_sharp_gate_diagonal"].count(-1) != 5 or endpoint["R_diagonal"].count(-1) != 10 or full["R_386_negative"] != 10:
        errors.append("source suspension arithmetic")
    progress = value.get("strict_gate_a_progress", {})
    if progress.get("status") != "FULL_SUSPENDED_GREEN_ADJOINT_REPLAYED_COMPONENT_PAIRING_D_Q2_OPEN" or progress.get("suspended_adjoint_control") != {"endpoint_pairing_entries": 54, "R_386_positive": 376, "R_386_negative": 10, "full_green_suspended_adjoint_replayed": True, "full_component_pairing_serialized": False}:
        errors.append("progress ledger")
    if value.get("classical_import_reconciliation") != previous.get("classical_import_reconciliation") or value.get("strict_endpoint_q1_content_bridge") != previous.get("strict_endpoint_q1_content_bridge") or value.get("berger_h26_c26_decision_chain") != previous.get("berger_h26_c26_decision_chain"):
        errors.append("predecessor control mutation")
    if [item.get("route") for item in value.get("route_selection", [])] != ROUTES or [item.get("rank") for item in value.get("route_selection", [])] != [1, 2, 3, 4, 5]:
        errors.append("route ranking")
    flags = value.get("claim_flags", {})
    for key in ("v5_preserved", "strict_386_pairing_suspension_bridge_certified", "strict_386_full_suspended_green_adjoint_replayed"):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in ("strict_386_component_pairing_serialized", "strict_386_common_bytes_identified", "strict_full_386_pairing_serialized", "strict_386_local_d_certified", "strict_386_q2_green_compatibility_certified", "strict_pure_weyl_classical_gate_passed", "lorentzian_full_theory_certified"):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)
    predecessor = value.get("predecessor")
    if predecessor != {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True}:
        errors.append("predecessor")
    expected_inputs = [*previous["provenance"]["inputs"], {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V5 atlas predecessor"}, {"path": str(SUSPENSION.relative_to(ROOT)), "sha256": sha(SUSPENSION), "role": "exact full-carrier suspended-adjoint bridge"}]
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
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V6: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors: print("  - " + error)
    else:
        print("  - 77 cells preserved; the five-row sign is an exact suspension twist")
        print("  - full R_386 has 376 positive and 10 negative signs")
        print("  - component pairing, D, q2, Hadamard and QME remain fail closed")
    return bool(errors)


if __name__ == "__main__": raise SystemExit(main())
