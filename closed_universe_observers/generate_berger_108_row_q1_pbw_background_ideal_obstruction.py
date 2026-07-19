#!/usr/bin/env python3
"""Certify the missing background differential ideal for scalar 108-row q1."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_108_row_component_jet_contract import (
    add,
    derivative,
    generator,
    normalize,
    scale,
    serialize,
)

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_Q1_PBW_BACKGROUND_IDEAL_OBSTRUCTION.json"
SCHEMA = P / "schema/berger-108-row-q1-pbw-background-ideal-obstruction-v1.schema.json"
REPORT = P / "reports/berger-108-row-q1-pbw-background-ideal-obstruction.md"
DEPENDENCIES = {
    "component_jet_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "base_64_q1": ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json",
    "rod_unary": P / "certificates/BERGER_84_ROW_ROD_GRAVITY_UNARY.json",
    "normalized_apparatus_unary": P / "certificates/BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY.json",
    "emitter_unary": P / "certificates/BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL.json",
    "global_rods": P / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "verify_berger_108_row_q1_pbw_background_ideal_obstruction.py",
    P / "tests/test_berger_108_row_q1_pbw_background_ideal_obstruction.py",
    SCHEMA,
    REPORT,
]

ONE = (Fraction(1), Fraction(0))
MINUS_ONE = (Fraction(-1), Fraction(0))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def free_jet_witness(*, delete_one_term: bool = False) -> dict[str, Any]:
    rod = normalize([(ONE, [generator("background", "R0_1")])])
    box_terms = [
        scale(derivative(derivative(rod, 0), 0), MINUS_ONE),
        *(derivative(derivative(rod, axis), axis) for axis in (1, 2, 3)),
    ]
    box_rod = add(*box_terms)
    residual = derivative(box_rod, 1)
    serialized = serialize(residual)
    if delete_one_term:
        serialized = serialized[:-1]
    evaluation = 0
    for term in serialized:
        multiindex = term["factors"][0]["spacetime_multiindex"]
        if multiindex == [0, 3, 0, 0]:
            coefficient = term["coefficient"]["rational"]
            evaluation += Fraction(coefficient["numerator"], coefficient["denominator"])
    return {
        "background_generator": "R0_1",
        "scalar_wave_operator": "Box=-e0^2+e1^2+e2^2+e3^2 (the invariant-frame connection trace vanishes)",
        "box_R_normal_form": serialize(box_rod),
        "required_q1_squared_noether_path": "K_RR(Gamma_R(e1))+K_Rh(Lie_e1 gHat)=e1(Box_gHat R0_1)",
        "free_jet_residual_normal_form": serialized,
        "free_jet_residual_term_count": len(serialized),
        "separating_evaluation": {
            "assignment": "R0_1 jet [0,3,0,0]=1 and the other displayed third jets=0",
            "value": str(evaluation),
            "nonzero": evaluation != 0,
        },
        "on_shell_differential_ideal_reduction": "e1(Box R0_1)=0 only after adjoining Box R0_1 and all Berger-frame prolongations to a differential ideal",
        "free_and_on_shell_realizations_distinct": evaluation != 0,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if not values["component_jet_contract"]["flags"]["NONCOMMUTING_BERGER_FRAME_PBW_CERTIFIED"]:
        raise AssertionError("PBW frame repair is unavailable")
    if not values["base_64_q1"]["flags"]["BERGER_PORTABLE_64_ROW_UNARY_Q1"]:
        raise AssertionError("scalar base q1 is unavailable")
    if values["global_rods"]["exact_checks"]["wave_residuals"] != ["0"] * 6:
        raise AssertionError("global rod on-shell witness drifted")
    specializations = values["component_jet_contract"]["coefficient_algebra"]["exact_profile_specializations"]
    if set(specializations) != {"detector_profiles", "emitter_switches"}:
        raise AssertionError("background-specialization disposition changed")
    witness = free_jet_witness()
    mutation = free_jet_witness(delete_one_term=True)
    if witness["free_jet_residual_term_count"] != 4 or not witness["separating_evaluation"]["nonzero"]:
        raise AssertionError("free background-jet obstruction disappeared")
    if mutation["free_jet_residual_term_count"] != 3:
        raise AssertionError("residual deletion mutation was not detected")
    boundary = (
        "This exact LOCAL-ALGEBRAIC obstruction preserves the pinned scalar 64-row q1, the corrected noncommuting 108-row component/jet contract, the certified covariant rod Noether identity, the six exact on-shell global rods and the covariant emitter/apparatus unary theorems. It proves that these artifacts still do not determine a nilpotent scalar 108-row PBW q1 inside the receiving free coefficient-jet algebra: the required rod/diffeomorphism length-two path reduces covariantly to e1(Box R0_1), whose free PBW normal form has four independent third-jet terms and admits the exact separating value 1. The global-rod certificate separately evaluates Box R_aI=0, but the component contract contains no content-addressed specialization from those rod functions (or Phi2) to its abstract background generators and no differential ideal generated by their equations and prolongations. Therefore the scalar q1 promotion remains NO_CERTIFIED_MAP. The minimal next declaration is a Berger-frame differential background ideal/crosswalk binding all six rods, Phi2 and the shifted gravity-clock equations, closed under the three nonzero frame brackets. No scalar 108-row q1/q2 payload, component replay, solved backreaction, tangent-cone restriction, Bridge 3, finite-parameter propagation or quantum claim is promoted."
    )
    return {
        "schema": "closed-universe-berger-108-row-q1-pbw-background-ideal-obstruction-v1",
        "result_id": "BERGER_108_ROW_Q1_PBW_BACKGROUND_IDEAL_OBSTRUCTION",
        "setting_id": values["component_jet_contract"]["setting_id"],
        "claim_status": "NO_CERTIFIED_MAP_FREE_JET_ALGEBRA_TO_NILPOTENT_SCALAR_108_ROW_Q1",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "available_scalar_data": {
            "base_q1_shape": values["base_64_q1"]["full_complex"]["classical_unary_q1"]["shape"],
            "base_q1_entry_count": len(values["base_64_q1"]["full_complex"]["classical_unary_q1"]["entries"]),
            "base_q1_payload_sha256": values["base_64_q1"]["full_complex"]["classical_unary_q1"]["sha256"],
            "rod_gauge_scalar_entry_count": len(values["rod_unary"]["rod_gauge_blocks"]["gamma_entries"]),
            "rod_gauge_adjoint_scalar_entry_count": len(values["rod_unary"]["rod_gauge_blocks"]["gamma_sharp_q1_entries"]),
            "covariant_rod_noether_identity": values["rod_unary"]["bv_noether_audit"]["scalar_naturality"],
            "global_rod_wave_residuals": values["global_rods"]["exact_checks"]["wave_residuals"],
        },
        "background_ideal_obstruction": witness,
        "missing_object_ledger": {
            "first_missing_object": "content-addressed specialization from abstract background generators to the six exact rods and Phi2, plus the differential ideal of shifted background equations and every Berger-frame prolongation",
            "component_contract_background_specializations": sorted(specializations),
            "rod_background_specialization_exported": False,
            "Phi2_background_specialization_exported": False,
            "background_equation_differential_ideal_exported": False,
            "complete_scalar_84_row_q1_exported": False,
            "complete_scalar_108_row_q1_exported": False,
        },
        "mutations": [
            {"name": "delete_one_free_residual_term", "detected": mutation["free_jet_residual_term_count"] != witness["free_jet_residual_term_count"]},
            {"name": "silently_impose_Box_R_without_crosswalk", "detected": witness["separating_evaluation"]["nonzero"]},
            {"name": "omit_differential_prolongation_e1_Box_R", "detected": witness["free_jet_residual_term_count"] > 0},
        ],
        "flags": {
            "PINNED_64_ROW_SCALAR_Q1_VERIFIED": True,
            "NONCOMMUTING_COMPONENT_JET_CONTRACT_VERIFIED": True,
            "COVARIANT_ROD_NOETHER_IDENTITY_PRESERVED": True,
            "GLOBAL_ROD_ON_SHELL_WAVE_EQUATIONS_PRESERVED": True,
            "BACKGROUND_DIFFERENTIAL_IDEAL_MISSING": True,
            "SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED": False,
            "SUPPORT_LOCAL_108_ROW_PBW_Q2_PAYLOAD_EXPORTED": False,
            "COMPONENT_COEFFICIENT_108_ROW_PBW_REPLAY_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EXPORT_CONTENT_ADDRESSED_BERGER_BACKGROUND_SPECIALIZATION_AND_DIFFERENTIAL_IDEAL_THEN_REPLAY_SCALAR_Q1",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]},
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
        raise SystemExit("stale q1 background-ideal obstruction certificate")
    print("BERGER_108_ROW_Q1_PBW_BACKGROUND_IDEAL_OBSTRUCTION generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
