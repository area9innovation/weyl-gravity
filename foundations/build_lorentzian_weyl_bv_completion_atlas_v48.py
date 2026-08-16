#!/usr/bin/env python3
"""Build Atlas V48 after the strict classical BV Gate-A freeze."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V47.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V30_RECONCILIATION.json"
DUAL = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1B_ACTION_DUAL_LIFT_V1.json"
CYCLIC = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1.json"
M1C = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1C_COMMON_SNAPSHOT_V1.json"
SCHEMA = ROOT / "foundations/schema/foundational-lorentzian-weyl-bv-completion-atlas-v48.schema.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V48.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v48.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v30_reconciliation", "strict_m1b_action_dual_lift",
        "strict_m1b_typed_cyclic_composite", "strict_m1c_common_snapshot",
        "route_selection", "research_queue", "claim_flags", "does_not_establish",
    )
    return hashlib.sha256(json.dumps(
        {key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode()).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(row for row in value["branches"] if row["id"] == branch_id)
    return next(row for row in branch["stages"] if row["stage"] == stage_id)


def route(previous: dict[str, Any], name: str, rank: int) -> dict[str, Any]:
    row = deepcopy(next(item for item in previous["route_selection"] if item["route"] == name))
    row["rank"] = rank
    return row


def build() -> dict[str, Any]:
    previous, gate, dual, cyclic, m1c = map(load, (PREDECESSOR, GATE, DUAL, CYCLIC, M1C))
    expected = (
        (previous, "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V47"),
        (gate, "CLASSICAL_IMPORT_GATE_V30_RECONCILIATION"),
        (dual, "STRICT_M1B_ACTION_DUAL_LIFT_V1"),
        (cyclic, "STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1"),
        (m1c, "STRICT_M1C_COMMON_SNAPSHOT_V1"),
    )
    if any(value.get("result_id") != result_id for value, result_id in expected):
        raise ValueError("Atlas V48 authority drift")
    if gate["gate_disposition"]["gate_a_status"] != "VERIFIED" or gate["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] is not True:
        raise ValueError("Gate A not verified")
    if not all(gate["claim_flags"][key] for key in (
        "M1B_ACTION_DUAL_LIFT_COMPLETE", "M1B_TYPED_CYCLIC_REPLAY_COMPLETE",
        "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE", "M1C_COMMON_MANIFEST_REPLAY_COMPLETE",
        "M1_COMMON_STRICT_SNAPSHOT_COMPLETE",
    )):
        raise ValueError("classical freeze lifecycle incomplete")
    if gate["claim_flags"]["NONLINEAR_GREEN_COMPATIBILITY_CERTIFIED"] is not False or gate["claim_flags"]["HADAMARD_STATE_CONSTRUCTED"] is not False:
        raise ValueError("quantum firewall drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v48",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V48",
        "created": "2026-08-16",
        "question": "What becomes the highest-leverage route once one immutable strict pure-Weyl classical BV snapshot passes Gate A?",
        "answer": "Atlas V48 closes M1B, M1C and classical import Gate A on one immutable six-object typed snapshot. It retires the three classical-freeze routes and promotes the first genuinely quantum-facing problem: certify q2/q3 compatibility with both typed Lorentzian Green orientations. The following decision route is an explicit BRST-compatible Hadamard two-point function or a scoped obstruction theorem. No such compatibility or Hadamard result is claimed here.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": str(REPORT.relative_to(ROOT)),
    })

    disposition = gate["gate_disposition"]
    snapshot = gate["m1c_common_snapshot_resolution"]
    value["classical_import_reconciliation"] = {
        "result_id": gate["result_id"], "status": gate["result_state"],
        "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "exports_total": disposition["exports_total"],
        "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "freeze_checks_total": disposition["freeze_checks_total"],
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "gate_a_status": disposition["gate_a_status"], "minimal_missing_bundle": [],
        "snapshot_id": snapshot["snapshot_id"], "snapshot_sha256": snapshot["snapshot_sha256"],
    }
    value["strict_gate_v30_reconciliation"] = {
        "result_id": gate["result_id"], "status": gate["result_state"],
        "exports_total": 20, "exports_receiver_verified": 20,
        "freeze_checks_total": 10, "freeze_checks_receiver_verified": 10,
        "accepted_top_level_hashes": 7, "remaining_top_level_hashes": 0,
        "M1B_complete": True, "M1C_complete": True, "gate_a_status": "VERIFIED",
        "nonlinear_green_compatibility_certified": False,
        "full_complex_hadamard_state_constructed": False,
    }
    exact_dual = dual["represented_dual_lift"]["exact_replay"]
    value["strict_m1b_action_dual_lift"] = {
        "result_id": dual["result_id"], "content_sha256": dual["content_sha256"],
        "compact_source_action_duals": 470, "represented_check_coordinates": 4080,
        "local_pairing_rank": 386, "residual_action_pairing_rank": 940,
        "identity_defects": sum(exact_dual.values()), "M1B_action_dual_complete": True,
        "full_algebraic_dual_identified_with_compact_sources": False,
    }
    totals = cyclic["exact_cyclic_replay"]["identity_totals"]
    value["strict_m1b_typed_cyclic_composite"] = {
        "result_id": cyclic["result_id"], "content_sha256": cyclic["content_sha256"],
        "verification_core_coordinates": 8160, "residual_action_pairing_rank": 940,
        "typed_identities_replayed": len(totals), "identity_defects": sum(totals.values()),
        "M1B_complete": True, "verification_core_is_authoritative_full_bv_source": False,
    }
    value["strict_m1c_common_snapshot"] = {
        "result_id": m1c["result_id"], "content_sha256": m1c["content_sha256"],
        "snapshot_id": m1c["snapshot_id"], "snapshot_sha256": m1c["snapshot_sha256"],
        "artifact_pins": len(m1c["artifact_pins"]), "exports_bound": len(m1c["export_bindings"]),
        "top_level_hashes_bound": len(m1c["accepted_top_level_hashes"]),
        "gate_checks_replayed": len(m1c["gate_a_replay"]),
        "supplemental_checks_replayed": len(m1c["supplemental_replay"]),
        "M1C_complete": True,
    }

    authority = stage(value, "STRICT_PURE_WEYL_386", "S0_CLASSICAL_AUTHORITY")
    authority.update({
        "status": "CERTIFIED",
        "statement": "One immutable strict pure-Weyl classical BV snapshot now passes Gate A. Its six typed carrier objects bind all twenty exports and seven top-level hashes; independent receivers replay ten required and three supplemental exact audits. M1B includes the action-derived compact-source dual and rank-940 cyclic contraction.",
        "evidence": list(dict.fromkeys([*authority["evidence"], dual["result_id"], cyclic["result_id"], m1c["result_id"], gate["result_id"]])),
        "boundary": "This certifies the classical import source. The 8,160-coordinate verification core is not the authoritative full BV source, harmonic projection remains support-expanding, and q2/q3 Green compatibility, a full-complex Hadamard two-point function, renormalization and QME restoration remain open.",
    })

    routes = [
        {
            "rank": 1, "route": "STRICT_Q2_Q3_TYPED_GREEN_COMPATIBILITY", "branch": "STRICT_PURE_WEYL_386",
            "scientific_leverage": "VERY_HIGH", "tractability": "MEDIUM", "dependency_depth": "HIGH",
            "recommendation": "On the immutable Gate-A snapshot, type both advanced and retarded Green actions and replay the q2/q3 homotopy, chain, cyclic and causal-support identities without importing Berger data.",
        },
        route(previous, "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE", 2),
        {
            "rank": 3, "route": "STRICT_BRST_HADAMARD_TWO_POINT_OR_OBSTRUCTION", "branch": "STRICT_PURE_WEYL_386",
            "scientific_leverage": "VERY_HIGH", "tractability": "LOW", "dependency_depth": "HIGH",
            "recommendation": "After nonlinear Green compatibility, either construct a full-complex BRST-compatible Hadamard two-point function or isolate an incompatible subset of field-equation, wavefront, BRST, pairing and positivity conditions and prove a scoped obstruction.",
        },
        route(previous, "STRICT_D_CARTAN_AND_CHARGE_DECISION", 4),
        route(previous, "DIRECT_SPACETIME_Q26_HADAMARD", 5),
        route(previous, "STRICT_ANALYTIC_MOLLER_CONVERGENCE", 6),
        route(previous, "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN", 7),
    ]
    value["route_selection"] = routes
    value["research_queue"] = [
        {"priority": row["rank"], "branch": row["branch"], "object": row["route"], "why": row["recommendation"]}
        for row in routes
    ]
    value["frontier_summary"] = {
        "highest_value_next_route": "STRICT_Q2_Q3_TYPED_GREEN_COMPATIBILITY",
        "route_count": 7,
        "completed_since_v47": [
            "STRICT_M1B_ACTION_DUAL_LIFT", "STRICT_M1B_TYPED_CYCLIC_REPLAY",
            "STRICT_M1C_COMMON_MANIFEST_REPLAY", "CLASSICAL_IMPORT_GATE_A",
        ],
        "new_positive_result": f"Gate A is verified on immutable snapshot {m1c['snapshot_id']}: 16 content pins, 20 exports, seven hashes, ten Gate-A checks and three supplemental checks.",
        "surprise": "The compact-source action dual is determined by adjointness on 470 residual modes even though the other 4,080 algebraic dual coordinates remain check-only. The resulting rank-940 cyclic replay closes M1B without promoting the finite verification core into a continuous BV model.",
        "hard_boundary": "The classical source is frozen, but the nonlinear vertices have not yet been certified against both Lorentzian Green orientations. Therefore no full-complex Hadamard, renormalization, QME or residual quantum claim follows.",
    }
    value["claim_flags"].update({
        "v47_preserved": True,
        "strict_M1B_action_dual_lift_complete": True,
        "strict_M1B_typed_cyclic_replay_complete": True,
        "strict_M1B_represented_composite_contraction_complete": True,
        "strict_M1C_common_manifest_replay_complete": True,
        "strict_M1_common_strict_snapshot_complete": True,
        "strict_pure_weyl_classical_gate_passed": True,
        "strict_386_q2_q3_green_compatibility_certified": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "renormalized_lorentzian_products_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "residual_quantum_transfer_authorized": False,
        "lorentzian_full_theory_certified": False,
    })
    # Branch cells preserve their historical boundaries.  The atlas-level
    # nonclaim ledger describes the current frontier and must not repeat gaps
    # which V48 has just closed.
    value["does_not_establish"] = [
        "a no-go theorem for every nonstationary Krein Hadamard representative",
        "a no-go theorem for the complete general non-cone 104-row completion class",
        "a no-finite-carrier theorem or a global lower bound above 104 added free rows",
        "a normalized Berger H26_plus carrier or serialized Berger C26 two-point function",
        "equivalence between strict pure Weyl and the positive-clock Berger theory",
        "that a numerical route rank is a theorem or proof of eventual success",
        "that the finite D x SO(4) residual contraction is an arbitrary-support or causal Green homotopy",
        "support-locality of the D-finite W+/W- harmonic projector",
        "that the formal 8,980-coordinate comparison source is the authoritative classical BV source",
        "an effective numerical Green solver or serialized distribution-kernel bytes",
        "a constructive, choice-free, or weakest-base proof of the imported analytic Green theorem",
        "q2/q3 compatibility with both typed advanced and retarded Lorentzian Green homotopies",
        "general lambda-squared source-cocycle closure or an analytic Moller inverse",
        "a nonlinear D-Cartan homotopy or a proper-gauge/charge decision for the cylinder generator",
        "a full-complex BRST-compatible Hadamard two-point function or a no-go theorem for one",
        "renormalized Lorentzian products, QME restoration, residual quantum transfer or a Lorentzian quantum theory",
    ]
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        *(
            {"path": str(path.relative_to(ROOT)), "result_or_artifact_id": authority["result_id"], "sha256": sha(path), "role": role}
            for path, authority, role in (
                (PREDECESSOR, previous, "immutable Atlas V47 predecessor"),
                (DUAL, dual, "exact action-derived compact-source dual lift"),
                (CYCLIC, cyclic, "exact rank-940 typed cyclic composite"),
                (M1C, m1c, "immutable common classical snapshot"),
                (GATE, gate, "independently verified classical Gate-A decision"),
            )
        ),
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v48.py",
        "checks": [
            "V47 predecessor and 77-cell preservation", "independent Gate V30 receiver replay",
            "M1B action-dual and thirteen cyclic identities", "M1C snapshot identity and census",
            "retirement of three classical-freeze routes", "nonlinear Green and Hadamard firewalls",
            "canonical atlas digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    return value


def report(value: dict[str, Any]) -> str:
    snapshot = value["strict_m1c_common_snapshot"]
    routes = "\n".join(f"{row['rank']}. `{row['route']}` — {row['recommendation']}" for row in value["route_selection"])
    return f"""# Lorentzian Weyl BV completion atlas v48

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Classical freeze

Gate A is verified on `{snapshot['snapshot_id']}`.  The immutable snapshot
contains {snapshot['artifact_pins']} content pins, binds all {snapshot['exports_bound']}
exports and all {snapshot['top_level_hashes_bound']} top-level hashes, and replays
{snapshot['gate_checks_replayed']} required plus {snapshot['supplemental_checks_replayed']}
supplemental checks.  The M1B action dual and all thirteen typed cyclic identities
have zero defects.

## Ranked routes

{routes}

## Boundary

This is the classical import freeze, not a quantum construction.  Compatibility
of q2 and q3 with both Lorentzian Green orientations is still open.  There is no
full-complex BRST-compatible Hadamard two-point function, renormalized Lorentzian
product, restored QME, residual quantum transfer, or certified Lorentzian quantum
theory.  The next result must either advance that exact chain or state a scoped
obstruction without borrowing a different-theory control.
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return json.dumps(value, indent=2, ensure_ascii=False).encode() + b"\n", report(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V48: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V48: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
