#!/usr/bin/env python3
"""Build Atlas V38 after typed local cyclic-pairing closure."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V37.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V20_RECONCILIATION.json"
M4L = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V38.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v38.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v20_reconciliation", "strict_local_cyclic_pairing_closure",
        "strict_common_endpoint_sdr_binding", "strict_residual_sdr_type_audit",
        "strict_source_q2_common_assembly", "strict_source_q3_common_assembly",
        "strict_residual_zero_mode_payload", "strict_centered_cohomology_payload",
        "route_selection", "research_queue",
    )
    return hashlib.sha256(json.dumps(
        {key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(item for item in value["branches"] if item["id"] == branch_id)
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    closure = json.loads(M4L.read_text(encoding="utf-8"))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V37":
        raise ValueError("Atlas V37 predecessor drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V20_RECONCILIATION":
        raise ValueError("Gate V20 unavailable")
    if closure.get("result_id") != "STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1":
        raise ValueError("M4L closure unavailable")
    if gate["claim_flags"]["M4L_LOCAL_GRAPH_CYCLIC_PAIRING_COMPLETE"] is not True:
        raise ValueError("Gate V20 does not accept scoped M4L completion")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v38",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V38",
        "created": "2026-08-16",
        "question": "After closing the full local graph cyclic pairing, what is the strongest surviving route toward Lorentzian Weyl BV completion?",
        "answer": "Atlas V38 closes M4L and removes the misleading suggestion that residual cyclicity is another unchecked block of the 386-row local pairing. The full local graph carrier has an exact nondegenerate pairing and zero q1/SDR/D/q2/q3 cyclicity defects. The highest-value route is now M3R: construct the typed endpoint-to-W+/W- harmonic comparison. Its induced pairing and cyclicity form M4R, the next dependent gate. Only then can the common M1 freeze be attempted. Gate A remains fail closed at one of seven hashes, so no Hadamard or QME stage is promoted.",
        "predecessor": {
            "result_id": previous["result_id"],
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "sha256": sha(PREDECESSOR),
            "preserved": True,
        },
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v38.md",
    })
    value.pop("strict_gate_v19_reconciliation", None)
    disposition = gate["gate_disposition"]
    value["strict_gate_v20_reconciliation"] = {
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
    value["strict_local_cyclic_pairing_closure"] = {
        "result_id": closure["result_id"],
        "carrier_rows": closure["pairing_replay"]["carrier_rows"],
        "pairing_entries": closure["pairing_replay"]["nonzero_ordered_pairing_entries"],
        "exact_pairing_rank": closure["pairing_replay"]["exact_rational_rank"],
        "local_cyclicity_defects": sum(
            count for key, count in closure["local_cyclicity_replay"].items() if key.endswith("defects")
        ),
        "M4L_status": "COMPLETE",
        "M4R_status": "OPEN_BLOCKED_BY_M3R",
        "residual_rows_in_local_carrier": 0,
    }
    s0 = stage(value, "STRICT_PURE_WEYL_386", "S0_CLASSICAL_AUTHORITY")
    s0.update({
        "statement": "The common 386-row q1/q2/q3/D/endpoint-SDR carrier now also has a complete rank-386 local odd pairing and zero local cyclicity defects. M3R and its induced M4R residual cyclicity remain separately typed, followed by the M1 freeze.",
        "evidence": list(dict.fromkeys([*s0["evidence"], closure["result_id"], gate["result_id"]])),
        "boundary": "M4L closes only the local graph carrier. It neither constructs the global harmonic comparison M3R nor its induced REDUCED-MODE pairing/cyclicity M4R, and it accepts no new Gate-A hash.",
    })

    prior = {row["route"]: deepcopy(row) for row in previous["route_selection"]}
    residual_route = deepcopy(prior["STRICT_FULL_CYCLIC_PAIRING"])
    residual_route.update({
        "route": "STRICT_TYPED_RESIDUAL_CYCLICITY",
        "scientific_leverage": "VERY_HIGH",
        "tractability": "MEDIUM",
        "dependency_depth": "HIGH",
        "recommendation": "After M3R fixes the comparison maps and domains, derive the induced W+/W- pairing and replay q_res, inclusion/projection, homotopy and transfer cyclic side conditions without importing local-row identities as substitutes.",
    })
    prior["STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON"]["recommendation"] = "Construct M3R as a typed harmonic restriction/comparison from endpoint sections to W+/W- coefficients, with explicit test/distribution domains, zero-mode policy, normalization and REDUCED-MODE labels for every support-expanding map."
    prior["STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION"]["recommendation"] = "After M3R and M4R, bind the local and reduced-mode objects under one typed M1 manifest and accept each top-level hash only after its category-correct identities replay."
    names = [
        "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON",
        "STRICT_TYPED_RESIDUAL_CYCLICITY",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION",
        "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE",
        "DIRECT_SPACETIME_Q26_HADAMARD",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION",
        "STRICT_ANALYTIC_MOLLER_CONVERGENCE",
        "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
    ]
    prior["STRICT_TYPED_RESIDUAL_CYCLICITY"] = residual_route
    ordered = [prior[name] for name in names]
    for rank, row in enumerate(ordered, 1):
        row["rank"] = rank
    value["route_selection"] = ordered
    why = {
        "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON": "M3R is now the first genuinely missing mathematical object: a typed global bridge from local endpoint sections to W+/W- coefficients.",
        "STRICT_TYPED_RESIDUAL_CYCLICITY": "M4R is well posed only after M3R fixes the comparison and normalization; local M4L is already complete.",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION": "The M1 freeze becomes meaningful only after both reduced-mode obligations close.",
    }
    value["research_queue"] = [
        {"priority": row["rank"], "branch": row["branch"], "object": row["route"], "why": why.get(row["route"], row["recommendation"])}
        for row in ordered
    ]
    value["frontier_summary"] = {
        "highest_value_next_route": "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON",
        "route_count": len(ordered),
        "completed_since_v37": ["STRICT_FULL_LOCAL_CYCLIC_PAIRING", "M4L_TYPED_GATE_INTEGRATION"],
        "new_positive_result": "All 386 local graph rows carry one exact nondegenerate odd pairing, and q1/endpoint-SDR/D/q2/q3 cyclicity closes on the M3L common manifest.",
        "new_no_go": "The old M4 requirement cannot be one untyped matrix problem: the 386 local rows contain zero W+/W- residual coefficient rows, so residual cyclicity is undefined before M3R.",
        "surprise": "The expensive-looking local M4 extension had already been built incrementally. Exact integration and a type census, not new pairing coefficients, close M4L.",
        "hard_boundary": "M3R typed spectral comparison, induced M4R cyclicity, M1 freeze, six hashes, nonlinear Green compatibility, Hadamard and QME remain open.",
    }
    value["claim_flags"].update({
        "v37_preserved": True,
        "strict_386_full_local_odd_pairing_nondegenerate": True,
        "strict_386_local_q1_sdr_D_q2_q3_cyclicity_complete": True,
        "strict_M4L_local_graph_cyclic_pairing_complete": True,
        "strict_M4R_typed_residual_cyclicity_complete": False,
        "strict_M3R_typed_residual_comparison_constructed": False,
        "strict_full_residual_cyclic_pairing_certified": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_q2_q3_green_compatibility_certified": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREDECESSOR), "role": "immutable V37 predecessor"},
        {"path": str(M4L.relative_to(ROOT)), "result_or_artifact_id": closure["result_id"], "sha256": sha(M4L), "role": "typed M4L local cyclic-pairing closure"},
        {"path": str(GATE.relative_to(ROOT)), "result_or_artifact_id": gate["result_id"], "sha256": sha(GATE), "role": "Gate-A V20 typed M4 reconciliation"},
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v38.py",
        "checks": [
            "V37 predecessor and 77-cell preservation",
            "Gate V20 and M4L content pins",
            "386-row rank-386 pairing and zero local cyclicity defects",
            "M4L completion with M3R/M4R type firewalls",
            "three-package Gate remainder and one accepted hash",
            "nine-route reranking with M3R first",
            "Gate-A/Green/Hadamard/QME firewalls",
            "canonical atlas digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    closure = value["strict_local_cyclic_pairing_closure"]
    gate = value["strict_gate_v20_reconciliation"]
    routes = "\n".join(f"{row['rank']}. `{row['route']}` — {row['recommendation']}" for row in value["route_selection"])
    return f"""# Lorentzian Weyl BV completion atlas v38

**Result:** `{value['result_id']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Decision

M4L is complete.  The common local carrier has {closure['carrier_rows']} rows,
an exact rank-{closure['exact_pairing_rank']} odd pairing with
{closure['pairing_entries']} ordered rational entries, and
{closure['local_cyclicity_defects']} combined q1/SDR/D/q2/q3 cyclicity defects.
It contains {closure['residual_rows_in_local_carrier']} W+/W- residual rows.

The remaining cyclicity task is therefore M4R, a `REDUCED-MODE` construction
that depends on M3R.  Gate V20 still accepts {gate['accepted_top_level_hashes']}
of seven hashes; M1, M3R and M4R remain open.

## Ranked routes

{routes}

## Boundary

No endpoint-to-residual comparison, residual pairing, nonlinear Green
compatibility, full-complex Hadamard state, renormalized Lorentzian product,
QME restoration or residual quantum transfer is claimed.
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V38: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V38: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
