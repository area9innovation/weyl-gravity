#!/usr/bin/env python3
"""Build Atlas V32 after the accepted common source-q2 assembly."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V31.json"
ASSEMBLY = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json"
GATE_V14 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V14_RECONCILIATION.json"
DIFF_V2 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2.json"
MASS = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V32.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v32.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = ("stages", "branches", "frontier_summary", "classical_import_reconciliation", "strict_gate_v14_reconciliation", "strict_source_q2_common_assembly", "route_selection", "research_queue")
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(item for item in value["branches"] if item["id"] == branch_id)
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous, assembly, gate, diff, mass = (json.loads(path.read_text()) for path in (PREDECESSOR, ASSEMBLY, GATE_V14, DIFF_V2, MASS))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V31":
        raise ValueError("Atlas V31 predecessor drift")
    if assembly.get("result_id") != "STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1" or not assembly["claim_flags"]["FULL_SHIFTED_SOURCE_Q2_COMMON_UNION_ASSEMBLED"]:
        raise ValueError("source-q2 common assembly unavailable")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V14_RECONCILIATION" or gate["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate V14 unavailable")
    if gate["gate_disposition"]["accepted_common_snapshot_hashes"] != 1 or gate["claim_flags"]["STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED"]:
        raise ValueError("Gate V14 q2/q3 boundary drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v32",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V32",
        "created": "2026-08-15",
        "question": "After accepting one common source-q2 hash, what is the strongest next Lorentzian Weyl BV completion route?",
        "answer": "Atlas V32 closes the arity-two assembly route. The authoritative shifted-source q2 now combines 22 minimal operations with 2,064 auxiliary component coefficients, extends by zero over the 320 receiver-added split-cone rows, and transports exactly to graph coordinates. Common q1/q2, cyclicity and stationary D/q2 defects all vanish. The highest-value next route is therefore the metric-dependent auxiliary q3: compute the h-h-f_hat-f_hat quartic action variation, pair-lift it, assemble it with minimal q3 and replay arity three. Gate A remains fail closed with one of seven hashes accepted.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v32.md",
    })
    value["strict_nonlinear_weyl_boost_ghost_manifest"]["full_386_source_q2_assembled"] = True
    value["strict_source_q2_common_assembly"] = {
        "result_id": assembly["result_id"],
        "accepted_source_q2_sha256": assembly["source_q2_snapshot"]["sha256"],
        "minimal_ordered_symbolic_components": assembly["source_q2_snapshot"]["minimal_ordered_symbolic_components"],
        "auxiliary_ordered_component_coefficients": assembly["source_q2_snapshot"]["auxiliary_ordered_component_coefficients"],
        "source_q2_families": assembly["family_census"]["total_shifted_source_q2_families"],
        "graph_block_triples": assembly["graph_transport"]["graph_block_triples"],
        "q1_q2_defects": assembly["q1_q2_replay"]["graph_386_q1_q2_defects"],
        "q2_cyclicity_defects": assembly["q2_cyclicity_replay"]["graph_386_q2_cyclicity_defects"],
        "D_q2_defects": assembly["D_q2_replay"]["graph_D_q2_derivation_defects"],
        "full_source_q3_assembled": False,
        "first_missing_q3_vertex": assembly["q3_boundary"]["first_missing_vertex"],
        "rejected_v1_q1_q2_defects": diff["canonical_sign_repair"]["unrepaired_q1_q2_nonzero_coefficients"],
        "accepted_v2_q1_q2_defects": diff["canonical_sign_repair"]["repaired_q1_q2_nonzero_coefficients"],
        "shifted_mass_cyclicity_equalities": mass["exact_replay"]["cyclicity_equalities_checked"],
    }
    disposition = gate["gate_disposition"]
    value["strict_gate_v14_reconciliation"] = {
        "result_id": gate["result_id"], "status": gate["result_state"],
        "exports_total": len(gate["export_reconciliation"]), "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": len(gate["freeze_check_reconciliation"]), "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "gate_a_status": disposition["gate_a_status"],
        "full_source_q2_assembled": gate["claim_flags"]["STRICT_386_FULL_SOURCE_Q2_ASSEMBLED"],
        "full_source_q3_assembled": gate["claim_flags"]["STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED"],
    }
    value.pop("strict_gate_v13_reconciliation", None)
    value["classical_import_reconciliation"] = {
        "result_id": gate["result_id"], "status": gate["result_state"],
        "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "exports_total": len(gate["export_reconciliation"]),
        "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "freeze_checks_total": len(gate["freeze_check_reconciliation"]),
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "gate_a_status": disposition["gate_a_status"],
        "minimal_missing_bundle": [item["id"] for item in gate["minimal_missing_bundle"]],
    }
    s0 = stage(value, "STRICT_PURE_WEYL_386", "S0_CLASSICAL_AUTHORITY")
    s0.update({
        "statement": "The authoritative shifted-source q2 is assembled and one common q2 hash is accepted. Its split and graph q1/q2, cyclicity and D/q2 identities have zero defects. Auxiliary q3 and six remaining freeze hashes remain open.",
        "evidence": list(dict.fromkeys([*s0["evidence"], diff["result_id"], mass["result_id"], assembly["result_id"], gate["result_id"]])),
        "boundary": "Arity-two source completion is not auxiliary q3, a full Gate-A freeze, q2/Green compatibility, Hadamard or QME.",
    })
    s3 = stage(value, "STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")
    s3.update({
        "status": "PARTIAL_CERTIFIED_FULL_SOURCE_Q2_IDENTITIES_ZERO_AUXILIARY_Q3_OPEN",
        "statement": "All sixteen shifted-source q2 families are bound on common bytes and transported canonically to the graph carrier. The first missing nonlinear operation is the metric-dependent auxiliary q3 from the quartic h-h-f_hat-f_hat action variation.",
        "evidence": list(dict.fromkeys([*s3["evidence"], diff["result_id"], mass["result_id"], assembly["result_id"], gate["result_id"]])),
        "boundary": "q2 completion does not establish arity three, causal lambda-squared closure, Hadamard data or QME restoration.",
    })
    value["route_selection"][0].update({
        "route": "STRICT_AUXILIARY_Q3_COMMON_ASSEMBLY_AND_ARITY3_IDENTITIES",
        "recommendation": "Differentiate the exact shifted auxiliary mass density twice in the metric direction, lift the resulting quartic vertex to q3 with the fixed pairing, assemble with minimal q3, then replay arity three and cyclicity.",
    })
    value["research_queue"][0].update({
        "object": "STRICT_AUXILIARY_Q3_COMMON_ASSEMBLY_AND_ARITY3_IDENTITIES",
        "why": "The common q2 hash and all arity-two identities are closed; the quartic auxiliary action is now the first explicit source-level gap.",
    })
    value["frontier_summary"] = {
        "highest_value_next_route": "STRICT_AUXILIARY_Q3_COMMON_ASSEMBLY_AND_ARITY3_IDENTITIES",
        "route_count": len(value["route_selection"]),
        "completed_since_v31": ["STRICT_386_SHIFTED_MASS_BV_Q2_LIFT", "STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2", "STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_AND_IDENTITIES"],
        "new_positive_result": "One common 386-row source-q2 hash is accepted; q1/q2, cyclicity and stationary D/q2 all have zero defects in split and graph coordinates.",
        "surprise": "The V1 auxiliary momentum-map convention left 336 exact q1/q2 coefficients. The previously certified T(c_star)=-c_star translation removes all 336 and is now part of the accepted q2 snapshot.",
        "hard_boundary": "Auxiliary q3, six Gate-A hashes, the final common cyclic contraction, q2/Green compatibility, Hadamard and QME remain open.",
    }
    value["claim_flags"].update({
        "v31_preserved": True,
        "strict_386_full_source_q2_assembled": True,
        "strict_386_full_source_q2_pullback_replayed": True,
        "strict_386_authoritative_full_q2_imported": True,
        "strict_386_full_carrier_q2_certified": True,
        "strict_386_d_q2_derivation_replayed": True,
        "strict_386_full_q1_q2_identity_replayed": True,
        "strict_386_full_q2_cyclicity_replayed": True,
        "strict_386_full_D_q2_derivation_replayed": True,
        "strict_386_full_source_q3_pullback_replayed": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREDECESSOR), "role": "immutable V31 predecessor"},
        {"path": str(MASS.relative_to(ROOT)), "result_or_artifact_id": mass["result_id"], "sha256": sha(MASS), "role": "exact shifted-mass q2 lift"},
        {"path": str(DIFF_V2.relative_to(ROOT)), "result_or_artifact_id": diff["result_id"], "sha256": sha(DIFF_V2), "role": "canonical c-star sign repair and coupled q1/q2 replay"},
        {"path": str(ASSEMBLY.relative_to(ROOT)), "result_or_artifact_id": assembly["result_id"], "sha256": sha(ASSEMBLY), "role": "accepted source-q2 common snapshot"},
        {"path": str(GATE_V14.relative_to(ROOT)), "result_or_artifact_id": gate["result_id"], "sha256": sha(GATE_V14), "role": "Gate-A V14 reconciliation"},
    ]
    value["independent_checker"] = {"path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v32.py", "checks": ["V31 predecessor and 77-cell preservation", "assembly and Gate V14 pins", "one accepted q2 hash", "zero common q2 identity defects", "336-to-zero sign-repair history", "ten-route q3 frontier", "Gate-A/Hadamard/QME firewalls"], "expected_digest": ""}
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    q2, gate = value["strict_source_q2_common_assembly"], value["strict_gate_v14_reconciliation"]
    routes = "\n".join(f"{row['rank']}. `{row['route']}` — {row['recommendation']}" for row in value["route_selection"])
    return f"""# Lorentzian Weyl BV completion atlas v32

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

## Decision

{value['answer']}

The accepted q2 snapshot has {q2['minimal_ordered_symbolic_components']}
minimal operations and {q2['auxiliary_ordered_component_coefficients']}
auxiliary coefficients.  Its graph `q1/q2`, cyclicity and `D/q2` defect counts
are **{q2['q1_q2_defects']} / {q2['q2_cyclicity_defects']} /
{q2['D_q2_defects']}**.  Gate V14 remains `{gate['gate_a_status']}` with
{gate['accepted_top_level_hashes']} of seven hashes accepted.

## Ranked routes

{routes}

## Boundary

The next route is still `LOCAL-ALGEBRAIC`: construct auxiliary q3 and replay
arity three.  No Green compatibility, full-complex Hadamard state, QME
restoration or residual transfer follows from q2 completion.
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V32: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V32: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
