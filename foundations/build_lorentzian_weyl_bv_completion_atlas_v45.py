#!/usr/bin/env python3
"""Build Atlas V45 after the exact local M1A2 semantic extension."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V44.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V27_RECONCILIATION.json"
LOCAL = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V45.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v45.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v27_reconciliation", "strict_m1a_local_semantic_extension",
        "strict_m1_common_snapshot_preflight", "strict_dfinite_cotangent_dual_comparison",
        "strict_m3rc_action_support_dual_identification", "strict_typed_residual_cyclicity",
        "strict_endpoint_to_residual_spectral_comparison", "strict_residual_cyclic_carrier_obstruction",
        "strict_local_cyclic_pairing_closure", "strict_common_endpoint_sdr_binding",
        "strict_residual_sdr_type_audit", "strict_source_q2_common_assembly",
        "strict_source_q3_common_assembly", "strict_residual_zero_mode_payload",
        "strict_centered_cohomology_payload", "route_selection", "research_queue",
    )
    projection = {key: value[key] for key in keys}
    return hashlib.sha256(json.dumps(
        projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode()).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(item for item in value["branches"] if item["id"] == branch_id)
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def route(
    route_id: str,
    rank: int,
    leverage: str,
    tractability: str,
    dependency: str,
    recommendation: str,
) -> dict[str, Any]:
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
    local = json.loads(LOCAL.read_text(encoding="utf-8"))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V44":
        raise ValueError("Atlas V44 predecessor drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V27_RECONCILIATION":
        raise ValueError("Gate V27 unavailable")
    if local.get("result_id") != "STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1":
        raise ValueError("M1A2 local semantic extension unavailable")
    if (
        gate["claim_flags"].get("M1A2_LOCAL_SEMANTIC_EXTENSION_COMPLETE") is not True
        or gate["claim_flags"].get("M1A3_REPRESENTED_CROSSWALK_COMPLETE") is not False
        or gate["claim_flags"].get("CLASSICAL_IMPORT_GATE_PASSED") is not False
        or local["claim_flags"].get("LOCAL_386_FULLY_TYPED") is not True
        or local["claim_flags"].get("M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE") is not False
    ):
        raise ValueError("M1A2/Gate-A firewall drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v45",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V45",
        "created": "2026-08-16",
        "question": "What remains after exact semantic classification of every local row in the strict M1 carrier ledger?",
        "answer": "Atlas V45 closes local M1A2: all 386 local graph rows are fully namespaced, including an exact proof that scalar nonlinear Weyl weight is not applicable to the fixed-background Cotton resolution rows. M1A now splits into a represented-coordinate crosswalk and an immutable ledger freeze. The next construction must crosswalk 4,080 endpoint-harmonic coordinates, classify 410 scalar test-nonminimal coordinates, and type the 470+470 action-residual carrier. M1B, M1C and Gate A remain downstream and fail closed.",
        "predecessor": {
            "result_id": previous["result_id"],
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "sha256": sha(PREDECESSOR),
            "preserved": True,
        },
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v45.md",
    })

    disposition = gate["gate_disposition"]
    resolution = gate["m1a_local_semantic_resolution"]
    value["strict_gate_v27_reconciliation"] = {
        "result_id": gate["result_id"],
        "status": gate["result_state"],
        "exports_total": disposition["exports_total"],
        "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": disposition["freeze_checks_total"],
        "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "remaining_top_level_hashes": 7 - disposition["accepted_common_snapshot_hashes"],
        "local_386_rows_fully_namespaced": resolution["local_386_rows_fully_namespaced"],
        "M1A2_local_semantic_extension_complete": gate["claim_flags"]["M1A2_LOCAL_SEMANTIC_EXTENSION_COMPLETE"],
        "M1A3_represented_crosswalk_complete": gate["claim_flags"]["M1A3_REPRESENTED_CROSSWALK_COMPLETE"],
        "M1A4_ledger_freeze_complete": gate["claim_flags"]["M1A4_LEDGER_FREEZE_COMPLETE"],
        "M1A_full_typed_carrier_ledger_complete": gate["claim_flags"]["M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE"],
        "gate_a_status": disposition["gate_a_status"],
    }
    value["classical_import_reconciliation"] = {
        "result_id": gate["result_id"],
        "status": gate["result_state"],
        "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "exports_total": disposition["exports_total"],
        "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "freeze_checks_total": disposition["freeze_checks_total"],
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "gate_a_status": disposition["gate_a_status"],
        "minimal_missing_bundle": [item["id"] for item in gate["minimal_missing_bundle"]],
    }
    counts = local["counts"]
    cotton = local["cotton_nonlinear_weyl_non_eigen_witness"]
    value["strict_m1a_local_semantic_extension"] = {
        "result_id": local["result_id"],
        "status": local["result_state"],
        "extension_rows": counts["extension_rows"],
        "auxiliary_rows_fully_namespaced": counts["auxiliary_rows_fully_namespaced"],
        "mapping_cone_rows_fully_namespaced": counts["mapping_cone_rows_fully_namespaced"],
        "local_386_rows_fully_namespaced": counts["local_386_rows_fully_namespaced_after_this_result"],
        "unresolved_local_rows": counts["local_386_rows_remaining_partial"],
        "scalar_nonlinear_weyl_weight": "NOT_APPLICABLE",
        "cotton_transformation_formula": cotton["infinitesimal_formula_in_dimension_four"],
        "cotton_component_checks": cotton["component_checks"],
        "cotton_component_defects": cotton["defects"],
        "M1A2_complete": True,
        "M1A_complete": False,
    }

    s0 = stage(value, "STRICT_PURE_WEYL_386", "S0_CLASSICAL_AUTHORITY")
    s0.update({
        "statement": "Local M1A2 is complete: all 386 graph rows carry explicit semantics. The remaining authority gate is the represented crosswalk, ledger freeze, represented composite contraction and final common-byte replay.",
        "evidence": list(dict.fromkeys([*s0["evidence"], local["result_id"], gate["result_id"]])),
        "boundary": "The represented and action-residual carriers are not yet crosswalked into the same frozen typed ledger. Gate A remains fail closed at one of seven hashes.",
    })

    old = {row["route"]: deepcopy(row) for row in previous["route_selection"]}
    ordered = [
        route("STRICT_M1A3_REPRESENTED_CROSSWALK", 1, "VERY_HIGH", "MEDIUM", "LOW", "Crosswalk the 4,080 endpoint-harmonic coordinates, classify the separate 410 scalar test-nonminimal coordinates, and type the 470 primal plus 470 action-dual residual rows without identifying distinct carriers."),
        route("STRICT_M1A4_LEDGER_FREEZE", 2, "VERY_HIGH", "HIGH", "LOW", "Freeze the represented crosswalk and the completed 386-row local semantics as one versioned typed diagram with explicit inclusion and exclusion ledgers."),
        route("STRICT_M1B_REPRESENTED_COMPOSITE_CONTRACTION", 3, "VERY_HIGH", "MEDIUM", "MEDIUM", "Materialize and independently replay pi_cl, iota_cl, s_cl and the action pairing across the frozen typed carriers."),
        route("STRICT_M1C_COMMON_MANIFEST_REPLAY", 4, "VERY_HIGH", "HIGH", "MEDIUM", "Bind all twenty exports and seven hashes, then replay all ten Gate-A checks on exactly one immutable manifest."),
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
    value["research_queue"] = [
        {
            "priority": row["rank"],
            "branch": row["branch"],
            "object": row["route"],
            "why": row["recommendation"],
        }
        for row in ordered
    ]
    value["frontier_summary"] = {
        "highest_value_next_route": "STRICT_M1A3_REPRESENTED_CROSSWALK",
        "route_count": len(ordered),
        "completed_since_v44": ["STRICT_M1A2_LOCAL_SEMANTIC_EXTENSION", "GATE_V27_LOCAL_SEMANTIC_RECONCILIATION"],
        "new_positive_result": "Every local row is now semantically explicit: 30 endpoint, 36 shifted auxiliary and 320 fixed-background mapping-cone rows, with zero unresolved local fields.",
        "surprise": "The Cotton resolution slot is provably not a nonlinear Weyl eigenrow. Its exact triangular transformation makes scalar row weight not applicable, rather than missing data.",
        "hard_boundary": "M1A is not complete until the represented endpoint, test-nonminimal and 940 action-residual coordinates are crosswalked and frozen. The formal 8,980-coordinate comparison remains non-authoritative.",
    }
    value["claim_flags"].update({
        "v44_preserved": True,
        "strict_M1A2_local_semantic_extension_complete": True,
        "strict_local_386_fully_typed": True,
        "strict_M1A3_represented_crosswalk_complete": False,
        "strict_M1A4_ledger_freeze_complete": False,
        "strict_M1A_full_typed_carrier_ledger_complete": False,
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
        "M1A completion from local 386-row coverage without the represented and action-residual crosswalk",
        "a scalar nonlinear Weyl weight for the fixed-background Cotton resolution rows",
        "a passed Gate A, full-complex Hadamard state, renormalized products, QME restoration or residual transfer",
    ]))
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREDECESSOR), "role": "immutable V44 predecessor"},
        {"path": str(LOCAL.relative_to(ROOT)), "result_or_artifact_id": local["result_id"], "sha256": sha(LOCAL), "role": "independently checked local M1A2 semantic extension"},
        {"path": str(GATE.relative_to(ROOT)), "result_or_artifact_id": gate["result_id"], "sha256": sha(GATE), "role": "Gate-A V27 local-semantic reconciliation"},
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v45.py",
        "checks": [
            "V44 predecessor and 77-cell preservation",
            "Gate V27 and M1A2 independent replay",
            "36+320+30 equals 386 complete local rows",
            "2,560-component Cotton non-eigen witness",
            "M1A3/M1A4/M1B/M1C route ordering",
            "one accepted hash and fail-closed Gate A",
            "formal-source/Hadamard/QME firewalls",
            "canonical atlas digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    local = value["strict_m1a_local_semantic_extension"]
    routes = "\n".join(
        f"{row['rank']}. `{row['route']}` — {row['recommendation']}"
        for row in value["route_selection"]
    )
    return f"""# Lorentzian Weyl BV completion atlas v45

**Result:** `{value['result_id']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Decision

Local M1A2 is complete.  All **{local['local_386_rows_fully_namespaced']} of
386** local graph rows are explicitly namespaced, with zero unresolved local
rows.  The exact {local['cotton_component_checks']:,}-component Cotton
transformation check has zero defects and proves that scalar nonlinear Weyl
weight is `NOT_APPLICABLE` on the fixed-background cone rows.

M1A now has two concrete successors: the represented-coordinate crosswalk and
the immutable ledger freeze.  Gate A remains fail closed at one of seven
accepted hashes.

## Ranked routes

{routes}

## Boundary

The local semantic result does not type the 4,080 represented endpoint
coordinates, the separate 410 test-nonminimal coordinates, or the 470+470
action-residual carrier.  It establishes no passed Gate A, full-complex
Hadamard state, renormalized product, QME restoration, residual transfer or
Lorentzian quantum theory.
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V45: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V45: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
