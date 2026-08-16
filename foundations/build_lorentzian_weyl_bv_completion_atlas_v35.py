#!/usr/bin/env python3
"""Build Atlas V35 after the exact centered cohomology export."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V34.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V17_RECONCILIATION.json"
CENTERED = ROOT / "quantum-weyl/classical_import/certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V35.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v35.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v17_reconciliation", "strict_source_q2_common_assembly",
        "strict_source_q3_common_assembly", "strict_residual_zero_mode_payload",
        "strict_centered_cohomology_payload", "route_selection", "research_queue",
    )
    return hashlib.sha256(
        json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(item for item in value["branches"] if item["id"] == branch_id)
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    centered = json.loads(CENTERED.read_text(encoding="utf-8"))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V34":
        raise ValueError("Atlas V34 predecessor drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V17_RECONCILIATION" or gate["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate V17 unavailable")
    if centered.get("result_id") != "STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1" or centered["claim_flags"]["M6_CENTERED_REPRESENTATIVES_COMPLETE"] is not True:
        raise ValueError("exact centered payload unavailable")
    if gate["claim_flags"]["M6_CENTERED_REPRESENTATIVES_COMPLETE"] is not True or gate["claim_flags"]["COMMON_GATE_A_FREEZE_BOUND"] is not False:
        raise ValueError("Gate V17 M6/common-freeze boundary drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v35",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V35",
        "created": "2026-08-16",
        "question": "After exporting the centered C3/C4/C5 complex and normalized H4 representatives, what is the strongest route toward a common Lorentzian Weyl BV freeze?",
        "answer": "Atlas V35 removes M6 from the construction frontier. The finite centered complex and its two normalized degree-four classes are portable and independently replayed, but their hash is not common-bound. Gate A still accepts only one of seven hashes. The highest-value dependency is now the common support-local residual SDR; it is needed before the full cyclic pairing can be closed and before the final all-object freeze can honestly accept hashes.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v35.md",
    })
    value.pop("strict_gate_v16_reconciliation", None)
    disposition = gate["gate_disposition"]
    value["strict_gate_v17_reconciliation"] = {
        "result_id": gate["result_id"],
        "status": gate["result_state"],
        "exports_total": len(gate["export_reconciliation"]),
        "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "exports_supporting_only": disposition["supporting_evidence_only"],
        "freeze_checks_total": len(gate["freeze_check_reconciliation"]),
        "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "remaining_top_level_hashes": 7 - disposition["accepted_common_snapshot_hashes"],
        "minimal_missing_bundle": [item["id"] for item in gate["minimal_missing_bundle"]],
        "M5_payload_complete": gate["claim_flags"]["M5_RESIDUAL_EXACT_PAYLOAD_COMPLETE"],
        "M6_payload_complete": gate["claim_flags"]["M6_CENTERED_REPRESENTATIVES_COMPLETE"],
        "representative_hash_common_bound": gate["claim_flags"]["COMMON_GATE_A_FREEZE_BOUND"],
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
    value["strict_centered_cohomology_payload"] = {
        "result_id": centered["result_id"],
        "centered_snapshot_sha256": centered["centered_snapshot"]["sha256"],
        "ordered_centered_basis_sha256": centered["canonical_hashes"]["ordered_centered_basis_sha256"],
        "representatives_sha256": centered["canonical_hashes"]["representatives_sha256"],
        "cochain_dimensions_C3_C4_C5": centered["scope"]["centered_cochain_dimensions_C3_C4_C5"],
        "differential_nonzero_coefficients": centered["centered_differential_summary"]["aggregate_nonzero_coefficients"],
        "ranks_d3_d4": centered["centered_differential_summary"]["aggregate_ranks_d3_d4"],
        "H4_dimension": centered["scope"]["cohomology_dimension_H4"],
        "normalized_gram": centered["normalized_H4_representatives"]["normalized_gram"],
        "identity_defects": sum(value_ for key, value_ in centered["exact_replay"].items() if key.endswith("defects")),
        "M6_payload_complete": True,
        "common_freeze_bound": False,
    }
    s0 = stage(value, "STRICT_PURE_WEYL_386", "S0_CLASSICAL_AUTHORITY")
    s0.update({
        "statement": "The authoritative q1/q2/q3/D/pairing bytes, exact residual zero modes and the centered C3/C4/C5 plus normalized H4 payload now exist. M5 and M6 are constructed; Gate A remains open at the common binding, support-local residual SDR and final full cyclic pairing layer.",
        "evidence": list(dict.fromkeys([*s0["evidence"], centered["result_id"], gate["result_id"]])),
        "boundary": "Exact finite centered coefficients do not bind the six unaccepted hashes, construct the common support-local residual SDR, close full-carrier cyclicity, or establish Hadamard data or QME.",
    })

    by_route = {row["route"]: deepcopy(row) for row in previous["route_selection"]}
    by_route.pop("STRICT_CENTERED_H3_H4_H5_REPRESENTATIVE_PAYLOAD")
    ordered_names = [
        "STRICT_RESIDUAL_SDR_COMMON_CARRIER",
        "STRICT_FULL_CYCLIC_PAIRING",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION",
        "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE",
        "DIRECT_SPACETIME_Q26_HADAMARD",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION",
        "STRICT_ANALYTIC_MOLLER_CONVERGENCE",
        "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
    ]
    ordered = [by_route[name] for name in ordered_names]
    recommendations = {
        "STRICT_RESIDUAL_SDR_COMMON_CARRIER": "Extend or reconstruct iota_cl, pi_cl and s_cl on the complete support-local 386-row carrier, including residual and nonminimal rows, and replay every contraction and intertwining identity against the M5/M6 bytes.",
        "STRICT_FULL_CYCLIC_PAIRING": "Once the common residual SDR carrier exists, extend the pairing/sign convention to every row and replay q1/q2/q3 adjointness plus all SDR cyclic side conditions.",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION": "Bind q1/q2/q3/D, zero modes, centered representatives, SDR and full pairing to one manifest; accept hashes only after all ten identities and the final cyclic contraction replay on those exact bytes.",
    }
    for row in ordered:
        if row["route"] in recommendations:
            row["recommendation"] = recommendations[row["route"]]
    for rank, row in enumerate(ordered, 1):
        row["rank"] = rank
    value["route_selection"] = ordered
    why = {
        "STRICT_RESIDUAL_SDR_COMMON_CARRIER": "M5 and M6 are exact; M3 is now the first dependency needed to connect finite residual coefficients to the complete support-local field carrier.",
        "STRICT_FULL_CYCLIC_PAIRING": "M4 depends on the common SDR carrier and is required for the final contraction and QME-compatible classical freeze.",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION": "M1 becomes honest only after M3 and M4 share one manifest with every already-certified object.",
    }
    value["research_queue"] = [
        {"priority": row["rank"], "branch": row["branch"], "object": row["route"], "why": why.get(row["route"], row["recommendation"])}
        for row in ordered
    ]
    value["frontier_summary"] = {
        "highest_value_next_route": ordered[0]["route"],
        "route_count": len(ordered),
        "completed_since_v34": ["STRICT_CENTERED_COHOMOLOGY_PAYLOAD", "GATE_V17_M6_RECONCILIATION"],
        "new_positive_result": "The centered C3/C4/C5 carrier and normalized W_+^2 v_- and W_-^2 v_- vectors are exact portable data, with reconstructed nilpotent differentials and H4 dimension two.",
        "surprise": "The representative gap was also primarily an export gap: the existing transferred metric-to-residual engine already generated the needed kernel, but discarded its ordered coordinates.",
        "hard_boundary": "The representative hash is not common-bound; M1, M3 and M4, six accepted hashes, the final cyclic contraction, nonlinear Green compatibility, Hadamard and QME remain open.",
    }
    value["claim_flags"].update({
        "v34_preserved": True,
        "strict_centered_C3_C4_C5_bases_serialized": True,
        "strict_centered_differential_reconstructed": True,
        "strict_normalized_weyl_square_representatives_serialized": True,
        "strict_centered_H4_cohomology_replayed": True,
        "strict_M6_centered_representatives_complete": True,
        "strict_representative_hash_common_bound": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_q2_q3_green_compatibility_certified": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREDECESSOR), "role": "immutable V34 predecessor"},
        {"path": str(CENTERED.relative_to(ROOT)), "result_or_artifact_id": centered["result_id"], "sha256": sha(CENTERED), "role": "portable centered cochain and normalized H4 payload"},
        {"path": str(GATE.relative_to(ROOT)), "result_or_artifact_id": gate["result_id"], "sha256": sha(GATE), "role": "Gate-A V17 M6 reconciliation"},
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v35.py",
        "checks": [
            "V34 predecessor and 77-cell preservation", "Gate V17 and centered payload pins",
            "C3/C4/C5 dimensions, exact ranks and normalized H4 Gram",
            "M5/M6 complete and common-bind false boundary", "three-package remaining bundle",
            "nine-route reranking", "Gate-A/Green/Hadamard/QME firewalls",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    centered = value["strict_centered_cohomology_payload"]
    gate = value["strict_gate_v17_reconciliation"]
    routes = "\n".join(f"{row['rank']}. `{row['route']}` — {row['recommendation']}" for row in value["route_selection"])
    return f"""# Lorentzian Weyl BV completion atlas v35

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Decision

{value['answer']}

The centered snapshot has cochain dimensions
`{centered['cochain_dimensions_C3_C4_C5']}`, reconstructs
{centered['differential_nonzero_coefficients']:,} nonzero coefficients with
ranks `{centered['ranks_d3_d4']}`, and proves `dim H4 =
{centered['H4_dimension']}` with Gram `{centered['normalized_gram']}` and
**{centered['identity_defects']}** declared defects.

Gate V17 now has {gate['exports_receiver_verified_scoped']} of 20 exports
receiver-verified in declared scopes and three typed replacement packages.
Gate A remains `{gate['gate_a_status']}`: the representative hash is a
candidate, and only {gate['accepted_top_level_hashes']} of seven top-level
hashes is accepted.

## Ranked routes

{routes}

## Boundary

This closes a finite coefficient export.  It does not construct the common
support-local SDR, the full cyclic contraction, causal nonlinear
compatibility, a Hadamard state, or the QME.
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V35: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V35: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
