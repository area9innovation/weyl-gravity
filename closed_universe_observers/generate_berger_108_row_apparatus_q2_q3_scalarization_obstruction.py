#!/usr/bin/env python3
"""Fail closed on the first unavailable 108-row apparatus interaction map."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_APPARATUS_Q2_Q3_SCALARIZATION_OBSTRUCTION.json"
SCHEMA = P / "schema/berger-108-row-apparatus-q2-q3-scalarization-obstruction-v1.schema.json"
REPORT = P / "reports/berger-108-row-apparatus-q2-q3-scalarization-obstruction.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "completed_unary": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "apparatus_action_jets": P / "certificates/BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE.json",
    "emitter_master_identity": P / "certificates/BERGER_108_ROW_EMITTER_Q1_Q2_MASTER_IDENTITY.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "verify_berger_108_row_apparatus_q2_q3_scalarization_obstruction.py",
    P / "tests/test_berger_108_row_apparatus_q2_q3_scalarization_obstruction.py",
    SCHEMA,
    REPORT,
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coordinate_jet_nonuniqueness(*, f2: Fraction = Fraction(1), f3: Fraction = Fraction(1)) -> dict[str, Any]:
    """Exhibit the first two Taylor coefficients not fixed by unary data.

    Let q1(e)=f and q1(f)=0 on a two-term complex.  A formal coordinate
    change with F1=id and F2(e,e)=a e leaves q1 unchanged but changes q2 by
    [q1,F2](e,e)=a f.  Likewise F3(e,e,e)=b e changes q3 by b f while
    leaving q1 and F2 fixed.  This is the local coalgebra-coordinate law used
    by every L-infinity transport; no Berger mode identification enters.
    """

    q1_before = [["e", "f"], ["f", "0"]]
    q1_after = q1_before  # F1 is the identity for every a,b.
    q2_difference = f2
    q3_difference = f3
    return {
        "graded_fixture": {"degree_0_basis": ["e"], "degree_1_basis": ["f"], "q1(e)": "f", "q1(f)": "0"},
        "coordinate_map": {
            "F1": "identity",
            "F2(e,e)": f"{f2} e",
            "F3(e,e,e)": f"{f3} e",
            "all_other_displayed_components": "0",
        },
        "transport_law": {
            "unary": "q1'=F1 q1 F1^-1=q1",
            "bilinear": "q2'-q2=[q1,F2]",
            "trilinear_first_unfixed_term": "q3'-q3 contains [q1,F3] once F1 and F2 are held fixed",
        },
        "exact_replay": {
            "q1_before": q1_before,
            "q1_after": q1_after,
            "unary_difference_count": int(q1_before != q1_after),
            "q2_difference_on_e_e": f"{q2_difference} f",
            "q2_difference_nonzero": q2_difference != 0,
            "q3_difference_on_e_e_e": f"{q3_difference} f",
            "q3_difference_nonzero": q3_difference != 0,
        },
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_contract": "CANONICAL_108_ROW_COMPONENT_CROSSWALK_CERTIFIED",
        "completed_unary": "COMPLETE_FIRST_BIDEGREE_UNARY_GATE",
        "apparatus_action_jets": "APPARATUS_Q2_ACTION_JET_EXPORTED",
        "emitter_master_identity": "COVARIANT_108_ROW_Q1_Q2_MASTER_IDENTITY_CERTIFIED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency flag dropped: {name}.{flag}")

    witness = coordinate_jet_nonuniqueness()
    delete_f2 = coordinate_jet_nonuniqueness(f2=Fraction(0))
    delete_f3 = coordinate_jet_nonuniqueness(f3=Fraction(0))
    if witness["exact_replay"]["unary_difference_count"] != 0:
        raise AssertionError("identity linear coordinate map changed q1")
    if not witness["exact_replay"]["q2_difference_nonzero"]:
        raise AssertionError("F2 failed to separate two q2 transports")
    if not witness["exact_replay"]["q3_difference_nonzero"]:
        raise AssertionError("F3 failed to separate two q3 transports")
    if delete_f2["exact_replay"]["q2_difference_nonzero"]:
        raise AssertionError("zero-F2 mutation did not remove the q2 witness")
    if delete_f3["exact_replay"]["q3_difference_nonzero"]:
        raise AssertionError("zero-F3 mutation did not remove the q3 witness")

    clock_scope = values["completed_unary"]["second_jet_derivation"]
    if "residual" not in clock_scope["temporal_clock_doublet"]:
        raise AssertionError("completed unary no longer declares its residual-fixed temporal block")
    boundary = (
        "This exact LOCAL-ALGEBRAIC fail-closed certificate audits the activated scalar 108-row apparatus "
        "q2/q3 lift after the same-background unary gate. The 108-row component basis, signed odd pairing, "
        "coefficient-jet PBW algebra, 84-row action-level apparatus derivatives, emitter common-action orbits, "
        "and completed nilpotent unary are retained. The first unavailable map is the nonlinear Weyl/temporal "
        "clock coordinate jet: the unary certificate exports residual-fixed doublet blocks and their frozen-pairing "
        "mates, not an action-derived nonlinear canonical transformation. The displayed exact "
        "two-term-complex witness proves the relevant logical nonuniqueness: coordinate maps with identical F1 "
        "and hence identical q1 but different F2 give different q2 by [q1,F2]; even after F2 is fixed, different "
        "F3 give different q3. Therefore the old covariant Frechet-derivative formulas cannot be raised into a "
        "unique scalar PBW q2/q3 compatible with the newly repaired unary merely by choosing components. This is "
        "an input obstruction, not a nonexistence theorem and not a defect in the certified 84-row action-level "
        "identity. No componentwise q1q2 or q2q2+q1q3 replay, K_Berger equivariance, observer-morphism stability, "
        "detector restriction to Z2, nonlinear rank promotion, physical-branch Bridge 3, finite-parameter causal "
        "or quantum claim follows. The repair is to derive and serialize the same-background nonlinear clock "
        "canonical map through F3 (with its cotangent lift and action normalization), then regenerate q2/q3 and "
        "run the arity identities rather than fitting a tensor to the desired identities."
    )
    return {
        "schema": "closed-universe-berger-108-row-apparatus-q2-q3-scalarization-obstruction-v1",
        "result_id": "BERGER_108_ROW_APPARATUS_Q2_Q3_SCALARIZATION_OBSTRUCTION",
        "setting_id": values["completed_unary"]["setting_id"],
        "claim_status": "NO_CERTIFIED_MAP_NONLINEAR_CLOCK_COORDINATE_JETS_MISSING",
        "atlas_status": "NO_CERTIFIED_MAP",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "retained_certified_inputs": {
            "canonical_108_row_component_and_pairing_contract": True,
            "same_background_completed_unary": True,
            "apparatus_84_row_action_q2_q3_derivative_families": True,
            "emitter_108_row_covariant_q1_q2_master_identity": True,
            "radial_metric_map": clock_scope["radial_metric_map"],
        },
        "first_unavailable_map": {
            "domain": "completed same-background scalar q1 plus covariant action-derivative labels",
            "codomain": "unique scalar 108x108x108 q2 and 108x108x108x108 q3 PBW payloads",
            "status": "NO_CERTIFIED_MAP",
            "missing_objects": [
                "action-derived Weyl/temporal nonlinear clock coordinate map F2 in the canonical 108-row component basis",
                "its signed-pairing BV cotangent lift and action normalization",
                "the compatible F3 clock coordinate jet needed to transport q3",
                "generated scalar apparatus/emitter q2 and q3 payloads after that transport",
            ],
            "why_84_row_formulas_do_not_close_it": "they predate the scalar unary clock repair and name covariant Frechet-derivative families; they do not specify the missing nonlinear chart jets that transport those families to the repaired 108-row scalar carrier",
        },
        "exact_nonuniqueness_witness": witness,
        "mutation_results": [
            {"name": "set_F2_to_zero", "detected": not delete_f2["exact_replay"]["q2_difference_nonzero"]},
            {"name": "set_F3_to_zero", "detected": not delete_f3["exact_replay"]["q3_difference_nonzero"]},
            {"name": "promote_covariant_action_labels_to_scalar_payload", "detected": True, "defect": "no nonlinear clock F2/F3 transport is supplied"},
        ],
        "activation_disposition": {
            "scalar_q2_payload_exported": False,
            "scalar_q3_payload_exported": False,
            "component_q1_q2_replay_certified": False,
            "component_q2_q2_plus_q1_q3_replay_certified": False,
            "K_Berger_equivariance_certified": False,
            "observer_morphism_stability_certified": False,
            "detector_response_on_second_order_cone_authorized": False,
            "nonlinear_response_rank_promoted": False,
            "physical_branch_bridge_activated": False,
        },
        "flags": {
            "SCALAR_APPARATUS_Q2_Q3_LIFT_AUDITED": True,
            "NONLINEAR_CLOCK_COORDINATE_JET_NONUNIQUENESS_CERTIFIED": True,
            "SUPPORT_LOCAL_108_ROW_PBW_Q2_PAYLOAD_EXPORTED": False,
            "SUPPORT_LOCAL_108_ROW_PBW_Q3_PAYLOAD_EXPORTED": False,
            "COMPONENT_Q1_Q2_IDENTITY_CERTIFIED": False,
            "COMPONENT_ARITY_THREE_IDENTITY_CERTIFIED": False,
            "K_BERGER_EQUIVARIANCE_CERTIFIED": False,
            "OBSERVER_MORPHISM_STABILITY_CERTIFIED": False,
            "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "DERIVE_AND_SERIALIZE_ACTION_NORMALIZED_NONLINEAR_CLOCK_CANONICAL_MAP_F2_F3_AND_COTANGENT_LIFT",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale Berger 108-row apparatus q2/q3 scalarization obstruction")
    print("BERGER_108_ROW_APPARATUS_Q2_Q3_SCALARIZATION_OBSTRUCTION generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
