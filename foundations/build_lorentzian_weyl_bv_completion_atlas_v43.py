#!/usr/bin/env python3
"""Build Atlas V43 after finite represented M4R residual cyclicity."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V42.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V25_RECONCILIATION.json"
M4R = ROOT / "quantum-weyl/classical_import/certificates/STRICT_TYPED_RESIDUAL_CYCLICITY_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V43.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v43.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v25_reconciliation", "strict_dfinite_cotangent_dual_comparison",
        "strict_m3rc_action_support_dual_identification", "strict_typed_residual_cyclicity",
        "strict_endpoint_to_residual_spectral_comparison",
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


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    m4r = json.loads(M4R.read_text(encoding="utf-8"))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V42":
        raise ValueError("Atlas V42 predecessor drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V25_RECONCILIATION":
        raise ValueError("Gate V25 unavailable")
    if m4r.get("result_id") != "STRICT_TYPED_RESIDUAL_CYCLICITY_V1":
        raise ValueError("M4R unavailable")
    if (
        gate["claim_flags"]["M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE"] is not True
        or gate["claim_flags"]["M1_COMMON_STRICT_SNAPSHOT_COMPLETE"] is not False
        or m4r["claim_flags"]["M4R_REPRESENTED_NORMALIZED_CYCLIC_CONTRACTION_COMPLETE"] is not True
        or m4r["claim_flags"]["FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX"] is not False
    ):
        raise ValueError("M4R/M1 firewall drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v43",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V43",
        "created": "2026-08-16",
        "question": "What remains after exact residual cyclicity is replayed on the action-identified represented carrier?",
        "answer": "Atlas V43 closes M4R on represented energies two through six. An independent sparse receiver reconstructs all five shifted-cotangent comparison blocks and verifies q_res cyclicity, projection equals inclusion-adjoint, homotopy skew-adjointness, inclusion isometry, contraction and normalized side conditions with zero defects. M3RC-B identifies the rank-940 residual form with compact-source action/Green classes. M1 is now the sole minimal classical import package: one authoritative source snapshot must bind all local, nonlinear, causal and residual objects and support replay of all twenty exports, ten checks and seven hashes. Gate A remains fail closed at one accepted hash.",
        "predecessor": {
            "result_id": previous["result_id"],
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "sha256": sha(PREDECESSOR),
            "preserved": True,
        },
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v43.md",
    })
    value.pop("strict_gate_v24_reconciliation", None)
    disposition = gate["gate_disposition"]
    resolution = gate["m4r_typed_residual_cyclicity_resolution"]
    value["strict_gate_v25_reconciliation"] = {
        "result_id": gate["result_id"],
        "status": gate["result_state"],
        "exports_total": len(gate["export_reconciliation"]),
        "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "legacy_accepted_scoped": disposition["legacy_accepted_scoped"],
        "freeze_checks_total": len(gate["freeze_check_reconciliation"]),
        "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "freeze_checks_blocked": disposition["freeze_checks_blocked"],
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "remaining_top_level_hashes": 7 - disposition["accepted_common_snapshot_hashes"],
        "minimal_missing_bundle": [item["id"] for item in gate["minimal_missing_bundle"]],
        "M3RC_action_support_dual_identification_complete": gate["claim_flags"]["M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE"],
        "M4R_typed_residual_cyclicity_complete": gate["claim_flags"]["M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE"],
        "M1_common_strict_snapshot_complete": gate["claim_flags"]["M1_COMMON_STRICT_SNAPSHOT_COMPLETE"],
        "gate_a_status": disposition["gate_a_status"],
    }
    value["classical_import_reconciliation"] = {
        "result_id": gate["result_id"],
        "status": gate["result_state"],
        "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "exports_total": len(gate["export_reconciliation"]),
        "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "freeze_checks_total": len(gate["freeze_check_reconciliation"]),
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "gate_a_status": disposition["gate_a_status"],
        "minimal_missing_bundle": [item["id"] for item in gate["minimal_missing_bundle"]],
    }
    value["strict_typed_residual_cyclicity"] = {
        "result_id": m4r["result_id"],
        "status": m4r["result_state"],
        "formal_comparison_source_dimension": resolution["formal_comparison_source_dimension"],
        "action_identified_residual_dimension": resolution["action_identified_residual_dimension"],
        "residual_pairing_rank": resolution["residual_pairing_rank"],
        "energy_blocks_replayed": resolution["energy_blocks_replayed"],
        "all_identity_defects": resolution["all_identity_defects"],
        "q_res_cyclic": resolution["q_res_cyclic"],
        "projection_equals_inclusion_sharp": resolution["projection_equals_inclusion_sharp"],
        "homotopy_skew_adjoint": resolution["homotopy_skew_adjoint"],
        "formal_source_authoritative": resolution["formal_source_authoritative"],
        "M4R_status": "COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6",
        "M1_status": "SOLE_MINIMAL_MISSING_PACKAGE",
    }
    value["strict_m3rc_action_support_dual_identification"].update({"M4R_status": "COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6"})
    value["strict_residual_cyclic_carrier_obstruction"].update({"M4R_status": "COMPLETE_ON_REPRESENTED_ACTION_IDENTIFIED_BLOCK"})
    value["strict_local_cyclic_pairing_closure"].update({"M4R_status": "COMPLETE_ON_REPRESENTED_ACTION_IDENTIFIED_BLOCK"})
    s0 = stage(value, "STRICT_PURE_WEYL_386", "S0_CLASSICAL_AUTHORITY")
    s0.update({
        "statement": "M3L, M4L, M3R, M3RC-A, represented M3RC-B and represented M4R are complete. The 940-coordinate action-identified residual carrier has an exact normalized cyclic contraction. M1 is the sole minimal classical import package.",
        "evidence": list(dict.fromkeys([*s0["evidence"], m4r["result_id"], gate["result_id"]])),
        "boundary": "M4R is finite and represented. The formal 8,980-coordinate comparison source is not authoritative until M1 binds the actual full classical source and every Gate-A object.",
    })

    prior = {row["route"]: deepcopy(row) for row in previous["route_selection"]}
    prior["STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION"].update({
        "scientific_leverage": "VERY_HIGH",
        "tractability": "HIGH",
        "dependency_depth": "LOW",
        "recommendation": "Build M1 as one immutable manifest over the actual strict source: bind the twenty exports, seven hashes, ten checks, local and residual maps, represented Green actions and the compact-source M4R dual dictionary; reject every category or basis mismatch.",
    })
    names = [
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION",
        "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE",
        "DIRECT_SPACETIME_Q26_HADAMARD",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION",
        "STRICT_ANALYTIC_MOLLER_CONVERGENCE",
        "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
    ]
    ordered = [prior[name] for name in names]
    for rank, row in enumerate(ordered, 1):
        row["rank"] = rank
    value["route_selection"] = ordered
    why = {
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION": "M4R removes the last residual cyclicity dependency. M1 is now the only missing classical import package and the mandatory gateway to any full-complex Hadamard work.",
        "DIRECT_SPACETIME_Q26_HADAMARD": "Begin only after M1: a Hadamard two-point function must live on the accepted full metric BV complex, not merely on the finite residual carrier.",
    }
    value["research_queue"] = [
        {"priority": row["rank"], "branch": row["branch"], "object": row["route"], "why": why.get(row["route"], row["recommendation"])}
        for row in ordered
    ]
    value["frontier_summary"] = {
        "highest_value_next_route": "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION",
        "route_count": len(ordered),
        "completed_since_v42": ["M4R_TYPED_RESIDUAL_CYCLICITY", "GATE_V25_M4R_RECONCILIATION"],
        "new_positive_result": "The five represented shifted-cotangent blocks give an exact rank-940 action-identified cyclic contraction: q_res cyclicity, projection-adjointness, homotopy skewness, inclusion isometry, contraction and normalized side conditions all have zero defects.",
        "surprise": "Once M3RC-B supplied the action/support semantics, M4R contained no further analytic obstruction; it reduced to a finite exact sparse receiver replay.",
        "hard_boundary": "M1 is not clerical aggregation. It must decide and freeze the authoritative common full source without equating the formal 8,980-coordinate comparison source, the local 386-row carrier and the residual 940-coordinate carrier by name alone.",
    }
    value["claim_flags"].update({
        "v42_preserved": True,
        "strict_M4R_typed_residual_cyclicity_ready": True,
        "strict_M4R_typed_residual_cyclicity_complete": True,
        "strict_M4R_represented_q_res_cyclic": True,
        "strict_M4R_represented_projection_equals_inclusion_sharp": True,
        "strict_M4R_represented_homotopy_skew_adjoint": True,
        "strict_represented_residual_cyclic_pairing_certified": True,
        "strict_full_residual_cyclic_pairing_certified": False,
        "strict_M1_common_strict_snapshot_complete": False,
        "strict_formal_8980_source_is_authoritative_original_BV_complex": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "that the formal 8,980-coordinate comparison source is the authoritative full classical BV source",
        "M1, a passed Gate A, a full-complex Hadamard state, renormalized products, QME restoration or residual quantum transfer",
    ]))
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREDECESSOR), "role": "immutable V42 predecessor"},
        {"path": str(M4R.relative_to(ROOT)), "result_or_artifact_id": m4r["result_id"], "sha256": sha(M4R), "role": "receiver-verified finite represented M4R cyclic contraction"},
        {"path": str(GATE.relative_to(ROOT)), "result_or_artifact_id": gate["result_id"], "sha256": sha(GATE), "role": "Gate-A V25 M4R reconciliation"},
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v43.py",
        "checks": [
            "V42 predecessor and 77-cell preservation",
            "Gate V25 and M4R independent receiver replay",
            "exact five-block 8,980-to-940 cyclic contraction projection",
            "M4R removal and sole M1 route",
            "one accepted hash and one-package dependency remainder",
            "formal comparison source versus authoritative full source firewall",
            "Gate-A/Hadamard/QME firewalls",
            "canonical atlas digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    m4r = value["strict_typed_residual_cyclicity"]
    gate = value["strict_gate_v25_reconciliation"]
    routes = "\n".join(f"{row['rank']}. `{row['route']}` — {row['recommendation']}" for row in value["route_selection"])
    return f"""# Lorentzian Weyl BV completion atlas v43

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Decision

M4R is complete on represented energies two through six.  The receiver
reconstructs {m4r['energy_blocks_replayed']} shifted-cotangent blocks and
verifies the normalized cyclic contraction from
{m4r['formal_comparison_source_dimension']} formal comparison coordinates to
{m4r['action_identified_residual_dimension']} action-identified residual
coordinates with {m4r['all_identity_defects']} defects.  The residual pairing
has exact rank {m4r['residual_pairing_rank']}.

M1 is now the sole minimal classical import package.  Gate V25 still accepts
{gate['accepted_top_level_hashes']} of seven hashes because the formal
comparison source has not been promoted to the authoritative common source.

## Ranked routes

{routes}

## Boundary

This is a finite represented cyclic contraction, not an all-energy completion
or common-source freeze.  No Gate-A pass, full-complex Hadamard state,
renormalized Lorentzian product, QME restoration or residual quantum transfer
is claimed.
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V43: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V43: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
