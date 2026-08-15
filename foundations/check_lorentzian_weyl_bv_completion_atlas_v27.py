#!/usr/bin/env python3
"""Independent structural checker for completion Atlas V27."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V27.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V26.json"
CHANNEL = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1.json"
GATE_V9 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V9_RECONCILIATION.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_gate_v8_reconciliation",
        "strict_gate_v9_reconciliation", "strict_q2_green_composition_preflight",
        "strict_recursive_causal_tree_domains", "strict_polarized_formal_coefficients",
        "strict_field_equation_green_quotient_inverse",
        "strict_quadratic_truncation_lambda2_source_obstruction",
        "strict_pure_weyl_q3_witness", "strict_minimal_q3_completion",
        "strict_386_stabilized_q3_preflight", "strict_nonminimal_theory_identity_obstruction",
        "strict_quadratic_auxiliary_elimination", "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def cells(value: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {(branch["id"], stage["stage"]): stage for branch in value["branches"] for stage in branch["stages"]}


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    previous, channel, gate_v9 = (
        json.loads(path.read_text()) for path in (PREDECESSOR, CHANNEL, GATE_V9)
    )
    errors: list[str] = []
    if (
        value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V27"
        or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v27"
        or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE", "LORENTZIAN-CAUSAL"]
    ):
        return ["result identity/version/dependency drift"]
    predecessor = value.get("predecessor", {})
    if predecessor.get("sha256") != sha(PREDECESSOR) or predecessor.get("preserved") is not True:
        errors.append("V26 predecessor binding")
    before, after = cells(previous), cells(value)
    if set(before) != set(after) or len(after) != 77:
        errors.append("77-cell preservation")
    if {key for key in before if before[key] != after[key]} != {("STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")}:
        errors.append("unexpected completion-cell mutation")

    replay = channel["channel_pullback_replay"]
    boundary = channel["equivalence_boundary"]
    exact = value.get("strict_quadratic_auxiliary_elimination", {})
    expected_exact = {
        "result_id": channel["result_id"],
        "carrier_rows": 386,
        "field_map_component": replay["source_to_split_homogeneous_quadratic_component"],
        "second_Frechet_component": replay["source_to_split_second_Frechet_component"],
        "cyclic_form_channel": "Omega(f_hat,q2(v,v))",
        "source_before_correction": "-1",
        "inverse_shift_correction": "1",
        "transformed_source": "0",
        "candidate": "0",
        "residual": "0",
        "first_nonlinear_component_constructed": True,
        "component_support_local": True,
        "component_uses_green_operator": False,
        "component_uses_choice_principle": False,
        "source_local_BV_canonical_lift_available": True,
        "receiver_componentwise_386_cotangent_lift_serialized": False,
        "complete_source_q2_pullback_replayed": False,
        "complete_source_q3_pullback_replayed": False,
        "full_cyclic_L_infinity_equivalence_constructed": False,
        "nonlinear_equivalence_obstructed": False,
        "remaining_shifted_cubic_families": boundary["remaining_shifted_cubic_families"],
        "foundational_classification": "FINITE_EXACT_SUPPORT_LOCAL_POINTWISE_ALGEBRAIC_MAP",
        "next_gate": channel["next_gate"],
    }
    if exact != expected_exact:
        errors.append("quadratic auxiliary-elimination projection")
    gate = value.get("strict_gate_v9_reconciliation", {})
    gate_source = gate_v9["m2_quadratic_elimination_resolution"]
    if not (
        gate.get("result_id") == gate_v9["result_id"]
        and gate.get("gate_a_status") == "FAIL_CLOSED"
        and gate.get("accepted_top_level_hashes") == 0
        and gate.get("source_before_correction") == gate_source["source_before_correction"] == "-1"
        and gate.get("inverse_shift_correction") == gate_source["inverse_shift_correction"] == "1"
        and gate.get("residual") == gate_source["residual"] == "0"
        and gate.get("full_bv_cotangent_lift_serialized") is False
        and gate.get("complete_source_q2_pullback_replayed") is False
        and gate.get("complete_source_q3_pullback_replayed") is False
    ):
        errors.append("Gate V9 projection")
    nonlinear = after.get(("STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN"), {})
    if nonlinear.get("status") != "PARTIAL_CERTIFIED_FIRST_NONLINEAR_COMPONENT_CONSTRUCTED_FULL_BV_PULLBACK_OPEN" or channel["result_id"] not in nonlinear.get("evidence", []):
        errors.append("strict nonlinear cell")

    routes = value.get("route_selection", [])
    expected_front = [
        "STRICT_NONLINEAR_SHIFT_CUBIC_CHANNEL_INVENTORY",
        "STRICT_386_BV_COTANGENT_LIFT_COMPONENTS",
        "STRICT_SOURCE_Q2_Q3_PULLBACK_IDENTITY",
        "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE",
    ]
    if len(routes) != 12 or [item.get("rank") for item in routes] != list(range(1, 13)) or [item.get("route") for item in routes[:5]] != expected_front:
        errors.append("route ordering")
    queue = value.get("research_queue", [])
    if [item.get("priority") for item in queue] != list(range(1, 13)) or [item.get("object") for item in queue] != [item.get("route") for item in routes]:
        errors.append("research queue")

    flags = value.get("claim_flags", {})
    for key in ("v26_preserved", "strict_386_first_nonlinear_equivalence_component_constructed", "strict_386_f_hat_v_v_pullback_channel_closed", "strict_386_component_support_local"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "strict_386_component_uses_green_operator", "strict_386_component_uses_choice_principle",
        "strict_386_full_bv_cotangent_lift_serialized", "strict_386_full_source_q2_pullback_replayed",
        "strict_386_full_source_q3_pullback_replayed", "strict_386_nonlinear_equivalence_constructed",
        "strict_386_nonlinear_equivalence_obstructed", "strict_386_authoritative_q2_imported",
        "strict_386_authoritative_q3_imported", "strict_386_candidate_causal_lambda2_source_closure_certified",
        "strict_pure_weyl_classical_gate_passed", "strict_386_full_bv_hadamard_state_constructed",
        "strict_pure_weyl_qme_restored", "lorentzian_full_theory_certified",
    ):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    provenance = value.get("provenance", {}).get("inputs", [])
    if len(provenance) != len(previous["provenance"]["inputs"]) + 3:
        errors.append("provenance count")
    else:
        for item, path in zip(provenance[-3:], (PREDECESSOR, CHANNEL, GATE_V9)):
            if item.get("path") != str(path.relative_to(ROOT)) or item.get("sha256") != sha(path):
                errors.append("provenance " + path.name)
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V27_CHECK: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
