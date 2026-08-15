#!/usr/bin/env python3
"""Independent structure and scope checker for completion-atlas V4."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V4.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V3.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V5_RECONCILIATION.json"
CYCLIC = ROOT / "quantum-weyl/classical_import/certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
TRANSPORT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_CAUSAL_SIGN_TRANSPORT_V1.json"
STAGES = ["S0_CLASSICAL_AUTHORITY", "S1_OFF_SHELL_BV", "S2_CAUSAL_GREEN", "S3_NONLINEAR_CARTAN", "S4_HADAMARD_CCR", "S5_BRST_WARD", "S6_PHYSICAL_POSITIVITY", "S7_RENORMALIZED_PRODUCTS", "S8_QME", "S9_RESIDUAL_TRANSFER", "S10_LORENTZIAN_CERTIFIED"]
BRANCHES = ["STRICT_PURE_WEYL_386", "PURE_WEYL_BACH_FLAT_RANK310", "EINSTEIN_NARIAI_KS", "BERGER_POSITIVE_CLOCK_54", "VACUUM_CYLINDER_REDUCED", "TAU_ADIC_COMPENSATOR", "COMPLEX_COMPENSATOR_CHANGED_ACTION"]
CHAIN = ["STATIONARY_NORMALIZATION_EMPTY", "REPRESENTATIVE_NOT_SERIALIZED", "FROZEN_CAUCHY_GRAPH_EMPTY", "SIX_ROW_CYCLIC_EMPTY", "FREE_MODULE_BOUND_104", "CANONICAL_CONE_EMPTY", "CANONICAL_TOWER_REGENERATES", "FULLY_MIXED_CONE_SDR_EMPTY", "RANK_ONLY_FEASIBLE", "FIXED_NONCONE_EVOLUTION_EMPTY", "MIXED_CORRECTION_RANK_MISS"]
ROUTES = ["STRICT_386_ENDPOINT_CONTENT_BRIDGE", "STRICT_386_FULL_PAIRING_D", "STRICT_386_Q2_GREEN_COMPATIBILITY", "DIRECT_SPACETIME_Q26_HADAMARD", "BACH_FLAT_NONLINEAR_CARTAN"]
FALSE_FLAGS = {"general_noncone_104_row_no_go", "berger_brst_hadamard_state_constructed", "strict_pure_weyl_classical_gate_passed", "strict_full_support_local_residual_sdr_constructed", "strict_386_common_bytes_identified", "strict_full_386_pairing_serialized", "strict_386_q2_green_compatibility_certified", "renormalized_lorentzian_products_constructed", "strict_pure_weyl_qme_restored", "residual_quantum_transfer_authorized", "lorentzian_full_theory_certified"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = ("stages", "branches", "frontier_summary", "classical_import_reconciliation", "strict_gate_a_progress", "strict_causal_sign_transport", "berger_h26_c26_decision_chain", "route_selection", "research_queue")
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, int]]:
    value = json.loads(RESULT.read_text()) if value is None else value
    previous = json.loads(PREDECESSOR.read_text())
    gate = json.loads(GATE.read_text())
    cyclic = json.loads(CYCLIC.read_text())
    transport = json.loads(TRANSPORT.read_text())
    errors: list[str] = []
    if [item.get("id") for item in value.get("stages", [])] != STAGES:
        errors.append("stage identity/order")
    if [item.get("id") for item in value.get("branches", [])] != BRANCHES:
        errors.append("branch identity/order")
    routes = {item.get("id"): item for item in value.get("branches", [])}
    previous_routes = {item.get("id"): item for item in previous.get("branches", [])}
    for route_id, branch in routes.items():
        if [item.get("stage") for item in branch.get("stages", [])] != STAGES:
            errors.append("stage closure " + str(route_id))
        if route_id != "STRICT_PURE_WEYL_386" and branch != previous_routes.get(route_id):
            errors.append("unlicensed branch mutation " + str(route_id))
    strict = routes.get("STRICT_PURE_WEYL_386", {})
    old_strict = previous_routes.get("STRICT_PURE_WEYL_386", {})
    strict_cells = {item.get("stage"): item for item in strict.get("stages", [])}
    old_cells = {item.get("stage"): item for item in old_strict.get("stages", [])}
    if strict.get("first_unclosed_gate") != "S0_CLASSICAL_AUTHORITY" or strict_cells.get("S0_CLASSICAL_AUTHORITY", {}).get("status") != "FAIL_CLOSED":
        errors.append("strict Gate-A firewall")
    for stage_id in STAGES:
        if stage_id not in {"S0_CLASSICAL_AUTHORITY", "S2_CAUSAL_GREEN"} and strict_cells.get(stage_id) != old_cells.get(stage_id):
            errors.append("unlicensed strict-cell mutation " + stage_id)
    s0_text = json.dumps(strict_cells.get("S0_CLASSICAL_AUTHORITY", {})).lower()
    s2_text = json.dumps(strict_cells.get("S2_CAUSAL_GREEN", {})).lower()
    if not all(token in s0_text for token in ("rank-30", "ten scoped exports", "seven scoped checks", "zero common")):
        errors.append("minimal/full-carrier boundary")
    if not all(token in s2_text for token in ("381-plus/5-minus", "does not invalidate", "common-byte", "q2/d")):
        errors.append("causal convention-stability boundary")

    if value.get("berger_h26_c26_decision_chain") != previous.get("berger_h26_c26_decision_chain") or [item.get("classification") for item in value.get("berger_h26_c26_decision_chain", [])] != CHAIN:
        errors.append("Berger decision-chain preservation")
    if [item.get("rank") for item in value.get("route_selection", [])] != list(range(1, 6)) or [item.get("route") for item in value.get("route_selection", [])] != ROUTES:
        errors.append("updated route identity/order")

    reconciliation = value.get("classical_import_reconciliation", {})
    expected_reconciliation = {
        "result_id": gate["result_id"],
        "gate": "FAIL_CLOSED",
        "claim_state": "CLASSICAL_IMPORT_MINIMAL_Q1_Q2_PAIRING_CYCLIC_REPAIRED_D_FULL_CARRIER_OPEN",
        "standalone_history_replay": "VERIFIED_BY_EXACT_CONTENT",
        "open_payload_families": [item["id"] for item in gate["minimal_missing_bundle"]],
        "missing_portable_objects": 0,
        "receiver_verified_scoped_exports": 10,
        "receiver_verified_scoped_checks": 7,
        "accepted_common_snapshot_hashes": 0,
        "rule": gate["gate_disposition"]["rule"],
    }
    if reconciliation != expected_reconciliation:
        errors.append("Gate-A V5 reconciliation")
    progress = value.get("strict_gate_a_progress", {})
    minimal = progress.get("minimal_cyclic_control", {})
    if progress.get("status") != "MINIMAL_CYCLICITY_AND_CAUSAL_CONVENTION_STABILITY_CERTIFIED_FULL_CARRIER_OPEN":
        errors.append("strict progress state")
    if progress.get("evidence") != [gate["result_id"], cyclic["result_id"], transport["result_id"]]:
        errors.append("strict progress evidence")
    if {key: minimal.get(key) for key in ("basis_dimension", "pairing_rank", "source_defects", "expanded_coefficients", "translated_defects")} != {"basis_dimension": 30, "pairing_rank": 30, "source_defects": 540, "expanded_coefficients": 932, "translated_defects": 0}:
        errors.append("minimal cyclic counts")
    if progress.get("finite_control") != previous.get("strict_gate_a_progress", {}).get("finite_control"):
        errors.append("finite SDR control not preserved")

    causal = value.get("strict_causal_sign_transport", {})
    expected_causal = {
        "result_id": transport["result_id"],
        "status": transport["result_state"],
        "endpoint_dimension": 30,
        "algebraic_complement_dimension": 356,
        "full_dimension": 386,
        "positive_signs": 381,
        "negative_signs": 5,
        "causal_stage_preserved": True,
        "common_bytes_identified": False,
        "nonlinear_stage_preserved": False,
        "fixed_carrier_transport_base": "PRA",
        "analytic_causal_weakest_base": "NOT_ESTABLISHED",
        "next_gate": transport["next_gate"],
    }
    if causal != expected_causal:
        errors.append("strict causal sign transport")

    flags = value.get("claim_flags", {})
    if any(flags.get(key) is not False for key in FALSE_FLAGS):
        errors.append("claim promotion")
    for key in ("v3_preserved", "strict_minimal_pairing_cyclicity_certified", "strict_386_sign_transport_certified", "strict_386_causal_stage_preserved_under_sign_transport"):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)

    predecessor = value.get("predecessor", {})
    if predecessor != {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True}:
        errors.append("V3 predecessor")
    expected_inputs = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V3 atlas predecessor"},
        {"path": str(GATE.relative_to(ROOT)), "sha256": sha(GATE), "role": "Gate-A V5 minimal cyclicity reconciliation"},
        {"path": str(CYCLIC.relative_to(ROOT)), "sha256": sha(CYCLIC), "role": "exact canonical minimal pairing and cyclic sign repair"},
        {"path": str(TRANSPORT.relative_to(ROOT)), "sha256": sha(TRANSPORT), "role": "strict 386-row causal convention-stability theorem"},
    ]
    if value.get("provenance", {}).get("inputs") != expected_inputs:
        errors.append("append-only provenance")
    evidence_ids = {Path(item["path"]).stem for item in expected_inputs}
    evidence_ids.add("pure-weyl-full-prolonged-green-homotopy-assembly-v1")
    for branch in routes.values():
        for item in branch.get("stages", []):
            if not set(item.get("evidence", [])).issubset(evidence_ids):
                errors.append("unresolved cell evidence")
    for item in expected_inputs:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            errors.append("provenance " + item["path"])
    if digest(value) != value.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {
        "branches": len(routes),
        "stages": len(STAGES),
        "cells": sum(len(item.get("stages", [])) for item in routes.values()),
        "chain": len(value.get("berger_h26_c26_decision_chain", [])),
        "routes": len(value.get("route_selection", [])),
        "inputs": len(expected_inputs),
    }


def main() -> int:
    errors, counts = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V4: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print(f"  - {counts['branches']} branches x {counts['stages']} stages = {counts['cells']} classified gates")
        print(f"  - Gate V5 and 386-row sign transport reconciled across {counts['inputs']} pinned inputs")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
