#!/usr/bin/env python3
"""Build Atlas V39 after the represented D-finite M3R comparison."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V38.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V21_RECONCILIATION.json"
M3R = ROOT / "quantum-weyl/classical_import/certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V39.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v39.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v21_reconciliation", "strict_endpoint_to_residual_spectral_comparison",
        "strict_local_cyclic_pairing_closure", "strict_common_endpoint_sdr_binding",
        "strict_residual_sdr_type_audit", "strict_source_q2_common_assembly",
        "strict_source_q3_common_assembly", "strict_residual_zero_mode_payload",
        "strict_centered_cohomology_payload", "route_selection", "research_queue",
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
    comparison = json.loads(M3R.read_text(encoding="utf-8"))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V38":
        raise ValueError("Atlas V38 predecessor drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V21_RECONCILIATION":
        raise ValueError("Gate V21 unavailable")
    if comparison.get("result_id") != "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1":
        raise ValueError("M3R comparison unavailable")
    if gate["claim_flags"]["M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED"] is not True:
        raise ValueError("Gate V21 does not accept scoped M3R completion")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v39",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V39",
        "created": "2026-08-16",
        "question": "After constructing the typed endpoint-to-residual comparison, what is the strongest surviving route toward Lorentzian Weyl BV completion?",
        "answer": "Atlas V39 closes M3R in the represented D-finite global category. All 470 energies-two-through-six W+/W- coordinates now have an explicit E/A/L magnetic dictionary, normalized synthesis names, a bijective crosswalk and exact retraction and q0 chain identities. The comparison is honestly nonlocal and does not claim smooth completion. The highest-value route is now M4R: derive the residual odd pairing on this fixed basis and replay its cyclic side conditions. M1 common freeze follows. Gate A remains fail closed at one of seven hashes, so causal Green, Hadamard and QME stages are unchanged.",
        "predecessor": {
            "result_id": previous["result_id"],
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "sha256": sha(PREDECESSOR),
            "preserved": True,
        },
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v39.md",
    })
    value.pop("strict_gate_v20_reconciliation", None)
    disposition = gate["gate_disposition"]
    value["strict_gate_v21_reconciliation"] = {
        "result_id": gate["result_id"],
        "status": gate["result_state"],
        "exports_total": len(gate["export_reconciliation"]),
        "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": len(gate["freeze_check_reconciliation"]),
        "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "remaining_top_level_hashes": 7 - disposition["accepted_common_snapshot_hashes"],
        "minimal_missing_bundle": [item["id"] for item in gate["minimal_missing_bundle"]],
        "M3L_common_endpoint_sdr_bound": gate["claim_flags"]["M3L_COMMON_ENDPOINT_SDR_BOUND"],
        "M3R_typed_residual_comparison_constructed": gate["claim_flags"]["M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED"],
        "M4L_local_graph_cyclic_pairing_complete": gate["claim_flags"]["M4L_LOCAL_GRAPH_CYCLIC_PAIRING_COMPLETE"],
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
    value["strict_endpoint_to_residual_spectral_comparison"] = {
        "result_id": comparison["result_id"],
        "source_category": comparison["scope"]["source_category"],
        "target_category": comparison["scope"]["target_category"],
        "energies": comparison["scope"]["energies"],
        "represented_endpoint_coordinates": comparison["comparison"]["source"]["total_dimension"],
        "residual_coordinates": comparison["comparison"]["target"]["dimension"],
        "level_dimensions": [item["dimension"] for item in comparison["level_blocks"]],
        "ordered_crosswalk_defects": comparison["exact_replay"]["ordered_crosswalk_defects"],
        "chain_identity_defects": sum(
            comparison["exact_replay"][key]
            for key in (
                "dfinite_pi_iota_identity_defects",
                "dfinite_q0_iota_chain_defects",
                "dfinite_pi_q0_chain_defects",
            )
        ),
        "support_local": comparison["claim_flags"]["HARMONIC_ANALYSIS_SUPPORT_LOCAL"],
        "smooth_completion_certified": comparison["claim_flags"]["ALL_ENERGY_OR_SMOOTH_COMPLETION_CERTIFIED"],
        "M3R_status": "COMPLETE_IN_REPRESENTED_DFINITE_ENERGIES_2_THROUGH_6",
    }
    value["strict_local_cyclic_pairing_closure"]["M4R_status"] = "OPEN_READY_AFTER_M3R"
    s0 = stage(value, "STRICT_PURE_WEYL_386", "S0_CLASSICAL_AUTHORITY")
    s0.update({
        "statement": "M3L, M4L and the represented finite M3R comparison are complete. The exact local carrier is now connected to 470 named positive-energy W+/W- modes without promoting harmonic analysis to a support-local operation. M4R and M1 remain.",
        "evidence": list(dict.fromkeys([*s0["evidence"], comparison["result_id"], gate["result_id"]])),
        "boundary": "M3R is a global finite-mode comparison. Raw all-magnetic coordinate tensors, all-energy completion, residual cyclicity M4R, M1 freeze, and every quantum promotion remain open.",
    })

    prior = {row["route"]: deepcopy(row) for row in previous["route_selection"]}
    prior.pop("STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON")
    prior["STRICT_TYPED_RESIDUAL_CYCLICITY"].update({
        "scientific_leverage": "VERY_HIGH",
        "tractability": "HIGH",
        "dependency_depth": "MEDIUM",
        "recommendation": "Use the fixed 470-mode M3R ordering and normalized E/A/L representatives to derive the induced W+/W- odd pairing, then replay q_res, inclusion/projection, homotopy and transfer cyclic side conditions exactly.",
    })
    prior["STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION"]["recommendation"] = "After M4R, bind M3L/M3R/M4L/M4R and every remaining classical export under one typed M1 manifest; accept hashes only after category-correct receiver replay."
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
        "STRICT_TYPED_RESIDUAL_CYCLICITY": "M3R has fixed the residual basis and comparison maps, so M4R is now the first well-posed missing classical object.",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION": "M1 can close immediately after M4R if every local and reduced-mode object is pinned without type collapse.",
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
        "highest_value_next_route": "STRICT_TYPED_RESIDUAL_CYCLICITY",
        "route_count": len(ordered),
        "completed_since_v38": ["STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON", "M3R_TYPED_GATE_INTEGRATION"],
        "new_positive_result": "A 470-element E/A/L magnetic dictionary now realizes the finite endpoint-to-W+/W- comparison with exact retraction and q0 chain identities.",
        "new_no_go": "The comparison cannot be promoted to a support-local map: its harmonic restriction is global and support-expanding; smooth and all-energy completion are separately unproved.",
        "surprise": "The full finite bridge required no Hilbert or Krein completion and no choice principle; the genuinely stronger assumptions enter only when passing beyond the fixed harmonic cutoff.",
        "hard_boundary": "M4R residual cyclicity, M1 freeze, six hashes, nonlinear Green compatibility, Hadamard and QME remain open.",
    }
    value["claim_flags"].update({
        "v38_preserved": True,
        "strict_M3R_typed_residual_comparison_constructed": True,
        "strict_M3R_ordered_470_mode_crosswalk_bijective": True,
        "strict_M3R_chain_identities_replayed": True,
        "strict_harmonic_analysis_support_local": False,
        "strict_all_energy_or_smooth_completion_certified": False,
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
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREDECESSOR), "role": "immutable V38 predecessor"},
        {"path": str(M3R.relative_to(ROOT)), "result_or_artifact_id": comparison["result_id"], "sha256": sha(M3R), "role": "typed represented finite M3R comparison"},
        {"path": str(GATE.relative_to(ROOT)), "result_or_artifact_id": gate["result_id"], "sha256": sha(GATE), "role": "Gate-A V21 M3R reconciliation"},
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v39.py",
        "checks": [
            "V38 predecessor and 77-cell preservation",
            "Gate V21 and M3R content pins",
            "4,080 represented endpoint and 470 residual coordinates",
            "zero-defect E/A/L crosswalk and q0 chain projection",
            "M3R completion with locality/completion firewalls",
            "two-package Gate remainder and one accepted hash",
            "eight-route reranking with M4R first",
            "Gate-A/Green/Hadamard/QME firewalls",
            "canonical atlas digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    comparison = value["strict_endpoint_to_residual_spectral_comparison"]
    gate = value["strict_gate_v21_reconciliation"]
    routes = "\n".join(
        f"{row['rank']}. `{row['route']}` — {row['recommendation']}"
        for row in value["route_selection"]
    )
    return f"""# Lorentzian Weyl BV completion atlas v39

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Decision

M3R is complete on the represented finite harmonic domain.  The comparison
connects {comparison['represented_endpoint_coordinates']:,} endpoint-complex
coefficients to {comparison['residual_coordinates']} W+/W- coordinates at
energies two through six.  Its E/A/L crosswalk and all retraction and q0 chain
identities have zero defects.

The harmonic restriction is global, not support-local.  No all-energy smooth
completion is claimed.  M4R residual cyclicity is now the highest-value next
route, followed by M1 common freeze.  Gate V21 still accepts
{gate['accepted_top_level_hashes']} of seven hashes.

## Ranked routes

{routes}

## Boundary

No residual cyclic pairing, nonlinear Green compatibility, full-complex
Hadamard state, renormalized Lorentzian product, QME restoration, or residual
quantum transfer is claimed.
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V39: " + (
            "generated artifacts current" if not stale else "stale: " + ", ".join(stale)
        ))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V39: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
