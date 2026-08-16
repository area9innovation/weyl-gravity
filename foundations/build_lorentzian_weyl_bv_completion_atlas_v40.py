#!/usr/bin/env python3
"""Build Atlas V40 after the residual cyclic-carrier obstruction."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V39.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V22_RECONCILIATION.json"
OBSTRUCTION = ROOT / "quantum-weyl/classical_import/certificates/STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V40.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v40.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v22_reconciliation", "strict_endpoint_to_residual_spectral_comparison",
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
    obstruction = json.loads(OBSTRUCTION.read_text(encoding="utf-8"))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V39":
        raise ValueError("Atlas V39 predecessor drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V22_RECONCILIATION":
        raise ValueError("Gate V22 unavailable")
    if obstruction.get("result_id") != "STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1":
        raise ValueError("residual cyclic obstruction unavailable")
    if (
        gate["claim_flags"]["CURRENT_470_MODE_INDUCED_ODD_PAIRING_RANK_ZERO"] is not True
        or gate["claim_flags"]["FINITE_940_CANONICAL_ODD_PAIRING_NONDEGENERATE"] is not True
        or gate["claim_flags"]["M3RC_DUAL_COMPARISON_MAPS_CONSTRUCTED"] is not False
    ):
        raise ValueError("Gate V22 obstruction projection drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v40",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V40",
        "created": "2026-08-16",
        "question": "After testing M4R on the fixed 470-mode target, what carrier repair is required and which route now has highest leverage?",
        "answer": "Atlas V40 records an exact rank-zero obstruction to direct M4R. The current M3R target is a one-sided degree-zero physical carrier, so the degree-minus-one local BV pairing vanishes on its image. The older symmetric cross-energy form is an even representation-theoretic form and is not a BV antibracket. A canonical 940-coordinate shifted-cotangent preflight has exact full rank, but its dual endpoint comparison maps and action-pairing identification are open. The highest-value route is therefore M3RC dual residual completion, followed by M4R and then M1. Gate A remains fail closed at one of seven hashes.",
        "predecessor": {
            "result_id": previous["result_id"],
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "sha256": sha(PREDECESSOR),
            "preserved": True,
        },
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v40.md",
    })
    value.pop("strict_gate_v21_reconciliation", None)
    disposition = gate["gate_disposition"]
    value["strict_gate_v22_reconciliation"] = {
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
        "M3R_primal_comparison_constructed": gate["claim_flags"]["M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED"],
        "current_470_induced_odd_pairing_rank_zero": gate["claim_flags"]["CURRENT_470_MODE_INDUCED_ODD_PAIRING_RANK_ZERO"],
        "finite_940_cotangent_preflight_constructed": gate["claim_flags"]["FINITE_940_SHIFTED_COTANGENT_CARRIER_CONSTRUCTED"],
        "M3RC_dual_comparison_maps_constructed": gate["claim_flags"]["M3RC_DUAL_COMPARISON_MAPS_CONSTRUCTED"],
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
    replay = obstruction["obstruction_replay"]
    preflight = obstruction["cotangent_preflight"]
    value["strict_residual_cyclic_carrier_obstruction"] = {
        "result_id": obstruction["result_id"],
        "current_carrier_coordinates": replay["m3r_residual_coordinates"],
        "current_carrier_degree_counts": replay["m3r_inclusion_degree_counts"],
        "authoritative_pairing_degree": replay["authoritative_local_pairing_degree"],
        "current_induced_pairing_rank": replay["pulled_back_odd_pairing_rank"],
        "current_induced_pairing_nullity": replay["pulled_back_odd_pairing_nullity"],
        "nondegeneracy_rank_defect": replay["nondegeneracy_rank_defect"],
        "older_even_form_is_BV_antibracket": obstruction["claim_flags"]["OLDER_EVEN_COHOMOLOGY_FORM_IS_BV_ANTIBRACKET"],
        "cotangent_preflight_coordinates": preflight["total_dimension"],
        "cotangent_preflight_pairing_rank": preflight["constructive_exact_rank"],
        "cotangent_action_pairing_identified": obstruction["claim_flags"]["FINITE_940_PAIRING_IDENTIFIED_WITH_ACTION_BV_PAIRING"],
        "M3RC_status": "OPEN",
        "M4R_status": "BLOCKED_BY_M3RC",
    }
    value["strict_local_cyclic_pairing_closure"]["M4R_status"] = "BLOCKED_BY_M3RC_RANK_ZERO"
    value["strict_local_cyclic_pairing_closure"]["M3RC_status"] = "OPEN"
    s0 = stage(value, "STRICT_PURE_WEYL_386", "S0_CLASSICAL_AUTHORITY")
    s0.update({
        "statement": "M3L, M4L and the represented finite M3R primal comparison are complete. Direct cyclic pullback to the 470 degree-zero modes has exact rank zero. A 940-coordinate cotangent preflight exists, but M3RC dual comparison maps, M4R and M1 remain.",
        "evidence": list(dict.fromkeys([*s0["evidence"], obstruction["result_id"], gate["result_id"]])),
        "boundary": "The rank-zero result rejects only direct M4R on the one-sided 470-mode carrier. It neither obstructs a dual-complete carrier nor identifies the 940-coordinate preflight with the action BV pairing.",
    })

    prior = {row["route"]: deepcopy(row) for row in previous["route_selection"]}
    prior["STRICT_TYPED_RESIDUAL_CYCLICITY"].update({
        "scientific_leverage": "VERY_HIGH",
        "tractability": "MEDIUM",
        "dependency_depth": "MEDIUM",
        "recommendation": "Only after M3RC, replay nondegeneracy, q_res cyclicity, p=iota-sharp, homotopy skew-adjointness and residual-transfer cyclic side conditions on the dual-complete carrier.",
    })
    prior["STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION"]["recommendation"] = "After M3RC and M4R, bind every local, primal-residual and dual-residual map under one typed M1 manifest; accept hashes only after category-correct receiver replay."
    m3rc_route = {
        "rank": 1,
        "route": "STRICT_M3RC_DUAL_RESIDUAL_COMPARISON",
        "branch": "STRICT_PURE_WEYL_386",
        "scientific_leverage": "VERY_HIGH",
        "tractability": "MEDIUM",
        "dependency_depth": "MEDIUM",
        "recommendation": "Construct degree-one dual residual representatives and exact dual inclusion/projection on the same energy-2-through-6 endpoint domain; identify their pulled pairing with the canonical 940-coordinate cotangent form without confusing the older even cohomology form with the BV antibracket.",
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
    ordered = [m3rc_route, *(prior[name] for name in names)]
    for rank, row in enumerate(ordered, 1):
        row["rank"] = rank
    value["route_selection"] = ordered
    why = {
        "STRICT_M3RC_DUAL_RESIDUAL_COMPARISON": "The exact rank-zero pullback proves that M4R is ill-typed on the current one-sided carrier; M3RC is the first missing mathematical object.",
        "STRICT_TYPED_RESIDUAL_CYCLICITY": "The canonical 940-row pairing makes the target formula explicit, but cyclic transfer is meaningful only after its dual comparison maps are source-identified.",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION": "M1 becomes meaningful only after both residual halves and the M4R identities exist on common bytes.",
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
        "highest_value_next_route": "STRICT_M3RC_DUAL_RESIDUAL_COMPARISON",
        "route_count": len(ordered),
        "completed_since_v39": ["M4R_DIRECT_470_CARRIER_OBSTRUCTION", "FINITE_940_COTANGENT_PREFLIGHT", "GATE_V22_DEPENDENCY_REPAIR"],
        "new_positive_result": "The finite 940-coordinate shifted-cotangent preflight has a canonical exact rank-940 degree-minus-one odd pairing with no choice or completion assumption.",
        "new_no_go": "The literal odd BV pairing pulled back to the current 470 degree-zero M3R coordinates is the zero form, with rank defect 470; direct M4R on that carrier is impossible.",
        "surprise": "The pre-existing symmetric cross-energy form is valid but categorically different: it is an even physical cohomology form and explicitly not a field-theoretic BV antibracket.",
        "hard_boundary": "Dual residual comparison maps and action-pairing identification (M3RC), M4R, M1, six hashes, nonlinear Green compatibility, Hadamard and QME remain open.",
    }
    value["claim_flags"].update({
        "v39_preserved": True,
        "strict_current_470_induced_odd_pairing_rank_zero": True,
        "strict_current_470_induced_odd_pairing_nondegenerate": False,
        "strict_older_even_cohomology_form_is_BV_antibracket": False,
        "strict_finite_940_cotangent_carrier_constructed": True,
        "strict_finite_940_canonical_odd_pairing_nondegenerate": True,
        "strict_finite_940_pairing_action_identified": False,
        "strict_M3RC_dual_comparison_maps_constructed": False,
        "strict_M4R_typed_residual_cyclicity_complete": False,
        "strict_full_residual_cyclic_pairing_certified": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_q2_q3_green_compatibility_certified": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREDECESSOR), "role": "immutable V39 predecessor"},
        {"path": str(OBSTRUCTION.relative_to(ROOT)), "result_or_artifact_id": obstruction["result_id"], "sha256": sha(OBSTRUCTION), "role": "exact M4R carrier obstruction and cotangent preflight"},
        {"path": str(GATE.relative_to(ROOT)), "result_or_artifact_id": gate["result_id"], "sha256": sha(GATE), "role": "Gate-A V22 M3RC dependency repair"},
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v40.py",
        "checks": [
            "V39 predecessor and 77-cell preservation",
            "Gate V22 and residual-obstruction content pins",
            "rank-zero 470-mode pullback and rank-940 cotangent preflight projection",
            "even physical form versus odd BV antibracket category firewall",
            "M3RC inserted before M4R and M1 in the nine-route queue",
            "one accepted hash and three-package dependency remainder",
            "Gate-A/Green/Hadamard/QME firewalls",
            "canonical atlas digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    obstruction = value["strict_residual_cyclic_carrier_obstruction"]
    gate = value["strict_gate_v22_reconciliation"]
    routes = "\n".join(
        f"{row['rank']}. `{row['route']}` — {row['recommendation']}"
        for row in value["route_selection"]
    )
    return f"""# Lorentzian Weyl BV completion atlas v40

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Decision

Direct M4R on the current {obstruction['current_carrier_coordinates']}-mode
target is impossible: the induced degree-minus-one BV form has rank
{obstruction['current_induced_pairing_rank']} and nullity
{obstruction['current_induced_pairing_nullity']}.  All current modes are
degree-zero metric modes, while the local odd pairing needs degree-one duals.

The explicit {obstruction['cotangent_preflight_coordinates']}-coordinate
shifted-cotangent preflight has exact pairing rank
{obstruction['cotangent_preflight_pairing_rank']}.  Its dual endpoint maps and
action-pairing identification remain open, so M3RC is now first, M4R second,
and M1 third.  Gate V22 still accepts {gate['accepted_top_level_hashes']} of
seven hashes.

## Ranked routes

{routes}

## Boundary

The obstruction rejects only direct cyclic transfer to the one-sided
470-mode carrier.  It does not obstruct a dual-complete residual complex.
No nonlinear Green compatibility, full-complex Hadamard state, renormalized
Lorentzian product, QME restoration, or residual quantum transfer is claimed.
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V40: " + (
            "generated artifacts current" if not stale else "stale: " + ", ".join(stale)
        ))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V40: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
