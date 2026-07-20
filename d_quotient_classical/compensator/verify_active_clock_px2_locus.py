#!/usr/bin/env python3
"""Independent exact replay of the quadratic active-clock locus theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_ACTIVE_CLOCK_PX2_LOCUS_V1.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "compensator-active-clock-px2-locus-v1.schema.json"
)

EXPECTED_IMPORTS = {
    "minimal_action_classification": {
        "path": (
            "d_quotient_classical/certificates/"
            "COMPENSATOR_MINIMAL_ACTION_CLASSIFICATION_AFTER_NEITHER_V1.json"
        ),
        "result_id": "COMPENSATOR_MINIMAL_ACTION_CLASSIFICATION_AFTER_NEITHER_V1",
        "sha256": "41ce6db6ab8fc58f4cc1ecedb205f732fd3dcee645f9408506d3535545f7026a",
        "source_commit": "a5924e707352bab92db2caa4c19cf4223c60f0e3",
        "lifecycle_commit": "091876a9504b7fda91aad75e82b24d7051417c18",
    },
    "positive_Berger_clock": {
        "path": (
            "d_quotient_classical/certificates/"
            "POSITIVE_BERGER_CLOCK_BACKGROUND.json"
        ),
        "result_id": "POSITIVE_BERGER_CLOCK_BACKGROUND",
        "sha256": "35e1bb8a56b0591b3dd00aa8f22c328ad826ecd341c290564cfd1a68fcc3e687",
        "source_commit": "bb5738d6e3e30a68adcc9a70c35dac089079e3db",
    },
    "Berger_charge_convention": {
        "path": (
            "d_quotient_classical/certificates/"
            "BERGER_FIXED_COUPLING_DELTA_CHARGE.json"
        ),
        "result_id": "BERGER_FIXED_COUPLING_DELTA_CHARGE",
        "sha256": "0ae894432b065f9f4ba116e6e2d42e69d1d60cd37dbf6ef21a14d7073c75b786",
        "source_commit": "cc5df8d547f7d2119282590a824ce92cd1d76d17",
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _dense(
    record: dict[str, Any], symbols: dict[str, sp.Expr] | None = None
) -> sp.Matrix:
    value = sp.zeros(record["row_count"], record["column_count"])
    for entry in record["entries"]:
        value[entry["row"], entry["column"]] = sp.sympify(
            entry["coefficient"], locals=symbols or {}
        )
    return value


def _check_matrix_hash(record: dict[str, Any]) -> None:
    core = {key: value for key, value in record.items() if key != "sha256"}
    if record["sha256"] != _digest(core):
        raise AssertionError("serialized matrix hash drifted")


def _independent_stationary_rows() -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    # Reconstruct each matter column from
    # -T_ab = 2 P_X d_a(theta)d_b(theta) - P g_ab, rather than
    # transcribing the producer's rows.
    cylinder = sp.Matrix(
        [
            [0, 36, 3, 1, 0, 0],
            [0, 12, -1, -1, 0, 0],
        ]
    )
    R = sp.Rational(151, 80)
    omega = sp.Rational(3, 4)
    X = -omega**2
    metric = [-1, 1, 1, 1]
    ricci = [
        0,
        sp.Rational(71, 80),
        sp.Rational(71, 80),
        sp.Rational(9, 80),
    ]
    bach = [
        sp.Rational(961, 9600),
        sp.Rational(403, 9600),
        sp.Rational(403, 9600),
        sp.Rational(31, 1920),
    ]
    rows: list[list[sp.Expr]] = []
    for index in (0, 1, 3):
        g = metric[index]
        gravity = [
            bach[index],
            4 * R * ricci[index] - R**2 * g,
            ricci[index] - R * g / 2,
        ]
        matter_columns: list[sp.Expr] = []
        for degree in range(3):
            P = X**degree
            P_X = 0 if degree == 0 else degree * X ** (degree - 1)
            time_gradient_square = omega**2 if index == 0 else 0
            matter_columns.append(
                sp.factor(2 * P_X * time_gradient_square - P * g)
            )
        rows.append(gravity + matter_columns)
    berger = sp.Matrix(rows)
    return cylinder, berger, cylinder.col_join(berger)


def _verify_stationary(payload: dict[str, Any]) -> sp.Symbol:
    cylinder, berger, stacked = _independent_stationary_rows()
    serialized = payload["stationary_background_equations"]
    records = (
        serialized["unit_cylinder"]["matrix"],
        serialized["frozen_Berger_clock"]["matrix"],
        serialized["common_system"]["matrix"],
        serialized["common_system"]["rref"],
    )
    for record in records:
        _check_matrix_hash(record)
    if _dense(records[0]) != cylinder:
        raise AssertionError("unit-cylinder rows drifted")
    if _dense(records[1]) != berger:
        raise AssertionError("Berger P(X) rows drifted")
    if _dense(records[2]) != stacked:
        raise AssertionError("stacked stationary rows drifted")

    p2 = sp.Symbol("p2", real=True)
    solution = sp.linsolve(
        (stacked[:, :5], -stacked[:, 5] * p2),
        *sp.symbols("alpha_B alpha_R M2 p0 p1"),
    )
    expected_tuple = (
        sp.Rational(81, 20) * p2,
        sp.Rational(27, 3290) * p2,
        -sp.Rational(324, 1645) * p2,
        sp.Rational(486, 1645) * p2,
        sp.Rational(18, 25) * p2,
    )
    if solution != sp.FiniteSet(expected_tuple):
        raise AssertionError("independent exact elimination drifted")
    rref, pivots = stacked.rref()
    if (
        stacked.rank() != 5
        or pivots != (0, 1, 2, 3, 4)
        or sp.factor(stacked[:, :5].det()) != sp.Rational(91791, 40960)
        or _dense(records[3]) != rref
    ):
        raise AssertionError("stationary rank certificate drifted")
    return p2


def _verify_hessian(payload: dict[str, Any], parameter: sp.Symbol) -> None:
    section = payload["coupled_homogeneous_analysis"]
    D = sp.Symbol("D")
    M = sp.Symbol("M", nonzero=True)
    spectral = sp.Symbol("spectral")
    p1 = sp.Rational(18, 25) * parameter

    # Build the velocity Hessian independently from the quadratic density.
    du, dpsi, dv = sp.symbols("du dpsi dv")
    kinetic = -3 * du * dpsi - p1 * dv**2
    velocity = sp.hessian(kinetic, (du, dpsi, dv))
    principal = -velocity
    hessian = sp.Matrix(
        [
            [0, 3 * (D**2 - 2), 0],
            [3 * (D**2 - 2), 12 / M, 0],
            [0, 0, 2 * p1 * D**2],
        ]
    )
    evolution = sp.Matrix(
        [
            [0, 1, 0, 0, 0, 0],
            [2, 0, -4 / M, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 2, 0, 0, 0],
            [0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0],
        ]
    )
    symbols = {"D": D, "M": M, "t": parameter}
    for key, expected in (
        ("velocity_Hessian", velocity),
        ("principal_D2_matrix", principal),
        ("Euler_Hessian_of_D", hessian),
        ("D_evolution_matrix", evolution),
    ):
        record = section[key]
        _check_matrix_hash(record)
        if _dense(record, symbols) != expected:
            raise AssertionError(f"{key} drifted")
    if (
        sp.factor(hessian.det())
        != -sp.Rational(324, 25)
        * parameter
        * D**2
        * (D**2 - 2) ** 2
    ):
        raise AssertionError("Hessian determinant drifted")
    if (
        sp.factor(evolution.charpoly(spectral).as_expr())
        != spectral**2 * (spectral**2 - 2) ** 2
        or evolution**2 * (evolution**2 - 2 * sp.eye(6)) ** 2
        != sp.zeros(6)
    ):
        raise AssertionError("evolution polynomial drifted")
    # Neither proper factor annihilates: the clock needs spectral^2 and the
    # scalar block needs both squared factors.
    if (
        evolution * (evolution**2 - 2 * sp.eye(6)) ** 2 == sp.zeros(6)
        or evolution**2 * (evolution**2 - 2 * sp.eye(6)) == sp.zeros(6)
    ):
        raise AssertionError("minimal polynomial was silently lowered")
    if section["velocity_inertia_strata_positive_negative_zero"] != {
        "t>0": [1, 2, 0],
        "t<0": [2, 1, 0],
        "t=0_in_declared_original_action": [0, 0, 3],
    }:
        raise AssertionError("velocity inertia strata drifted")


def _verify_cones_charges_and_gates(
    payload: dict[str, Any], parameter: sp.Symbol
) -> None:
    X = -sp.Rational(9, 16)
    omega = sp.Rational(3, 4)
    p0 = sp.Rational(486, 1645) * parameter
    p1 = sp.Rational(18, 25) * parameter
    p2 = parameter
    P = sp.factor(p0 + p1 * X + p2 * X**2)
    P_X = sp.factor(p1 + 2 * p2 * X)
    longitudinal = sp.factor(P_X + 4 * p2 * X)
    energy = sp.factor(-2 * P_X * omega**2 - P)
    charge = sp.factor(-2 * P_X * omega)
    if (
        P != sp.Rational(435537, 2105600) * parameter
        or P_X != -sp.Rational(81, 200) * parameter
        or longitudinal != -sp.Rational(531, 200) * parameter
        or sp.factor(P_X / longitudinal) != sp.Rational(9, 59)
        or energy != sp.Rational(523827, 2105600) * parameter
        or charge != sp.Rational(243, 400) * parameter
        or sp.factor(energy - omega * charge) != -P
    ):
        raise AssertionError("independent cone/charge replay drifted")
    cone = payload["Berger_sound_cone_and_clock"]
    if (
        cone["P_X"] != "-81 t/200"
        or cone["P_X_plus_2X_P_XX"] != "-531 t/200"
        or cone["sound_speed_squared"] != "P_X/(P_X+2X P_XX)=9/59"
        or cone["standard_sign_and_hyperbolic_locus"] != "t>0"
    ):
        raise AssertionError("serialized sound cone drifted")
    if "different linear clock action" not in payload["charges"]["important_scope"]:
        raise AssertionError("changed-action charge boundary was erased")

    gates = payload["seven_gate_classification"]["gates"]
    if [row["gate"] for row in gates] != list(range(1, 8)):
        raise AssertionError("seven-gate enumeration drifted")
    gate5 = gates[4]
    gate6 = gates[5]
    if (
        gate5["status"] != "FAIL_ALL_REAL_STATIONARY_POINTS"
        or gate6["status"] != "FAIL"
        or payload["seven_gate_classification"]["all_seven_gate_good_locus"]
        != "EMPTY"
    ):
        raise AssertionError("terminal gate disposition drifted")
    # Real sign certificate: the two healthy-clock half-lines are disjoint,
    # and the scalar (+3,-3) pair is split on both.
    common_healthy_locus = sp.reduce_inequalities(
        [
            sp.Rational(18, 25) * parameter < 0,
            -sp.Rational(81, 200) * parameter < 0,
        ],
        parameter,
    )
    if common_healthy_locus is not sp.false:
        raise AssertionError("healthy clock sign separator failed")


def verify(value: dict[str, Any] | None = None) -> None:
    payload = value if value is not None else json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    for name, expected in EXPECTED_IMPORTS.items():
        row = payload["dependencies"][name]
        for key, target in expected.items():
            if row[key] != target:
                raise AssertionError(f"{name} pinned {key} drifted")
        if _sha(ROOT / row["path"]) != row["sha256"]:
            raise AssertionError(f"{name} content hash drifted")

    family = payload["action_family"]
    if (
        family["coefficient_basis_mod_topology"]
        != ["alpha_B", "alpha_R", "M_P_squared", "p0", "p1", "p2"]
        or "Henneaux-Teitelboim or any multiplier sector"
        not in family["excluded"]
        or payload["action_family_sha256"] != _digest(family)
    ):
        raise AssertionError("declared P(X) action family drifted")

    parameter = _verify_stationary(payload)
    _verify_hessian(payload, parameter)
    _verify_cones_charges_and_gates(payload, parameter)

    hashes = payload["content_hashes"]
    if (
        hashes["action_family_sha256"] != payload["action_family_sha256"]
        or hashes["stationary_system_sha256"]
        != _digest(payload["stationary_background_equations"])
        or hashes["coupled_homogeneous_sha256"]
        != _digest(payload["coupled_homogeneous_analysis"])
        or hashes["sound_charge_sha256"]
        != _digest(
            {
                "cone": payload["Berger_sound_cone_and_clock"],
                "charges": payload["charges"],
            }
        )
        or hashes["classification_sha256"]
        != _digest(payload["seven_gate_classification"])
    ):
        raise AssertionError("section content hash drifted")
    if (
        payload["selection"]["candidate_C_active_selected"]
        or payload["selection"]["candidate_C_active_action_hash"] is not None
        or payload["claim_flags"]["UNIVERSAL_K_ESSENCE_OR_COMPENSATOR_NO_GO"]
        or payload["claim_flags"]["HADAMARD_OR_QUANTUM_RESULT"]
    ):
        raise AssertionError("scoped no-go was promoted")


def main() -> None:
    verify()
    print("COMPENSATOR_ACTIVE_CLOCK_PX2_LOCUS_V1 independent replay: PASS")


if __name__ == "__main__":
    main()
