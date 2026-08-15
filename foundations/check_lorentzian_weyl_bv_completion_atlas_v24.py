#!/usr/bin/env python3
"""Independent structural checker for completion Atlas V24."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V24.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V23.json"
Q3 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1.json"
ARITY3 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.json"
CYCLIC = ROOT / "quantum-weyl/classical_import/certificates/STRICT_MINIMAL_BV_Q3_CYCLICITY_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = ("stages", "branches", "frontier_summary", "classical_import_reconciliation", "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight", "strict_gate_v7_reconciliation", "strict_q2_green_composition_preflight", "strict_recursive_causal_tree_domains", "strict_polarized_formal_coefficients", "strict_field_equation_green_quotient_inverse", "strict_quadratic_truncation_lambda2_source_obstruction", "strict_pure_weyl_q3_witness", "strict_minimal_q3_completion", "route_selection", "research_queue")
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def cell_map(value: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {(branch["id"], stage["stage"]): stage for branch in value["branches"] for stage in branch["stages"]}


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    previous = json.loads(PREDECESSOR.read_text())
    q3, arity3, cyclic = (json.loads(path.read_text()) for path in (Q3, ARITY3, CYCLIC))
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V24" or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v24":
        return ["result identity/version drift"]
    predecessor = value.get("predecessor", {})
    if predecessor.get("sha256") != sha(PREDECESSOR) or predecessor.get("preserved") is not True:
        errors.append("V23 predecessor binding drift")
    before, after = cell_map(previous), cell_map(value)
    if set(before) != set(after) or len(after) != 77:
        errors.append("77-cell preservation drift")
    changed = {key for key in before.keys() & after.keys() if before[key] != after[key]}
    if changed != {("STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")}:
        errors.append("unexpected completion-cell mutation")

    p = value.get("strict_minimal_q3_completion", {})
    expected = {
        "quantum_import_result_id": q3["result_id"],
        "arity_three_result_id": arity3["result_id"],
        "cyclicity_result_id": cyclic["result_id"],
        "minimal_carrier_generators": 6,
        "minimal_q3_nonzero_components": 1,
        "minimal_q3_zero_output_rows": 5,
        "arbitrary_three_metric_inputs": True,
        "S3_input_permutations_replayed": 6,
        "diagonal_witness_terms_reproduced": 41,
        "diagonal_witness_q1_q3": "-75760/9",
        "arity_three_channels": 72,
        "arity_three_paths": 212,
        "arity_three_identity_on_arbitrary_inputs": True,
        "quartic_cyclicity_mod_d": True,
        "quartic_permutation_group": "S4",
        "strict_386_q3_stabilized": False,
        "strict_386_authoritative_nonminimal_equivalence": False,
        "strict_386_general_lambda2_source_closed": False,
        "classical_import_gate_a_passed": False,
    }
    for key, wanted in expected.items():
        if p.get(key) != wanted:
            errors.append(f"minimal q3 completion projection drift: {key}")
    nonlinear = after.get(("STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN"), {})
    if nonlinear.get("status") != "PARTIAL_CERTIFIED_WITH_COMPLETE_MINIMAL_Q3_ARITY_AND_CYCLICITY":
        errors.append("strict nonlinear stage status drift")
    for result_id in (q3["result_id"], arity3["result_id"], cyclic["result_id"]):
        if result_id not in nonlinear.get("evidence", []):
            errors.append(f"strict nonlinear evidence missing: {result_id}")
    if "minimal local cubic" not in nonlinear.get("boundary", "") or "Gate A" not in nonlinear.get("boundary", ""):
        errors.append("minimal-versus-386 narrative firewall drift")

    routes = value.get("route_selection", [])
    names = [item.get("route") for item in routes]
    if len(routes) != 11 or [item.get("rank") for item in routes] != list(range(1, 12)):
        errors.append("route rank/count drift")
    if names[:3] != ["STRICT_ARITY_THREE_386_CYCLIC_STABILIZATION", "STRICT_NONMINIMAL_THEORY_IDENTITY", "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE"]:
        errors.append("post-minimal-completion route ordering drift")
    if [item.get("object") for item in value.get("research_queue", [])] != names:
        errors.append("research queue projection drift")

    flags = value.get("claim_flags", {})
    true_flags = ("v23_preserved", "strict_authoritative_minimal_q3_imported", "strict_minimal_arbitrary_input_q3_certified", "strict_minimal_full_bv_arity_three_identity_certified", "strict_minimal_q3_cyclicity_certified")
    false_flags = ("strict_386_authoritative_q3_imported", "strict_386_q3_stabilized", "strict_386_full_bv_arity_three_identity_certified", "strict_386_general_full_weyl_lambda2_source_closure_certified", "strict_386_authoritative_formal_moller_map_certified", "strict_pure_weyl_classical_gate_passed", "strict_386_full_bv_hadamard_state_constructed", "strict_pure_weyl_qme_restored", "lorentzian_full_theory_certified")
    if any(flags.get(key) is not True for key in true_flags) or any(flags.get(key) is not False for key in false_flags):
        errors.append("V24 lifecycle/authority flag drift")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical atlas digest drift")
    for path in (Q3, ARITY3, CYCLIC):
        if not any(item.get("path") == str(path.relative_to(ROOT)) and item.get("sha256") == sha(path) for item in value.get("provenance", {}).get("inputs", [])):
            errors.append(f"atlas provenance binding drift: {path.name}")
    return errors


def main() -> int:
    errors = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V24: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
