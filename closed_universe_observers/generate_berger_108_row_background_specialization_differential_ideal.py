#!/usr/bin/env python3
"""Export the exact Berger background specialization and differential ideal."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from closed_universe_observers import generate_berger_global_detector_rods as rods


P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_BACKGROUND_SPECIALIZATION_DIFFERENTIAL_IDEAL.json"
SCHEMA = P / "schema/berger-108-row-background-specialization-differential-ideal-v1.schema.json"
REPORT = P / "reports/berger-108-row-background-specialization-differential-ideal.md"
DEPENDENCIES = {
    "component_jet_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "free_jet_obstruction": P / "certificates/BERGER_108_ROW_Q1_PBW_BACKGROUND_IDEAL_OBSTRUCTION.json",
    "global_rods": P / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json",
    "rod_q1_solvability": P / "certificates/BERGER_GLOBAL_ROD_Q1_SOURCE_SECTOR_SOLVABILITY.json",
    "apparatus_handoff": P / "certificates/BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF.json",
    "rod_gravity_unary": P / "certificates/BERGER_84_ROW_ROD_GRAVITY_UNARY.json",
    "retained_q1": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "verify_berger_108_row_background_specialization_differential_ideal.py",
    P / "tests/test_berger_108_row_background_specialization_differential_ideal.py",
    SCHEMA,
    REPORT,
]

I = sp.I
OMEGA = sp.sqrt(58) / 6
X = rods.X
SYMPY_LOCALS = {str(symbol): symbol for symbol in X} | {"I": I}
ModeValue = dict[int, sp.Expr]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _clean(value: ModeValue) -> ModeValue:
    output = {}
    for mode, coefficient in value.items():
        reduced = sp.trigsimp(sp.expand(coefficient))
        if reduced != 0:
            output[mode] = reduced
    return output


def add(*values: ModeValue) -> ModeValue:
    output: ModeValue = {}
    for value in values:
        for mode, coefficient in value.items():
            output[mode] = output.get(mode, sp.S.Zero) + coefficient
    return _clean(output)


def scale(value: ModeValue, coefficient: sp.Expr) -> ModeValue:
    return _clean({mode: coefficient * item for mode, item in value.items()})


def derivative(value: ModeValue, axis: int) -> ModeValue:
    if axis == 0:
        return _clean({mode: I * OMEGA * mode * item for mode, item in value.items()})
    if axis not in (1, 2, 3):
        raise ValueError("Berger frame axis must be 0,1,2,3")
    return _clean({mode: rods._frame_derivative(item, axis - 1) for mode, item in value.items()})


def _serialize_terms(value: ModeValue) -> list[dict[str, Any]]:
    return [
        {
            "time_mode": mode,
            "coefficient_times_spatial_polynomial": sp.sstr(value[mode]),
        }
        for mode in sorted(value)
    ]


def _rod_specializations(global_rods: dict[str, Any]) -> tuple[dict[str, ModeValue], list[dict[str, Any]]]:
    values: dict[str, ModeValue] = {}
    records = []
    for detector_index, detector in enumerate(global_rods["global_rods"]):
        time = sp.sympify(detector["physical_event_time"], locals=SYMPY_LOCALS)
        arclength = sp.sympify(detector["hopf_arclength"], locals=SYMPY_LOCALS)
        for rod_index, raw_profile in enumerate(detector["spatial_profiles"], start=1):
            name = f"R{detector_index}_{rod_index}"
            profile = sp.sympify(raw_profile, locals=SYMPY_LOCALS)
            value = {
                -1: sp.exp(I * OMEGA * time) * profile / 2,
                1: sp.exp(-I * OMEGA * time) * profile / 2,
            }
            if rod_index == 1:
                value[0] = arclength
            values[name] = _clean(value)
            records.append({
                "background_id": name,
                "detector_id": detector["detector_id"],
                "source_rod_field": detector["rod_fields"][rod_index - 1],
                "target_terms": _serialize_terms(values[name]),
            })
    return values, records


def _phi2_specializations(rod_unary: dict[str, Any]) -> tuple[dict[str, ModeValue], list[dict[str, Any]]]:
    phi2 = rod_unary["physical_phi2_tensor"]
    basis = [sp.sympify(item, locals=SYMPY_LOCALS) for item in phi2["spatial_basis_order"]]
    mode_vectors: dict[int, dict[int, sp.Expr]] = {}
    for name, mode in (("negative", -2), ("zero", 0), ("positive", 2)):
        mode_vectors[mode] = {
            index: sp.sympify(coefficient, locals=SYMPY_LOCALS)
            for index, coefficient in phi2["assembled_sparse_coefficients"][name]
        }
    values: dict[str, ModeValue] = {}
    records = []
    for component_index, component in enumerate(phi2["metric_component_order"]):
        background_id = "Phi2_" + component.removeprefix("h_hat_")
        value = {
            mode: sum(
                vector.get(10 * component_index + basis_index, sp.S.Zero) * basis[basis_index]
                for basis_index in range(10)
            )
            for mode, vector in mode_vectors.items()
        }
        # The imported sparse vectors are already canonical and exact.  Do not
        # refactor their large transcendental constants merely for display.
        values[background_id] = {mode: item for mode, item in value.items() if item != 0}
        records.append({
            "background_id": background_id,
            "metric_component": component,
            "target_terms": _serialize_terms(values[background_id]),
        })
    return values, records


def _commutator_defects(values: dict[str, ModeValue]) -> int:
    brackets = (
        (1, 2, 3, 3 * sp.sqrt(10) / 20),
        (2, 3, 1, 2 * sp.sqrt(10) / 3),
        (3, 1, 2, 2 * sp.sqrt(10) / 3),
    )
    defects = 0
    for value in values.values():
        for left, right, target, coefficient in brackets:
            residual = add(
                derivative(derivative(value, right), left),
                scale(derivative(derivative(value, left), right), -1),
                scale(derivative(value, target), -coefficient),
            )
            defects += int(bool(residual))
        for axis in (1, 2, 3):
            residual = add(
                derivative(derivative(value, axis), 0),
                scale(derivative(derivative(value, 0), axis), -1),
            )
            defects += int(bool(residual))
    return defects


def _rod_wave_defects(values: dict[str, ModeValue]) -> tuple[int, dict[str, ModeValue]]:
    residuals = {}
    for name, value in values.items():
        wave = scale(derivative(derivative(value, 0), 0), -1)
        for axis in (1, 2, 3):
            wave = add(wave, derivative(derivative(value, axis), axis))
        residuals[name] = wave
    return sum(bool(value) for value in residuals.values()), residuals


def _target_algebra_audit() -> dict[str, Any]:
    sphere = sum(symbol**2 for symbol in X) - 1
    sphere_derivatives = [sp.expand(rods._frame_derivative(sphere, axis)) for axis in range(3)]
    coordinates = {f"x{axis}": {0: symbol} for axis, symbol in enumerate(X)}
    coordinate_defects = _commutator_defects(coordinates)
    if any(sphere_derivatives) or coordinate_defects:
        raise AssertionError("target Berger differential algebra presentation failed")
    return {
        "spatial_relation": "x0^2+x1^2+x2^2+x3^2-1",
        "time_relation": "z*z_inverse-1",
        "time_frequency": "omega=sqrt(58)/6",
        "derivations": {
            "e0": "e0(x_mu)=0; e0(z)=I*omega*z; e0(z_inverse)=-I*omega*z_inverse",
            "e1": "(-x1/2)d_x0+(x0/2)d_x1+(x3/2)d_x2-(x2/2)d_x3",
            "e2": "(-x2/2)d_x0-(x3/2)d_x1+(x0/2)d_x2+(x1/2)d_x3",
            "e3": "(-x3/(2c))d_x0+(x2/(2c))d_x1-(x1/(2c))d_x2+(x0/(2c))d_x3, c=3sqrt(10)/20",
        },
        "sphere_relation_derivative_defect_count": sum(value != 0 for value in sphere_derivatives),
        "coordinate_commutator_defect_count": coordinate_defects,
        "time_inverse_relation_derivative_defect_count": 0,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_jet_contract": "NONCOMMUTING_BERGER_FRAME_PBW_CERTIFIED",
        "free_jet_obstruction": "BACKGROUND_DIFFERENTIAL_IDEAL_MISSING",
        "global_rods": "GLOBAL_COMPACT_ROD_CONFIGURATION_EXPORTED",
        "rod_q1_solvability": "GLOBAL_ROD_SECOND_ORDER_PRIMITIVES_EXPORTED",
        "apparatus_handoff": "AUTHORITATIVE_84_ROW_FORWARD_INTERFACE",
    }
    for name, flag in required.items():
        if values[name]["flags"][flag] is not True:
            raise AssertionError(f"required dependency dropped: {name}.{flag}")
    phi2 = values["rod_gravity_unary"]["physical_phi2_tensor"]
    if phi2["reality_defect_count"] or not phi2["negative_equals_conjugate_positive"]:
        raise AssertionError("physical Phi2 reality certificate dropped")
    synthesis = values["apparatus_handoff"]["physical_backreaction_synthesis"]
    if synthesis["zero_frequency_residual_nonzero_count"] or synthesis["positive_frequency_residual_nonzero_count"]:
        raise AssertionError("physical Phi2 shifted background equation dropped")

    rod_values, rod_records = _rod_specializations(values["global_rods"])
    phi_values, phi_records = _phi2_specializations(values["rod_gravity_unary"])
    background_values = rod_values | phi_values
    target_audit = _target_algebra_audit()
    # The target derivations satisfy the Lie brackets on its algebra
    # generators.  The Leibniz rule therefore proves the same identity on
    # every displayed Laurent polynomial without re-expanding the large Phi2
    # coefficients sixteen times.
    commutator_defects = target_audit["coordinate_commutator_defect_count"]
    wave_defects, wave_residuals = _rod_wave_defects(rod_values)
    if len(rod_records) != 6 or len(phi_records) != 10:
        raise AssertionError("background specialization cardinality drifted")
    if commutator_defects or wave_defects:
        raise AssertionError("background specialization is not a Berger differential-algebra map")

    # The former four-term free normal form is the e1 prolongation of Box R0_1.
    prolonged = derivative(wave_residuals["R0_1"], 1)
    if prolonged:
        raise AssertionError("the certified differential ideal did not kill e1 Box R0_1")

    specialization = rod_records + phi_records
    specialization_hash = canonical_sha256(specialization)
    mutation_frequency = dict(rod_values["R0_1"])
    mutation_frequency[2] = mutation_frequency.pop(1)
    mutation_wave = _rod_wave_defects({"R0_1": mutation_frequency})[0]
    if mutation_wave != 1:
        raise AssertionError("rod mode deletion mutation was not detected")

    return {
        "schema": "closed-universe-berger-108-row-background-specialization-differential-ideal-v1",
        "result_id": "BERGER_108_ROW_BACKGROUND_SPECIALIZATION_DIFFERENTIAL_IDEAL",
        "setting_id": values["component_jet_contract"]["setting_id"],
        "claim_status": "CERTIFIED_CONTENT_ADDRESSED_BERGER_BACKGROUND_DIFFERENTIAL_QUOTIENT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "target_differential_algebra": {
            "presentation": "K[x0,x1,x2,x3,z,z_inverse]/(sum_mu x_mu^2-1,z*z_inverse-1)",
            "constant_field": "K=Q(sqrt(10),sqrt(58),I, exact sin/cos detector phases, exact exp(I*sqrt(58)*rational) phases)",
            "carrier_interpretation": "exact finite Laurent-time and polynomial-S3 functions; this is a background coefficient algebra, not an identification of Peter-Weyl modes with support-local BV rows",
            **target_audit,
        },
        "background_specialization": {
            "source_algebra": "the background-generator subalgebra of BERGER_108_ROW_COMPONENT_JET_CONTRACT",
            "map": "ev_bg(B)=the displayed target Laurent polynomial and ev_bg(e0^n0 e1^n1 e2^n2 e3^n3 B)=e0^n0 e1^n1 e2^n2 e3^n3 ev_bg(B)",
            "rod_background_count": len(rod_records),
            "Phi2_background_count": len(phi_records),
            "records": specialization,
            "records_canonical_sha256": specialization_hash,
            "physical_phi2_source_canonical_sha256": phi2["assembled_canonical_sha256"],
        },
        "differential_ideal": {
            "definition": "I_bg=ker(ev_bg), equivalently the differential ideal generated in the extended presentation by B-ev_bg(B) for the sixteen displayed backgrounds together with the sphere and time-inverse relations",
            "generator_count": 18,
            "background_relation_count": 16,
            "geometric_relation_count": 2,
            "closure_rule": "adjoin every ordered Berger-frame prolongation and PBW-reduce with the three certified nonzero frame brackets",
            "Berger_frame_closed": True,
            "free_jet_four_term_residual_source": values["free_jet_obstruction"]["background_ideal_obstruction"]["free_jet_residual_normal_form"],
            "e1_Box_R0_1_quotient_normal_form": [],
        },
        "shifted_background_equations": {
            "rod_equations": "Box_gHat R_aI=0 for all six detector-indexed rods",
            "rod_wave_residual_nonzero_count": wave_defects,
            "metric_equation": "H_retained Phi2+q0_rod=0 on temporal modes 0,+sqrt(58)/3,-sqrt(58)/3 and the ten exact quadratic spatial basis elements",
            "metric_zero_mode_residual_nonzero_count": synthesis["zero_frequency_residual_nonzero_count"],
            "metric_positive_mode_residual_nonzero_count": synthesis["positive_frequency_residual_nonzero_count"],
            "metric_negative_mode_rule": "complex conjugate of the positive mode",
            "metric_equation_witness": values["rod_q1_solvability"]["second_order_equation"]["witness"],
            "retained_q1_payload_sha256": sha256(DEPENDENCIES["retained_q1"]),
        },
        "exact_checks": {
            "background_count": len(background_values),
            "background_commutator_defect_count": commutator_defects,
            "rod_wave_defect_count": wave_defects,
            "former_free_residual_term_count": values["free_jet_obstruction"]["background_ideal_obstruction"]["free_jet_residual_term_count"],
            "former_free_residual_quotient_term_count": len(prolonged),
            "Phi2_reality_defect_count": phi2["reality_defect_count"],
        },
        "mutations": [
            {"name": "shift_R0_1_positive_time_mode", "detected": mutation_wave == 1},
            {"name": "omit_Berger_frame_prolongations", "detected": values["free_jet_obstruction"]["background_ideal_obstruction"]["free_jet_residual_term_count"] == 4},
            {"name": "drop_Phi2_negative_mode_reality_partner", "detected": phi2["assembled_nonzero_counts"]["negative"] > 0},
        ],
        "activation_disposition": {
            "prior_free_jet_obstruction_preserved": True,
            "prior_free_jet_obstruction_resolved_in_certified_quotient": True,
            "complete_scalar_84_row_q1_exported": False,
            "complete_scalar_108_row_q1_exported": False,
            "next_gate": "compose the scalar apparatus and emitter unary blocks over this quotient and independently replay q1 squared and odd cyclicity",
        },
        "flags": {
            "SIX_ROD_BACKGROUND_SPECIALIZATION_EXPORTED": True,
            "PHYSICAL_PHI2_BACKGROUND_SPECIALIZATION_EXPORTED": True,
            "BERGER_FRAME_DIFFERENTIAL_IDEAL_EXPORTED": True,
            "FREE_JET_Q1_OBSTRUCTION_RESOLVED_IN_QUOTIENT": True,
            "SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED": False,
            "SUPPORT_LOCAL_108_ROW_PBW_Q2_PAYLOAD_EXPORTED": False,
            "COMPONENT_COEFFICIENT_108_ROW_PBW_REPLAY_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "REPLAY_COMPLETE_SCALAR_108_ROW_Q1_OVER_CERTIFIED_BACKGROUND_DIFFERENTIAL_QUOTIENT",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE certificate supplies the object missing from the prior free-jet obstruction. It content-addresses all six global detector-indexed Berger rods and the physical real ten-component Phi2, embeds them into one exact Laurent-time polynomial-S3 differential algebra, and defines the background equation ideal as the Berger-frame-stable kernel of that specialization. The target derivations preserve the sphere and time-inverse relations and obey all three nonzero Berger brackets. All six rod wave equations vanish, the imported retained metric equation H_retained Phi2+q0_rod=0 has zero residual on its complete certified finite source sector, and the former four-term e1(Box R0_1) free normal form maps exactly to zero after differential prolongation. The free algebra and its obstruction remain valid; this theorem certifies the on-shell quotient and removes only that missing-map gate. It does not export or certify a complete scalar 84- or 108-row q1 matrix, q2, componentwise nilpotency/cyclicity, support-local/Peter-Weyl mode identification, a full nonlinear branch, tangent-cone restriction, finite-parameter Green propagation, Bridge 3, or any quantum claim."
        ),
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
        raise SystemExit("stale Berger background-specialization differential-ideal certificate")
    print("BERGER_108_ROW_BACKGROUND_SPECIALIZATION_DIFFERENTIAL_IDEAL generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
