#!/usr/bin/env python3
"""Build Atlas V33 after authoritative common source-q3 completion."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V32.json"
Q3 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V15_RECONCILIATION.json"
AUXILIARY = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1.json"
QUARTIC = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V33.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v33.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = ("stages", "branches", "frontier_summary", "classical_import_reconciliation", "strict_gate_v15_reconciliation", "strict_source_q2_common_assembly", "strict_source_q3_common_assembly", "route_selection", "research_queue")
    payload = {key: value[key] for key in keys}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(item for item in value["branches"] if item["id"] == branch_id)
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous, q3, gate, auxiliary, quartic = (json.loads(path.read_text()) for path in (PREDECESSOR, Q3, GATE, AUXILIARY, QUARTIC))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V32":
        raise ValueError("Atlas V32 predecessor drift")
    if q3.get("result_id") != "STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1" or not q3["claim_flags"]["FULL_SOURCE_Q3_ASSEMBLED"]:
        raise ValueError("authoritative common q3 unavailable")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V15_RECONCILIATION" or gate["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate V15 unavailable")
    if gate["claim_flags"]["STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED"] is not True or gate["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] is not False:
        raise ValueError("Gate V15 q3/freeze boundary drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v33",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V33",
        "created": "2026-08-16",
        "question": "After completing the authoritative source q3 and arity-three identities, what is the strongest next Lorentzian Weyl BV route?",
        "answer": "Atlas V33 closes the local nonlinear source through arity three. The exact shifted mass supplies 321 independent quartic monomials, 912 ordered fourth variations and 5,952 paired q3 coefficients. Together with minimal Bach q3 they exhaust the two source families; arity three, cyclicity modulo horizontal boundary and stationary D/q3 have zero split/graph defects. The priority now shifts from constructing brackets to freezing one common classical snapshot: accept the six remaining hashes, residual SDR/payload and final cyclic contraction. Gate A remains fail closed until that work is done.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v33.md",
    })
    value["strict_source_q2_common_assembly"]["full_source_q3_assembled"] = True
    value.pop("strict_gate_v14_reconciliation", None)
    value["strict_source_q3_common_assembly"] = {
        "result_id": q3["result_id"],
        "accepted_source_q2_sha256": q3["source_q3_snapshot"]["accepted_q2_snapshot_sha256"],
        "accepted_source_q3_sha256": q3["source_q3_snapshot"]["sha256"],
        "source_q3_families": q3["family_census"]["total_source_q3_families"],
        "classical_independent_monomials": quartic["shifted_auxiliary_quartic_mass_vertex"]["nonzero_independent_component_monomials"],
        "classical_ordered_fourth_variations": quartic["shifted_auxiliary_quartic_mass_vertex"]["nonzero_ordered_fourth_variation_coefficients"],
        "auxiliary_ordered_q3_coefficients": q3["source_q3_snapshot"]["auxiliary_ordered_component_coefficients"],
        "cyclic_equalities_checked": auxiliary["exact_replay"]["cyclicity_equalities_checked"],
        "Weyl_Ward_checks": quartic["exact_replay"]["pure_trace_second_variation_checks"] + quartic["exact_replay"]["mixed_conformal_recursion_checks"],
        "graph_block_quadruples": q3["graph_transport"]["graph_block_quadruples"],
        "arity_three_defects": q3["arity_three_replay"]["graph_386_arity_three_defects"],
        "q3_cyclicity_defects_mod_d": q3["q3_cyclicity_replay"]["graph_386_q3_cyclicity_defects_mod_d"],
        "D_q3_defects": q3["D_q3_replay"]["graph_D_q3_derivation_defects"],
        "full_source_q3_assembled": True,
    }
    disposition = gate["gate_disposition"]
    value["strict_gate_v15_reconciliation"] = {
        "result_id": gate["result_id"], "status": gate["result_state"],
        "exports_total": len(gate["export_reconciliation"]), "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": len(gate["freeze_check_reconciliation"]), "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "remaining_top_level_hashes": 7 - disposition["accepted_common_snapshot_hashes"],
        "minimal_missing_bundle": [item["id"] for item in gate["minimal_missing_bundle"]],
        "gate_a_status": disposition["gate_a_status"],
        "full_source_q2_assembled": gate["claim_flags"]["STRICT_386_FULL_SOURCE_Q2_ASSEMBLED"],
        "full_source_q3_assembled": gate["claim_flags"]["STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED"],
    }
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
        "statement": "The authoritative shifted-source q2/q3 are assembled on linked common snapshots. Arity three, q2/q3 cyclicity and stationary D derivations are closed. Gate A remains open only at the common freeze, residual and final cyclic-contraction layer.",
        "evidence": list(dict.fromkeys([*s0["evidence"], quartic["result_id"], auxiliary["result_id"], q3["result_id"], gate["result_id"]])),
        "boundary": "Local q2/q3 completion is not the six missing freeze hashes, the full residual contraction, Green compatibility, Hadamard data or QME.",
    })
    s3 = stage(value, "STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")
    s3.update({
        "status": "CERTIFIED_FULL_SOURCE_Q2_Q3_ARITY_THREE_AND_CYCLICITY_ZERO",
        "statement": "The complete shifted-source q2/q3 Taylor data are bound on common bytes and transported canonically to the graph carrier. Exactly two q3 families occur, and the full arity-three identity has zero defects.",
        "evidence": list(dict.fromkeys([*s3["evidence"], quartic["result_id"], auxiliary["result_id"], q3["result_id"], gate["result_id"]])),
        "boundary": "This does not establish q2/q3 compatibility with a causal Green homotopy, analytic Moller convergence, Hadamard data or QME restoration.",
    })
    value["route_selection"][0].update({
        "route": "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION",
        "recommendation": "Bind the field dictionary, differential, D action, residual SDR, pairing, exact residual payload and centered representatives to one manifest; accept the remaining six hashes and replay the tenth freeze identity.",
    })
    value["research_queue"][0].update({
        "object": "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION",
        "why": "The source q2/q3 and all local identities are complete; the classical import gate is now blocked only by the shared freeze/residual package rather than a missing nonlinear bracket.",
    })
    value["frontier_summary"] = {
        "highest_value_next_route": "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION",
        "route_count": len(value["route_selection"]),
        "completed_since_v32": ["CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS", "STRICT_386_SHIFTED_MASS_BV_Q3_LIFT", "STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_AND_ARITY_THREE", "GATE_V15_M2_RECONCILIATION"],
        "new_positive_result": "The authoritative source q3 is complete: two exhaustive families, 5,952 auxiliary coefficients and zero arity-three/cyclicity/D-q3 defects in split and graph coordinates.",
        "surprise": "The supposedly missing q3 is entirely forced by the second metric variation of the algebraic shifted mass; 605 conformal Ward checks close its Weyl channels without any Hilbert completion, Green inverse or choice operation.",
        "hard_boundary": "Six Gate-A hashes, the final common cyclic contraction, q2/q3 Green compatibility, Hadamard and QME remain open.",
    }
    value["claim_flags"].update({
        "v32_preserved": True,
        "strict_386_full_source_q3_pullback_replayed": True,
        "strict_386_authoritative_full_q3_imported": True,
        "strict_386_full_arity_three_identity_replayed": True,
        "strict_386_full_q3_cyclicity_replayed_mod_d": True,
        "strict_386_full_D_q3_derivation_replayed": True,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_q2_q3_green_compatibility_certified": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREDECESSOR), "role": "immutable V32 predecessor"},
        {"path": str(QUARTIC.relative_to(ROOT)), "result_or_artifact_id": quartic["result_id"], "sha256": sha(QUARTIC), "role": "authoritative classical quartic auxiliary tensor"},
        {"path": str(AUXILIARY.relative_to(ROOT)), "result_or_artifact_id": auxiliary["result_id"], "sha256": sha(AUXILIARY), "role": "fixed-pairing auxiliary q3 lift"},
        {"path": str(Q3.relative_to(ROOT)), "result_or_artifact_id": q3["result_id"], "sha256": sha(Q3), "role": "authoritative common source-q3 snapshot and identities"},
        {"path": str(GATE.relative_to(ROOT)), "result_or_artifact_id": gate["result_id"], "sha256": sha(GATE), "role": "Gate-A V15 reconciliation"},
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v33.py",
        "checks": ["V32 predecessor and 77-cell preservation", "q3/Gate V15 pins", "321/912/5952 coefficient chain", "two-family census", "zero arity-three/cyclicity/D-q3 defects", "five-item freeze bundle", "Gate-A/Green/Hadamard/QME firewalls"],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    q3, gate = value["strict_source_q3_common_assembly"], value["strict_gate_v15_reconciliation"]
    routes = "\n".join(f"{row['rank']}. `{row['route']}` — {row['recommendation']}" for row in value["route_selection"])
    return f"""# Lorentzian Weyl BV completion atlas v33

**Result:** `{value['result_id']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

## Decision

{value['answer']}

The q3 chain contains {q3['classical_independent_monomials']} independent
classical monomials, {q3['classical_ordered_fourth_variations']} ordered
fourth variations and {q3['auxiliary_ordered_q3_coefficients']} paired q3
coefficients.  Its graph arity-three, cyclicity and `D/q3` defects are
**{q3['arity_three_defects']} / {q3['q3_cyclicity_defects_mod_d']} /
{q3['D_q3_defects']}**.

Gate V15 remains `{gate['gate_a_status']}`: {gate['accepted_top_level_hashes']}
of seven hashes are accepted, with five typed work bundles covering the six
remaining hashes and final contraction.

## Ranked routes

{routes}

## Boundary

The next route freezes the classical import.  No causal Green compatibility,
full-complex Hadamard state, QME restoration or residual transfer follows from
local q3 completion.
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V33: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V33: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
