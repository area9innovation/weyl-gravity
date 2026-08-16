#!/usr/bin/env python3
"""Build Atlas V46 after the complete M1A typed-diagram freeze."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V45.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V28_RECONCILIATION.json"
M1A3 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1.json"
M1A4 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V46.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v46.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
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
    branch = next(item for item in value["branches"] if item["id"] == branch_id)
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def route(route_id: str, rank: int, leverage: str, tractability: str, dependency: str, recommendation: str) -> dict[str, Any]:
    return {
        "rank": rank, "route": route_id, "branch": "STRICT_PURE_WEYL_386",
        "scientific_leverage": leverage, "tractability": tractability,
        "dependency_depth": dependency, "recommendation": recommendation,
    }


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    m1a3 = json.loads(M1A3.read_text(encoding="utf-8"))
    m1a4 = json.loads(M1A4.read_text(encoding="utf-8"))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V45":
        raise ValueError("Atlas V45 predecessor drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V28_RECONCILIATION":
        raise ValueError("Gate V28 unavailable")
    if m1a3.get("result_id") != "STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1" or m1a4.get("result_id") != "STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1":
        raise ValueError("M1A3/M1A4 unavailable")
    if (
        gate["claim_flags"].get("M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE") is not True
        or gate["claim_flags"].get("M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE") is not False
        or gate["claim_flags"].get("CLASSICAL_IMPORT_GATE_PASSED") is not False
        or m1a3["claim_flags"].get("M1A3_REPRESENTED_CROSSWALK_COMPLETE") is not True
        or m1a4["claim_flags"].get("M1A4_IMMUTABLE_LEDGER_FREEZE_COMPLETE") is not True
    ):
        raise ValueError("M1A/Gate-A firewall drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v46",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V46",
        "created": "2026-08-16",
        "question": "What is the highest-leverage route after the complete M1A typed-carrier freeze?",
        "answer": "Atlas V46 closes M1A. The 386 local rows, 4,080 represented endpoint rows, 470+470 action-residual rows, thirty zero modes and 12,343 centered cochains are content-addressed as six distinct authoritative objects. The 410 test coordinates are exactly 205 comparison-only doublets, and the formal 8,980-coordinate cotangent remains non-authoritative. The frontier is now M1B: construct the composite contraction as typed arrows through the local endpoint and harmonic realization, not as a false 386-by-940 matrix. M1C and Gate A remain downstream and fail closed.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v46.md",
    })
    disposition = gate["gate_disposition"]
    resolution = gate["m1a_completion_resolution"]
    value["strict_gate_v28_reconciliation"] = {
        "result_id": gate["result_id"], "status": gate["result_state"],
        "exports_total": disposition["exports_total"],
        "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": disposition["freeze_checks_total"],
        "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "remaining_top_level_hashes": 7 - disposition["accepted_common_snapshot_hashes"],
        "authoritative_rows_total": resolution["authoritative_rows_total"],
        "M1A_complete": resolution["M1A_complete"],
        "M1B_represented_composite_contraction_complete": gate["claim_flags"]["M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE"],
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
        "minimal_missing_bundle": [item["id"] for item in gate["minimal_missing_bundle"]],
    }
    value["strict_m1a_represented_crosswalk"] = {
        "result_id": m1a3["result_id"], "status": m1a3["result_state"],
        "represented_endpoint_rows": m1a3["counts"]["represented_endpoint_coordinates"],
        "represented_endpoint_sectors": m1a3["counts"]["represented_endpoint_sectors"],
        "local_endpoint_species_crosswalked": m1a3["counts"]["local_endpoint_species_crosswalked"],
        "excluded_test_rows": m1a3["counts"]["test_nonminimal_coordinates_excluded"],
        "excluded_test_doublets": m1a3["counts"]["test_nonminimal_doublets"],
        "action_residual_primal_rows": m1a3["counts"]["action_residual_primal_coordinates"],
        "action_residual_dual_rows": m1a3["counts"]["action_residual_dual_coordinates"],
        "q0_cross_partition_defects": m1a3["counts"]["q0_cross_partition_defects"],
        "q0_chain_degree_defects": m1a3["counts"]["q0_chain_degree_defects"],
        "residual_crosswalk_defects": m1a3["counts"]["residual_crosswalk_defects"],
        "M1A3_complete": True,
    }
    value["strict_m1a_immutable_typed_ledger"] = {
        "result_id": m1a4["result_id"], "status": m1a4["result_state"],
        "authoritative_rows_total": m1a4["counts"]["authoritative_rows_total"],
        "authoritative_carrier_objects": m1a4["counts"]["authoritative_carrier_objects"],
        "untyped_authoritative_rows": m1a4["counts"]["untyped_authoritative_rows"],
        "category_identification_defects": m1a4["counts"]["category_identification_defects"],
        "typed_field_dictionary_sha256": m1a4["typed_field_dictionary"]["sha256"],
        "typed_diagram_sha256": m1a4["diagram_freeze"]["sha256"],
        "M1A4_complete": True, "M1A_complete": True,
    }

    s0 = stage(value, "STRICT_PURE_WEYL_386", "S0_CLASSICAL_AUTHORITY")
    s0.update({
        "statement": "M1A is complete: 17,779 rows across six distinct authoritative carrier objects are content-addressed with zero untyped rows. The remaining authority gate is the M1B typed composite contraction followed by the M1C common-byte replay.",
        "evidence": list(dict.fromkeys([*s0["evidence"], m1a3["result_id"], m1a4["result_id"], gate["result_id"]])),
        "boundary": "A typed diagram is not yet a composite contraction. The local 386-to-30 support-local arrow and global harmonic/action-residual arrows must be composed without identifying their source categories. Gate A remains fail closed at one of seven hashes.",
    })

    old = {row["route"]: deepcopy(row) for row in previous["route_selection"]}
    ordered = [
        route("STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION", 1, "VERY_HIGH", "MEDIUM", "LOW", "Materialize the typed primal composite from the 386-row graph through the thirty endpoint species and finite harmonic realization to all 470 residual classes; serialize operator formulas and exact coordinate actions without inventing a 386-by-470 component matrix."),
        route("STRICT_M1B_ACTION_DUAL_LIFT", 2, "VERY_HIGH", "MEDIUM", "MEDIUM", "Lift the primal composite through the action-derived compact-source dual, retaining the distinction between the represented 470-dimensional dual and any full continuous dual."),
        route("STRICT_M1B_TYPED_CYCLIC_REPLAY", 3, "VERY_HIGH", "MEDIUM", "MEDIUM", "Assemble pi_cl, iota_cl, s_cl and the rank-940 action pairing as one typed contraction and replay chain, side-condition, adjoint and cyclic identities on the frozen M1A hashes."),
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
        {"priority": row["rank"], "branch": row["branch"], "object": row["route"], "why": row["recommendation"]}
        for row in ordered
    ]
    value["frontier_summary"] = {
        "highest_value_next_route": "STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION",
        "route_count": len(ordered),
        "completed_since_v45": ["STRICT_M1A3_REPRESENTED_CROSSWALK", "STRICT_M1A4_IMMUTABLE_TYPED_LEDGER", "GATE_V28_M1A_RECONCILIATION"],
        "new_positive_result": "M1A is complete: 17,779 authoritative rows are content-addressed across six category-distinct carriers with zero untyped rows or category-identification defects.",
        "surprise": "The historical 410-coordinate ambiguity is exactly 205 isolated q0 test doublets. Exclusion, not guessed BV typing, yields the authoritative 4,080-coordinate represented endpoint.",
        "hard_boundary": "M1B must be a typed composition of local, harmonic and compact-source arrows. No single finite matrix may identify 386 local component species with 940 global residual coordinates, and the formal 8,980-coordinate comparison remains non-authoritative.",
    }
    value["claim_flags"].update({
        "v45_preserved": True,
        "strict_M1A3_represented_crosswalk_complete": True,
        "strict_M1A4_ledger_freeze_complete": True,
        "strict_M1A_full_typed_carrier_ledger_complete": True,
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
        "M1B composite contraction or M1C common replay from a typed row freeze alone",
        "a componentwise identification of local species with global harmonic or residual coordinates",
        "that the test-doublet or formal-cotangent comparison carriers are authoritative source fields",
        "a passed Gate A, full-complex Hadamard state, renormalized products, QME restoration or residual transfer",
    ]))
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREDECESSOR), "role": "immutable V45 predecessor"},
        {"path": str(M1A3.relative_to(ROOT)), "result_or_artifact_id": m1a3["result_id"], "sha256": sha(M1A3), "role": "represented and action-residual crosswalk"},
        {"path": str(M1A4.relative_to(ROOT)), "result_or_artifact_id": m1a4["result_id"], "sha256": sha(M1A4), "role": "immutable M1A typed diagram"},
        {"path": str(GATE.relative_to(ROOT)), "result_or_artifact_id": gate["result_id"], "sha256": sha(GATE), "role": "Gate-A V28 M1A reconciliation"},
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v46.py",
        "checks": [
            "V45 predecessor and 77-cell preservation", "Gate V28 and M1A3/M1A4 independent replay",
            "4,080+410 D-finite partition and 470+470 action residual", "17,779-row six-carrier freeze",
            "M1B primal/dual/cyclic route decomposition", "one accepted hash and fail-closed Gate A",
            "formal-source/Hadamard/QME firewalls", "canonical atlas digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    ledger = value["strict_m1a_immutable_typed_ledger"]
    crosswalk = value["strict_m1a_represented_crosswalk"]
    routes = "\n".join(f"{row['rank']}. `{row['route']}` — {row['recommendation']}" for row in value["route_selection"])
    return f"""# Lorentzian Weyl BV completion atlas v46

**Result:** `{value['result_id']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Decision

M1A is complete.  The typed diagram freezes **{ledger['authoritative_rows_total']:,}
authoritative rows** across {ledger['authoritative_carrier_objects']} distinct
carrier objects, with zero untyped rows and zero category-identification
defects.  The represented endpoint contains {crosswalk['represented_endpoint_rows']:,}
rows; the wider D-finite control contributes {crosswalk['excluded_test_rows']}
explicitly excluded rows, exactly {crosswalk['excluded_test_doublets']} q0
test doublets.  The rank-940 action residual is typed as 470 primal plus 470
compact-source dual rows.

The next frontier is M1B.  It must be assembled as a typed diagram of arrows,
not as a false matrix identifying 386 position-space component species with
940 global residual coordinates.

## Ranked routes

{routes}

## Boundary

M1A supplies the immutable row domains and candidate field-dictionary hash.
It does not supply the M1B composite contraction or the M1C common replay.
Gate A remains fail closed at one of seven hashes.  No full-complex Hadamard
state, renormalized Lorentzian product, QME restoration, residual transfer or
Lorentzian quantum theory is established.
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False).encode() + b"\n", report(value).encode())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V46: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V46: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
