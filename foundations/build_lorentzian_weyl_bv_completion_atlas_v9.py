#!/usr/bin/env python3
"""Build atlas V9 from V8 plus the exact split-q1 auxiliary sign gate."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V8.json"
SIGN_GATE = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V9.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v9.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_causal_sign_transport",
        "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge",
        "strict_component_pairing_serialization", "strict_operator_portability",
        "strict_full_q1_split_sign_gate", "berger_h26_c26_decision_chain",
        "route_selection", "research_queue",
    )
    return hashlib.sha256(
        json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def strict_branch(value: dict[str, Any]) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == "STRICT_PURE_WEYL_386")


def stage(value: dict[str, Any], stage_id: str) -> dict[str, Any]:
    return next(item for item in strict_branch(value)["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text())
    gate = json.loads(SIGN_GATE.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V8":
        raise ValueError("V8 predecessor drift")
    if gate.get("result_id") != "STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1":
        raise ValueError("split-q1 sign-gate dependency drift")
    flags = gate["claim_flags"]
    if not flags["STRICT_386_AUXILIARY_Q_TEXT_MATRIX_SIGN_CONFLICT_CERTIFIED"]:
        raise ValueError("sign conflict certification drift")
    if not flags["STRICT_386_EXECUTABLE_AUXILIARY_Q_CYCLIC_WITH_SERIALIZED_PAIRING"]:
        raise ValueError("executable cyclicity drift")
    if flags["STRICT_FULL_386_Q1_PORTABLE_COMPONENT_BYTES"] or gate["repair_analysis"]["repair_applied"]:
        raise ValueError("full-q1 or repair promotion drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v9",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V9",
        "created": "2026-08-15",
        "repository_base_commit": "f4ca51aac8f44117686464d17f2c61767d0d780a",
        "question": "Does the fixed 386-row split presentation already support an honest full-q1 serialization, or is there a smaller exact classical inconsistency that must be repaired before the finite operator bytes and later causal Green-homotopy actions can share one accepted snapshot?",
        "answer": "Atlas V9 reaches the first concrete obstruction inside the V8 full-q1 serialization route. The published 386-row carrier is a split mapping-cylinder presentation: its primitive unary differential consists of the endpoint complex, the generalized-auxiliary contractible summand, and the autonomous curvature cone with its cotangent dual. The T, A and B attachment maps belong to the separate degree-zero canonical shear and inclusion/projection data, rather than being additional primitive q1 arrows in this split basis. On the 36 generalized-auxiliary rows, the exact executable matrix already pinned by the classical certificate contains the dual arrow v_star to eta_star with sign +I_4. The factorized curved-Q source and human-readable certificate ledgers declare -I_4 instead. Both candidates remain nilpotent and admit the recorded contraction, so those two checks cannot distinguish them. The independent exact odd-pairing replay does distinguish them: +I_4 has zero cyclicity defects, while -I_4 has eight rational defects, two orientations for each of four components. Full-q1 serialization is therefore blocked before any analytic issue arises. The preferred repair is local and explicit—change the factorized dual arrow and its textual ledgers to +I_4, matching the executable matrix and serialized pairing—then regenerate the affected classical certificate chain. V9 records the discrepancy without applying the repair or promoting the full q1 bytes. The causal Green-homotopy theorem, support transfer, suspension result and operator-type classification remain preserved. Gate A, local D, q2, a represented advanced/retarded action, Hadamard construction, Ward identities, renormalized products, QME restoration and residual transfer all remain fail closed.",
        "predecessor": {
            "result_id": previous["result_id"],
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "sha256": sha(PREDECESSOR),
            "preserved": True,
        },
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v9.md",
    })
    stage(value, "S0_CLASSICAL_AUTHORITY").update({
        "status": "FAIL_CLOSED",
        "statement": "The fixed 386-row basis and pairing expose an exact text/matrix sign conflict in the 36-row auxiliary q1 summand: executable +I4 is cyclic, while declared -I4 has eight pairing defects. Full q1 serialization pauses pending a classical source-and-ledger repair.",
        "evidence": [*stage(value, "S0_CLASSICAL_AUTHORITY")["evidence"], gate["result_id"]],
        "boundary": "The preferred +I4 repair has not been applied or propagated through the affected classical certificate chain. Full q1, local SDR, Green actions, all-row adjoints, a common snapshot hash, local D, q2 and residual extension remain open.",
    })
    strict_branch(value)["next_decisive_object"] = "Repair the factorized auxiliary cotangent arrow and textual ledgers to v_star -> +eta_star, regenerate the affected classical chain, and independently replay the 36-row cyclicity gate before emitting the full 386-row q1 table."
    value["frontier_summary"]["theory_identity_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "first_gate": "S0_CLASSICAL_AUTHORITY",
        "current_fact": "The fixed carrier identifies a four-entry text/matrix sign conflict invisible to nilpotency and contraction but detected by eight exact odd-pairing defects.",
        "best_next_object": "A repaired authoritative auxiliary q source and regenerated affected certificate chain, followed by the receiver-readable full-q1 table.",
    }
    replay = gate["exact_replay"]
    value["strict_full_q1_split_sign_gate"] = {
        "result_id": gate["result_id"],
        "status": gate["result_state"],
        "carrier_rows": gate["carrier"]["rows"],
        "auxiliary_rows": gate["carrier"]["auxiliary_rows"],
        "block": gate["sign_conflict"]["block"],
        "executable_sign": gate["sign_conflict"]["executable_matrix_sign"],
        "declared_sign": gate["sign_conflict"]["factorized_source_and_certificate_sign"],
        "executable_cyclicity_defects": replay["executable_plus_sign"]["cyclicity_defects"],
        "declared_cyclicity_defects": replay["declared_minus_sign"]["cyclicity_defects"],
        "both_nilpotent": replay["executable_plus_sign"]["q_squared_defects"] == replay["declared_minus_sign"]["q_squared_defects"] == 0,
        "both_contractible": replay["executable_plus_sign"]["contraction_defects"] == replay["declared_minus_sign"]["contraction_defects"] == 0,
        "repair_applied": gate["repair_analysis"]["repair_applied"],
        "split_coordinate_classified": flags["STRICT_386_SPLIT_COORDINATE_LOCATION_CLASSIFIED"],
        "foundational_upper_bound": gate["foundational_strength"]["exact_sign_gate_upper_bound"],
        "choice_operation_added": gate["foundational_strength"]["choice_operation_added"],
        "next_gate": gate["next_gate"],
    }
    value["strict_gate_a_progress"].update({
        "status": "AUXILIARY_Q_TEXT_MATRIX_SIGN_REPAIR_REQUIRED",
        "full_q1_split_sign_control": value["strict_full_q1_split_sign_gate"],
        "remaining_common_carrier": gate["next_gate"],
        "boundary": "The exact +I4/-I4 conflict must be repaired in the classical authority before full q1 or downstream local and analytic action artifacts can be accepted on one snapshot.",
    })
    value["route_selection"] = [
        {"rank": 1, "route": "STRICT_386_AUXILIARY_Q_SIGN_REPAIR", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "VERY_HIGH", "tractability": "VERY_HIGH", "dependency_depth": "LOW", "recommendation": "Change the factorized auxiliary dual arrow and matching textual ledgers to +I4, regenerate the affected classical certificates, and replay exact pairing cyclicity before any full-q1 claim."},
        {"rank": 2, "route": "STRICT_386_FULL_Q1_JET_TABLE", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "VERY_HIGH", "tractability": "HIGH", "dependency_depth": "LOW", "recommendation": "After the sign repair, emit endpoint, auxiliary and mapping-cylinder blocks as one canonical sparse 386-row q1 table and independently replay q1 squared and pairing adjointness."},
        *[{**route, "rank": route["rank"] + 1} for route in previous["route_selection"][1:]],
    ]
    value["research_queue"] = [
        {"priority": route["rank"], "branch": route["branch"], "object": route["route"], "why": route["recommendation"]}
        for route in value["route_selection"]
    ]
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V8 atlas predecessor"},
        {"path": str(SIGN_GATE.relative_to(ROOT)), "sha256": sha(SIGN_GATE), "role": "exact split-q1 auxiliary text/matrix sign gate"},
    ]
    value["claim_flags"].update({
        "v8_preserved": True,
        "strict_386_auxiliary_q_text_matrix_sign_conflict_certified": True,
        "strict_386_executable_auxiliary_q_cyclic_with_serialized_pairing": True,
        "strict_386_declared_minus_sign_cyclic_with_serialized_pairing": False,
        "strict_386_split_coordinate_location_classified": True,
        "strict_386_auxiliary_q_sign_repair_applied": False,
        "strict_full_386_q1_portable_component_bytes": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys(previous["does_not_establish"] + gate["does_not_establish"]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v9.py",
        "checks": [
            "V8 preservation", "77-cell closure", "strict S0-only mutation",
            "36-row sign-gate projection", "zero-versus-eight cyclicity replay",
            "nilpotency/contraction nondiscrimination", "split-coordinate classification",
            "repair/full-q1 firewall", "causal theorem preservation", "nine-route ranking",
            "append-only provenance", "content hashes", "canonical digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    item = value["strict_full_q1_split_sign_gate"]
    lines = [
        "# Lorentzian Weyl BV completion atlas V9", "", "## Outcome", "", value["answer"], "",
        "## Exact auxiliary sign gate", "",
        "| candidate | q1 squared | contraction | odd-pairing cyclicity |", "|---|---:|---:|---:|",
        f"| executable `{item['executable_sign']}` | 0 defects | 0 defects | **{item['executable_cyclicity_defects']} defects** |",
        f"| declared `{item['declared_sign']}` | 0 defects | 0 defects | **{item['declared_cyclicity_defects']} defects** |", "",
        "This is a finite exact PRA-level gate and adds no choice operation. It does not weaken the previously certified causal Green-homotopy theorem; it blocks acceptance of the shared classical operator snapshot until repaired.", "",
        "## Updated route selection", "", "| rank | route | branch | leverage | tractability |", "|---:|---|---|---|---|",
    ]
    for route in value["route_selection"]:
        lines.append(f"| {route['rank']} | `{route['route']}` | `{route['branch']}` | {route['scientific_leverage']} | {route['tractability']} |")
    lines += [
        "", "## Reproduction", "", "```text",
        "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v9.py --check",
        "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v9.py",
        "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v9.py",
        "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v9.py",
        "```", "", "## Boundaries", "",
    ]
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
    stale = [
        str(path.relative_to(ROOT))
        for path, content in ((RESULT, result), (REPORT, report))
        if not path.is_file() or path.read_bytes() != content
    ]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V9: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V9: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
