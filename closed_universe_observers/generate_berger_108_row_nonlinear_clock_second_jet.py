#!/usr/bin/env python3
"""Generate the Berger nonlinear clock second-jet unary certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers import berger_108_row_nonlinear_clock_second_jet as second_jet
from closed_universe_observers.generate_berger_108_row_local_rod_hessian_pbw_overlay import (
    serialize_operator,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json"
PAYLOAD = P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET_PAYLOAD.json"
SCHEMA = P / "schema/berger-108-row-nonlinear-clock-second-jet-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-nonlinear-clock-second-jet-payload-v1.schema.json"
REPORT = P / "reports/berger-108-row-nonlinear-clock-second-jet.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "background_quotient": P / "certificates/BERGER_108_ROW_BACKGROUND_SPECIALIZATION_DIFFERENTIAL_IDEAL.json",
    "shifted_q2": P / "certificates/BERGER_108_ROW_SHIFTED_Q2_PHI2_PBW_OVERLAY.json",
    "local_rod_hessian": P / "certificates/BERGER_108_ROW_LOCAL_ROD_HESSIAN_PBW_OVERLAY.json",
    "first_jet_obstruction": P / "certificates/BERGER_108_ROW_Q1_PBW_FIRST_JET_REPLAY_OBSTRUCTION.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "berger_108_row_nonlinear_clock_second_jet.py",
    P / "verify_berger_108_row_nonlinear_clock_second_jet.py",
    P / "tests/test_berger_108_row_nonlinear_clock_second_jet.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
    REPORT,
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def payload_document(parts: dict[str, replay.Operator]) -> dict[str, Any]:
    blocks = [
        {"id": name, "entries": serialize_operator(parts[name])}
        for name in ("radial", "weyl", "temporal")
    ]
    correction = replay.add_operators(*parts.values())
    return {
        "schema": "closed-universe-berger-108-row-nonlinear-clock-second-jet-payload-v1",
        "result_id": "BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET_PAYLOAD",
        "scalar_matrix_shape": [108, 108],
        "blocks": blocks,
        "block_count": len(blocks),
        "correction_summary": replay.summary(correction),
        "blocks_canonical_sha256": canonical_sha256(blocks),
    }


def build(*, payload: dict[str, Any] | None = None, payload_hash: str | None = None) -> dict[str, Any]:
    dependencies = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if dependencies["first_jet_obstruction"]["atlas_status"] != "OBSTRUCTED":
        raise AssertionError("first-jet predecessor ceased to be fail-closed")

    q1 = replay.load_q1()
    q00 = q1[(0, 0)]
    correction, parts = second_jet.candidate_completion(q00, q1[(1, 0)])
    expected = {
        "radial": (21, 21, 288),
        "weyl": (9, 2, 619),
        "temporal": (65, 21, 5552),
    }
    for name, operator in parts.items():
        summary = replay.summary(operator)
        actual = (
            summary["operator_key_count"],
            summary["matrix_position_count"],
            summary["serialized_term_count"],
        )
        if actual != expected[name] or replay.cyclicity_defect(operator):
            raise AssertionError(f"{name} second-jet block drifted")

    payload = payload or payload_document(parts)
    rendered_payload = json.dumps(
        payload, sort_keys=True, separators=(",", ":")
    ) + "\n"
    payload_hash = payload_hash or hashlib.sha256(rendered_payload.encode()).hexdigest()
    if payload["correction_summary"] != replay.summary(correction):
        raise AssertionError("second-jet payload summary drifted")

    radial_q10 = replay.add_operators(q1[(1, 0)], parts["radial"])
    radial_square = second_jet.square_coefficient(q00, radial_q10)
    if (27, 4, ()) not in radial_square:
        raise AssertionError("radial diagnostic lost its free Weyl entry")

    after_weyl = replay.add_operators(radial_q10, parts["weyl"])
    weyl_square = second_jet.square_coefficient(q00, after_weyl)
    if any(row == 38 and column == 4 for row, column, _word in weyl_square):
        raise AssertionError("Weyl clock-doublet completion failed")
    temporal_input_keys = sum(
        row in (*range(27, 37), 38) and column == 3
        for row, column, _word in weyl_square
    )
    if temporal_input_keys != 43:
        raise AssertionError("temporal clock-doublet source drifted")

    q1[(1, 0)] = replay.add_operators(q1[(1, 0)], correction)
    cyclicity = {
        str(degree): replay.summary(replay.cyclicity_defect(operator))
        for degree, operator in q1.items()
    }
    if any(summary["operator_key_count"] for summary in cyclicity.values()):
        raise AssertionError("completed q1 ceased to be odd-cyclic")
    squared = replay.q1_squared_coefficients(q1)
    for degree in ((0, 0), (0, 1), (1, 1)):
        if squared[degree]:
            raise AssertionError(f"completed q1 free square failed at {degree}")
    if any(column in (3, 16) for _row, column, _word in squared[(1, 0)]):
        raise AssertionError("clock-ghost columns survived the second jet")
    quotient_defects, quotient_summary = replay.quotient_defect(squared[(1, 0)])
    if quotient_defects:
        raise AssertionError("completed epsilon_R_squared square is nonzero in the Berger quotient")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/REDUCED-MODE certificate completes the scalar Berger unary q1 only through the declared first bidegree jet in epsilon_R_squared and kappa and only after evaluation in the pinned finite six-rod/Phi2 Berger background differential quotient. The 95-key correction is generated, not hand curated. Its 21-key radial block is the Hessian induced in the action-normalized rod source by H_true=H+2 R H-3 R^2 eta+O(3). The 9-key Weyl-clock block is uniquely fixed on the certified contractible pair q00(sigma)=-R and completed by the frozen-pairing cotangent lift. The 65-key temporal block is uniquely fixed on q00(tau)=Theta and likewise completed by its cotangent lift; its Theta-star/Theta corner is formally self-adjoint. All three blocks and the corrected q1 coefficients are exactly odd-cyclic. The old -49/20 Weyl witness and every free tau/Theta input-column defect cancel. The remaining free epsilon_R_squared square has 261 keys because the background equations have not been imposed syntactically; all 699 evaluated modes reduce to zero in the certified same-background quotient. The mixed epsilon_R_squared*kappa square remains freely zero, satisfying the nonlinear team's unary activation gate. This authorizes, but does not itself construct or certify, apparatus q2/q3, K_Berger equivariance, observer-morphism stability, detector response on Z2, a same-background physical-branch dictionary, finite-parameter causal propagation, or any quantum claim."
    )
    return {
        "schema": "closed-universe-berger-108-row-nonlinear-clock-second-jet-v1",
        "result_id": "BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET",
        "setting_id": dependencies["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_SAME_BACKGROUND_FIRST_BIDEGREE_UNARY_COMPLETION",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": dependencies[name]["result_id"],
                "sha256": sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": payload_hash,
            "blocks_canonical_sha256": payload["blocks_canonical_sha256"],
            "correction_summary": payload["correction_summary"],
        },
        "second_jet_derivation": {
            "radial_metric_map": "H_true=H+2*R*H-3*R^2*eta+O(3)",
            "radial_action_source": "delta S_R/d H_A=(1/2) h_A^(mu nu) v_mu v_nu-(1/4) tr(h_A) v^2, summed over six rods",
            "weyl_clock_doublet": "q00(sigma)=-R fixes C(Theta_star,R); frozen-pairing adjunction fixes C(R_star,Theta)",
            "temporal_clock_doublet": "q00(tau)=Theta fixes C(-,Theta) from the tau residual; frozen-pairing adjunction fixes every metric-column cotangent mate",
            "block_summaries": {name: replay.summary(operator) for name, operator in parts.items()},
            "each_block_odd_cyclic": True,
            "temporal_source_operator_key_count": temporal_input_keys,
        },
        "completed_q1": {
            "shape": [108, 108],
            "bidegree_summaries": {
                str(degree): replay.summary(operator) for degree, operator in q1.items()
            },
            "odd_cyclicity_defects": cyclicity,
        },
        "nilpotency_replay": {
            "bidegree_summaries": {
                str(degree): replay.summary(operator) for degree, operator in squared.items()
            },
            "free_zero_bidegrees": ["(0, 0)", "(0, 1)", "(1, 1)"],
            "epsilon_R_squared_free_residual_summary": replay.summary(squared[(1, 0)]),
            "epsilon_R_squared_background_quotient_summary": quotient_summary,
            "clock_ghost_input_columns_absent_from_free_residual": True,
        },
        "activation_disposition": {
            "mixed_epsilon_R_squared_kappa_unary_gate": "PASSED",
            "apparatus_q2_q3_extension_authorized": True,
            "apparatus_q2_q3_extension_certified": False,
            "K_Berger_equivariance_certified": False,
            "observer_morphism_stability_certified": False,
            "tangent_cone_observer_restriction_authorized": False,
            "physical_branch_bridge_activated": False,
        },
        "flags": {
            "NONLINEAR_CLOCK_SECOND_JET_PAYLOAD_EXPORTED": True,
            "ALL_SECOND_JET_BLOCKS_ODD_CYCLIC": True,
            "EPSILON_R_SQUARED_Q1_SQUARED_ZERO_IN_BACKGROUND_QUOTIENT": True,
            "MIXED_EPSILON_R_SQUARED_KAPPA_Q1_SQUARED_ZERO": True,
            "COMPLETE_FIRST_BIDEGREE_UNARY_GATE": True,
            "APPARATUS_Q2_Q3_EXTENSION_AUTHORIZED": True,
            "APPARATUS_Q2_Q3_EXTENSION_CERTIFIED": False,
            "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EXPORT_APPARATUS_Q2_Q3_K_BERGER_EQUIVARIANCE_AND_OBSERVER_MORPHISM_STABILITY_ON_THE_COMPLETED_UNARY",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    q1 = replay.load_q1()
    _correction, parts = second_jet.candidate_completion(q1[(0, 0)], q1[(1, 0)])
    payload = payload_document(parts)
    payload_rendered = json.dumps(
        payload, sort_keys=True, separators=(",", ":")
    ) + "\n"
    value = build(payload=payload, payload_hash=hashlib.sha256(payload_rendered.encode()).hexdigest())
    for schema_path, document in ((PAYLOAD_SCHEMA, payload), (SCHEMA, value)):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(document)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        PAYLOAD.write_text(payload_rendered)
        CERTIFICATE.write_text(rendered)
    if args.check:
        if not PAYLOAD.exists() or PAYLOAD.read_text() != payload_rendered:
            raise SystemExit("stale Berger nonlinear clock second-jet payload")
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered:
            raise SystemExit("stale Berger nonlinear clock second-jet certificate")
    print("BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
