#!/usr/bin/env python3
"""Build Atlas V34 after the exact residual zero-mode export."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V33.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V16_RECONCILIATION.json"
RESIDUAL = ROOT / "quantum-weyl/classical_import/certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V34.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v34.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v16_reconciliation", "strict_source_q2_common_assembly",
        "strict_source_q3_common_assembly", "strict_residual_zero_mode_payload",
        "route_selection", "research_queue",
    )
    return hashlib.sha256(
        json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(item for item in value["branches"] if item["id"] == branch_id)
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text())
    gate = json.loads(GATE.read_text())
    residual = json.loads(RESIDUAL.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V33":
        raise ValueError("Atlas V33 predecessor drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V16_RECONCILIATION" or gate["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate V16 unavailable")
    if residual.get("result_id") != "STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1" or residual["claim_flags"]["M5_RESIDUAL_EXACT_PAYLOAD_COMPLETE"] is not True:
        raise ValueError("exact residual zero-mode payload unavailable")
    if gate["claim_flags"]["M5_RESIDUAL_EXACT_PAYLOAD_COMPLETE"] is not True or gate["claim_flags"]["COMMON_GATE_A_FREEZE_BOUND"] is not False:
        raise ValueError("Gate V16 M5/common-freeze boundary drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v34",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V34",
        "created": "2026-08-16",
        "question": "After exporting the exact residual zero-mode payload, what is the strongest tractable route toward a common Lorentzian Weyl BV freeze?",
        "answer": "Atlas V34 removes the residual M5 coefficient package from the construction frontier. Fifteen primal modes, fifteen normalized dual modes, the complete SO(4,2) tensor, all residual representation matrices and q_res^(0) are now portable and independently replayed. They are not yet common-bound, so Gate A still accepts only one of seven hashes. The highest-value tractable next certificate is the exact centered H3/H4/H5 representative payload; it should then be integrated with the harder support-local residual SDR and full cyclic contraction in one freeze.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v34.md",
    })
    value.pop("strict_gate_v15_reconciliation", None)
    disposition = gate["gate_disposition"]
    value["strict_gate_v16_reconciliation"] = {
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
        "zero_mode_hash_common_bound": gate["claim_flags"]["COMMON_GATE_A_FREEZE_BOUND"],
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
    value["strict_residual_zero_mode_payload"] = {
        "result_id": residual["result_id"],
        "residual_snapshot_sha256": residual["residual_snapshot"]["sha256"],
        "zero_mode_basis_sha256": residual["canonical_hashes"]["zero_mode_basis_sha256"],
        "primal_modes": residual["scope"]["primal_dimension"],
        "dual_modes": residual["scope"]["dual_dimension"],
        "residual_cotangent_dimension": residual["scope"]["residual_cotangent_dimension"],
        "structure_nonzero_entries": residual["so42_structure_constants"]["nonzero_entries"],
        "representation_matrices": len(residual["residual_representation"]["matrices"]),
        "identity_defects": sum(residual["exact_replay"].values()),
        "M5_payload_complete": True,
        "common_freeze_bound": False,
    }
    s0 = stage(value, "STRICT_PURE_WEYL_386", "S0_CLASSICAL_AUTHORITY")
    s0.update({
        "statement": "The authoritative q1/q2/q3/D/pairing bytes and the exact 15+15 residual zero-mode/Lie payload now exist. M5 is constructed; Gate A remains open at the common binding, support-local residual SDR, final cyclic contraction and centered-representative layer.",
        "evidence": list(dict.fromkeys([*s0["evidence"], residual["result_id"], gate["result_id"]])),
        "boundary": "Exact finite residual coefficients do not bind the six unaccepted hashes, construct the support-local SDR, or establish Green compatibility, Hadamard data or QME.",
    })

    by_route = {row["route"]: deepcopy(row) for row in previous["route_selection"]}
    centered = {
        "route": "STRICT_CENTERED_H3_H4_H5_REPRESENTATIVE_PAYLOAD",
        "branch": "STRICT_PURE_WEYL_386",
        "scientific_leverage": "VERY_HIGH",
        "tractability": "MEDIUM",
        "dependency_depth": "MEDIUM",
        "recommendation": "Generate the centered complex from an ansatz and serialize normalized coefficient vectors for H3, W_+^2/W_-^2 in H4, and H5 without hard-coding the cohomology answer.",
    }
    ordered = [
        centered,
        by_route["STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION"],
        by_route["STRICT_RESIDUAL_SDR_COMMON_CARRIER"],
        by_route["STRICT_FULL_CYCLIC_PAIRING"],
        by_route["STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE"],
        by_route["STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE"],
        by_route["DIRECT_SPACETIME_Q26_HADAMARD"],
        by_route["STRICT_D_CARTAN_AND_CHARGE_DECISION"],
        by_route["STRICT_ANALYTIC_MOLLER_CONVERGENCE"],
        by_route["STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN"],
    ]
    ordered[1]["recommendation"] = "After M6, bind the field dictionary, q1/q2/q3, D, exact residual payload, SDR and pairing to one manifest; accept hashes only when the final cyclic contraction replays."
    for rank, row in enumerate(ordered, 1):
        row["rank"] = rank
    value["route_selection"] = ordered
    why = {
        "STRICT_CENTERED_H3_H4_H5_REPRESENTATIVE_PAYLOAD": "M5 is now exact; M6 is the remaining finite coefficient package and the most tractable way to shrink the four-package freeze frontier.",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION": "The compatible local and residual bytes must eventually be bound to one manifest, but acceptance waits on M3, M4 and M6.",
        "STRICT_RESIDUAL_SDR_COMMON_CARRIER": "Extend or reconstruct iota_cl, pi_cl and s_cl beyond the D-finite control and replay every common-carrier identity.",
        "STRICT_FULL_CYCLIC_PAIRING": "Bind the full pairing/sign convention to the common residual SDR and replay all adjointness and side conditions.",
    }
    value["research_queue"] = [
        {"priority": row["rank"], "branch": row["branch"], "object": row["route"], "why": why.get(row["route"], row["recommendation"])}
        for row in ordered
    ]
    value["frontier_summary"] = {
        "highest_value_next_route": ordered[0]["route"],
        "route_count": len(ordered),
        "completed_since_v33": ["STRICT_RESIDUAL_ZERO_MODE_PAYLOAD", "GATE_V16_M5_RECONCILIATION"],
        "new_positive_result": "The previously hash-only residual sector is now a 15+15 exact portable basis with the complete SO(4,2) tensor, fifteen cotangent representation matrices and q_res^(0).",
        "surprise": "The residual coefficient absence was primarily an export gap, not a mathematical construction gap: existing exact kernels already produced all matrices needed for M5.",
        "hard_boundary": "The zero-mode hash is not common-bound; M1, M3, M4 and M6, six accepted hashes, the final cyclic contraction, Green compatibility, Hadamard and QME remain open.",
    }
    value["claim_flags"].update({
        "v33_preserved": True,
        "strict_residual_primal_dual_modes_serialized": True,
        "strict_so42_structure_constants_serialized": True,
        "strict_residual_representation_matrices_serialized": True,
        "strict_q_res_0_serialized": True,
        "strict_M5_residual_exact_payload_complete": True,
        "strict_residual_zero_mode_hash_common_bound": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_q2_q3_green_compatibility_certified": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREDECESSOR), "role": "immutable V33 predecessor"},
        {"path": str(RESIDUAL.relative_to(ROOT)), "result_or_artifact_id": residual["result_id"], "sha256": sha(RESIDUAL), "role": "portable exact residual zero-mode/Lie payload"},
        {"path": str(GATE.relative_to(ROOT)), "result_or_artifact_id": gate["result_id"], "sha256": sha(GATE), "role": "Gate-A V16 M5 reconciliation"},
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v34.py",
        "checks": [
            "V33 predecessor and 77-cell preservation", "Gate V16 and residual pins",
            "15+15 modes, 120 structure entries and fifteen representations",
            "zero residual identity defects", "M5 complete/common-bind false boundary",
            "four-package remaining bundle", "ten-route reranking",
            "Gate-A/Green/Hadamard/QME firewalls",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    residual = value["strict_residual_zero_mode_payload"]
    gate = value["strict_gate_v16_reconciliation"]
    routes = "\n".join(f"{row['rank']}. `{row['route']}` — {row['recommendation']}" for row in value["route_selection"])
    return f"""# Lorentzian Weyl BV completion atlas v34

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

## Decision

{value['answer']}

The new residual snapshot contains {residual['primal_modes']} primal and
{residual['dual_modes']} dual modes, {residual['structure_nonzero_entries']}
nonzero SO(4,2) coefficients and {residual['representation_matrices']}
representation matrices, with **{residual['identity_defects']}** replay
defects.  Gate V16 now has {gate['exports_receiver_verified_scoped']} of 20
exports receiver-verified in declared scopes and four typed replacement
packages instead of five.

Gate A remains `{gate['gate_a_status']}`.  The zero-mode hash is a candidate,
not an accepted common-freeze hash; only {gate['accepted_top_level_hashes']}
of seven top-level hashes is accepted.

## Ranked routes

{routes}

## Boundary

The exact residual payload closes an export gap.  It does not construct the
support-local residual SDR, centered representatives, final cyclic
contraction, causal nonlinear compatibility, Hadamard state or QME.
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V34: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V34: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
