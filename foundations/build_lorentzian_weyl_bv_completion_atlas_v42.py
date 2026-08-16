#!/usr/bin/env python3
"""Build Atlas V42 after represented M3RC action/support identification."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V41.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V24_RECONCILIATION.json"
ACTION_DUAL = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V42.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v42.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v24_reconciliation", "strict_dfinite_cotangent_dual_comparison",
        "strict_m3rc_action_support_dual_identification",
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
    action = json.loads(ACTION_DUAL.read_text(encoding="utf-8"))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V41":
        raise ValueError("Atlas V41 predecessor drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V24_RECONCILIATION":
        raise ValueError("Gate V24 unavailable")
    if action.get("result_id") != "STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1":
        raise ValueError("M3RC-B certificate unavailable")
    if (
        gate["claim_flags"]["M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE"] is not True
        or gate["claim_flags"]["M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE"] is not False
        or action["claim_flags"]["ACTION_PAIRING_EQUALS_CANONICAL_940_COTANGENT_PAIRING"] is not True
        or action["claim_flags"]["FULL_ALL_ENERGY_CONTINUOUS_DUAL_IDENTIFIED"] is not False
    ):
        raise ValueError("M3RC-B/M4R firewall drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v42",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V42",
        "created": "2026-08-16",
        "question": "What remains after the formal residual dual is identified with compact-source action-dual classes?",
        "answer": "Atlas V42 closes M3RC-B on represented energies two through six. The classical causal quasi-isomorphism, compact cutoff inverse, action/Green current equality and all-energy +E,-A,-L harmonic isometry identify all 470 formal residual duals with explicit compact-source classes. After one BV-BFV suspension, the action-derived and canonical cotangent pairings agree at exact rank 940. The next route is no longer a topology search: it is the finite M4R receiver replay of residual cyclicity and adjoint side conditions, followed by the M1 common freeze. Gate A remains fail closed at one of seven hashes.",
        "predecessor": {
            "result_id": previous["result_id"],
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "sha256": sha(PREDECESSOR),
            "preserved": True,
        },
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v42.md",
    })
    value.pop("strict_gate_v23_reconciliation", None)
    disposition = gate["gate_disposition"]
    resolution = gate["m3rc_action_support_dual_resolution"]
    value["strict_gate_v24_reconciliation"] = {
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
        "M4R_typed_residual_cyclicity_ready": gate["claim_flags"]["M4R_TYPED_RESIDUAL_CYCLICITY_READY"],
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
    value["strict_dfinite_cotangent_dual_comparison"].update({
        "M3RC_B_status": "COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6",
        "action_support_dual_identified": True,
        "full_all_energy_continuous_dual_identified": False,
    })
    value["strict_m3rc_action_support_dual_identification"] = {
        "result_id": action["result_id"],
        "status": action["result_state"],
        "represented_primal_modes": resolution["represented_primal_modes"],
        "compact_source_dual_classes": resolution["compact_source_dual_classes"],
        "phase_space_dimension": resolution["phase_space_dimension"],
        "action_pairing_rank": resolution["action_pairing_rank"],
        "positive_krein_inertia": resolution["positive_krein_inertia"],
        "support_exact_sequence_defects": resolution["support_exact_sequence_defects"],
        "compact_source_support_defects": resolution["compact_source_support_defects"],
        "causal_recovery_defects": resolution["causal_recovery_defects"],
        "basis_crosswalk_defects": resolution["basis_crosswalk_defects"],
        "pairing_identification_defects": resolution["pairing_identification_defects"],
        "full_continuous_dual_identified": False,
        "M3RC_B_status": "COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6",
        "M4R_status": "READY",
    }
    value["strict_residual_cyclic_carrier_obstruction"].update({
        "M3RC_status": "M3RC_A_AND_REPRESENTED_M3RC_B_COMPLETE",
        "M4R_status": "READY",
    })
    value["strict_local_cyclic_pairing_closure"].update({
        "M3RC_status": "M3RC_A_AND_REPRESENTED_M3RC_B_COMPLETE",
        "M4R_status": "READY_FOR_TYPED_RECEIVER_REPLAY",
    })
    s0 = stage(value, "STRICT_PURE_WEYL_386", "S0_CLASSICAL_AUTHORITY")
    s0.update({
        "statement": "M3L, M4L, M3R, M3RC-A and represented M3RC-B are complete. All 470 cotangent duals have compact-source causal representatives and the action pairing agrees with the canonical rank-940 form. M4R and M1 remain.",
        "evidence": list(dict.fromkeys([*s0["evidence"], action["result_id"], gate["result_id"]])),
        "boundary": "The result is a finite represented causal subquotient identification. It does not identify the full continuous all-energy dual, complete M4R, or bind a common M1 snapshot.",
    })

    prior = {row["route"]: deepcopy(row) for row in previous["route_selection"]}
    prior["STRICT_TYPED_RESIDUAL_CYCLICITY"]["recommendation"] = "Replay the canonical rank-940 action-identified pairing against the exact cotangent SDR: nondegeneracy, q_res cyclicity, p=iota-sharp, homotopy skew-adjointness and residual-transfer cyclic side conditions."
    prior["STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION"]["recommendation"] = "After M4R, bind the local, primal-residual, compact-source dual, action-pairing and cotangent-SDR maps under one typed M1 manifest; accept hashes only after receiver replay."
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
    ordered = [prior[name] for name in names]
    for rank, row in enumerate(ordered, 1):
        row["rank"] = rank
    value["route_selection"] = ordered
    why = {
        "STRICT_TYPED_RESIDUAL_CYCLICITY": "M3RC-B now supplies the action/support meaning of the rank-940 carrier, so every finite M4R identity is well typed and directly testable.",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION": "M1 becomes the last classical import obligation after the M4R receiver accepts the action-identified cyclic contraction.",
    }
    value["research_queue"] = [
        {"priority": row["rank"], "branch": row["branch"], "object": row["route"], "why": why.get(row["route"], row["recommendation"])}
        for row in ordered
    ]
    value["frontier_summary"] = {
        "highest_value_next_route": "STRICT_TYPED_RESIDUAL_CYCLICITY",
        "route_count": len(ordered),
        "completed_since_v41": ["M3RC_B_REPRESENTED_ACTION_SUPPORT_DUAL_IDENTIFICATION", "GATE_V24_M3RC_B_RECONCILIATION"],
        "new_positive_result": "Every one of the 470 formal residual duals is represented by a compact source Q(chi_plus*(-i*s_i)*conjugate(u_i)); the causal image and action-derived Cauchy pairing identify the suspended 940-coordinate carrier at exact rank 940.",
        "surprise": "The missing support dual was already latent in the classical causal theorem. The compact cutoff quasi-inverse, rather than a new distributional completion, supplies an explicit dual representative for every finite E/A/L mode.",
        "hard_boundary": "The identification is finite and represented. M4R, M1, six hashes, nonlinear Green compatibility, full-carrier Hadamard/Ward data, renormalized products and Lorentzian QME remain open.",
    }
    value["claim_flags"].update({
        "v41_preserved": True,
        "strict_M3RC_B_action_support_dual_identification_complete": True,
        "strict_M3RC_B_represented_action_support_dual_identification_complete": True,
        "strict_all_470_formal_duals_have_compact_source_representatives": True,
        "strict_action_pairing_equals_canonical_940_cotangent_pairing": True,
        "strict_M3RC_dual_comparison_maps_constructed": True,
        "strict_M4R_typed_residual_cyclicity_ready": True,
        "strict_M4R_typed_residual_cyclicity_complete": False,
        "strict_full_all_energy_continuous_dual_identified": False,
        "strict_formal_8980_source_is_authoritative_original_BV_complex": False,
        "strict_full_residual_cyclic_pairing_certified": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "the full continuous dual of every smooth or all-energy solution space",
        "that the formal 8,980-coordinate source is the unchanged authoritative classical BV source",
        "M4R, M1, a passed Gate A, Hadamard data, renormalized products, QME restoration or residual transfer",
    ]))
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREDECESSOR), "role": "immutable V41 predecessor"},
        {"path": str(ACTION_DUAL.relative_to(ROOT)), "result_or_artifact_id": action["result_id"], "sha256": sha(ACTION_DUAL), "role": "receiver-verified represented action/support dual identification"},
        {"path": str(GATE.relative_to(ROOT)), "result_or_artifact_id": gate["result_id"], "sha256": sha(GATE), "role": "Gate-A V24 M3RC-B reconciliation"},
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v42.py",
        "checks": [
            "V41 predecessor and 77-cell preservation",
            "Gate V24 and M3RC-B receiver replay",
            "470 compact-source representatives and exact rank-940 action pairing",
            "represented finite dual versus full continuous dual firewall",
            "M4R before M1 in the eight-route queue",
            "one accepted hash and two-package dependency remainder",
            "Gate-A/Hadamard/QME firewalls",
            "canonical atlas digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    comparison = value["strict_m3rc_action_support_dual_identification"]
    gate = value["strict_gate_v24_reconciliation"]
    routes = "\n".join(f"{row['rank']}. `{row['route']}` — {row['recommendation']}" for row in value["route_selection"])
    return f"""# Lorentzian Weyl BV completion atlas v42

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Decision

M3RC-B is complete on represented energies two through six.  The classical
causal cutoff inverse supplies {comparison['compact_source_dual_classes']}
compact-source duals for {comparison['represented_primal_modes']} E/A/L
positive-frequency modes.  The action-derived Cauchy and Green pairings agree
with the canonical cotangent pairing at exact rank
{comparison['action_pairing_rank']}, with zero declared defects.

M4R is now the first route.  It must replay the residual cyclic contraction
on this action-identified carrier; M1 then binds the result to a common frozen
snapshot.  Gate V24 still accepts {gate['accepted_top_level_hashes']} of seven
hashes.

## Ranked routes

{routes}

## Boundary

The result is a finite represented causal subquotient theorem, not a full
continuous all-energy dual or a declaration that the formal doubled source is
the original BV complex.  No M4R, M1, Gate-A pass, full-complex Hadamard state,
renormalized Lorentzian product, QME restoration, or residual quantum transfer
is claimed.
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
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V42: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V42: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
