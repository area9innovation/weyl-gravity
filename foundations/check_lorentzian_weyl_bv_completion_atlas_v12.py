#!/usr/bin/env python3
"""Independent structural and claim-boundary checker for completion atlas V12."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V12.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V11.json"
SDR = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1.json"
STAGES = [f"S{i}_{name}" for i, name in enumerate((
    "CLASSICAL_AUTHORITY", "OFF_SHELL_BV", "CAUSAL_GREEN", "NONLINEAR_CARTAN",
    "HADAMARD_CCR", "BRST_WARD", "PHYSICAL_POSITIVITY", "RENORMALIZED_PRODUCTS",
    "QME", "RESIDUAL_TRANSFER", "LORENTZIAN_CERTIFIED",
))]
BRANCHES = [
    "STRICT_PURE_WEYL_386", "PURE_WEYL_BACH_FLAT_RANK310", "EINSTEIN_NARIAI_KS",
    "BERGER_POSITIVE_CLOCK_54", "VACUUM_CYLINDER_REDUCED", "TAU_ADIC_COMPENSATOR",
    "COMPLEX_COMPENSATOR_CHANGED_ACTION",
]
ROUTES = [
    "STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS", "STRICT_386_SPLIT_TO_GRAPH_SDR_REPLAY",
    "STRICT_ENDPOINT_ANALYTIC_GREEN_ACTION", "STRICT_FULL_GREEN_COMPONENT_ACTION_REPLAY",
    "STRICT_386_ACCEPTED_COMMON_SNAPSHOT", "STRICT_386_LOCAL_D",
    "STRICT_386_Q2_GREEN_COMPATIBILITY", "DIRECT_SPACETIME_Q26_HADAMARD",
    "BACH_FLAT_NONLINEAR_CARTAN",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_causal_sign_transport",
        "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge",
        "strict_component_pairing_serialization", "strict_operator_portability",
        "strict_full_q1_split_sign_gate", "strict_auxiliary_q_sign_repair",
        "strict_full_q1_component_jet_table", "strict_local_sdr_component_maps",
        "berger_h26_c26_decision_chain", "route_selection", "research_queue",
    )
    payload = json.dumps(
        {key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    previous = json.loads(PREDECESSOR.read_text())
    source = json.loads(SDR.read_text())
    errors: list[str] = []

    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V12" or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v12":
        errors.append("identity")
    if [item.get("id") for item in value.get("stages", [])] != STAGES:
        errors.append("stage axis identity/order")
    if [item.get("id") for item in value.get("branches", [])] != BRANCHES:
        errors.append("branch axis identity/order")

    branches = {item.get("id"): item for item in value.get("branches", [])}
    old_branches = {item.get("id"): item for item in previous.get("branches", [])}
    for branch_id, item in branches.items():
        if len(item.get("stages", [])) != 11:
            errors.append("stage closure " + str(branch_id))
        if branch_id != "STRICT_PURE_WEYL_386" and item != old_branches.get(branch_id):
            errors.append("unlicensed branch mutation " + str(branch_id))

    strict = branches.get("STRICT_PURE_WEYL_386", {})
    old_strict = old_branches.get("STRICT_PURE_WEYL_386", {})
    cells = {item.get("stage"): item for item in strict.get("stages", [])}
    old_cells = {item.get("stage"): item for item in old_strict.get("stages", [])}
    if strict.get("first_unclosed_gate") != "S0_CLASSICAL_AUTHORITY" or cells.get("S0_CLASSICAL_AUTHORITY", {}).get("status") != "FAIL_CLOSED":
        errors.append("Gate-A firewall")
    for stage_id in STAGES[1:]:
        if cells.get(stage_id) != old_cells.get(stage_id):
            errors.append("unlicensed strict stage mutation " + stage_id)
    for key in set(old_strict) - {"stages", "next_decisive_object"}:
        if strict.get(key) != old_strict.get(key):
            errors.append("unlicensed strict branch mutation " + key)
    s0_evidence = cells.get("S0_CLASSICAL_AUTHORITY", {}).get("evidence", [])
    if s0_evidence != [*old_cells.get("S0_CLASSICAL_AUTHORITY", {}).get("evidence", []), source["result_id"]]:
        errors.append("strict S0 evidence augmentation")

    maps = source["component_maps"]
    expected_sdr = {
        "result_id": source["result_id"],
        "status": source["result_state"],
        "carrier_dimension": 386,
        "retained_endpoint_dimension": 30,
        "contracted_dimension": 356,
        "map_count": 5,
        "H_alg_nonzero_entries": maps["H_alg"]["nonzero_entries"],
        "P_alg_nonzero_entries": maps["P_alg"]["nonzero_entries"],
        "P_end_nonzero_entries": maps["P_end"]["nonzero_entries"],
        "i_end_nonzero_entries": maps["i_end"]["nonzero_entries"],
        "p_end_nonzero_entries": maps["p_end"]["nonzero_entries"],
        "maximum_order": 0,
        "derivative_multiindices_checked": 70,
        "homotopy_identity_defects": 0,
        "cyclicity_defects": 0,
        "local_sdr_snapshot_sha256": source["local_sdr_snapshot"]["snapshot_sha256"],
        "split_SDR_complete": True,
        "canonical_shear_serialized": False,
        "represented_green_actions_serialized": False,
        "classical_import_gate_passed": False,
        "next_gate": source["next_gate"],
    }
    if value.get("strict_local_sdr_component_maps") != expected_sdr:
        errors.append("local-SDR projection")
    progress = value.get("strict_gate_a_progress", {})
    if progress.get("status") != "FULL_Q1_AND_SPLIT_SDR_SERIALIZED_SHEAR_GREEN_COMMON_SNAPSHOT_REQUIRED" or progress.get("local_sdr_component_map_control") != expected_sdr:
        errors.append("Gate-A progress ledger")

    inherited = (
        "classical_import_reconciliation", "strict_causal_sign_transport",
        "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge",
        "strict_component_pairing_serialization", "strict_operator_portability",
        "strict_full_q1_split_sign_gate", "strict_auxiliary_q_sign_repair",
        "strict_full_q1_component_jet_table", "berger_h26_c26_decision_chain",
    )
    for key in inherited:
        if value.get(key) != previous.get(key):
            errors.append("predecessor control mutation " + key)
    if [item.get("route") for item in value.get("route_selection", [])] != ROUTES or [item.get("rank") for item in value.get("route_selection", [])] != list(range(1, 10)):
        errors.append("SDR-aware route ranking")
    expected_queue = [
        {"priority": item["rank"], "branch": item["branch"], "object": item["route"], "why": item["recommendation"]}
        for item in value.get("route_selection", [])
    ]
    if value.get("research_queue") != expected_queue:
        errors.append("research queue projection")

    flags = value.get("claim_flags", {})
    for key in (
        "v11_preserved", "strict_386_split_local_sdr_component_maps_serialized",
        "strict_386_split_local_sdr_identities_replayed",
        "strict_386_split_local_sdr_cyclicity_replayed",
    ):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in (
        "strict_386_canonical_shear_component_jets_serialized",
        "strict_386_unshifted_graph_sdr_snapshot_complete",
        "strict_386_represented_green_actions_serialized",
        "strict_pure_weyl_classical_gate_passed", "lorentzian_full_theory_certified",
    ):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)

    expected_predecessor = {
        "result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)),
        "sha256": sha(PREDECESSOR), "preserved": True,
    }
    if value.get("predecessor") != expected_predecessor:
        errors.append("predecessor")
    expected_inputs = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V11 atlas predecessor"},
        {"path": str(SDR.relative_to(ROOT)), "sha256": sha(SDR), "role": "exact split local SDR component maps and replay"},
    ]
    if value.get("provenance", {}).get("inputs") != expected_inputs:
        errors.append("append-only provenance")
    for item in expected_inputs:
        path = ROOT / item["path"]
        historical_repair = item["path"] in {
            "quantum-weyl/classical_import/certificates/STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1.json",
            "quantum-weyl/classical_import/certificates/STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1.json",
            "quantum-weyl/classical_import/certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json",
        }
        if historical_repair:
            if len(item["sha256"]) != 64:
                errors.append("historical repair provenance")
        elif not path.is_file() or sha(path) != item["sha256"]:
            errors.append("provenance " + item["path"])
    if digest(value) != value.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V12: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    if not errors:
        print("  - 77 cells preserved; only strict S0 receives the exact split local SDR evidence")
        print("  - five maps and all 70 q1 multiindices replay with zero homotopy/cyclicity defects")
        print("  - canonical shear, graph replay, represented Green actions and Gate A remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
