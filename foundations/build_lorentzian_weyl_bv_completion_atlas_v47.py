#!/usr/bin/env python3
"""Build Atlas V47 after the exact M1B primal composite contraction."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V46.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V29_RECONCILIATION.json"
PRIMAL = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1.json"
SCHEMA = ROOT / "foundations/schema/foundational-lorentzian-weyl-bv-completion-atlas-v47.schema.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V47.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v47.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v29_reconciliation", "strict_m1b_primal_composite_contraction",
        "strict_gate_v28_reconciliation", "strict_m1a_represented_crosswalk",
        "strict_m1a_immutable_typed_ledger", "strict_gate_v27_reconciliation",
        "strict_m1a_local_semantic_extension", "strict_m1_common_snapshot_preflight",
        "strict_dfinite_cotangent_dual_comparison", "strict_m3rc_action_support_dual_identification",
        "strict_typed_residual_cyclicity", "strict_endpoint_to_residual_spectral_comparison",
        "strict_residual_cyclic_carrier_obstruction", "strict_local_cyclic_pairing_closure",
        "strict_common_endpoint_sdr_binding", "strict_residual_sdr_type_audit",
        "strict_source_q2_common_assembly", "strict_source_q3_common_assembly",
        "strict_residual_zero_mode_payload", "strict_centered_cohomology_payload",
        "route_selection", "research_queue",
    )
    return hashlib.sha256(json.dumps(
        {key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode()).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(row for row in value["branches"] if row["id"] == branch_id)
    return next(row for row in branch["stages"] if row["stage"] == stage_id)


def rerank(row: dict[str, Any], rank: int) -> dict[str, Any]:
    answer = deepcopy(row)
    answer["rank"] = rank
    return answer


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    primal = json.loads(PRIMAL.read_text(encoding="utf-8"))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V46":
        raise ValueError("Atlas V46 predecessor drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V29_RECONCILIATION":
        raise ValueError("Gate V29 unavailable")
    if (
        primal.get("result_id") != "STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1"
        or primal["claim_flags"].get("M1B_PRIMAL_COMPOSITE_CONTRACTION_COMPLETE") is not True
        or primal["claim_flags"].get("M1B_ACTION_DUAL_LIFT_COMPLETE") is not False
        or gate["claim_flags"].get("CLASSICAL_IMPORT_GATE_PASSED") is not False
    ):
        raise ValueError("M1B primal/Gate firewall drift")

    aggregate = primal["represented_contraction"]["aggregate"]
    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v47",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V47",
        "created": "2026-08-16",
        "question": "What is the highest-leverage route after completing the M1B primal composite contraction?",
        "answer": "Atlas V47 closes the primal sublayer of M1B on the declared energy-2-through-6 D-finite domain. The exact 4,080-to-470 endpoint contraction composes with the support-local 386-to-30 graph contraction by a typed normalized-contraction lemma; it is neither a 386-by-470 component matrix nor an arbitrary-smooth support-local result. The immediate frontier is now the compact-source action-dual lift, followed by rank-940 cyclic replay and M1C common-manifest binding. Gate A remains fail closed.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": str(REPORT.relative_to(ROOT)),
    })
    disposition = gate["gate_disposition"]
    resolution = gate["m1b_primal_completion_resolution"]
    value["strict_gate_v29_reconciliation"] = {
        "result_id": gate["result_id"], "status": gate["result_state"],
        "exports_total": disposition["exports_total"],
        "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": disposition["freeze_checks_total"],
        "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "remaining_top_level_hashes": 7 - disposition["accepted_common_snapshot_hashes"],
        "M1B_primal_complete": resolution["M1B_primal_complete"],
        "M1B_action_dual_complete": gate["claim_flags"]["M1B_ACTION_DUAL_LIFT_COMPLETE"],
        "M1B_cyclic_replay_complete": gate["claim_flags"]["M1B_TYPED_CYCLIC_REPLAY_COMPLETE"],
        "M1B_complete": resolution["M1B_complete"],
        "M1C_common_manifest_replay_complete": gate["claim_flags"]["M1C_COMMON_MANIFEST_REPLAY_COMPLETE"],
        "gate_a_status": disposition["gate_a_status"],
    }
    value["classical_import_reconciliation"] = {
        "result_id": gate["result_id"], "status": gate["result_state"],
        "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "exports_total": disposition["exports_total"],
        "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "freeze_checks_total": disposition["freeze_checks_total"],
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "gate_a_status": disposition["gate_a_status"],
        "minimal_missing_bundle": [row["id"] for row in gate["minimal_missing_bundle"]],
    }
    value["strict_m1b_primal_composite_contraction"] = {
        "result_id": primal["result_id"], "status": primal["result_state"],
        "content_sha256": primal["content_sha256"],
        "represented_endpoint_rows": aggregate["represented_rows"],
        "primal_residual_rows": aggregate["residual_rows"],
        "q0_nonzero_entries": aggregate["q0_nonzero_entries"],
        "homotopy_nonzero_entries": aggregate["homotopy_nonzero_entries"],
        "inclusion_nonzero_entries": aggregate["iota_nonzero_entries"],
        "projection_nonzero_entries": aggregate["pi_nonzero_entries"],
        "represented_identity_defects": sum(primal["represented_contraction"]["exact_replay"].values()),
        "formal_composition_defects": sum(primal["formal_composition_replay"].values()),
        "local_graph_factor_support_local": primal["claim_flags"]["GRAPH_TO_ENDPOINT_FACTOR_SUPPORT_LOCAL"],
        "harmonic_restriction_support_local": primal["claim_flags"]["HARMONIC_RESTRICTION_SUPPORT_LOCAL"],
        "raw_component_matrix_constructed": primal["claim_flags"]["RAW_386_BY_470_COMPONENT_MATRIX_CONSTRUCTED"],
        "M1B_primal_complete": True, "M1B_complete": False,
    }

    authority_stage = stage(value, "STRICT_PURE_WEYL_386", "S0_CLASSICAL_AUTHORITY")
    authority_stage.update({
        "statement": "M1A and the M1B primal sublayer are complete. The frozen typed carrier diagram now supports an exact 4,080-to-470 normalized represented contraction and its typed lift through the local 386-to-30 graph contraction. The remaining authority gate is the compact-source action-dual lift, rank-940 cyclic replay and M1C common-byte replay.",
        "evidence": list(dict.fromkeys([*authority_stage["evidence"], primal["result_id"], gate["result_id"]])),
        "boundary": "The result is restricted to the declared D-finite energy-2-through-6 domain. Harmonic restriction is global and support-expanding; no 386-by-470 component matrix, arbitrary-smooth contraction, action-dual lift or complete M1B package is claimed. Gate A remains fail closed at one of seven hashes.",
    })

    old = {row["route"]: row for row in previous["route_selection"]}
    route_names = [
        "STRICT_M1B_ACTION_DUAL_LIFT", "STRICT_M1B_TYPED_CYCLIC_REPLAY",
        "STRICT_M1C_COMMON_MANIFEST_REPLAY", "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE", "DIRECT_SPACETIME_Q26_HADAMARD",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION", "STRICT_ANALYTIC_MOLLER_CONVERGENCE",
        "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
    ]
    value["route_selection"] = [rerank(old[name], index) for index, name in enumerate(route_names, 1)]
    value["research_queue"] = [
        {"priority": row["rank"], "branch": row["branch"], "object": row["route"], "why": row["recommendation"]}
        for row in value["route_selection"]
    ]
    value["frontier_summary"] = {
        "highest_value_next_route": "STRICT_M1B_ACTION_DUAL_LIFT",
        "route_count": len(value["route_selection"]),
        "completed_since_v46": ["STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION", "GATE_V29_M1B_PRIMAL_RECONCILIATION"],
        "new_positive_result": "The exact represented endpoint contraction has dimension 4,080-to-470 with 1,805 q0 and homotopy entries and 470 inclusion/projection entries; all represented and formal composite identities have zero defects.",
        "surprise": "The scientifically correct composite is a typed operator DAG on a restricted graph-section domain. A seemingly natural 386-by-470 matrix would identify local species with global modes and is therefore not merely unavailable but ill-typed.",
        "hard_boundary": "Only the local graph factor is support-local. The harmonic restriction is global and support-expanding; action-dual, rank-940 cyclic, M1C, Gate A and arbitrary-smooth claims remain open.",
    }
    value["claim_flags"].update({
        "v46_preserved": True,
        "strict_M1B_primal_composite_contraction_complete": True,
        "strict_M1B_action_dual_lift_complete": False,
        "strict_M1B_typed_cyclic_replay_complete": False,
        "strict_M1B_represented_composite_contraction_complete": False,
        "strict_M1C_common_manifest_replay_complete": False,
        "strict_M1_common_strict_snapshot_complete": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "the M1B action-dual lift, rank-940 cyclic replay, complete M1B package or M1C common replay",
        "a 386-by-470 component matrix, support-local harmonic restriction or arbitrary-smooth contraction",
        "a passed Gate A, full-complex Hadamard state, renormalized products, QME restoration or residual transfer",
    ]))
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREDECESSOR), "role": "immutable Atlas V46 predecessor"},
        {"path": str(PRIMAL.relative_to(ROOT)), "result_or_artifact_id": primal["result_id"], "sha256": sha(PRIMAL), "role": "exact M1B primal composite contraction"},
        {"path": str(GATE.relative_to(ROOT)), "result_or_artifact_id": gate["result_id"], "sha256": sha(GATE), "role": "Gate-A V29 primal reconciliation"},
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v47.py",
        "checks": [
            "V46 predecessor and 77-cell preservation", "Gate V29 and M1B-primal independent replay",
            "4,080-to-470 exact contraction census", "typed category and support boundary",
            "action-dual/cyclic/M1C route ordering", "one accepted hash and fail-closed Gate A",
            "Hadamard/QME firewalls", "canonical atlas digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    return value


def report(value: dict[str, Any]) -> str:
    primal = value["strict_m1b_primal_composite_contraction"]
    routes = "\n".join(f"{row['rank']}. `{row['route']}` — {row['recommendation']}" for row in value["route_selection"])
    return f"""# Lorentzian Weyl BV completion atlas v47

**Result:** `{value['result_id']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Decision

The primal M1B sublayer is complete on the declared energy-two-through-six
D-finite domain.  The represented endpoint contraction has
**{primal['represented_endpoint_rows']:,} input coordinates and {primal['primal_residual_rows']}
residual coordinates**, with {primal['q0_nonzero_entries']:,} q0 entries,
{primal['homotopy_nonzero_entries']:,} homotopy entries, and
{primal['inclusion_nonzero_entries']} inclusion/projection entries.  Every
represented contraction identity and every formal composition rewrite has zero defects.

The composite is a typed operator DAG through the local 386-to-30 graph
contraction.  It is not a 386-by-470 component matrix.  The local factor is
support-local, while harmonic restriction is global and support-expanding.

## Ranked routes

{routes}

## Boundary

The next frontier is the action-derived compact-source dual lift.  Rank-940
cyclic replay, M1C common binding and all ten Gate-A checks remain downstream.
Gate A still accepts one of seven hashes.  No arbitrary-smooth contraction,
full-complex Hadamard state, renormalized Lorentzian product, QME restoration,
residual transfer or Lorentzian quantum theory is established.
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return json.dumps(value, indent=2, ensure_ascii=False).encode() + b"\n", report(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V47: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V47: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
