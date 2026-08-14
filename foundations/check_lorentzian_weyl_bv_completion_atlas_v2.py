#!/usr/bin/env python3
"""Independent scope and structure checker for completion-atlas V2."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V2.json"
STAGES = ["S0_CLASSICAL_AUTHORITY", "S1_OFF_SHELL_BV", "S2_CAUSAL_GREEN", "S3_NONLINEAR_CARTAN", "S4_HADAMARD_CCR", "S5_BRST_WARD", "S6_PHYSICAL_POSITIVITY", "S7_RENORMALIZED_PRODUCTS", "S8_QME", "S9_RESIDUAL_TRANSFER", "S10_LORENTZIAN_CERTIFIED"]
BRANCHES = ["STRICT_PURE_WEYL_386", "PURE_WEYL_BACH_FLAT_RANK310", "EINSTEIN_NARIAI_KS", "BERGER_POSITIVE_CLOCK_54", "VACUUM_CYLINDER_REDUCED", "TAU_ADIC_COMPENSATOR", "COMPLEX_COMPENSATOR_CHANGED_ACTION"]
CHAIN = ["STATIONARY_NORMALIZATION_EMPTY", "REPRESENTATIVE_NOT_SERIALIZED", "FROZEN_CAUCHY_GRAPH_EMPTY", "SIX_ROW_CYCLIC_EMPTY", "FREE_MODULE_BOUND_104", "CANONICAL_CONE_EMPTY", "CANONICAL_TOWER_REGENERATES", "FULLY_MIXED_CONE_SDR_EMPTY", "RANK_ONLY_FEASIBLE", "FIXED_NONCONE_EVOLUTION_EMPTY", "MIXED_CORRECTION_RANK_MISS"]
ROUTES = ["STRICT_RESIDUAL_SDR", "DIRECT_SPACETIME_Q26_HADAMARD", "STRICT_SUPPORT_LOCAL_Q2_D", "BACH_FLAT_NONLINEAR_CARTAN", "GENERAL_NONCONE_104_COMPLETION"]
FALSE_FLAGS = {"general_noncone_104_row_no_go", "berger_brst_hadamard_state_constructed", "strict_pure_weyl_classical_gate_passed", "renormalized_lorentzian_products_constructed", "strict_pure_weyl_qme_restored", "residual_quantum_transfer_authorized", "lorentzian_full_theory_certified"}


def digest(value: dict[str, Any]) -> str:
    keys = ("stages", "branches", "frontier_summary", "classical_import_reconciliation", "berger_h26_c26_decision_chain", "route_selection", "research_queue")
    payload = {key: value[key] for key in keys}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, int]]:
    value = json.loads(RESULT.read_text()) if value is None else value
    errors: list[str] = []
    if [item.get("id") for item in value.get("stages", [])] != STAGES:
        errors.append("stage identity/order")
    if [item.get("id") for item in value.get("branches", [])] != BRANCHES:
        errors.append("branch identity/order")
    routes = {item.get("id"): item for item in value.get("branches", [])}
    for route_id, route in routes.items():
        if [item.get("stage") for item in route.get("stages", [])] != STAGES:
            errors.append("stage closure " + str(route_id))
    strict = routes.get("STRICT_PURE_WEYL_386", {})
    berger = routes.get("BERGER_POSITIVE_CLOCK_54", {})
    strict_cells = {item["stage"]: item for item in strict.get("stages", [])}
    berger_cells = {item["stage"]: item for item in berger.get("stages", [])}
    if strict.get("first_unclosed_gate") != "S0_CLASSICAL_AUTHORITY" or strict_cells.get("S0_CLASSICAL_AUTHORITY", {}).get("status") != "FAIL_CLOSED":
        errors.append("strict Gate-A firewall")
    if berger.get("first_unclosed_gate") != "S4_HADAMARD_CCR":
        errors.append("Berger first gate")
    if berger_cells.get("S4_HADAMARD_CCR", {}).get("status") != "PARTIAL_CERTIFIED" or berger_cells.get("S5_BRST_WARD", {}).get("status") != "OBSTRUCTED_SCOPED":
        errors.append("Berger Hadamard/Ward status")
    if "complete general non-cone" not in berger_cells.get("S5_BRST_WARD", {}).get("boundary", ""):
        errors.append("general non-cone scope firewall")
    decision = value.get("berger_h26_c26_decision_chain", [])
    if [item.get("sequence") for item in decision] != list(range(1, 12)) or [item.get("classification") for item in decision] != CHAIN:
        errors.append("Berger decision chain")
    feasible = next((item for item in decision if item.get("classification") == "RANK_ONLY_FEASIBLE"), {})
    if "not a PBW operator" not in feasible.get("does_not_imply", ""):
        errors.append("rank-feasibility control boundary")
    if [item.get("rank") for item in value.get("route_selection", [])] != list(range(1, 6)) or [item.get("route") for item in value.get("route_selection", [])] != ROUTES:
        errors.append("route selection identity/order")
    reconciliation = value.get("classical_import_reconciliation", {})
    if reconciliation.get("gate") != "FAIL_CLOSED" or reconciliation.get("standalone_history_replay") != "VERIFIED_BY_EXACT_CONTENT" or len(reconciliation.get("missing_payload_families", [])) != 6:
        errors.append("Gate-A V2 reconciliation")
    flags = value.get("claim_flags", {})
    if any(flags.get(key) is not False for key in FALSE_FLAGS):
        errors.append("claim promotion")
    if flags.get("berger_h26_c26_decision_chain_classified") is not True or flags.get("v1_preserved") is not True:
        errors.append("positive classification flags")
    predecessor = value.get("predecessor", {})
    predecessor_path = ROOT / predecessor.get("path", "")
    if predecessor.get("preserved") is not True or not predecessor_path.is_file() or sha(predecessor_path) != predecessor.get("sha256"):
        errors.append("V1 predecessor")
    evidence_ids = {Path(item.get("path", "")).stem for item in value.get("provenance", {}).get("inputs", [])}
    evidence_ids.add("pure-weyl-full-prolonged-green-homotopy-assembly-v1")
    for route in routes.values():
        for item in route.get("stages", []):
            if not set(item.get("evidence", [])).issubset(evidence_ids):
                errors.append("unresolved cell evidence")
    for item in decision:
        if item.get("evidence") not in evidence_ids:
            errors.append("unresolved decision evidence")
    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            errors.append("provenance " + item.get("path", ""))
    if digest(value) != value.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {"branches": len(routes), "stages": len(STAGES), "cells": sum(len(item.get("stages", [])) for item in routes.values()), "chain": len(decision), "inputs": len(value.get("provenance", {}).get("inputs", []))}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors, counts = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V2: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print(f"  - {counts['branches']} branches x {counts['stages']} stages = {counts['cells']} classified gates")
        print(f"  - {counts['chain']}-step Berger decision chain and {counts['inputs']} pinned inputs")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
