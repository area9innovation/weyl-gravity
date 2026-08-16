#!/usr/bin/env python3
"""Build Atlas V36 after the residual-SDR type/locality repair."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V35.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V18_RECONCILIATION.json"
AUDIT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V36.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v36.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v18_reconciliation", "strict_residual_sdr_type_audit",
        "strict_source_q2_common_assembly", "strict_source_q3_common_assembly",
        "strict_residual_zero_mode_payload", "strict_centered_cohomology_payload",
        "route_selection", "research_queue",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(item for item in value["branches"] if item["id"] == branch_id)
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V35":
        raise ValueError("Atlas V35 predecessor drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V18_RECONCILIATION" or gate["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate V18 unavailable")
    if audit.get("result_id") != "STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1" or audit["claim_flags"]["M3_TYPED_SPLIT_REQUIRED"] is not True:
        raise ValueError("M3 type audit unavailable")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v36",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V36",
        "created": "2026-08-16",
        "question": "After separating local endpoint contraction from global residual projection, what is the strongest viable route toward a Lorentzian Weyl BV completion?",
        "answer": "Atlas V36 rejects the former single M3 route as ill-typed. The exact support-local 386-to-30 endpoint SDR is preserved and now needs common-hash binding, while the W+/W- harmonic comparison is a distinct REDUCED-MODE construction whose global projections must not be used as local Green-transfer maps. The strongest route is therefore to bind the existing graph endpoint SDR, close its full cyclic pairing, construct the typed endpoint-to-residual spectral comparison in parallel, and only then perform the all-object freeze. This removes a false shortcut without rejecting the surviving local causal architecture.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v36.md",
    })
    value.pop("strict_gate_v17_reconciliation", None)
    disposition = gate["gate_disposition"]
    value["strict_gate_v18_reconciliation"] = {
        "result_id": gate["result_id"],
        "status": gate["result_state"],
        "exports_total": len(gate["export_reconciliation"]),
        "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": len(gate["freeze_check_reconciliation"]),
        "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "remaining_top_level_hashes": 7 - disposition["accepted_common_snapshot_hashes"],
        "minimal_missing_bundle": [item["id"] for item in gate["minimal_missing_bundle"]],
        "M3_typed_split_required": gate["claim_flags"]["M3_TYPED_SPLIT_REQUIRED"],
        "M3L_common_endpoint_sdr_bound": gate["claim_flags"]["M3L_COMMON_ENDPOINT_SDR_BOUND"],
        "M3R_typed_residual_comparison_constructed": gate["claim_flags"]["M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED"],
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
    value["strict_residual_sdr_type_audit"] = {
        "result_id": audit["result_id"],
        "type_census_sha256": audit["type_census"]["sha256"],
        "architecture_decision_sha256": audit["architecture_decision"]["sha256"],
        "graph_carrier_component_species": 386,
        "graph_endpoint_component_species": 30,
        "dfinite_full_coordinates": 4490,
        "dfinite_residual_coordinates": 470,
        "symmetry_cotangent_coordinates": 30,
        "graph_endpoint_is_symmetry_cotangent": False,
        "dfinite_projector_support_local": False,
        "M3_typed_split_required": True,
    }
    s0 = stage(value, "STRICT_PURE_WEYL_386", "S0_CLASSICAL_AUTHORITY")
    s0.update({
        "statement": "The q1/q2/q3/D/pairing, exact local graph endpoint SDR, residual zero modes and centered H4 payload all exist in scoped exact forms. The local endpoint SDR, finite W+/W- residual SDR and symmetry cotangent payload are now explicitly separated by type; common binding, a typed spectral comparison and full cyclic freeze remain open.",
        "evidence": list(dict.fromkeys([*s0["evidence"], audit["result_id"], gate["result_id"]])),
        "boundary": "A global harmonic or zero-mode projector is not support-local. It cannot be substituted for the local endpoint SDR in Green-homotopy transfer, and no common hash, Hadamard state or QME is promoted.",
    })

    by_route = {row["route"]: deepcopy(row) for row in previous["route_selection"]}
    by_route.pop("STRICT_RESIDUAL_SDR_COMMON_CARRIER")
    by_route["STRICT_COMMON_ENDPOINT_SDR_BINDING"] = {
        "route": "STRICT_COMMON_ENDPOINT_SDR_BINDING",
        "branch": "STRICT_PURE_WEYL_386",
        "scientific_leverage": "VERY_HIGH",
        "tractability": "HIGH",
        "dependency_depth": "LOW",
        "recommendation": "Bind the already exact graph-coordinate i_end, p_end and H_alg, transported suspension and q1 bytes to the same strict manifest used by q2/q3/D; replay the contraction and intertwiners without rebuilding a different SDR.",
    }
    by_route["STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON"] = {
        "route": "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON",
        "branch": "STRICT_PURE_WEYL_386",
        "scientific_leverage": "VERY_HIGH",
        "tractability": "LOW",
        "dependency_depth": "HIGH",
        "recommendation": "Construct a typed harmonic restriction/comparison from endpoint sections to W+/W- residual coefficients, declare test/distribution domains and zero-mode policy, and label every support-expanding projection REDUCED-MODE rather than local.",
    }
    ordered_names = [
        "STRICT_COMMON_ENDPOINT_SDR_BINDING",
        "STRICT_FULL_CYCLIC_PAIRING",
        "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION",
        "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE",
        "DIRECT_SPACETIME_Q26_HADAMARD",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION",
        "STRICT_ANALYTIC_MOLLER_CONVERGENCE",
        "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
    ]
    ordered = [by_route[name] for name in ordered_names]
    by_route["STRICT_FULL_CYCLIC_PAIRING"]["recommendation"] = "On the common endpoint SDR carrier, replay the serialized 386-row pairing against q1/q2/q3 and every SDR cyclic side condition; do not couple it to global-mode projection until M3R is separately typed."
    by_route["STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION"]["recommendation"] = "After M3L, M3R and M4, bind q1/q2/q3/D, endpoint SDR, residual comparison, zero modes, centered representatives and pairing to one manifest; accept hashes only after all identities replay in their declared categories."
    for rank, row in enumerate(ordered, 1):
        row["rank"] = rank
    value["route_selection"] = ordered
    why = {
        "STRICT_COMMON_ENDPOINT_SDR_BINDING": "The exact support-local graph SDR already exists; the next task is a common-byte binding and replay, not a speculative reconstruction of a finite residual projector.",
        "STRICT_FULL_CYCLIC_PAIRING": "The full 386-row pairing is already serialized and can be closed against the common endpoint SDR while the harder spectral comparison proceeds independently.",
        "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON": "Residual and centered data become relevant to the field theory only through a typed harmonic restriction that admits its nonlocality.",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION": "The freeze becomes honest only after local and reduced-mode maps are distinct, manifest-bound and independently replayed.",
    }
    value["research_queue"] = [
        {"priority": row["rank"], "branch": row["branch"], "object": row["route"], "why": why.get(row["route"], row["recommendation"])}
        for row in ordered
    ]
    value["frontier_summary"] = {
        "highest_value_next_route": ordered[0]["route"],
        "route_count": len(ordered),
        "completed_since_v35": ["STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT", "GATE_V18_M3_TYPED_REPAIR"],
        "new_positive_result": "The exact support-local graph endpoint SDR survives unchanged and is now cleanly separated from both finite W+/W- harmonic cohomology and conformal-Killing cotangent data.",
        "new_no_go": "The specified global harmonic and zero-mode projectors expand support, so they cannot be promoted directly to support-local maps in the Green-homotopy transfer premise.",
        "surprise": "The leading M3 task was partly a type error: the two occurrences of dimension thirty counted local field species and global symmetry-cotangent coefficients, not the same vector space.",
        "hard_boundary": "M3L common binding, M3R typed spectral comparison, M4 pairing, M1 freeze, six hashes, nonlinear Green compatibility, Hadamard and QME remain open.",
    }
    value["claim_flags"].update({
        "v35_preserved": True,
        "strict_386_graph_endpoint_sdr_support_local": True,
        "strict_graph_endpoint_30_is_finite_residual_30": False,
        "strict_dfinite_residual_projector_support_local": False,
        "strict_zero_mode_projector_support_local": False,
        "strict_M3_typed_split_required": True,
        "strict_M3L_common_endpoint_sdr_bound": False,
        "strict_M3R_typed_residual_comparison_constructed": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_q2_q3_green_compatibility_certified": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREDECESSOR), "role": "immutable V35 predecessor"},
        {"path": str(AUDIT.relative_to(ROOT)), "result_or_artifact_id": audit["result_id"], "sha256": sha(AUDIT), "role": "M3 carrier-type and locality decision"},
        {"path": str(GATE.relative_to(ROOT)), "result_or_artifact_id": gate["result_id"], "sha256": sha(GATE), "role": "Gate-A V18 typed M3 reconciliation"},
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v36.py",
        "checks": [
            "V35 predecessor and 77-cell preservation", "Gate V18 and type-audit pins",
            "386/30 local, 4,490/470 harmonic and 30 symmetry-cotangent type census",
            "M3L/M3R split and support-locality firewall", "four-package Gate remainder",
            "ten-route reranking", "Gate-A/Green/Hadamard/QME firewalls",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    audit = value["strict_residual_sdr_type_audit"]
    gate = value["strict_gate_v18_reconciliation"]
    routes = "\n".join(f"{row['rank']}. `{row['route']}` — {row['recommendation']}" for row in value["route_selection"])
    return f"""# Lorentzian Weyl BV completion atlas v36

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Decision

The old M3 route is not one map.  The exact graph SDR relates
{audit['graph_carrier_component_species']} local component species to
{audit['graph_endpoint_component_species']} local endpoint species.  The
D-finite residual SDR relates {audit['dfinite_full_coordinates']:,} harmonic
coefficients to {audit['dfinite_residual_coordinates']} W+/W- coefficients.
The separate M5 `30` counts global symmetry-cotangent coefficients.

The specified harmonic and zero-mode projectors expand support.  They cannot
be passed as support-local maps to the causal transfer theorem.  This removes
a false shortcut while preserving the exact local graph SDR and every
reduced-mode theorem in its proper category.

Gate V18 still accepts {gate['accepted_top_level_hashes']} of seven hashes and
leaves M1, M3L, M3R and M4 open.

## Ranked routes

{routes}

## Boundary

No new Green homotopy, Hadamard state, renormalized product, QME or residual
quantum transfer is claimed.
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), report(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V36: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V36: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
