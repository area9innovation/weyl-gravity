#!/usr/bin/env python3
"""Build atlas V8 from V7 plus the typed strict-operator portability audit."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V7.json"
PORTABILITY = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V8.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v8.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_causal_sign_transport",
        "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge",
        "strict_component_pairing_serialization", "strict_operator_portability",
        "berger_h26_c26_decision_chain", "route_selection", "research_queue",
    )
    payload = {key: value[key] for key in keys}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def strict_branch(value: dict[str, Any]) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == "STRICT_PURE_WEYL_386")


def stage(value: dict[str, Any], stage_id: str) -> dict[str, Any]:
    return next(item for item in strict_branch(value)["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text())
    portability = json.loads(PORTABILITY.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V7":
        raise ValueError("V7 predecessor drift")
    if portability.get("result_id") != "STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1":
        raise ValueError("operator portability dependency drift")
    flags = portability["claim_flags"]
    if not flags["STRICT_ENDPOINT_Q1_PORTABLE_COMPONENT_BYTES"]:
        raise ValueError("endpoint q1 portability drift")
    if flags["STRICT_FULL_386_Q1_PORTABLE_COMPONENT_BYTES"] or flags["STRICT_ENDPOINT_GREEN_PORTABLE_ACTION_SERIALIZED"]:
        raise ValueError("operator portability promotion drift")
    if not flags["STRICT_CAUSAL_GREEN_HOMOTOPY_THEOREM_PRESERVED"]:
        raise ValueError("causal theorem preservation drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v8",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V8",
        "created": "2026-08-15",
        "repository_base_commit": "2d92392e9840eed7a2da81551a25e33d7f0815d1",
        "question": "Which mathematically typed portable artifacts are actually missing after the strict 386-row basis and pairing were serialized, and how should the completion route be split without mistaking a nonlocal Green map for a finite local coefficient table?",
        "answer": "Atlas V8 replaces the single vague all-operator serialization task by three nonconflated portability contracts. A finite-order local differential operator needs a sparse component jet table; an algebraic inclusion, projection or contracting homotopy needs a finite sparse component map; an advanced or retarded Green operator needs a represented nonlocal action, convergent operator name or distribution kernel on declared topological source and target spaces. The thirty-row endpoint q1 already satisfies the first contract through 80 exact arrow tables, 619 common nonzero coefficients and 700 checked Bach columns. The full 386-row q1 is coefficientwise complete in its exact producers, and H_alg, P_alg, P_end, i_end and p_end are executable and hashed, but their receiver-readable all-row tables are absent. The endpoint and full Green homotopies remain theorem-level causally certified: V8 does not revoke their support, homotopy or adjoint transfer. What is absent is a receiver-executable nonlocal action or kernel, so demanding a finite Green jet table would be a category error. The resulting route is now operational: serialize full q1; serialize the local SDR maps; specify and import a portable endpoint Green action; then assemble and replay the full action. The finite serialization work has a PRA upper bound and adds no infinite choice operation. The weakest foundation for the analytic Green theorem is not established and no Choice principle is inferred from physics. Gate A, local D, q2, Hadamard, Ward, positivity, renormalized products, QME and residual transfer remain fail closed.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v8.md",
    })
    stage(value, "S0_CLASSICAL_AUTHORITY").update({
        "status": "FAIL_CLOSED",
        "statement": "The 386-row basis and pairing are portable, and endpoint q1 has receiver-readable exact component bytes. Full q1 and the local SDR are exact in producers but not serialized as stable all-row receiver objects.",
        "evidence": [*stage(value, "S0_CLASSICAL_AUTHORITY")["evidence"], portability["result_id"]],
        "boundary": "Gate A still lacks portable full-q1 and local-SDR component maps, a portable endpoint/full Green action, all-row identity replay, one accepted operator snapshot hash, local D, q2 and the full residual extension.",
    })
    stage(value, "S2_CAUSAL_GREEN").update({
        "status": "SCOPED_CERTIFIED",
        "statement": "The causal Green-homotopy existence and support/adjoint transfer remain certified. Green maps are nonlocal analytic objects: the missing portable artifact is an action, convergent name or distribution kernel on declared represented spaces, not a finite jet table.",
        "evidence": [*stage(value, "S2_CAUSAL_GREEN")["evidence"], portability["result_id"]],
        "boundary": "No receiver-executable endpoint or full advanced/retarded action is serialized, so component action, homotopy and suspended-adjoint replay remain open; q2 and D are not established.",
    })
    strict_branch(value)["next_decisive_object"] = "Emit one canonical full-q1 finite component jet table on the fixed 386-row basis and independently replay q1 squared and pairing adjointness; then serialize the local SDR maps under their separate contract."
    value["frontier_summary"]["theory_identity_front"] = {
        "branch": "STRICT_PURE_WEYL_386", "first_gate": "S0_CLASSICAL_AUTHORITY",
        "current_fact": "Endpoint q1, all 386 row names and the exact pairing are portable. Full q1/local SDR are exact but producer-bound; Green existence is certified but its nonlocal action is not portable.",
        "best_next_object": "A canonical receiver-readable full-q1 component jet table, followed by exact local SDR component maps and a separately represented endpoint Green action.",
    }
    counts = portability["status_counts"]
    value["strict_operator_portability"] = {
        "result_id": portability["result_id"],
        "status": portability["result_state"],
        "contracts": [item["id"] for item in portability["portability_contracts"]],
        "operator_families_classified": len(portability["operator_inventory"]),
        "status_counts": counts,
        "endpoint_q1_arrow_tables": portability["operator_inventory"][0]["present"]["arrow_tables"],
        "endpoint_q1_nonzero_coefficients": portability["operator_inventory"][0]["present"]["common_nonzero_coefficients"],
        "endpoint_q1_bach_columns": portability["operator_inventory"][0]["present"]["Bach_columns_checked"],
        "full_q1_portable": flags["STRICT_FULL_386_Q1_PORTABLE_COMPONENT_BYTES"],
        "local_sdr_portable": flags["STRICT_FULL_386_LOCAL_SDR_PORTABLE_COMPONENT_BYTES"],
        "endpoint_green_action_portable": flags["STRICT_ENDPOINT_GREEN_PORTABLE_ACTION_SERIALIZED"],
        "full_green_action_portable": flags["STRICT_FULL_GREEN_PORTABLE_ACTION_SERIALIZED"],
        "causal_green_theorem_preserved": flags["STRICT_CAUSAL_GREEN_HOMOTOPY_THEOREM_PRESERVED"],
        "finite_local_upper_bound": portability["foundational_strength"]["finite_local_serialization_upper_bound"],
        "analytic_green_weakest_base": portability["foundational_strength"]["weakest_base_for_analytic_green_action"],
        "next_gate": portability["next_gate"],
    }
    value["strict_gate_a_progress"].update({
        "status": "ENDPOINT_Q1_PORTABLE_FULL_LOCAL_AND_ANALYTIC_ACTION_ARTIFACTS_OPEN",
        "operator_portability_control": value["strict_operator_portability"],
        "remaining_common_carrier": portability["next_gate"],
        "boundary": "Endpoint q1 is portable. Full q1/local SDR tables, endpoint/full nonlocal Green actions, all-row replay, common hashes, local D, q2 and residual-SDR extension remain open.",
    })
    value["route_selection"] = [
        {"rank": 1, "route": "STRICT_386_FULL_Q1_JET_TABLE", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "VERY_HIGH", "tractability": "HIGH", "dependency_depth": "LOW", "recommendation": "Emit the already computed endpoint, auxiliary and mapping-cylinder q1 blocks as one canonical sparse 386-row jet table and independently replay q1 squared and pairing adjointness."},
        {"rank": 2, "route": "STRICT_386_LOCAL_SDR_COMPONENT_MAPS", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "HIGH", "tractability": "HIGH", "dependency_depth": "LOW", "recommendation": "Serialize H_alg, P_alg, P_end, i_end and p_end from the exact producers and replay the support-local SDR and cyclic identities without rerunning those producers."},
        {"rank": 3, "route": "STRICT_ENDPOINT_ANALYTIC_GREEN_ACTION", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "VERY_HIGH", "tractability": "LOW", "dependency_depth": "MEDIUM", "recommendation": "Declare represented test and distribution spaces and import an advanced/retarded endpoint action or kernel with topology, continuity, uniqueness, support and adjoint data."},
        {"rank": 4, "route": "STRICT_FULL_GREEN_COMPONENT_ACTION_REPLAY", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "HIGH", "tractability": "LOW", "dependency_depth": "HIGH", "recommendation": "Compose the portable endpoint Green action with the local SDR maps and replay full homotopy, causal support and suspended adjointness on the fixed carrier."},
        {"rank": 5, "route": "STRICT_386_LOCAL_D", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "VERY_HIGH", "tractability": "LOW", "dependency_depth": "MEDIUM", "recommendation": "Serialize cylinder-time D on the accepted operator carrier and verify its q1 commutator only after the unary carrier artifacts share one digest."},
        {"rank": 6, "route": "STRICT_386_Q2_GREEN_COMPATIBILITY", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "HIGH", "tractability": "LOW", "dependency_depth": "HIGH", "recommendation": "Bind target-action q2 to the same paired D-equivariant causal carrier and test contraction compatibility after the complete unary action replay."},
        {"rank": 7, "route": "DIRECT_SPACETIME_Q26_HADAMARD", "branch": "BERGER_POSITIVE_CLOCK_54", "scientific_leverage": "VERY_HIGH", "tractability": "LOW", "dependency_depth": "MEDIUM", "recommendation": "Retain the analytically mature independent route through direct nonstationary q26-equivariant distributional selection."},
        {"rank": 8, "route": "BACH_FLAT_NONLINEAR_CARTAN", "branch": "PURE_WEYL_BACH_FLAT_RANK310", "scientific_leverage": "HIGH", "tractability": "MEDIUM", "dependency_depth": "MEDIUM", "recommendation": "Use the broad curved strict causal branch as an independent nonlinear compatibility control while the target-theory portability route advances."},
    ]
    value["research_queue"] = [
        {"priority": route["rank"], "branch": route["branch"], "object": route["route"], "why": route["recommendation"]}
        for route in value["route_selection"]
    ]
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V7 atlas predecessor"},
        {"path": str(PORTABILITY.relative_to(ROOT)), "sha256": sha(PORTABILITY), "role": "typed local/nonlocal strict-operator portability audit"},
    ]
    value["claim_flags"].update({
        "v7_preserved": True,
        "strict_386_operator_portability_types_classified": True,
        "strict_endpoint_q1_portable_component_bytes": True,
        "strict_causal_green_homotopy_theorem_preserved": True,
        "strict_full_386_q1_portable_component_bytes": False,
        "strict_full_386_local_sdr_portable_component_bytes": False,
        "strict_endpoint_green_portable_action_serialized": False,
        "strict_full_green_portable_action_serialized": False,
    })
    value["does_not_establish"] = list(dict.fromkeys(previous["does_not_establish"] + portability["does_not_establish"]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v8.py",
        "checks": ["V7 preservation", "77-cell closure", "three typed portability contracts", "six-family operator inventory", "endpoint q1 exact-count projection", "local/nonlocal firewall", "causal theorem preservation", "Gate-A/D/q2/quantum firewalls", "eight-route ranking", "append-only provenance", "content hashes", "canonical digest"],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    item = value["strict_operator_portability"]
    lines = [
        "# Lorentzian Weyl BV completion atlas V8", "", "## Outcome", "", value["answer"], "",
        "## Typed portability result", "",
        "| object type | portable artifact | current disposition |", "|---|---|---|",
        "| `FINITE_COMPONENT_JET_TABLE` — finite local differential operator | sparse component jet table | endpoint q1 portable; full q1 open |",
        "| `FINITE_SPARSE_COMPONENT_MAP` — support-local algebraic map | finite sparse component map | exact producer matrices; receiver tables open |",
        "| `ANALYTIC_GREEN_ACTION` — advanced/retarded Green operator | represented action, convergent name, or distribution kernel | theorem certified; portable action open |", "",
        f"The endpoint q1 projection contains **{item['endpoint_q1_arrow_tables']}** arrow tables, **{item['endpoint_q1_nonzero_coefficients']}** nonzero coefficients and **{item['endpoint_q1_bach_columns']}** checked Bach columns. The causal Green theorem is preserved; its receiver-executable nonlocal action remains open.", "",
        "## Updated route selection", "", "| rank | route | branch | leverage | tractability |", "|---:|---|---|---|---|",
    ]
    for route in value["route_selection"]:
        lines.append(f"| {route['rank']} | `{route['route']}` | `{route['branch']}` | {route['scientific_leverage']} | {route['tractability']} |")
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v8.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v8.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v8.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v8.py", "```", "", "## Boundaries", ""]
    lines.extend(f"- This does not establish {boundary}." for boundary in value["does_not_establish"])
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [str(path.relative_to(ROOT)) for path, content in ((RESULT, result), (REPORT, report)) if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V8: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V8: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
