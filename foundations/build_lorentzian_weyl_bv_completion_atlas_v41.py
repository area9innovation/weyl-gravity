#!/usr/bin/env python3
"""Build Atlas V41 after the exact formal cotangent-dual comparison."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V40.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V23_RECONCILIATION.json"
DUAL = ROOT / "quantum-weyl/classical_import/certificates/STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V41.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v41.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v23_reconciliation", "strict_dfinite_cotangent_dual_comparison",
        "strict_endpoint_to_residual_spectral_comparison",
        "strict_residual_cyclic_carrier_obstruction", "strict_local_cyclic_pairing_closure",
        "strict_common_endpoint_sdr_binding", "strict_residual_sdr_type_audit",
        "strict_source_q2_common_assembly", "strict_source_q3_common_assembly",
        "strict_residual_zero_mode_payload", "strict_centered_cohomology_payload",
        "route_selection", "research_queue",
    )
    return hashlib.sha256(json.dumps(
        {key: value[key] for key in keys},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(item for item in value["branches"] if item["id"] == branch_id)
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    dual = json.loads(DUAL.read_text(encoding="utf-8"))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V40":
        raise ValueError("Atlas V40 predecessor drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V23_RECONCILIATION":
        raise ValueError("Gate V23 unavailable")
    if dual.get("result_id") != "STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1":
        raise ValueError("formal cotangent-dual comparison unavailable")
    if (
        gate["claim_flags"]["M3RC_A_FORMAL_COTANGENT_DUAL_COMPARISON_COMPLETE"] is not True
        or gate["claim_flags"]["M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE"] is not False
        or dual["claim_flags"]["FORMAL_COTANGENT_SDR_CYCLIC"] is not True
        or dual["claim_flags"]["FORMAL_DUAL_IDENTIFIED_WITH_ACTION_SUPPORT_DUAL"] is not False
    ):
        raise ValueError("M3RC-A/M3RC-B firewall drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v41",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V41",
        "created": "2026-08-16",
        "question": "What remains after exact formal cotangent completion of the residual comparison?",
        "answer": "Atlas V41 closes M3RC-A: the unchanged 4,490-coordinate D-finite source has H0=470 and H1=0 and therefore cannot retract onto a 940-coordinate cotangent residual carrier, while its declared 8,980-coordinate shifted cotangent completion retracts exactly onto that carrier with full-rank canonical odd pairings and zero declared SDR defects. This is a formal finite algebraic comparison, not an action-derived support dual. The highest-value route is now M3RC-B: select paired support/topology classes and prove that harmonic integration identifies the action BV pairing and adjoint maps with the formal cotangent construction. M4R and M1 follow; Gate A remains fail closed at one of seven hashes.",
        "predecessor": {
            "result_id": previous["result_id"],
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "sha256": sha(PREDECESSOR),
            "preserved": True,
        },
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v41.md",
    })
    value.pop("strict_gate_v22_reconciliation", None)
    disposition = gate["gate_disposition"]
    resolution = gate["m3rc_formal_cotangent_dual_resolution"]
    value["strict_gate_v23_reconciliation"] = {
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
        "M3RC_A_formal_cotangent_dual_comparison_complete": gate["claim_flags"]["M3RC_A_FORMAL_COTANGENT_DUAL_COMPARISON_COMPLETE"],
        "M3RC_B_action_support_dual_identification_complete": gate["claim_flags"]["M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE"],
        "M4R_typed_residual_cyclicity_complete": gate["claim_flags"]["M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE"],
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
    value["strict_dfinite_cotangent_dual_comparison"] = {
        "result_id": dual["result_id"],
        "original_source_full_dimension": resolution["original_source_full_dimension"],
        "original_source_H0_dimension": resolution["original_source_H0_dimension"],
        "original_source_H1_dimension": resolution["original_source_H1_dimension"],
        "same_source_retract_to_940_possible": resolution["same_source_retract_to_940_possible"],
        "formal_cotangent_source_dimension": resolution["formal_cotangent_source_dimension"],
        "formal_cotangent_residual_dimension": resolution["formal_cotangent_residual_dimension"],
        "formal_full_pairing_rank": resolution["formal_full_pairing_rank"],
        "formal_residual_pairing_rank": resolution["formal_residual_pairing_rank"],
        "formal_identity_defects": resolution["formal_identity_defects"],
        "M3RC_A_status": "COMPLETE",
        "M3RC_B_status": "OPEN",
        "action_support_dual_identified": False,
    }
    value["strict_residual_cyclic_carrier_obstruction"].update({
        "M3RC_status": "SPLIT_M3RC_A_COMPLETE_M3RC_B_OPEN",
        "M4R_status": "BLOCKED_BY_M3RC_B",
    })
    value["strict_local_cyclic_pairing_closure"].update({
        "M3RC_status": "SPLIT_M3RC_A_COMPLETE_M3RC_B_OPEN",
        "M4R_status": "BLOCKED_BY_M3RC_B_ACTION_SUPPORT_IDENTIFICATION",
    })
    s0 = stage(value, "STRICT_PURE_WEYL_386", "S0_CLASSICAL_AUTHORITY")
    s0.update({
        "statement": "M3L, M4L, M3R and the formal algebraic M3RC-A cotangent comparison are complete. The unchanged source has no degree-one cohomology, so M3RC-B must identify an enlarged action/support dual before M4R and M1.",
        "evidence": list(dict.fromkeys([*s0["evidence"], dual["result_id"], gate["result_id"]])),
        "boundary": "The 8,980-to-940 formal cotangent SDR is exact finite algebra. It is not the unchanged classical source and does not identify the continuous action-derived BV dual, support classes or harmonic integration pairing.",
    })

    prior = {row["route"]: deepcopy(row) for row in previous["route_selection"]}
    prior["STRICT_TYPED_RESIDUAL_CYCLICITY"]["recommendation"] = "After M3RC-B, replay nondegeneracy, q_res cyclicity, p=iota-sharp, homotopy skew-adjointness and residual-transfer cyclic side conditions on the action-identified cotangent carrier."
    prior["STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION"]["recommendation"] = "After M3RC-B and M4R, bind the local, primal-residual, dual-residual and action-pairing maps under one typed M1 manifest; accept hashes only after category-correct receiver replay."
    m3rc_b_route = {
        "rank": 1,
        "route": "STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION",
        "branch": "STRICT_PURE_WEYL_386",
        "scientific_leverage": "VERY_HIGH",
        "tractability": "MEDIUM_LOW",
        "dependency_depth": "MEDIUM",
        "recommendation": "Declare paired compact/test and distributional/solution support classes, construct the harmonic integration map to the algebraic cotangent dual, and prove that the action-derived BV density and adjoint comparison maps agree with the exact M3RC-A formulas.",
    }
    names = [
        "STRICT_TYPED_RESIDUAL_CYCLICITY",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION",
        "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE",
        "DIRECT_SPACETIME_Q26_HADAMARD",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION",
        "STRICT_ANALYTIC_MOLLER_CONVERGENCE",
        "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
    ]
    ordered = [m3rc_b_route, *(prior[name] for name in names)]
    for rank, row in enumerate(ordered, 1):
        row["rank"] = rank
    value["route_selection"] = ordered
    why = {
        "STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION": "M3RC-A proves the algebraic formulas; M3RC-B is now the sole missing comparison that decides whether they represent the action-derived BV dual.",
        "STRICT_TYPED_RESIDUAL_CYCLICITY": "Residual cyclicity is meaningful only after the formal cotangent dual is identified with declared support/topology classes and the action pairing.",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION": "M1 becomes meaningful only after the action-identified dual and M4R identities exist on common bytes.",
    }
    value["research_queue"] = [
        {
            "priority": row["rank"],
            "branch": row["branch"],
            "object": row["route"],
            "why": why.get(row["route"], row["recommendation"]),
        }
        for row in ordered
    ]
    value["frontier_summary"] = {
        "highest_value_next_route": "STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION",
        "route_count": len(ordered),
        "completed_since_v40": ["M3RC_A_FORMAL_COTANGENT_DUAL_COMPARISON", "GATE_V23_M3RC_SPLIT"],
        "new_positive_result": "The declared 8,980-coordinate shifted cotangent complex retracts exactly onto the 940-coordinate residual cotangent carrier; full and residual canonical odd pairings have ranks 8,980 and 940 and every declared SDR/cyclicity defect is zero.",
        "new_no_go": "The unchanged 4,490-coordinate D-finite source has H0 dimension 470 and H1 dimension zero, so no deformation retract from that same source to a 940-coordinate residual cotangent carrier can exist.",
        "surprise": "The missing dual maps are not algebraically mysterious: they are exact transposes of the primal SDR. The real missing theorem is categorical and analytic—what support dual the action selects and whether harmonic integration realizes those transposes.",
        "hard_boundary": "M3RC-B action/support identification, M4R, M1, six hashes, nonlinear Green compatibility, full-carrier Hadamard/Ward data, renormalized products and Lorentzian QME remain open.",
    }
    value["claim_flags"].update({
        "v40_preserved": True,
        "strict_original_dfinite_H1_zero": True,
        "strict_unchanged_4490_source_retracts_to_940_residual": False,
        "strict_M3RC_A_formal_cotangent_dual_comparison_complete": True,
        "strict_formal_8980_to_940_cotangent_SDR_exact": True,
        "strict_formal_cotangent_pairing_nondegenerate": True,
        "strict_M3RC_B_action_support_dual_identification_complete": False,
        "strict_formal_dual_identified_with_action_support_dual": False,
        "strict_M3RC_dual_comparison_maps_constructed": False,
        "strict_M4R_typed_residual_cyclicity_complete": False,
        "strict_full_residual_cyclic_pairing_certified": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_q2_q3_green_compatibility_certified": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "that the formal 8,980-coordinate shifted cotangent complex is the unchanged authoritative classical BV source",
        "a selected continuous action/support dual or harmonic integration identification",
        "M3RC-B, M4R, M1, a passed Gate A, Hadamard data, renormalized products, QME restoration or residual transfer",
    ]))
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREDECESSOR), "role": "immutable V40 predecessor"},
        {"path": str(DUAL.relative_to(ROOT)), "result_or_artifact_id": dual["result_id"], "sha256": sha(DUAL), "role": "receiver-verified formal cotangent-dual comparison"},
        {"path": str(GATE.relative_to(ROOT)), "result_or_artifact_id": gate["result_id"], "sha256": sha(GATE), "role": "Gate-A V23 M3RC-A/M3RC-B reconciliation"},
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v41.py",
        "checks": [
            "V40 predecessor and 77-cell preservation",
            "Gate V23 and formal cotangent-dual receiver replay",
            "same-source H1-zero obstruction and exact 8980-to-940 SDR projection",
            "formal algebraic dual versus action/support dual firewall",
            "M3RC-B before M4R and M1 in the nine-route queue",
            "one accepted hash and three-package dependency remainder",
            "Gate-A/Green/Hadamard/QME firewalls",
            "canonical atlas digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    comparison = value["strict_dfinite_cotangent_dual_comparison"]
    gate = value["strict_gate_v23_reconciliation"]
    routes = "\n".join(
        f"{row['rank']}. `{row['route']}` — {row['recommendation']}"
        for row in value["route_selection"]
    )
    return f"""# Lorentzian Weyl BV completion atlas v41

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Decision

M3RC-A is complete.  The unchanged
{comparison['original_source_full_dimension']}-coordinate D-finite source has
H0={comparison['original_source_H0_dimension']} and
H1={comparison['original_source_H1_dimension']}; it cannot retract to a
940-coordinate cotangent residual carrier.  The declared
{comparison['formal_cotangent_source_dimension']}-coordinate shifted
cotangent complex instead retracts exactly onto
{comparison['formal_cotangent_residual_dimension']} residual coordinates.
Its full and residual canonical odd pairings have ranks
{comparison['formal_full_pairing_rank']} and
{comparison['formal_residual_pairing_rank']}, with zero declared defects.

M3RC-B is now the first route: select paired support/topology classes and
identify the action-derived BV pairing and adjoints with the formal algebraic
construction.  Gate V23 still accepts {gate['accepted_top_level_hashes']} of
seven hashes.

## Ranked routes

{routes}

## Boundary

The formal cotangent complex is not the unchanged authoritative classical
source, and finite evaluation duality is not yet an action/support duality.
No M4R, M1, Gate-A pass, nonlinear Green compatibility, full-complex Hadamard
state, renormalized Lorentzian product, QME restoration, or residual quantum
transfer is claimed.
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (
        (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(),
        report(value).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [
        str(path.relative_to(ROOT))
        for path, content in outputs
        if not path.is_file() or path.read_bytes() != content
    ]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V41: " + (
            "generated artifacts current" if not stale else "stale: " + ", ".join(stale)
        ))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V41: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
