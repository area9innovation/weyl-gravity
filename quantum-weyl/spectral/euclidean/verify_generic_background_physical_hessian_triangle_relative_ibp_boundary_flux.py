#!/usr/bin/env python3
"""Independently verify the physical triangle relative-IBP boundary flux."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from .generic_background_ghost_n3_i29_integrated_function import _pole4_system
from .generic_background_ghost_n3_pole3_relative_ibp import (
    A,
    B,
    X1,
    X2,
    X3,
    _domain_matrix,
)
from .generic_background_physical_hessian_triangle_master_completeness import (
    PIVOT_FIXTURE,
    PROJECTION,
    _system,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RELATIVE_IBP_BOUNDARY_FLUX.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-triangle-relative-ibp-boundary-flux-v1.schema.json"
XS = (X1, X2, X3)
MASTER_IDS = (
    "J_triangle",
    "M_x1",
    "M_x2",
    "M14_singlet",
    "M15_standard_u",
    "M16_standard_v",
)
INTEGRATED_BASIS = (
    "J_triangle",
    "log_x2_over_x1",
    "log_x3_over_x1",
    "rational_corner",
    "M14_singlet",
    "M15_standard_u",
    "M16_standard_v",
)
HOLDOUT_POINTS = ((2, 3, 5), (3, 5, 7))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _evaluate_terms(terms: list[dict], point: tuple[int, int, int]) -> sp.Rational:
    return sum(
        sp.Rational(
            term["coefficient"]["numerator"],
            term["coefficient"]["denominator"],
        )
        * point[0] ** term["exponents"][0]
        * point[1] ** term["exponents"][1]
        * point[2] ** term["exponents"][2]
        for term in terms
    )


def _evaluate(value: dict, point: tuple[int, int, int]) -> sp.Rational:
    return sp.cancel(
        _evaluate_terms(value["numerator_terms"], point)
        / _evaluate_terms(value["denominator_terms"], point)
    )


def _from_q(value: dict) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _corner_weights(
    vector_fields: list[tuple[sp.Expr, sp.Expr]], tangent_indices: list[int]
) -> list[list[sp.Expr]]:
    epsilon, parameter = sp.symbols("epsilon parameter")
    rows: list[list[sp.Expr]] = []
    for column_index in tangent_indices:
        p_value, q_value = vector_fields[column_index]
        candidates = (
            -epsilon
            * (p_value + q_value).subs(
                {A: epsilon * (1 - parameter), B: epsilon * parameter}
            ),
            epsilon
            * p_value.subs(
                {A: 1 - epsilon, B: epsilon * (1 - parameter)}
            ),
            epsilon
            * q_value.subs(
                {A: epsilon * parameter, B: 1 - epsilon}
            ),
        )
        rows.append(
            [
                sp.Poly(sp.expand(candidate), epsilon).coeff_monomial(epsilon**3)
                for candidate in candidates
            ]
        )
    return rows


def _verify_angular_rows(row: dict, point: tuple[int, int, int]) -> dict[str, sp.Expr]:
    local_logs: list[sp.Expr] = []
    rational_total = sp.S.Zero
    for corner in row["corner_rows"]:
        c0, c1, c2 = [
            _evaluate(value, point)
            for value in corner["angular_numerator_coefficients"]
        ]
        start = {
            "x1": sp.Rational(point[0]),
            "x2": sp.Rational(point[1]),
            "x3": sp.Rational(point[2]),
        }[corner["start_box"]]
        end = {
            "x1": sp.Rational(point[0]),
            "x2": sp.Rational(point[1]),
            "x3": sp.Rational(point[2]),
        }[corner["end_box"]]
        difference = end - start
        i0 = (start + end) / (2 * start**2 * end**2)
        i1 = 1 / (2 * start * end**2)
        i2_rational = (
            2 * start / end - start**2 / (2 * end**2) - sp.Rational(3, 2)
        ) / difference**3
        expected_rational = sp.cancel(c0 * i0 + c1 * i1 + c2 * i2_rational)
        expected_log = sp.cancel(c2 / difference**3)
        if _evaluate(corner["integrated_rational"], point) != expected_rational:
            raise ValueError(f"corner rational integral mismatch: {row['channel_id']} {corner['corner_id']} {point}")
        if _evaluate(corner["local_log_coefficient"], point) != expected_log:
            raise ValueError(f"corner logarithm mismatch: {row['channel_id']} {corner['corner_id']} {point}")
        rational_total += expected_rational
        local_logs.append(expected_log)
    expected_flux = {
        "log_x2_over_x1": sp.cancel(-local_logs[1] + local_logs[2]),
        "log_x3_over_x1": sp.cancel(local_logs[0] - local_logs[2]),
        "rational_corner": sp.cancel(rational_total),
    }
    for basis_id, expected in expected_flux.items():
        if _evaluate(row["flux_coordinates"][basis_id], point) != expected:
            raise ValueError(f"global flux mismatch: {row['channel_id']} {basis_id} {point}")
    return expected_flux


def verify(value: dict) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    payload = {
        key: value[key]
        for key in (
            "tangent_ledger",
            "angular_moment_basis",
            "channel_rows",
            "identity_ledger",
        )
    }
    if _digest(payload) != value["formula_digest"]:
        raise ValueError("physical triangle boundary-flux digest mismatch")
    dependencies: dict[str, dict] = {}
    for dependency_id, reference in value["dependencies"].items():
        path = ROOT / reference["path"]
        source = json.loads(path.read_text())
        if _sha256(path) != reference["sha256"] or source["result_id"] != reference["result_id"]:
            raise ValueError(f"dependency mismatch: {path}")
        dependencies[dependency_id] = source

    projection = json.loads(PROJECTION.read_text())
    expected_channels = [row["channel_id"] for row in projection["projection_rows"]]
    rows = value["channel_rows"]
    if [row["channel_id"] for row in rows] != expected_channels:
        raise ValueError("physical channel order drifted")

    coordinate_rows = dependencies["six_master_coordinates"]["channel_rows"]
    scalar_rows = dependencies["scalar_triangle_differential_system"]["master_rows"]
    master_value_rows = {
        row["master_id"]: row
        for row in dependencies["renormalized_master_values"]["master_rows"]
    }
    z_value = sp.Symbol("z")
    canonical_master_scales = {
        master_id: sp.factor(
            sp.cancel(
                sp.sympify(
                    row["scale_derivative"],
                    locals={"x1": X1, "x2": X2, "x3": X3, "z": z_value, "log": sp.log},
                )
            )
        )
        for master_id, row in master_value_rows.items()
    }
    obstruction_rows = {
        row["channel_id"]: row
        for row in dependencies["symmetric_integration_obstruction"]["channel_rows"]
    }
    symmetric_point = (1, 1, 1)
    symmetric_substitution = dict(zip(XS, symmetric_point))
    for row, coordinate_row in zip(rows, coordinate_rows):
        new_coordinates = [
            _evaluate(master_row["coordinate"], symmetric_point)
            for master_row in coordinate_row["master_coordinates"][3:]
        ]
        actual = sum(
            coordinate * canonical_master_scales[master_id].subs(symmetric_substitution)
            for coordinate, master_id in zip(
                new_coordinates,
                ("M14_singlet", "M15_standard_u", "M16_standard_v"),
            )
        )
        expected = _from_q(
            obstruction_rows[row["channel_id"]]["log_corner_coefficient"]
        )
        regression = row["symmetric_scale_regression"]
        if actual != expected or _from_q(regression["actual"]) != actual or _from_q(regression["expected"]) != expected:
            raise ValueError(f"symmetric scale regression mismatch: {row['channel_id']}")

    system = _system(projection)
    columns, vector_fields, old_masters = _pole4_system()
    tangent_indices = [index for index in system["pivot_columns"] if index < 84]
    if tangent_indices != value["tangent_ledger"]["tangent_columns"]:
        raise ValueError("tangent-column ledger drifted")
    tangent = _domain_matrix(
        [columns[index] for index in tangent_indices], system["basis"]
    ).to_Matrix()
    tangent_rows = tuple(tangent.subs(PIVOT_FIXTURE).transpose().rref()[1])
    if list(tangent_rows) != value["tangent_ledger"]["tangent_rows"]:
        raise ValueError("tangent-row ledger drifted")
    targets = _domain_matrix(system["targets"], system["basis"]).to_Matrix()
    masters = _domain_matrix(
        [*old_masters, *system["all_columns"][-3:]], system["basis"]
    ).to_Matrix()
    corner_weights = _corner_weights(vector_fields, tangent_indices)
    parameter = sp.symbols("parameter")

    for point in HOLDOUT_POINTS:
        substitution = dict(zip(XS, map(sp.Rational, point)))
        coordinates = sp.Matrix(
            [
                [
                    _evaluate(master_row["coordinate"], point)
                    for master_row in channel_row["master_coordinates"]
                ]
                for channel_row in coordinate_rows
            ]
        )
        residual = targets.subs(substitution) - masters.subs(substitution) * coordinates.transpose()
        square = tangent.extract(tangent_rows, range(46)).subs(substitution)
        primitive = square.inv() * residual.extract(tangent_rows, range(11))
        if tangent.subs(substitution) * primitive != residual:
            raise ValueError(f"full tangent identity failed at holdout {point}")

        for channel_index, row in enumerate(rows):
            for corner_index, corner in enumerate(row["corner_rows"]):
                actual_numerator = sp.expand(
                    sum(
                        primitive[column_index, channel_index]
                        * corner_weights[column_index][corner_index].subs(substitution)
                        for column_index in range(46)
                    )
                )
                actual_coefficients = [
                    sp.Poly(actual_numerator, parameter).coeff_monomial(parameter**power)
                    for power in range(3)
                ]
                stored_coefficients = [
                    _evaluate(coefficient, point)
                    for coefficient in corner["angular_numerator_coefficients"]
                ]
                if actual_coefficients != stored_coefficients:
                    raise ValueError(
                        f"independent corner-carrier mismatch: {row['channel_id']} {corner['corner_id']} {point}"
                    )

            flux = _verify_angular_rows(row, point)
            c_j, c_x1, c_x2, c14, c15, c16 = coordinates[channel_index, :]
            expected_integrated = {
                "J_triangle": sp.cancel(
                    c_j
                    + c_x1 * _evaluate(scalar_rows["M_x1"]["J_triangle"], point)
                    + c_x2 * _evaluate(scalar_rows["M_x2"]["J_triangle"], point)
                ),
                "log_x2_over_x1": sp.cancel(
                    c_x1 * _evaluate(scalar_rows["M_x1"]["log_x2_over_x1"], point)
                    + c_x2 * _evaluate(scalar_rows["M_x2"]["log_x2_over_x1"], point)
                    + flux["log_x2_over_x1"]
                ),
                "log_x3_over_x1": sp.cancel(
                    c_x1 * _evaluate(scalar_rows["M_x1"]["log_x3_over_x1"], point)
                    + c_x2 * _evaluate(scalar_rows["M_x2"]["log_x3_over_x1"], point)
                    + flux["log_x3_over_x1"]
                ),
                "rational_corner": flux["rational_corner"],
                "M14_singlet": c14,
                "M15_standard_u": c15,
                "M16_standard_v": c16,
            }
            for basis_id in INTEGRATED_BASIS:
                if _evaluate(row["integrated_function_basis"][basis_id], point) != expected_integrated[basis_id]:
                    raise ValueError(f"integrated basis mismatch: {row['channel_id']} {basis_id} {point}")

            local_dict = {"x1": point[0], "x2": point[1], "x3": point[2], "z": sp.Symbol("z"), "log": sp.log}
            expected_scale = sp.cancel(
                c14 * sp.sympify(master_value_rows["M14_singlet"]["scale_derivative"], locals=local_dict)
                + c15 * sp.sympify(master_value_rows["M15_standard_u"]["scale_derivative"], locals=local_dict)
                + c16 * sp.sympify(master_value_rows["M16_standard_v"]["scale_derivative"], locals=local_dict)
            )
            scale_row = row["scale_derivative"]
            expected_recipe = [
                {
                    "coordinate_master_id": master_id,
                    "scale_master_id": master_id,
                }
                for master_id in ("M14_singlet", "M15_standard_u", "M16_standard_v")
            ]
            if scale_row["additive_terms"] != expected_recipe:
                raise ValueError(f"scale derivative recipe mismatch: {row['channel_id']}")
            holdout = next(
                item for item in scale_row["exact_holdouts"]
                if tuple(item["box_point"]) == point
            )
            if _from_q(holdout["value"]) != expected_scale:
                raise ValueError(f"scale derivative mismatch: {row['channel_id']} {point}")

    flags = value["claim_flags"]
    if not (
        flags["PHYSICAL_N3_TRIANGLE_BOUNDARY_FLUX_COMPUTED"]
        and flags["PHYSICAL_N3_TRIANGLE_INTEGRATED"]
        and flags["PHYSICAL_N3_TRIANGLE_FUNCTION_BASIS_DECOMPOSITION_COMPUTED"]
        and flags["ALL_ELEVEN_CHANNELS_INTEGRATED"]
    ):
        raise ValueError("integrated triangle claim flags are not closed")
    if (
        flags["REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"]
        or flags["COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED"]
        or flags["COMPLETE_RENORMALIZED_Q1_SUPPLIED"]
        or flags["QME_RESTORED"]
        or flags["RESIDUAL_TRANSFER_AUTHORIZED"]
        or flags["LORENTZIAN_CERTIFIED"]
    ):
        raise ValueError("a downstream lifecycle flag was promoted")


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("generic physical triangle relative-IBP boundary flux: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
