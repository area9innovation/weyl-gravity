#!/usr/bin/env python3
"""Build atlas V7 from V6 plus the strict component-pairing serialization."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V6.json"
PAIRING = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V7.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v7.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = ("stages", "branches", "frontier_summary", "classical_import_reconciliation", "strict_gate_a_progress", "strict_causal_sign_transport", "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge", "strict_component_pairing_serialization", "berger_h26_c26_decision_chain", "route_selection", "research_queue")
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def strict_branch(value: dict[str, Any]) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == "STRICT_PURE_WEYL_386")


def stage(value: dict[str, Any], stage_id: str) -> dict[str, Any]:
    return next(item for item in strict_branch(value)["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text())
    pairing = json.loads(PAIRING.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V6":
        raise ValueError("V6 predecessor drift")
    if pairing.get("result_id") != "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1":
        raise ValueError("component pairing dependency drift")
    flags = pairing["claim_flags"]
    if not flags["STRICT_386_COMPONENT_PAIRING_SERIALIZED_IN_GATE_CONVENTION"] or flags["STRICT_386_ALL_OPERATOR_COMPONENT_ADJOINTS_REPLAYED"]:
        raise ValueError("pairing/operator-adjoint boundary drift")

    value = deepcopy(previous)
    stage(value, "S0_CLASSICAL_AUTHORITY").update({
        "status": "FAIL_CLOSED",
        "statement": "The common endpoint q1, suspension character and full 386-row hybrid component basis/pairing are now exact. The basis has 30 endpoint, 36 generalized-auxiliary and 320 mapping-cylinder rows; its rank-386 odd pairing has 410 ordered rational entries.",
        "evidence": ["CLASSICAL_IMPORT_GATE_V5_RECONCILIATION", "STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1", "STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1", "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1"],
        "boundary": "Gate A still lacks full prolonged q1, H_alg, endpoint inclusion/projection and Green operator component tables, one common accepted operator snapshot hash, local D, q2 and the full residual extension.",
    })
    stage(value, "S2_CAUSAL_GREEN").update({
        "status": "SCOPED_CERTIFIED",
        "statement": "The projector-level suspended Green adjoint remains certified, and T^T Omega=Omega T^sharp now replays on all 410 serialized pairing entries. The full Green operators themselves are not component coefficient tables in this basis.",
        "evidence": ["pure-weyl-full-prolonged-green-homotopy-assembly-v1", "STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1", "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1"],
        "boundary": "A component-by-component q1/projector/Green adjoint and homotopy replay awaits portable operator coefficient tables; q2 and D are not established.",
    })
    strict_branch(value)["next_decisive_object"] = "Serialize full prolonged q1, H_alg, endpoint inclusion/projection and advanced/retarded Green coefficient tables in the fixed 386-row hybrid basis, then independently replay every component adjoint and homotopy identity."
    basis = pairing["component_basis"]
    omega = pairing["pairing_serialization"]
    signs = pairing["suspension_serialization"]
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v7",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V7",
        "created": "2026-08-15",
        "repository_base_commit": "7066e14d17bb37e6ad8dacdc10726dbb830ebec4",
        "question": "After fixing the suspension convention, can the full strict 386-row carrier and pairing be serialized componentwise, and which exact operator bytes now block Gate A?",
        "answer": "Yes. Atlas V7 imports an explicit hybrid Gate basis with 386 unique component rows: thirty Gate-canonical endpoint rows, thirty-six ordered generalized-auxiliary doublet rows and all 320 split curvature mapping-cylinder cone/cotangent rows. The algebraic complement is therefore concretely 356=36+320 rather than only a projector rank. The odd pairing is a complete exact rational table with 410 ordered nonzero entries and rank 386: 30 endpoint, 60 auxiliary-complement and 320 cone-complement entries. Every entry has total degree one and the reverse coefficient is its negative. The full T, T^sharp_G and R diagonals are serialized on those same row indices; T^T Omega=Omega T^sharp_G and R=T^sharp_G T replay componentwise with the certified 381/5, 381/5 and 376/10 sign counts. V7 also corrects a coordinate label: the earlier count 54 describes the endpoint DeWitt/ghost pairing before Gate pullback, whereas the Gate-coordinate endpoint pairing has 30 entries; the suspension algebra is unchanged. Gate A remains fail closed because the full prolonged q1, H_alg, endpoint inclusion/projection and advanced/retarded Green operator coefficient tables are still represented by formal block identities and hashes rather than one portable component snapshot. Thus not every component operator adjoint or homotopy identity has been independently replayed. Local D, q2, Hadamard, Ward, positivity, renormalized products, QME and residual transfer remain open.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v7.md",
    })
    value["frontier_summary"]["theory_identity_front"] = {
        "branch": "STRICT_PURE_WEYL_386", "first_gate": "S0_CLASSICAL_AUTHORITY",
        "current_fact": "The common endpoint q1, suspension character, all 386 hybrid row names and the rank-386 odd pairing are exact; T adjointness replays on all 410 pairing entries.",
        "best_next_object": "Portable component coefficient tables for full prolonged q1, H_alg, endpoint inclusion/projection and both Green operators, followed by an independent all-row replay.",
    }
    value["strict_gate_a_progress"].update({
        "status": "FULL_COMPONENT_BASIS_PAIRING_AND_SUSPENSION_SERIALIZED_OPERATOR_TABLES_D_Q2_OPEN",
        "evidence": [*value["strict_gate_a_progress"]["evidence"], pairing["result_id"]],
        "component_pairing_control": {"rows": basis["dimension"], "complement_split": basis["algebraic_complement_split"], "pairing_entries": omega["nonzero_ordered_entry_count"], "pairing_rank": omega["rank"], "T_negative": signs["T_negative"], "R_negative": signs["R_negative"]},
        "remaining_common_carrier": pairing["next_gate"],
        "boundary": "The component basis and pairing are closed. Gate A still requires portable all-row operator tables, component adjoint/homotopy replay, common hashes, local D, q2 and residual-SDR extension.",
    })
    value["strict_gate_a_progress"]["endpoint_q1_control"].update({"full_pairing_open": False, "full_operator_snapshot_open": True})
    value["strict_gate_a_progress"]["suspended_adjoint_control"].update({"endpoint_pairing_entries": 30, "endpoint_pairing_entries_pre_pullback": 54, "full_component_pairing_serialized": True, "all_operator_component_adjoints_replayed": False})
    value["strict_component_pairing_serialization"] = {
        "result_id": pairing["result_id"], "status": pairing["result_state"],
        "full_rows": basis["dimension"], "endpoint_rows": basis["endpoint_dimension"],
        "algebraic_complement_rows": basis["algebraic_complement_dimension"], "algebraic_complement_split": basis["algebraic_complement_split"],
        "pairing_entries": omega["nonzero_ordered_entry_count"], "pairing_rank": omega["rank"],
        "endpoint_pairing_entries_gate_coordinates": pairing["terminology_reconciliation"]["gate_coordinate_endpoint_pairing_nonzero_entries"],
        "endpoint_pairing_entries_pre_pullback": pairing["terminology_reconciliation"]["suspension_v1_value"],
        "componentwise_T_adjoint_replayed": signs["componentwise_T_adjoint_relation_replayed"],
        "all_operator_component_adjoints_replayed": pairing["operator_adjoint_disposition"]["every_component_operator_adjoint_replayed"],
        "finite_serialization_base": pairing["foundational_strength"]["finite_serialization_base"],
        "next_gate": pairing["next_gate"],
    }
    value["route_selection"] = [
        {"rank": 1, "route": "STRICT_386_OPERATOR_COMPONENT_SERIALIZATION", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "VERY_HIGH", "tractability": "MEDIUM", "dependency_depth": "LOW", "recommendation": "Emit q1, H_alg, endpoint inclusion/projection and both Green operators on the fixed 386-row basis and replay every component identity."},
        {"rank": 2, "route": "STRICT_386_LOCAL_D", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "VERY_HIGH", "tractability": "LOW", "dependency_depth": "MEDIUM", "recommendation": "Serialize cylinder-time D on the accepted operator carrier and verify its q1 commutator before nonlinear transfer."},
        {"rank": 3, "route": "STRICT_386_Q2_GREEN_COMPATIBILITY", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "HIGH", "tractability": "LOW", "dependency_depth": "HIGH", "recommendation": "Bind target-action q2 to the same paired D-equivariant causal carrier and test contraction compatibility."},
        {"rank": 4, "route": "DIRECT_SPACETIME_Q26_HADAMARD", "branch": "BERGER_POSITIVE_CLOCK_54", "scientific_leverage": "VERY_HIGH", "tractability": "LOW", "dependency_depth": "MEDIUM", "recommendation": "Retain the analytically mature parallel route through direct nonstationary q26-equivariant distributional selection."},
        {"rank": 5, "route": "BACH_FLAT_NONLINEAR_CARTAN", "branch": "PURE_WEYL_BACH_FLAT_RANK310", "scientific_leverage": "HIGH", "tractability": "MEDIUM", "dependency_depth": "MEDIUM", "recommendation": "Use the broad curved strict causal branch as the independent nonlinear compatibility control."},
    ]
    value["research_queue"] = [
        {"priority": 1, "branch": "STRICT_PURE_WEYL_386", "object": "all-row operator component serialization", "why": "The basis and pairing are exact; portable q1/projector/Green bytes are the smallest remaining same-carrier object."},
        {"priority": 2, "branch": "STRICT_PURE_WEYL_386", "object": "same-carrier local D", "why": "D equivariance is the next admission gate after component operator replay."},
        {"priority": 3, "branch": "STRICT_PURE_WEYL_386", "object": "same-carrier q2/Green compatibility", "why": "This is the first nonlinear target-theory test after the complete unary carrier."},
        {"priority": 4, "branch": "BERGER_POSITIVE_CLOCK_54", "object": "direct spacetime q26-equivariant nonstationary Hadamard selection", "why": "Berger remains the shortest independent route toward a full-carrier Hadamard/Ward result."},
        {"priority": 5, "branch": "PURE_WEYL_BACH_FLAT_RANK310", "object": "same-carrier nonlinear cyclic D-Cartan transfer", "why": "It tests nonlinear survival on the broadest curved strict causal control."},
    ]
    value["provenance"]["inputs"] = [*previous["provenance"]["inputs"], {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V6 atlas predecessor"}, {"path": str(PAIRING.relative_to(ROOT)), "sha256": sha(PAIRING), "role": "exact 386-row component basis and pairing serialization"}]
    value["claim_flags"].update({"v6_preserved": True, "strict_386_component_pairing_serialized": True, "strict_full_386_pairing_serialized": True, "strict_386_component_basis_serialized": True, "strict_386_componentwise_t_adjoint_replayed": True, "strict_386_all_operator_component_adjoints_replayed": False, "strict_386_common_bytes_identified": False, "strict_386_local_d_certified": False, "strict_386_q2_green_compatibility_certified": False})
    remove = (
        "serialized 356-row complement pairing",
        "356 component pairing",
        "canonical odd pairing and cyclic convention on all 386 rows",
    )
    value["does_not_establish"] = list(dict.fromkeys(
        [item for item in previous["does_not_establish"] if not any(token in item for token in remove)]
        + [
            "portable full prolonged q1, H_alg, endpoint inclusion/projection or Green operator component tables",
            "an independent component-by-component replay of every operator adjoint and homotopy identity",
            "one accepted common Gate-A operator hash, local D, q2, Hadamard, QME or Lorentzian quantum theory",
        ]
    ))
    value["independent_checker"] = {"path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v7.py", "checks": ["V6 preservation", "77-cell closure", "386=30+36+320 row projection", "410-entry rank-386 pairing projection", "54-to-30 coordinate terminology repair", "componentwise suspension replay", "operator-byte and Gate-A firewalls", "route ranking", "content hashes", "canonical digest"], "expected_digest": ""}
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    item = value["strict_component_pairing_serialization"]
    lines = ["# Lorentzian Weyl BV completion atlas V7", "", "## Outcome", "", value["answer"], "", "## Component carrier result", "", f"- Rows: **{item['full_rows']} = {item['endpoint_rows']} + {item['algebraic_complement_split']}**.", f"- Odd pairing: **{item['pairing_entries']} ordered rational entries**, exact rank **{item['pairing_rank']}**.", f"- Endpoint pairing counts: **{item['endpoint_pairing_entries_gate_coordinates']}** in Gate coordinates; **{item['endpoint_pairing_entries_pre_pullback']}** before pullback.", "- Componentwise `T` pairing adjoint: **replayed**; every q1/projector/Green operator adjoint: **open**.", "", "## Updated route selection", "", "| rank | route | leverage | tractability | dependency depth |", "|---:|---|---|---|---|"]
    for route in value["route_selection"]:
        lines.append(f"| {route['rank']} | `{route['route']}` | {route['scientific_leverage']} | {route['tractability']} | {route['dependency_depth']} |")
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v7.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v7.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v7.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v7.py", "```", "", "## Boundaries", ""]
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V7: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result); REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V7: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
