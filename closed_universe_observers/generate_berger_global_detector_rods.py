#!/usr/bin/env python3
"""Export exact global detector-indexed rods on the compact Berger cylinder."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
INPUT = PACKAGE / "fixtures/berger_global_detector_rods_input.json"
DETECTOR_INPUT = PACKAGE / "fixtures/berger_localized_detector_records_input.json"
DETECTOR_CERTIFICATE = PACKAGE / "certificates/BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS.json"
SCHEMA = PACKAGE / "schema/berger-global-detector-rods-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json"
REPORT = PACKAGE / "reports/berger-global-detector-rods.md"

DEPENDENCIES = {
    "detector_input": DETECTOR_INPUT,
    "detector_preflight": DETECTOR_CERTIFICATE,
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "independent_verifier": PACKAGE / "verify_berger_global_detector_rods.py",
    "tests": PACKAGE / "tests/test_berger_global_detector_rods.py",
    "report": REPORT,
    "certificate_schema": SCHEMA,
}

X = sp.symbols("x0:4", real=True)
T = sp.symbols("t", real=True)
C = 3 * sp.sqrt(10) / 20
OMEGA = sp.sqrt(sp.Rational(29, 18))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: str | int) -> sp.Rational:
    return sp.Rational(value)


def _frame_derivative(value: sp.Expr, axis: int) -> sp.Expr:
    x0, x1, x2, x3 = X
    coefficients = (
        (-x1 / 2, x0 / 2, x3 / 2, -x2 / 2),
        (-x2 / 2, -x3 / 2, x0 / 2, x1 / 2),
        (-x3 / (2 * C), x2 / (2 * C), -x1 / (2 * C), x0 / (2 * C)),
    )[axis]
    return sp.expand(sum(coefficients[index] * sp.diff(value, X[index]) for index in range(4)))


def _commutator_residual(first: int, second: int, target: int, factor: sp.Expr) -> sp.Expr:
    residuals = [
        sp.trigsimp(
            _frame_derivative(_frame_derivative(coordinate, second), first)
            - _frame_derivative(_frame_derivative(coordinate, first), second)
            - factor * _frame_derivative(coordinate, target)
        )
        for coordinate in X
    ]
    if any(value != 0 for value in residuals):
        raise AssertionError(f"Berger frame commutator failed: {residuals}")
    return sp.S.Zero


def _profiles(phase: sp.Expr) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    x0, x1, x2, x3 = X
    cosine, sine = sp.cos(phase), sp.sin(phase)
    return (
        2 * C * (-sine * x0 + cosine * x3),
        2 * (cosine * x1 + sine * x2),
        2 * (-sine * x1 + cosine * x2),
    )


def _event_jacobian(phase: sp.Expr, profiles: tuple[sp.Expr, ...]) -> sp.Matrix:
    event = {X[0]: sp.cos(phase), X[1]: 0, X[2]: 0, X[3]: sp.sin(phase)}
    spatial_directions = (2, 0, 1)  # e3, e1, e2: the declared local rod order.
    matrix = sp.eye(4)
    for row, profile in enumerate(profiles, start=1):
        matrix[row, 0] = 0
        for column, direction in enumerate(spatial_directions, start=1):
            matrix[row, column] = sp.trigsimp(_frame_derivative(profile, direction).subs(event))
    return matrix


def _strings(matrix: sp.Matrix) -> list[list[str]]:
    return [[sp.sstr(sp.simplify(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _detector_rows(detector_data: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], list[list[str]]]:
    output: list[dict[str, Any]] = []
    wave_residuals: list[str] = []
    jacobians: list[list[str]] = []
    clock_rate = _q(detector_data["clock_rate"])
    for detector in detector_data["detectors"]:
        label = _q(detector["clock_label"])
        arclength = _q(detector["hopf_arclength"])
        event_time = sp.simplify(label / clock_rate)
        if event_time != arclength:
            raise AssertionError("detector is not on the declared central Hopf ray")
        phase = sp.simplify(arclength / (2 * C))
        profiles = _profiles(phase)
        event = {X[0]: sp.cos(phase), X[1]: 0, X[2]: 0, X[3]: sp.sin(phase)}
        values = [sp.trigsimp(profile.subs(event)) for profile in profiles]
        if values != [0, 0, 0]:
            raise AssertionError("global profiles do not vanish at their detector event")
        jacobian = _event_jacobian(phase, profiles)
        if jacobian != sp.eye(4):
            raise AssertionError(f"detector rod Jacobian is not identity: {jacobian}")
        jacobians.append(_strings(jacobian))

        fields = (
            arclength + sp.cos(OMEGA * (T - event_time)) * profiles[0],
            sp.cos(OMEGA * (T - event_time)) * profiles[1],
            sp.cos(OMEGA * (T - event_time)) * profiles[2],
        )
        for field in fields:
            box = -sp.diff(field, T, 2) + sum(
                _frame_derivative(_frame_derivative(field, axis), axis) for axis in range(3)
            )
            residual = sp.trigsimp(sp.expand_trig(box))
            if residual != 0:
                raise AssertionError(f"global rod wave equation failed: {residual}")
            wave_residuals.append("0")
        normal = [sp.trigsimp(sp.diff(field, T).subs(T, event_time)) for field in fields]
        if normal != [0, 0, 0]:
            raise AssertionError("rod normal derivative does not vanish at detector event")

        phase_text = sp.sstr(phase)
        profile_text = [sp.sstr(profile) for profile in profiles]
        output.append({
            "detector_id": detector["id"],
            "physical_event_time": sp.sstr(event_time),
            "clock_label": detector["clock_label"],
            "hopf_arclength": detector["hopf_arclength"],
            "hopf_phase": phase_text,
            "event_point": [f"cos({phase_text})", "0", "0", f"sin({phase_text})"],
            "spatial_profiles": profile_text,
            "rod_fields": [sp.sstr(field) for field in fields],
        })
    return output, wave_residuals, jacobians


def build() -> dict[str, Any]:
    declaration = json.loads(INPUT.read_text())
    detector_data = json.loads(DETECTOR_INPUT.read_text())
    detector_certificate = json.loads(DETECTOR_CERTIFICATE.read_text())
    if declaration["allocation"] != "detector_indexed" or declaration["rods_per_detector"] != 3:
        raise AssertionError("global rod allocation must be three rods per detector")
    mutation_rejected = declaration["mutation"]["allocation"] != declaration["allocation"]
    if not mutation_rejected:
        raise AssertionError("shared-allocation mutation did not fail")
    if detector_certificate["flags"]["LOCAL_STANDARD_SIGN_ROD_SOLUTIONS"] is not True:
        raise AssertionError("local rod preflight is unavailable")

    commutators = [
        _commutator_residual(0, 1, 2, C),
        _commutator_residual(1, 2, 0, 1 / C),
        _commutator_residual(2, 0, 1, 1 / C),
    ]
    eigenvalues = []
    for coordinate in X:
        laplacian = -sum(_frame_derivative(_frame_derivative(coordinate, axis), axis) for axis in range(3))
        eigenvalues.append(sp.simplify(laplacian / coordinate))
    if eigenvalues != [sp.Rational(29, 18)] * 4:
        raise AssertionError(f"linear Berger harmonic eigenvalue drifted: {eigenvalues}")
    rods, wave_residuals, jacobians = _detector_rows(detector_data)

    degree_zero = [f"R{detector}_{axis}" for detector in range(2) for axis in range(1, 4)] + ["m0", "m1", "p0", "p1"]
    degree_one = [f"{row}_plus" for row in degree_zero]
    payload = {
        "schema": "closed-universe-berger-global-detector-rods-v1",
        "result_id": "BERGER_GLOBAL_DETECTOR_INDEXED_RODS",
        "setting_id": declaration["setting_id"],
        "claim_status": "GLOBAL_ROD_FIELDS_AND_Q0_FORMULA_EXPORTED_COMPACT_TAUB_PROJECTOR_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path), "result_id": json.loads(path.read_text()).get("result_id", "DECLARED_DETECTOR_INPUT")}
            for name, path in DEPENDENCIES.items()
        },
        "allocation_correction": {
            "reason": "the two identity rod Jacobians are Cauchy data at distinct times; assigning a separate scalar triplet to each detector avoids an unproved two-time interpolation constraint on one shared triplet",
            "old_shared_rod_count": 3,
            "new_detector_indexed_rod_count": 6,
            "old_proposed_total_rows": 78,
            "corrected_proposed_total_rows": 84,
            "new_degree_zero_rows": degree_zero,
            "new_degree_one_rows": degree_one,
            "mutation_rejected": mutation_rejected,
        },
        "berger_geometry": {
            "squashing_c": "3*sqrt(10)/20",
            "rod_frequency": "sqrt(58)/6",
            "spatial_model": declaration["ambient_spatial_model"],
            "frame": ["e0=partial_t", "e1=xi1", "e2=xi2", "e3=xi3/c", declaration["invariant_frame_normalization"], "local relational direction order=((4/3)e0,e3,e1,e2)"],
        },
        "global_rods": rods,
        "exact_checks": {
            "frame_commutators": [sp.sstr(value) for value in commutators],
            "linear_spatial_eigenvalue": "29/18",
            "wave_residuals": wave_residuals,
            "event_relational_jacobians": jacobians,
            "event_normal_derivatives": [["0", "0", "0"], ["0", "0", "0"]],
            "all_pass": True,
        },
        "global_source_export": {
            "rod_action": "S_R=-1/2 sum_{a=0}^1 sum_{I=1}^3 integral sqrt(-gHat) gHat^mn partial_m R_{aI} partial_n R_{aI}",
            "stress_tensor": "T_rod_mn=sum_{a,I}(partial_m R_{aI} partial_n R_{aI}-1/2 gHat_mn gHat^rs partial_r R_{aI} partial_s R_{aI})",
            "retained_metric_source": "q0_(h_plus_ab)=(2-delta_ab) T_rod^{ab}/2 in field order (00,01,02,03,11,12,13,22,23,33), as fixed by delta S_R/delta g_ab=sqrt(-gHat) T_rod^{ab}/2",
            "conservation_identity": "nabla^m T_rod_mn=sum_{a,I}(Box_gHat R_{aI}) partial_n R_{aI}=0",
            "spatial_harmonic_support": ["j=0", "j=1"],
            "temporal_frequency_support": ["0", "+sqrt(58)/3", "-sqrt(58)/3"],
            "source_is_global_smooth": True,
            "source_is_fully_determined_by_displayed_rods": True,
        },
        "nonlinear_import_contract": {
            "required_carrier_rows": 84,
            "source_sector": "temporal {0,+sqrt(58)/3,-sqrt(58)/3} tensor spatial {j=0,j=1}",
            "required_next_calculation": "evaluate the exact retained Berger q1 and its compact adjoint-kernel pairing on the displayed finite source sector, then solve q1 Phi2=-q0^rod or exhibit a nonzero Taub pairing",
            "status": "OPEN",
        },
        "flags": {
            "GLOBAL_COMPACT_ROD_CONFIGURATION_EXPORTED": True,
            "GLOBAL_COMPACT_ROD_Q0_FORMULA_EXPORTED": True,
            "EXACT_ROD_HARMONIC_SUPPORT_EXPORTED": True,
            "DETECTOR_INDEXED_ROD_ALLOCATION": True,
            "FULL_COMPACT_ADJOINT_KERNEL_EXPORTED": False,
            "COMPACT_TAUB_PROJECTION_COMPUTED": False,
            "PERTURBATIVE_BACKREACTED_ROD_BRANCH_CERTIFIED": False,
            "LORENTZIAN_GREEN_HOMOTOPY_FOR_84_ROWS": False,
            "QUANTUM_CLAIM": False,
        },
        "not_established": [
            "the compact adjoint-kernel projector on the finite rod-source sector",
            "vanishing or nonvanishing of every compact Taub pairing",
            "an exact second-order gravitational primitive Phi2",
            "the 84-row interacting BV complex or its causal Green homotopy",
            "apparatus recoil, nonlinear observer consistency, or a quantum observer algebra",
        ],
        "provenance": {
            "declared_input_sha256": _sha256(INPUT),
            "source_manifest": [
                {"role": role, "path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for role, path in SOURCE_FILES.items()
            ],
        },
        "claim_boundary": "This exact fixed-Berger classical export supplies six globally smooth detector-indexed massless scalar rods, reproduces both prescribed detector-event rod charts, and determines their global conserved order-epsilon_R^2 metric source and finite harmonic support. It corrects the prospective apparatus carrier from 78 to 84 rows. It does not compute the full compact Taub projection, certify a backreacted branch, construct the 84-row interacting or causal complex, include apparatus recoil, or make a quantum claim.",
    }
    jsonschema.Draft202012Validator.check_schema(json.loads(SCHEMA.read_text()))
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).validate(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered:
            raise AssertionError("global detector rod certificate is stale")
    else:
        CERTIFICATE.write_text(rendered)
    print("BERGER_GLOBAL_DETECTOR_INDEXED_RODS generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
