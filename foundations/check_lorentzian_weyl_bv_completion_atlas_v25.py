#!/usr/bin/env python3
"""Independent structural checker for completion Atlas V25."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V25.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V24.json"
Q3_PREFLIGHT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_q2_green_composition_preflight",
        "strict_recursive_causal_tree_domains", "strict_polarized_formal_coefficients",
        "strict_field_equation_green_quotient_inverse",
        "strict_quadratic_truncation_lambda2_source_obstruction",
        "strict_pure_weyl_q3_witness", "strict_minimal_q3_completion",
        "strict_386_stabilized_q3_preflight", "route_selection", "research_queue",
    )
    payload = json.dumps(
        {key: value[key] for key in keys},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def cell_map(value: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (branch["id"], stage["stage"]): stage
        for branch in value["branches"]
        for stage in branch["stages"]
    }


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    previous = json.loads(PREDECESSOR.read_text())
    preflight = json.loads(Q3_PREFLIGHT.read_text())
    errors: list[str] = []
    if (
        value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V25"
        or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v25"
    ):
        return ["result identity/version drift"]
    predecessor = value.get("predecessor", {})
    if predecessor.get("sha256") != sha(PREDECESSOR) or predecessor.get("preserved") is not True:
        errors.append("V24 predecessor binding drift")

    before, after = cell_map(previous), cell_map(value)
    if set(before) != set(after) or len(after) != 77:
        errors.append("77-cell preservation drift")
    changed = {key for key in before.keys() & after.keys() if before[key] != after[key]}
    if changed != {("STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")}:
        errors.append("unexpected completion-cell mutation")

    dag = preflight["graph_transport_dag"]
    identity = preflight["identity_transport"]
    theory = preflight["theory_identity_boundary"]
    expected = {
        "result_id": preflight["result_id"],
        "carrier_rows": 386,
        "endpoint_rows": 30,
        "contractible_rows": 356,
        "construction_kind": "CYCLIC_TRIVIAL_TERNARY_STABILIZATION_CANDIDATE",
        "graph_transport_kind": "EXACT_CANONICAL_TERNARY_TRANSPORT_DAG",
        "expanded_ternary_block_channels": 16,
        "active_input_row_envelope": 50,
        "active_output_row_envelope": 50,
        "interaction_inert_rows": 286,
        "arity_three_channels_transported": 72,
        "arity_three_paths_transported": 212,
        "arity_three_defects": 0,
        "q3_S3_defects": 0,
        "q3_cyclicity_mod_d_defects": 0,
        "D_q3_derivation_defects": 0,
        "candidate_q3_stabilized": True,
        "authoritative_full_q3_imported": False,
        "authoritative_nonminimal_equivalence": False,
        "candidate_causal_lambda2_source_closure": False,
        "classical_import_gate_a_passed": False,
        "foundational_classification": "FINITE_EXACT_STABILIZATION_PLUS_SMOOTH_LOCAL_VARIATIONAL_INPUT",
        "next_gate": preflight["next_gate"],
    }
    projection = value.get("strict_386_stabilized_q3_preflight", {})
    if projection != expected:
        errors.append("386-row q3 preflight projection drift")
    if (
        dag.get("expanded_ternary_block_channels") != expected["expanded_ternary_block_channels"]
        or identity["q1_q2_q3_arity_three"].get("defects") != 0
        or identity["q3_cyclicity_mod_d"].get("defects_mod_d") != 0
        or theory.get("candidate_equals_authoritative_nonminimal_classical_theory") != "NOT_ESTABLISHED"
    ):
        errors.append("source preflight semantic drift")

    minimal = value.get("strict_minimal_q3_completion", {})
    if minimal.get("strict_386_candidate_q3_stabilized") is not True:
        errors.append("minimal-to-candidate bridge missing")
    if minimal.get("strict_386_q3_stabilized") is not False:
        errors.append("authoritative stabilization firewall drift")
    nonlinear = after.get(("STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN"), {})
    if nonlinear.get("status") != "PARTIAL_CERTIFIED_WITH_386_CANDIDATE_Q3_ARITY_AND_CYCLICITY":
        errors.append("strict nonlinear stage status drift")
    if preflight["result_id"] not in nonlinear.get("evidence", []):
        errors.append("strict nonlinear evidence missing")
    boundary = nonlinear.get("boundary", "")
    if "candidate stabilization" not in boundary or "Gate A" not in boundary:
        errors.append("candidate-versus-authority narrative firewall drift")

    routes = value.get("route_selection", [])
    names = [item.get("route") for item in routes]
    if len(routes) != 11 or [item.get("rank") for item in routes] != list(range(1, 12)):
        errors.append("route rank/count drift")
    if names[:3] != [
        "STRICT_NONMINIMAL_THEORY_IDENTITY",
        "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE",
    ]:
        errors.append("post-stabilization route ordering drift")
    if [item.get("object") for item in value.get("research_queue", [])] != names:
        errors.append("research queue projection drift")

    flags = value.get("claim_flags", {})
    true_flags = (
        "v24_preserved",
        "strict_386_candidate_q3_stabilized",
        "strict_386_candidate_full_bv_arity_three_identity_certified",
        "strict_386_candidate_q3_cyclicity_mod_d_certified",
        "strict_386_candidate_D_q3_derivation_certified",
    )
    false_flags = (
        "strict_386_authoritative_q3_imported",
        "strict_386_authoritative_nonminimal_equivalence_certified",
        "strict_386_candidate_causal_lambda2_source_closure_certified",
        "strict_pure_weyl_classical_gate_passed",
        "strict_386_full_bv_hadamard_state_constructed",
        "strict_pure_weyl_qme_restored",
        "lorentzian_full_theory_certified",
    )
    if any(flags.get(key) is not True for key in true_flags):
        errors.append("V25 positive flag drift")
    if any(flags.get(key) is not False for key in false_flags):
        errors.append("V25 lifecycle/authority firewall drift")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical atlas digest drift")
    if not any(
        item.get("path") == str(Q3_PREFLIGHT.relative_to(ROOT))
        and item.get("sha256") == sha(Q3_PREFLIGHT)
        for item in value.get("provenance", {}).get("inputs", [])
    ):
        errors.append("q3 preflight provenance binding drift")
    return errors


def main() -> int:
    errors = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V25: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
