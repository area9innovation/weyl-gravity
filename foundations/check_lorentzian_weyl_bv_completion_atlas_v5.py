#!/usr/bin/env python3
"""Independent structure and claim-boundary checker for completion atlas V5."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V5.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V4.json"
BRIDGE = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.json"
WITNESS = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_WITNESS_V1.json"
STAGES = ["S0_CLASSICAL_AUTHORITY", "S1_OFF_SHELL_BV", "S2_CAUSAL_GREEN", "S3_NONLINEAR_CARTAN", "S4_HADAMARD_CCR", "S5_BRST_WARD", "S6_PHYSICAL_POSITIVITY", "S7_RENORMALIZED_PRODUCTS", "S8_QME", "S9_RESIDUAL_TRANSFER", "S10_LORENTZIAN_CERTIFIED"]
BRANCHES = ["STRICT_PURE_WEYL_386", "PURE_WEYL_BACH_FLAT_RANK310", "EINSTEIN_NARIAI_KS", "BERGER_POSITIVE_CLOCK_54", "VACUUM_CYLINDER_REDUCED", "TAU_ADIC_COMPENSATOR", "COMPLEX_COMPENSATOR_CHANGED_ACTION"]
ROUTES = ["STRICT_386_PAIRING_SUSPENSION_BRIDGE", "STRICT_386_FULL_PAIRING_D", "STRICT_386_Q2_GREEN_COMPATIBILITY", "DIRECT_SPACETIME_Q26_HADAMARD", "BACH_FLAT_NONLINEAR_CARTAN"]
FALSE_FLAGS = {
    "general_noncone_104_row_no_go", "berger_brst_hadamard_state_constructed",
    "strict_pure_weyl_classical_gate_passed", "strict_full_support_local_residual_sdr_constructed",
    "strict_386_pairing_suspension_bridge_certified", "strict_386_common_bytes_identified",
    "strict_full_386_pairing_serialized", "strict_386_q2_green_compatibility_certified",
    "renormalized_lorentzian_products_constructed", "strict_pure_weyl_qme_restored",
    "residual_quantum_transfer_authorized", "lorentzian_full_theory_certified",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_causal_sign_transport",
        "strict_endpoint_q1_content_bridge", "berger_h26_c26_decision_chain",
        "route_selection", "research_queue",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, int]]:
    value = json.loads(RESULT.read_text()) if value is None else value
    previous = json.loads(PREDECESSOR.read_text())
    bridge = json.loads(BRIDGE.read_text())
    errors: list[str] = []
    if value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v5" or value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V5":
        errors.append("identity")
    if [item.get("id") for item in value.get("stages", [])] != STAGES:
        errors.append("stage identity/order")
    if [item.get("id") for item in value.get("branches", [])] != BRANCHES:
        errors.append("branch identity/order")
    routes = {item.get("id"): item for item in value.get("branches", [])}
    old_routes = {item.get("id"): item for item in previous.get("branches", [])}
    for branch_id, branch in routes.items():
        if [item.get("stage") for item in branch.get("stages", [])] != STAGES:
            errors.append("stage closure " + str(branch_id))
        if branch_id != "STRICT_PURE_WEYL_386" and branch != old_routes.get(branch_id):
            errors.append("unlicensed branch mutation " + str(branch_id))
    strict = routes.get("STRICT_PURE_WEYL_386", {})
    old_strict = old_routes.get("STRICT_PURE_WEYL_386", {})
    cells = {item.get("stage"): item for item in strict.get("stages", [])}
    old_cells = {item.get("stage"): item for item in old_strict.get("stages", [])}
    if strict.get("first_unclosed_gate") != "S0_CLASSICAL_AUTHORITY" or cells.get("S0_CLASSICAL_AUTHORITY", {}).get("status") != "FAIL_CLOSED":
        errors.append("Gate-A firewall")
    for stage_id in STAGES:
        if stage_id not in {"S0_CLASSICAL_AUTHORITY", "S2_CAUSAL_GREEN"} and cells.get(stage_id) != old_cells.get(stage_id):
            errors.append("unlicensed strict stage mutation " + stage_id)
    s0 = json.dumps(cells.get("S0_CLASSICAL_AUTHORITY", {})).lower()
    s2 = json.dumps(cells.get("S2_CAUSAL_GREEN", {})).lower()
    if not all(token in s0 for token in ("5/5", "700/700", "5/5", "full 386-row pairing")):
        errors.append("endpoint equality projection")
    if not all(token in s2 for token in ("619", "-i_5", "q2/d")):
        errors.append("causal pairing boundary")

    source = bridge["coefficientwise_identification"]
    pairing = bridge["pairing_disposition"]
    projected = value.get("strict_endpoint_q1_content_bridge", {})
    expected_projected = {
        "result_id": bridge["result_id"], "status": bridge["result_state"],
        "endpoint_dimension": 30, "full_causal_dimension": 386,
        "arrow_tables_matching": source["arrow_table_counts"]["total"],
        "bach_columns_matching": source["gate_bach_columns_matching"],
        "triangular_equations": bridge["basis_bridge"]["triangular_equations"],
        "common_nonzero_coefficients": source["common_nonzero_coefficients"],
        "common_q1_sha256": source["common_q1_sha256"],
        "field_pairing_canonical": True, "original_ghost_pairing_canonical": True,
        "transported_ghost_pairing_canonical": False,
        "transported_ghost_pairing_negative_canonical": True,
        "finite_bridge_base": "PRA", "analytic_causal_weakest_base": "NOT_ESTABLISHED",
        "next_gate": bridge["next_gate"],
    }
    if projected != expected_projected:
        errors.append("endpoint bridge projection")
    if source["arrow_table_counts"]["total"] != 80 or source["gate_bach_columns_matching"] != 700 or source["common_nonzero_coefficients"] != 619:
        errors.append("source coefficient counts")
    if {key: pairing[key] for key in (
        "field_pullback_equals_gate_canonical", "original_endpoint_ghost_pullback_equals_gate_canonical",
        "simultaneously_transported_causal_ghost_pullback_equals_gate_canonical",
        "simultaneously_transported_causal_ghost_pullback_equals_negative_gate_canonical",
    )} != {
        "field_pullback_equals_gate_canonical": True,
        "original_endpoint_ghost_pullback_equals_gate_canonical": True,
        "simultaneously_transported_causal_ghost_pullback_equals_gate_canonical": False,
        "simultaneously_transported_causal_ghost_pullback_equals_negative_gate_canonical": True,
    }:
        errors.append("source pairing sign")
    progress = value.get("strict_gate_a_progress", {})
    if progress.get("status") != "MINIMAL_Q1_ENDPOINT_CONTENT_IDENTIFIED_FULL_PAIRED_CARRIER_OPEN":
        errors.append("strict progress state")
    control = progress.get("endpoint_q1_control", {})
    if control != {"dimension": 30, "arrow_tables_matching": 80, "bach_columns_matching": 700, "common_nonzero_coefficients": 619, "common_q1_sha256": source["common_q1_sha256"], "full_pairing_open": True}:
        errors.append("endpoint progress ledger")
    if value.get("classical_import_reconciliation") != previous.get("classical_import_reconciliation") or value.get("strict_causal_sign_transport") != previous.get("strict_causal_sign_transport"):
        errors.append("predecessor gate/transport mutation")
    if value.get("berger_h26_c26_decision_chain") != previous.get("berger_h26_c26_decision_chain"):
        errors.append("Berger chain mutation")
    if [item.get("rank") for item in value.get("route_selection", [])] != [1, 2, 3, 4, 5] or [item.get("route") for item in value.get("route_selection", [])] != ROUTES:
        errors.append("route ranking")
    flags = value.get("claim_flags", {})
    if any(flags.get(key) is not False for key in FALSE_FLAGS):
        errors.append("claim promotion")
    for key in ("v4_preserved", "strict_386_endpoint_q1_content_identified", "strict_386_all_700_bach_columns_match"):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    predecessor = value.get("predecessor")
    if predecessor != {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True}:
        errors.append("predecessor")
    expected_inputs = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V4 atlas predecessor"},
        {"path": str(BRIDGE.relative_to(ROOT)), "sha256": sha(BRIDGE), "role": "exact strict thirty-row endpoint q1 content bridge"},
        {"path": str(WITNESS.relative_to(ROOT)), "sha256": sha(WITNESS), "role": "700-column coordinate-to-covariant proof witness"},
    ]
    if value.get("provenance", {}).get("inputs") != expected_inputs:
        errors.append("append-only provenance")
    for item in expected_inputs:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            errors.append("provenance " + item["path"])
    if digest(value) != value.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {
        "branches": len(routes), "stages": len(STAGES),
        "cells": sum(len(item.get("stages", [])) for item in routes.values()),
        "tables": projected.get("arrow_tables_matching", 0),
        "columns": projected.get("bach_columns_matching", 0),
        "inputs": len(expected_inputs),
    }


def main() -> int:
    errors, counts = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V5: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print(f"  - {counts['branches']} branches x {counts['stages']} stages = {counts['cells']} classified gates")
        print(f"  - {counts['tables']}/80 q1 tables and {counts['columns']}/700 Bach columns linked to the causal endpoint")
        print("  - full pairing, q2/D, Hadamard and QME claims remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
