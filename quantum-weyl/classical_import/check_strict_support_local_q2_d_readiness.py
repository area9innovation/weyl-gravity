#!/usr/bin/env python3
"""Independent fail-closed checker for strict q2/D readiness."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / "quantum-weyl/classical_import"
RESULT = DIRECTORY / "certificates/STRICT_SUPPORT_LOCAL_Q2_D_READINESS_V1.json"
SOURCE = ROOT / "bridge/certificates/CYLINDER_ARBITRARY_SUPPORT_FULL_BV_Q2_TIME_SLICE_CHAIN_MAP_OBSTRUCTION_V1.json"
CONTRACT = DIRECTORY / "certificates/SUPPORT_LOCAL_Q2_EXPORT_CONTRACT.json"
GATE = DIRECTORY / "certificates/CLASSICAL_IMPORT_GATE_V3_RECONCILIATION.json"
SYMBOLS = ("c_mu", "omega", "h_mu_nu", "hstar_mu_nu", "cstar_mu", "omegastar")
PROOFS = ("q1_squared_zero", "q1_q2_arity_two_nilpotency", "q2_koszul_symmetry", "q2_row_completeness", "D_q1_commutator_zero", "D_q2_derivation", "BV_cyclicity_q2")
FALSE_FLAGS = {"STRICT_SUPPORT_LOCAL_Q2_COMPONENT_PAYLOAD_CERTIFIED", "STRICT_FULL_LOCAL_D_ACTION_CERTIFIED", "STRICT_Q1_Q2_IDENTITY_REPLAYED", "STRICT_D_Q2_DERIVATION_REPLAYED", "STRICT_BV_CYCLICITY_Q2_REPLAYED", "ALL_ENERGY_SUPPORT_LOCAL_Q2_OBSTRUCTED", "CLASSICAL_IMPORT_GATE_PASSED", "LORENTZIAN_QUANTUM_THEORY", "QME_RESTORED"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = ("scope", "source_completeness", "q2_row_readiness", "proof_gate_readiness", "D_action_readiness", "finite_receiver_obstruction", "next_executable_cut")
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, int]]:
    value = json.loads(RESULT.read_text()) if value is None else value
    source = json.loads(SOURCE.read_text())
    contract = json.loads(CONTRACT.read_text())
    gate = json.loads(GATE.read_text())
    errors: list[str] = []
    rows = value.get("q2_row_readiness", [])
    if [row.get("symbol") for row in rows] != list(SYMBOLS):
        errors.append("six-row identity/order")
    source_rows = source.get("local_q2_ansatz", {}).get("complete_minimal_roles", [])
    for row, source_row in zip(rows, source_rows):
        if row.get("symbol") != source_row.get("symbol") or row.get("role") != source_row.get("role") or row.get("degree") != source_row.get("degree") or row.get("source_terms") != source_row.get("q2_source_terms"):
            errors.append("source row reproduction " + str(row.get("symbol")))
        hard = row.get("symbol") == "hstar_mu_nu"
        expected = "HARD_COEFFICIENT_KERNEL_OPEN" if hard else "NOT_COMPONENT_SERIALIZED"
        if row.get("portable_component_status") != expected:
            errors.append("row readiness firewall " + str(row.get("symbol")))
        if hard and "second Bach" not in row.get("remaining", ""):
            errors.append("D2 Bach isolation")
    if sum(row.get("portable_component_status") == "HARD_COEFFICIENT_KERNEL_OPEN" for row in rows) != 1:
        errors.append("unique hard kernel")
    proofs = value.get("proof_gate_readiness", [])
    if [item.get("check_id") for item in proofs] != list(PROOFS):
        errors.append("seven-proof identity/order")
    if [item.get("check_id") for item in proofs] != contract.get("required_proof_checks"):
        errors.append("receiver proof inventory")
    if any(item.get("status") in {"VERIFIED", "CERTIFIED"} for item in proofs[1:]):
        errors.append("interaction proof promotion")
    complete = value.get("source_completeness", {})
    ansatz = source["local_q2_ansatz"]
    if complete.get("master_action") != ansatz.get("master_action") or complete.get("minimal_output_roles") != 6 or complete.get("maximum_metric_derivative_order") != 4 or complete.get("support_rule") != ansatz.get("domain", {}).get("support_rule"):
        errors.append("source completeness")
    obstruction = value.get("finite_receiver_obstruction", {})
    witness = source["first_failed_gate"]["witness"]
    expected_witness = {
        "status": "OBSTRUCTED_BEFORE_Q2", "kind": source["first_failed_gate"]["kind"],
        "energy": 5, "family": "E", "source_cohomology_dimension": 64,
        "selected_target_dimension": 0, "minimum_sdr_defect_rank": 64,
        "does_not_obstruct": "support-local full-BV q2 on the all-energy local carrier",
    }
    if obstruction != expected_witness or witness.get("minimum_sdr_defect_rank") != 64:
        errors.append("finite-receiver witness")
    d_action = value.get("D_action_readiness", {})
    if d_action.get("full_local_status") != "NOT_SERIALIZED_OR_REPLAYED" or "finite residual" not in d_action.get("boundary", ""):
        errors.append("finite/local D firewall")
    flags = value.get("claim_flags", {})
    if any(flags.get(key) is not False for key in FALSE_FLAGS):
        errors.append("claim promotion")
    if flags.get("STRICT_MINIMAL_Q2_SOURCE_ANSATZ_COMPLETE") is not True or flags.get("FINITE_SELECTED_RECEIVER_EQUIVARIANT_SDR_OBSTRUCTED") is not True:
        errors.append("positive source/receiver findings")
    m2 = next((item for item in gate.get("minimal_missing_bundle", []) if item.get("id") == "M2_STRICT_Q2_D"), {})
    if "support-local strict pure-Weyl q2" not in m2.get("object", ""):
        errors.append("Gate V3 M2 crosswalk")
    inputs = value.get("provenance", {}).get("inputs", [])
    if len(inputs) != 6:
        errors.append("provenance count")
    for item in inputs:
        path = ROOT / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            errors.append("provenance " + item.get("path", ""))
    if digest(value) != value.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {"rows": len(rows), "proof_gates": len(proofs), "inputs": len(inputs), "next_cuts": len(value.get("next_executable_cut", []))}


def main() -> int:
    errors, counts = check()
    print("STRICT_SUPPORT_LOCAL_Q2_D_READINESS_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print(f"  - {counts['rows']} action-defined rows, {counts['proof_gates']} receiver gates and {counts['next_cuts']} ordered construction cuts")
        print("  - finite-receiver rank-64 obstruction kept separate from all-energy support-local q2")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
