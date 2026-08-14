#!/usr/bin/env python3
"""Independent structural and boundary checker for the completion atlas."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V1.json"
STAGES = [
    "S0_CLASSICAL_AUTHORITY", "S1_OFF_SHELL_BV", "S2_CAUSAL_GREEN", "S3_NONLINEAR_CARTAN",
    "S4_HADAMARD_CCR", "S5_BRST_WARD", "S6_PHYSICAL_POSITIVITY", "S7_RENORMALIZED_PRODUCTS",
    "S8_QME", "S9_RESIDUAL_TRANSFER", "S10_LORENTZIAN_CERTIFIED",
]
BRANCHES = [
    "STRICT_PURE_WEYL_386", "PURE_WEYL_BACH_FLAT_RANK310", "EINSTEIN_NARIAI_KS",
    "BERGER_POSITIVE_CLOCK_54", "VACUUM_CYLINDER_REDUCED", "TAU_ADIC_COMPENSATOR",
    "COMPLEX_COMPENSATOR_CHANGED_ACTION",
]
STATUSES = {"CERTIFIED", "SCOPED_CERTIFIED", "PARTIAL_CERTIFIED", "CONDITIONAL", "OPEN_SEEDED", "OBSTRUCTED_SCOPED", "FAIL_CLOSED", "FORBIDDEN_TRANSFER", "NOT_APPLICABLE"}
FALSE_FLAGS = {
    "berger_brst_hadamard_state_constructed", "strict_pure_weyl_qme_restored",
    "renormalized_lorentzian_products_constructed", "residual_quantum_transfer_authorized",
    "lorentzian_full_theory_certified",
}


def digest(value: dict[str, Any]) -> str:
    payload = {key: value[key] for key in ("status_vocabulary", "stages", "branches", "frontier_summary", "classical_import_reconciliation", "research_queue")}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    value = json.loads(RESULT.read_text()) if value is None else value
    errors: list[str] = []
    if [item.get("id") for item in value.get("stages", [])] != STAGES:
        errors.append("stage identity/order")
    if [item.get("id") for item in value.get("branches", [])] != BRANCHES:
        errors.append("branch identity/order")
    if {item.get("id") for item in value.get("status_vocabulary", [])} != STATUSES:
        errors.append("status vocabulary")
    evidence_ids = {Path(item["path"]).stem for item in value.get("provenance", {}).get("inputs", [])}
    evidence_ids.add("pure-weyl-full-prolonged-green-homotopy-assembly-v1")
    for route in value.get("branches", []):
        cells = route.get("stages", [])
        if [item.get("stage") for item in cells] != STAGES:
            errors.append("stage closure " + str(route.get("id")))
            continue
        if route.get("first_unclosed_gate") not in STAGES:
            errors.append("first gate " + str(route.get("id")))
        for item in cells:
            if item.get("status") not in STATUSES:
                errors.append("unknown status")
            if not item.get("statement") or not item.get("boundary"):
                errors.append("empty cell boundary")
            if not set(item.get("evidence", [])).issubset(evidence_ids):
                errors.append("unresolved evidence id " + str(item.get("evidence")))
    by_id = {route["id"]: route for route in value.get("branches", [])}
    expected = {
        ("STRICT_PURE_WEYL_386", "S0_CLASSICAL_AUTHORITY"): "FAIL_CLOSED",
        ("STRICT_PURE_WEYL_386", "S2_CAUSAL_GREEN"): "SCOPED_CERTIFIED",
        ("STRICT_PURE_WEYL_386", "S8_QME"): "OBSTRUCTED_SCOPED",
        ("BERGER_POSITIVE_CLOCK_54", "S2_CAUSAL_GREEN"): "CERTIFIED",
        ("BERGER_POSITIVE_CLOCK_54", "S3_NONLINEAR_CARTAN"): "SCOPED_CERTIFIED",
        ("BERGER_POSITIVE_CLOCK_54", "S4_HADAMARD_CCR"): "PARTIAL_CERTIFIED",
        ("BERGER_POSITIVE_CLOCK_54", "S5_BRST_WARD"): "OPEN_SEEDED",
        ("VACUUM_CYLINDER_REDUCED", "S4_HADAMARD_CCR"): "SCOPED_CERTIFIED",
        ("TAU_ADIC_COMPENSATOR", "S2_CAUSAL_GREEN"): "OBSTRUCTED_SCOPED",
        ("TAU_ADIC_COMPENSATOR", "S8_QME"): "CONDITIONAL",
        ("COMPLEX_COMPENSATOR_CHANGED_ACTION", "S2_CAUSAL_GREEN"): "CERTIFIED",
    }
    for (route_id, stage_id), status in expected.items():
        actual = {cell["stage"]: cell["status"] for cell in by_id.get(route_id, {}).get("stages", [])}.get(stage_id)
        if actual != status:
            errors.append(f"boundary status {route_id}/{stage_id}")
    if by_id.get("BERGER_POSITIVE_CLOCK_54", {}).get("first_unclosed_gate") != "S5_BRST_WARD":
        errors.append("Berger frontier")
    if by_id.get("STRICT_PURE_WEYL_386", {}).get("first_unclosed_gate") != "S0_CLASSICAL_AUTHORITY":
        errors.append("strict frontier")
    reconciliation = value.get("classical_import_reconciliation", {})
    if reconciliation.get("historical_gate") != "FAIL_CLOSED" or reconciliation.get("current_disposition") != "PARTIALLY_REPAIRED_REPLACEMENT_FREEZE_CERTIFICATE_ABSENT":
        errors.append("classical import reconciliation")
    flags = value.get("claim_flags", {})
    for key in FALSE_FLAGS:
        if flags.get(key) is not False:
            errors.append("promoted flag " + key)
    if flags.get("strict_pure_weyl_scoped_full_causal_homotopy_recorded") is not True:
        errors.append("strict causal result omitted")
    if flags.get("berger_arity_three_d_cartan_recorded") is not True:
        errors.append("Berger arity-three result omitted")
    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append("provenance " + item.get("path", ""))
    if digest(value) != value.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {"branches": len(value.get("branches", [])), "stages": len(STAGES), "cells": sum(len(route.get("stages", [])) for route in value.get("branches", []))}


def main() -> int:
    errors, counts = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print(f"  - {counts['branches']} branches x {counts['stages']} stages = {counts['cells']} classified gates")
        print("  - evidence hashes, lifecycle firewalls and first-gate frontiers verified")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
