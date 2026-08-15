#!/usr/bin/env python3
"""Build atlas V11 from V10 plus the complete strict 386-row q1 snapshot."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V10.json"
Q1 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V11.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v11.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_causal_sign_transport",
        "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge",
        "strict_component_pairing_serialization", "strict_operator_portability",
        "strict_full_q1_split_sign_gate", "strict_auxiliary_q_sign_repair",
        "strict_full_q1_component_jet_table", "berger_h26_c26_decision_chain",
        "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def strict_branch(value: dict[str, Any]) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == "STRICT_PURE_WEYL_386")


def stage(value: dict[str, Any], stage_id: str) -> dict[str, Any]:
    return next(item for item in strict_branch(value)["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text())
    q1 = json.loads(Q1.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V10":
        raise ValueError("V10 predecessor drift")
    if q1.get("result_id") != "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1":
        raise ValueError("full-q1 dependency drift")
    flags = q1["claim_flags"]
    for key in (
        "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_SERIALIZED",
        "STRICT_386_FULL_Q1_SQUARED_ZERO_REPLAYED",
        "STRICT_386_FULL_Q1_SUSPENDED_CYCLICITY_REPLAYED",
        "STRICT_386_UNARY_SNAPSHOT_HASH_ESTABLISHED",
    ):
        if flags.get(key) is not True:
            raise ValueError("full-q1 positive flag drift: " + key)
    if flags["STRICT_386_FULL_SDR_OPERATOR_TABLES_SERIALIZED"] or flags["CLASSICAL_IMPORT_GATE_PASSED"]:
        raise ValueError("SDR/import promotion drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v11",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V11",
        "created": "2026-08-15",
        "repository_base_commit": "cfc609324416133a1a0c712e2f706d3bc3fddd88",
        "question": "After Atlas V10 repaired the auxiliary cotangent sign, can the entire strict 386-row split unary BV differential now be treated as one receiver-readable exact object, and what is the first remaining boundary before a common Lorentzian classical import snapshot can be accepted?",
        "answer": "Atlas V11 records the first complete content-addressed unary snapshot on the published strict 386-row carrier. The snapshot binds the 30-row Gate endpoint, repaired 36-row generalized-auxiliary complement and 320-row split curvature mapping cylinder to the rank-386 odd pairing and the certified suspension character. Eighteen operator tables contain 127 symmetrized-covariant jet coefficient tables and 2,193 nonzero rational coefficients: 619 on the endpoint, 30 on the auxiliary summand and 1,544 on the cone and its cotangent dual. The endpoint tables independently reproduce all 80 previously matched gauge, Bach and Noether tables; the cone includes complete lower-order Ecurv and Ncurv tables, their formal adjoints and every incidence arrow. Nilpotency replays in the appropriate exact natural/PBW calculus, including the unit-S3 commutator correction, and all 70 derivative multiindices satisfy the Gate suspended-cyclicity identity with zero exact defects. Crucially, the replay distinguishes the 30-row endpoint's certified suspended adjoint from the ordinary adjoint used on the 356-row complement: erasing that distinction creates spurious endpoint defects even though the underlying causal complex is unchanged. The artifact records the suspension character explicitly, so future consumers cannot accidentally compare operators under incompatible adjoint conventions. This closes the highest-ranked V10 route without converting the degree-zero T/A/B shear into primitive q1 arrows. Gate A nevertheless remains fail closed. The local contraction, endpoint inclusion/projection, canonical shear and represented advanced/retarded Green actions are not yet serialized against the unary snapshot, so the full SDR, causal support and suspended Green-adjoint identities cannot yet be replayed componentwise on one accepted object. Local D, q2 compatibility, Hadamard construction, Ward identities, renormalized Lorentzian products, QME restoration and residual transfer remain downstream and unpromoted.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v11.md",
    })

    q1_projection = {
        "result_id": q1["result_id"],
        "status": q1["result_state"],
        "carrier_dimension": q1["q1_serialization"]["carrier_dimension"],
        "carrier_split": q1["q1_serialization"]["carrier_split"],
        "operator_tables": q1["q1_serialization"]["counts"]["operator_tables"],
        "coefficient_multiindex_tables": q1["q1_serialization"]["counts"]["coefficient_multiindex_tables"],
        "nonzero_rational_coefficients": q1["q1_serialization"]["counts"]["nonzero_rational_coefficients"],
        "sector_coefficients": q1["q1_serialization"]["counts"]["by_sector"],
        "maximum_order": q1["q1_serialization"]["maximum_order"],
        "q1_squared_zero": q1["nilpotency_replay"]["full_q1_squared_zero"],
        "suspended_cyclicity_defects": q1["suspended_cyclicity_replay"]["exact_defects"],
        "derivative_multiindices_checked": q1["suspended_cyclicity_replay"]["coefficientwise_multiindices_checked"],
        "unary_snapshot_sha256": q1["unary_snapshot"]["snapshot_sha256"],
        "full_sdr_tables_serialized": flags["STRICT_386_FULL_SDR_OPERATOR_TABLES_SERIALIZED"],
        "classical_import_gate_passed": flags["CLASSICAL_IMPORT_GATE_PASSED"],
        "next_gate": q1["next_gate"],
    }
    value["strict_full_q1_component_jet_table"] = q1_projection
    stage(value, "S0_CLASSICAL_AUTHORITY").update({
        "status": "FAIL_CLOSED",
        "statement": "The complete 386-row split q1 is now exact receiver-readable data: 18 operator tables, 2,193 rational coefficients, sectorwise nilpotency and zero suspended-cyclicity defects. Gate A remains closed because the SDR, canonical shear and represented Green actions are not yet bound to the unary snapshot.",
        "evidence": [*stage(value, "S0_CLASSICAL_AUTHORITY")["evidence"], q1["result_id"]],
        "boundary": "A unary snapshot is necessary but not a common Gate-A snapshot. H_alg, endpoint inclusion/projection, T/A/B shear, advanced/retarded Green actions, local D and q2 remain absent from the accepted common object.",
    })
    strict_branch(value)["next_decisive_object"] = "Serialize H_alg, endpoint inclusion/projection and the canonical T/A/B shear on the unary snapshot, then add represented endpoint/full Green actions and replay the SDR, causal-support and suspended-adjoint identities componentwise."
    value["frontier_summary"]["theory_identity_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "first_gate": "S0_CLASSICAL_AUTHORITY",
        "current_fact": "The full 386-row unary differential, pairing and suspension are one exact snapshot with nilpotency and suspended cyclicity replayed; the remaining Gate-A gap is the local SDR/shear/represented-Green action bundle.",
        "best_next_object": "Component tables for H_alg, endpoint inclusion/projection and the T/A/B shear, followed by represented advanced/retarded Green actions on the same snapshot.",
    }
    value["strict_gate_a_progress"].update({
        "status": "FULL_Q1_SERIALIZED_SDR_COMMON_SNAPSHOT_REQUIRED",
        "full_q1_component_jet_control": q1_projection,
        "remaining_common_carrier": q1["next_gate"],
        "boundary": "The unary snapshot passes exact q1 tests, but Gate A still requires componentwise SDR/shear/Green actions and one receiver-accepted common snapshot before q2 or D are bound.",
    })

    routes = [
        ("STRICT_386_LOCAL_SDR_COMPONENT_MAPS", "STRICT_PURE_WEYL_386", "VERY_HIGH", "HIGH", "LOW", "Serialize H_alg and endpoint inclusion/projection from the exact producers and independently replay PI, IP-I=qH+Hq and cyclicity on the fixed unary snapshot."),
        ("STRICT_386_CANONICAL_SHEAR_TABLE", "STRICT_PURE_WEYL_386", "HIGH", "HIGH", "LOW", "Serialize the degree-zero T/A/B canonical shear and inverse separately from q1, preserving the split-coordinate theorem and support locality."),
        ("STRICT_ENDPOINT_ANALYTIC_GREEN_ACTION", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "MEDIUM", "Declare represented test/distribution spaces and import advanced/retarded endpoint actions with topology, continuity, uniqueness, support and adjoint data."),
        ("STRICT_FULL_GREEN_COMPONENT_ACTION_REPLAY", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Compose the represented endpoint Green action with accepted SDR/shear tables and replay full homotopy, causal support and suspended adjointness on the fixed carrier."),
        ("STRICT_386_ACCEPTED_COMMON_SNAPSHOT", "STRICT_PURE_WEYL_386", "VERY_HIGH", "HIGH", "LOW", "Bind basis, pairing, q1, SDR, shear and represented Green actions into one receiver-accepted import snapshot without treating producer regeneration as independent verification."),
        ("STRICT_386_LOCAL_D", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "MEDIUM", "Serialize cylinder-time D on the accepted common carrier and verify its q1 commutator before any nonlinear promotion."),
        ("STRICT_386_Q2_GREEN_COMPATIBILITY", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Bind target-action q2 to the same paired D-equivariant causal carrier and test contraction compatibility after the complete unary action replay."),
        ("DIRECT_SPACETIME_Q26_HADAMARD", "BERGER_POSITIVE_CLOCK_54", "VERY_HIGH", "LOW", "MEDIUM", "Retain the analytically mature independent route through direct nonstationary q26-equivariant distributional state selection."),
        ("BACH_FLAT_NONLINEAR_CARTAN", "PURE_WEYL_BACH_FLAT_RANK310", "HIGH", "MEDIUM", "MEDIUM", "Use the broad curved strict causal branch as an independent nonlinear compatibility control while the target-theory import route advances."),
    ]
    value["route_selection"] = [
        {"rank": rank, "route": route, "branch": branch, "scientific_leverage": leverage, "tractability": tractability, "dependency_depth": depth, "recommendation": recommendation}
        for rank, (route, branch, leverage, tractability, depth, recommendation) in enumerate(routes, 1)
    ]
    value["research_queue"] = [{"priority": item["rank"], "branch": item["branch"], "object": item["route"], "why": item["recommendation"]} for item in value["route_selection"]]
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V10 atlas predecessor"},
        {"path": str(Q1.relative_to(ROOT)), "sha256": sha(Q1), "role": "complete exact 386-row unary snapshot and replay"},
    ]
    value["claim_flags"].update({
        "v10_preserved": True,
        "strict_full_386_q1_portable_component_bytes": True,
        "strict_386_full_q1_squared_zero_replayed": True,
        "strict_386_full_q1_suspended_cyclicity_replayed": True,
        "strict_386_unary_snapshot_hash_established": True,
        "strict_386_full_sdr_operator_tables_serialized": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys(previous["does_not_establish"] + q1["does_not_establish"]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v11.py",
        "checks": ["V10 preservation", "77-cell closure", "strict S0-only mutation", "full-q1 projection", "2,193 coefficient inventory", "zero nilpotency/cyclicity defects", "unary snapshot binding", "SDR/import firewall", "causal theorem preservation", "nine-route ranking", "append-only provenance", "content hashes", "canonical digest"],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    item = value["strict_full_q1_component_jet_table"]
    lines = [
        "# Lorentzian Weyl BV completion atlas V11", "", "## Outcome", "", value["answer"], "",
        "## Complete unary snapshot", "",
        "| carrier sector | nonzero rational coefficients |", "|---|---:|",
        f"| Gate endpoint 30 | {item['sector_coefficients']['endpoint_30']} |",
        f"| auxiliary complement 36 | {item['sector_coefficients']['auxiliary_36']} |",
        f"| mapping cone/cotangent 320 | {item['sector_coefficients']['mapping_cone_320']} |",
        f"| **total 386** | **{item['nonzero_rational_coefficients']}** |", "",
        f"The {item['operator_tables']} operator tables contain {item['coefficient_multiindex_tables']} jet tables. q1 squared is `{item['q1_squared_zero']}` and suspended cyclicity has **{item['suspended_cyclicity_defects']} defects** over {item['derivative_multiindices_checked']} derivative multiindices.", "",
        f"Unary snapshot: `{item['unary_snapshot_sha256']}`.", "",
        "## Updated route selection", "", "| rank | route | branch | leverage | tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(f"| {route['rank']} | `{route['route']}` | `{route['branch']}` | {route['scientific_leverage']} | {route['tractability']} |" for route in value["route_selection"])
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v11.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v11.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v11.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v11.py", "```", "", "## Boundaries", ""]
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V11: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V11: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
