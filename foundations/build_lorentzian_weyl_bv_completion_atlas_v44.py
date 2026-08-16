#!/usr/bin/env python3
"""Build Atlas V44 from the strict M1 typed-diagram preflight."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V43.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V26_RECONCILIATION.json"
PREFLIGHT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V44.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v44.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v26_reconciliation", "strict_m1_common_snapshot_preflight",
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
    branch = next(item for item in value["branches"] if item["id"] == branch_id)
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def route(route_id: str, rank: int, leverage: str, tractability: str, dependency: str, recommendation: str) -> dict[str, Any]:
    return {
        "rank": rank,
        "route": route_id,
        "branch": "STRICT_PURE_WEYL_386",
        "scientific_leverage": leverage,
        "tractability": tractability,
        "dependency_depth": dependency,
        "recommendation": recommendation,
    }


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V43":
        raise ValueError("Atlas V43 predecessor drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V26_RECONCILIATION":
        raise ValueError("Gate V26 unavailable")
    if preflight.get("result_id") != "STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT_V1":
        raise ValueError("M1 preflight unavailable")
    if (
        gate["claim_flags"]["M1_PREFLIGHT_COMPLETE"] is not True
        or gate["claim_flags"]["M1_COMMON_STRICT_SNAPSHOT_COMPLETE"] is not False
        or preflight["claim_flags"]["M1_TYPED_DIAGRAM_REQUIRED"] is not True
        or preflight["claim_flags"]["FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX"] is not False
    ):
        raise ValueError("M1/Gate-A firewall drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v44",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V44",
        "created": "2026-08-16",
        "question": "What is the executable route through the sole remaining M1 classical-import package?",
        "answer": "Atlas V44 resolves M1 into three ordered construction routes. M1A must add explicit type and grading data to the authoritative carriers; M1B must serialize the actual represented inclusion, projection, homotopy and action pairing from the 386-row local graph architecture to the rank-940 residual target; M1C must freeze the resulting typed diagram and replay twenty exports, seven hashes and ten checks. Fourteen exports and four hash objects are ready, but Gate A remains fail closed at one accepted hash.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v44.md",
    })
    disposition = gate["gate_disposition"]
    resolution = gate["m1_common_snapshot_preflight_resolution"]
    value["strict_gate_v26_reconciliation"] = {
        "result_id": gate["result_id"],
        "status": gate["result_state"],
        "exports_total": len(gate["export_reconciliation"]),
        "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": len(gate["freeze_check_reconciliation"]),
        "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "remaining_top_level_hashes": 7 - disposition["accepted_common_snapshot_hashes"],
        "minimal_missing_bundle": [item["id"] for item in gate["minimal_missing_bundle"]],
        "M1_preflight_complete": gate["claim_flags"]["M1_PREFLIGHT_COMPLETE"],
        "M1_common_strict_snapshot_complete": gate["claim_flags"]["M1_COMMON_STRICT_SNAPSHOT_COMPLETE"],
        "gate_a_status": disposition["gate_a_status"],
    }
    value["classical_import_reconciliation"] = {
        "result_id": gate["result_id"], "status": gate["result_state"],
        "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "exports_total": len(gate["export_reconciliation"]),
        "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "freeze_checks_total": len(gate["freeze_check_reconciliation"]),
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "gate_a_status": disposition["gate_a_status"],
        "minimal_missing_bundle": [item["id"] for item in gate["minimal_missing_bundle"]],
    }
    value["strict_m1_common_snapshot_preflight"] = {
        "result_id": preflight["result_id"],
        "status": preflight["result_state"],
        "snapshot_shape": resolution["snapshot_shape"],
        "authoritative_local_source": resolution["authoritative_local_source"],
        "carrier_count": resolution["carrier_count"],
        "typed_edge_count": resolution["typed_edge_count"],
        "exports_total": resolution["exports_total"],
        "exports_object_ready": resolution["exports_object_ready"],
        "exports_blocked_typed_ledger": resolution["exports_blocked_typed_ledger"],
        "exports_blocked_composite": resolution["exports_blocked_composite"],
        "hashes_total": resolution["hashes_total"],
        "hash_objects_ready": resolution["hash_objects_ready"],
        "hashes_blocked": resolution["hashes_blocked"],
        "freeze_checks_common_snapshot_replayed": resolution["freeze_checks_common_snapshot_replayed"],
        "work_packages": [row["id"] for row in resolution["work_packages"]],
        "formal_8980_source_authoritative": resolution["formal_8980_source_authoritative"],
    }
    s0 = stage(value, "STRICT_PURE_WEYL_386", "S0_CLASSICAL_AUTHORITY")
    s0.update({
        "statement": "All scoped M3/M4 prerequisites are complete. M1 is now an explicit three-step construction: typed carrier ledger, actual represented composite contraction, and final immutable manifest replay.",
        "evidence": list(dict.fromkeys([*s0["evidence"], preflight["result_id"], gate["result_id"]])),
        "boundary": "The preflight classifies missing data but completes none of M1A, M1B or M1C. Gate A remains fail closed at one of seven hashes.",
    })

    old = {row["route"]: deepcopy(row) for row in previous["route_selection"]}
    ordered = [
        route("STRICT_M1A_FULL_TYPED_CARRIER_LEDGER", 1, "VERY_HIGH", "HIGH", "LOW", "Serialize authoritative role, ghost number, antifield number, form degree, parity, mass dimension, Weyl weight, compact degree and derivative bounds without inferring them from row names."),
        route("STRICT_M1B_REPRESENTED_COMPOSITE_CONTRACTION", 2, "VERY_HIGH", "MEDIUM", "MEDIUM", "After M1A, materialize and independently replay pi_cl, iota_cl, s_cl and the action pairing from the 386-row local carrier through the endpoint/harmonic stages to the 940 residual target."),
        route("STRICT_M1C_COMMON_MANIFEST_REPLAY", 3, "VERY_HIGH", "HIGH", "MEDIUM", "After M1A and M1B, freeze one typed diagram, bind all twenty exports and seven hashes, and replay all ten Gate-A checks on exactly those bytes."),
    ]
    for name in (
        "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE",
        "DIRECT_SPACETIME_Q26_HADAMARD",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION",
        "STRICT_ANALYTIC_MOLLER_CONVERGENCE",
        "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
    ):
        row = old[name]
        row["rank"] = len(ordered) + 1
        ordered.append(row)
    value["route_selection"] = ordered
    why = {
        "STRICT_M1A_FULL_TYPED_CARRIER_LEDGER": "The missing explicit row semantics block the field dictionary and differential hashes and must precede every composite map.",
        "STRICT_M1B_REPRESENTED_COMPOSITE_CONTRACTION": "Four required exports and the pairing hash remain only as separate typed stages until the actual composite is serialized.",
        "STRICT_M1C_COMMON_MANIFEST_REPLAY": "Only a final same-byte replay can decide Gate A and unlock full-complex Hadamard work.",
        "DIRECT_SPACETIME_Q26_HADAMARD": "Begin only after M1C passes Gate A; a full-complex state cannot live on a preflight inventory.",
    }
    value["research_queue"] = [
        {"priority": row["rank"], "branch": row["branch"], "object": row["route"], "why": why.get(row["route"], row["recommendation"])}
        for row in ordered
    ]
    value["frontier_summary"] = {
        "highest_value_next_route": "STRICT_M1A_FULL_TYPED_CARRIER_LEDGER",
        "route_count": len(ordered),
        "completed_since_v43": ["STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT", "GATE_V26_M1_PREFLIGHT_RECONCILIATION"],
        "new_positive_result": "The sole M1 bundle now has a receiver-checked blocker partition: fourteen exports and four hash objects ready; two ledger exports, four composite exports and three hash objects blocked.",
        "surprise": "The apparent final packaging task contains two missing mathematical objects: an explicit full grading ledger and an actual cross-category composite contraction.",
        "hard_boundary": "No M1 work package is complete. The formal 8,980-coordinate comparison source remains non-authoritative, and zero final common-snapshot checks have been replayed.",
    }
    value["claim_flags"].update({
        "v43_preserved": True,
        "strict_M1_preflight_complete": True,
        "strict_M1_typed_diagram_required": True,
        "strict_M1_is_clerical_hash_bundle": False,
        "strict_M1A_full_typed_carrier_ledger_complete": False,
        "strict_M1B_represented_composite_contraction_complete": False,
        "strict_M1C_common_manifest_replay_complete": False,
        "strict_M1_common_strict_snapshot_complete": False,
        "strict_formal_8980_source_is_authoritative_original_BV_complex": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "completion of M1A, M1B or M1C merely from their exact preflight classification",
        "a passed Gate A, full-complex Hadamard state, renormalized products, QME restoration or residual transfer",
    ]))
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREDECESSOR), "role": "immutable V43 predecessor"},
        {"path": str(PREFLIGHT.relative_to(ROOT)), "result_or_artifact_id": preflight["result_id"], "sha256": sha(PREFLIGHT), "role": "receiver-checked M1 typed-diagram preflight"},
        {"path": str(GATE.relative_to(ROOT)), "result_or_artifact_id": gate["result_id"], "sha256": sha(GATE), "role": "Gate-A V26 M1 preflight reconciliation"},
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v44.py",
        "checks": [
            "V43 predecessor and 77-cell preservation", "Gate V26 and M1 preflight independent replay",
            "eight-carrier/seven-edge typed-diagram projection", "twenty-export and seven-hash blocker partition",
            "M1A/M1B/M1C route ordering", "one accepted hash and zero final replay checks",
            "formal-source/Gate-A/Hadamard/QME firewalls", "canonical atlas digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    preflight = value["strict_m1_common_snapshot_preflight"]
    routes = "\n".join(f"{row['rank']}. `{row['route']}` — {row['recommendation']}" for row in value["route_selection"])
    return f"""# Lorentzian Weyl BV completion atlas v44

**Result:** `{value['result_id']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Decision

M1 is now an executable three-stage construction rather than an opaque final
box.  {preflight['exports_object_ready']} of {preflight['exports_total']} exports
and {preflight['hash_objects_ready']} of {preflight['hashes_total']} hash objects
are ready.  The full typed row ledger and actual represented composite
contraction remain missing, so none of the ten final common-snapshot checks has
run and Gate A stays fail closed at one accepted hash.

## Ranked routes

{routes}

## Boundary

The preflight is a classification, not an M1 completion.  It establishes no
full-complex Hadamard state, renormalized product, QME restoration, residual
transfer or Lorentzian quantum theory.
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return ((json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), report(value).encode())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V44: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V44: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
