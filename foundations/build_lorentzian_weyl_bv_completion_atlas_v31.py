#!/usr/bin/env python3
"""Build Atlas V31 after the exhaustive Weyl/boost ghost manifest."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V30.json"
MANIFEST = ROOT / "d_quotient_classical/certificates/CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1.json"
GATE_V13 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V13_RECONCILIATION.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V31.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v31.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = ("stages", "branches", "frontier_summary", "classical_import_reconciliation", "strict_gate_v13_reconciliation", "strict_nonlinear_weyl_boost_ghost_manifest", "route_selection", "research_queue")
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(item for item in value["branches"] if item["id"] == branch_id)
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous, manifest, gate = (json.loads(path.read_text()) for path in (PREDECESSOR, MANIFEST, GATE_V13))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V30":
        raise ValueError("V30 predecessor drift")
    if manifest.get("claim_flags", {}).get("EXHAUSTIVE_NONLINEAR_WEYL_BOOST_GHOST_ANTIFIELD_MANIFEST") is not True:
        raise ValueError("ghost manifest unavailable")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V13_RECONCILIATION" or gate.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("Gate V13 unavailable")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v31",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V31",
        "created": "2026-08-15",
        "question": "After the primary source closes the nonlinear Weyl/boost ghost census, what is the shortest route to an authoritative nonlinear source import?",
        "answer": "Atlas V31 closes the V30 manifest route. Metsaev's full nonlinear boost law makes the Weyl/boost internal algebra Abelian and the exactly shifted auxiliary tensor invariant, so no additional Weyl/boost ghost-antifield families exist in the declared source scope. The seven serialized auxiliary cubic families are now an exhaustive family census. The frontier moves to assembly: combine the minimal and seven auxiliary families into one source-certified 386-row q2/q3 payload, then replay q1/q2, cyclicity and D-equivariance. Gate A remains fail closed with zero accepted hashes.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v31.md",
    })
    value["strict_nonlinear_weyl_boost_ghost_manifest"] = {
        "result_id": manifest["result_id"],
        **manifest["manifest_summary"],
        "off_shell_closure": manifest["gauge_algebra"]["off_shell_closure"],
        "field_dependent_structure_functions": manifest["gauge_algebra"]["field_dependent_structure_functions"],
        "shifted_f_hat_Weyl_invariant": manifest["shifted_auxiliary_covariance"]["Weyl"]["f_hat_Weyl_invariant"],
        "shifted_f_hat_boost_invariant": manifest["shifted_auxiliary_covariance"]["boost"]["f_hat_boost_invariant"],
        "exhaustive_in_declared_scope": True,
        "full_386_source_q2_assembled": False,
    }
    disposition = gate["gate_disposition"]
    value["strict_gate_v13_reconciliation"] = {
        "result_id": gate["result_id"], "status": gate["result_state"],
        "exports_total": len(gate["export_reconciliation"]), "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": len(gate["freeze_check_reconciliation"]), "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "gate_a_status": disposition["gate_a_status"],
        "exhaustive_auxiliary_family_census": gate["m2_shifted_cubic_inventory_resolution"]["exhaustive_full_nonlinear_BV_family_census"],
        "full_source_q2_assembled": gate["m2_nonlinear_ghost_manifest_resolution"]["full_386_source_q2_assembled"],
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
        "statement": "The primary-source nonlinear Weyl/boost manifest is now exhaustive in scope and adds no auxiliary families. All seven auxiliary cubic families are component-complete, but their common source q2/q3 assembly and full identities remain open; Gate V13 accepts zero hashes.",
        "evidence": list(dict.fromkeys([*s0["evidence"], manifest["result_id"], gate["result_id"]])),
        "boundary": "An exhaustive family census is not an assembled source operator, an accepted q2 hash, a Gate-A pass, Hadamard state or QME state.",
    })
    s3 = stage(value, "STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")
    s3.update({
        "status": "PARTIAL_CERTIFIED_EXHAUSTIVE_AUXILIARY_FAMILY_CENSUS_SOURCE_Q2_ASSEMBLY_OPEN",
        "statement": "All seven auxiliary cubic families are component-complete and exhaustive in the declared source scope. The next obstruction is compositional: assemble them with minimal q2/q3 and replay q1/q2, cyclicity and D on common bytes.",
        "evidence": list(dict.fromkeys([*s3["evidence"], manifest["result_id"], gate["result_id"]])),
        "boundary": "Census and component completeness do not establish the combined source identities, causal lambda-squared closure, Hadamard data or QME restoration.",
    })
    value["route_selection"] = [item for item in value["route_selection"] if item["route"] != "STRICT_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST"]
    value["research_queue"] = [item for item in value["research_queue"] if item["object"] != "STRICT_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST"]
    for rank, item in enumerate(value["route_selection"], 1):
        item["rank"] = rank
    for priority, item in enumerate(value["research_queue"], 1):
        item["priority"] = priority
    value["route_selection"][0].update({
        "route": "STRICT_SOURCE_Q2_Q3_COMMON_ASSEMBLY_AND_IDENTITIES",
        "recommendation": "Assemble the minimal and seven exhaustive auxiliary families on the exact 386-row carrier, then replay q1/q2, cyclicity and D-equivariance before any causal source promotion.",
    })
    value["research_queue"][0].update({
        "object": "STRICT_SOURCE_Q2_Q3_COMMON_ASSEMBLY_AND_IDENTITIES",
        "why": "The family census is closed; the decisive object is now one source-certified operator payload and its common-byte identities.",
    })
    value["frontier_summary"] = {
        "highest_value_next_route": "STRICT_SOURCE_Q2_Q3_COMMON_ASSEMBLY_AND_IDENTITIES",
        "route_count": len(value["route_selection"]),
        "completed_since_v30": ["STRICT_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST"],
        "new_positive_result": "The seven auxiliary cubic families are exhaustive in the declared ordinary-derivative source scope.",
        "hard_boundary": "No assembled source q2/q3, full identity replay, Gate-A hash, Hadamard state or QME state is promoted.",
    }
    value["claim_flags"].update({
        "v30_preserved": True,
        "strict_386_exhaustive_full_nonlinear_bv_family_census": True,
        "strict_nonlinear_weyl_boost_ghost_manifest_complete": True,
        "strict_386_full_source_q2_assembled": False,
        "strict_386_full_source_q2_pullback_replayed": False,
        "strict_386_full_source_q3_pullback_replayed": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREDECESSOR), "role": "immutable V30 predecessor"},
        {"path": str(MANIFEST.relative_to(ROOT)), "result_or_artifact_id": manifest["result_id"], "sha256": sha(MANIFEST), "role": "exhaustive scoped nonlinear Weyl/boost ghost manifest"},
        {"path": str(GATE_V13.relative_to(ROOT)), "result_or_artifact_id": gate["result_id"], "sha256": sha(GATE_V13), "role": "Gate-A V13 fail-closed reconciliation"},
    ]
    value["independent_checker"] = {"path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v31.py", "checks": ["V30 predecessor and 77-cell preservation", "manifest and Gate V13 pins", "exhaustive seven-family promotion", "source-q2 assembly firewall", "ten-route deterministic queue", "Gate-A/Hadamard/QME firewalls"], "expected_digest": ""}
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    m, g = value["strict_nonlinear_weyl_boost_ghost_manifest"], value["strict_gate_v13_reconciliation"]
    routes = "\n".join(f"{row['rank']}. `{row['route']}` — {row['recommendation']}" for row in value["route_selection"])
    return f"""# Lorentzian Weyl BV completion atlas v31

**Result:** `{value['result_id']}`

**Dependency:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

## Decision

{value['answer']}

The primary-source manifest has {m['nonzero_ghost_antifield_families']} nonzero
ghost-antifield families and requires
{m['additional_nonlinear_Weyl_boost_ghost_antifield_families']} additional
Weyl/boost families.  Gate V13 remains `{g['gate_a_status']}` with
{g['accepted_top_level_hashes']} accepted hashes.

## Ranked routes

{routes}

## Boundary

The census result is `LOCAL-ALGEBRAIC`.  It does not assemble the common
source `q2/q3`, prove causal source closure, construct a full-complex Hadamard
state, restore the QME, or authorize residual transfer.
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V31: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V31: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
