#!/usr/bin/env python3
"""Compute physical triangle corner flux and the complete master assembly."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import multiprocessing
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp
from sympy.polys.matrices import DomainMatrix

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
from .generic_background_physical_hessian_triangle_six_master_coordinates import (
    _rational_function,
    polynomial_from_terms,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RELATIVE_IBP_BOUNDARY_FLUX.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-triangle-relative-ibp-boundary-flux-v1.schema.json"
COORDINATES = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_SIX_MASTER_COORDINATES.json"
COMPLETENESS = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_MASTER_COMPLETENESS.json"
MASTER_VALUES = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RENORMALIZED_MASTER_VALUES.json"
SCALAR_TRIANGLE = HERE / "certificates/GENERIC_SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM.json"
VOLTERRA = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_COVARIANT_VOLTERRA_CARRIER.json"
OBSTRUCTION = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_INTEGRATION_OBSTRUCTION.json"

XS = (X1, X2, X3)
MASTER_IDS = (
    "J_triangle",
    "M_x1",
    "M_x2",
    "M14_singlet",
    "M15_standard_u",
    "M16_standard_v",
)
FLUX_BASIS = ("log_x2_over_x1", "log_x3_over_x1", "rational_corner")
INTEGRATED_BASIS = (
    "J_triangle",
    "log_x2_over_x1",
    "log_x3_over_x1",
    "rational_corner",
    "M14_singlet",
    "M15_standard_u",
    "M16_standard_v",
)
SCALE_MASTER_IDS = ("M14_singlet", "M15_standard_u", "M16_standard_v")
SCALE_HOLDOUT_POINTS = ((2, 3, 5), (3, 5, 7))

_TANGENT_SQUARE: DomainMatrix | None = None
_RESIDUALS: DomainMatrix | None = None
_RESIDUAL_DENOMINATORS: list[sp.Expr] | None = None
_CORNER_WEIGHTS: list[list[sp.Expr]] | None = None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": value["result_id"],
        "sha256": _sha256(path),
    }


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _q(value: sp.Expr) -> dict[str, int]:
    rational = sp.Rational(value)
    return {"numerator": int(rational.p), "denominator": int(rational.q)}


def rational_from_data(value: dict[str, Any]) -> sp.Expr:
    return sp.cancel(
        polynomial_from_terms(value["numerator_terms"])
        / polynomial_from_terms(value["denominator_terms"])
    )


def _field_to_polynomial_matrix(matrix: Any, ring: Any) -> DomainMatrix:
    return DomainMatrix.from_list(
        [
            [ring.from_sympy(value.as_expr()) for value in row]
            for row in matrix.rep.to_list()
        ],
        ring,
    )


def _corner_weight_rows(
    vector_fields: list[tuple[sp.Expr, sp.Expr]], tangent_indices: list[int]
) -> list[list[sp.Expr]]:
    epsilon, parameter = sp.symbols("epsilon parameter")
    rows: list[list[sp.Expr]] = []
    for column_index in tangent_indices:
        P, Q = vector_fields[column_index]
        candidates = (
            -epsilon
            * (P + Q).subs(
                {A: epsilon * (1 - parameter), B: epsilon * parameter}
            ),
            epsilon * P.subs(
                {A: 1 - epsilon, B: epsilon * (1 - parameter)}
            ),
            epsilon * Q.subs({A: epsilon * parameter, B: 1 - epsilon}),
        )
        rows.append(
            [
                sp.Poly(sp.expand(candidate), epsilon).coeff_monomial(epsilon**3)
                for candidate in candidates
            ]
        )
    return rows


def _angular_integral(
    numerator: sp.Expr, start: sp.Expr, end: sp.Expr
) -> tuple[sp.Expr, sp.Expr, list[sp.Expr]]:
    parameter = sp.symbols("parameter")
    polynomial = sp.Poly(sp.cancel(numerator), parameter)
    if polynomial.degree() > 2:
        raise ValueError("physical corner numerator exceeds quadratic angular basis")
    coefficients = [
        sp.cancel(polynomial.coeff_monomial(parameter**power))
        for power in range(3)
    ]
    c0, c1, c2 = coefficients
    difference = end - start
    i0 = sp.cancel((start + end) / (2 * start**2 * end**2))
    i1 = sp.cancel(1 / (2 * start * end**2))
    i2_rational = sp.cancel(
        (2 * start / end - start**2 / (2 * end**2) - sp.Rational(3, 2))
        / difference**3
    )
    i2_log = sp.cancel(1 / difference**3)
    rational = sp.cancel(c0 * i0 + c1 * i1 + c2 * i2_rational)
    local_log = sp.cancel(c2 * i2_log)
    return rational, local_log, coefficients


def _solve_flux(channel_index: int) -> dict[str, Any]:
    if (
        _TANGENT_SQUARE is None
        or _RESIDUALS is None
        or _RESIDUAL_DENOMINATORS is None
        or _CORNER_WEIGHTS is None
    ):
        raise RuntimeError("boundary-flux worker was not initialized")
    right_hand_side = _RESIDUALS.extract(range(46), [channel_index])
    numerator, denominator = _TANGENT_SQUARE.solve_den(right_hand_side)
    if _TANGENT_SQUARE.matmul(numerator) != right_hand_side.scalarmul(denominator):
        raise ValueError(f"tangent primitive solve failed: channel {channel_index}")
    primitive_numerators = numerator.to_Matrix()[:, 0]
    residual_denominator = _RESIDUAL_DENOMINATORS[channel_index]
    common_denominator = sp.expand(denominator.as_expr()) * residual_denominator

    corner_numerators = [sp.S.Zero, sp.S.Zero, sp.S.Zero]
    for coefficient, weights in zip(primitive_numerators, _CORNER_WEIGHTS):
        if coefficient == 0:
            continue
        for corner_index, weight in enumerate(weights):
            if weight:
                corner_numerators[corner_index] += coefficient * weight
    corner_numerators = [
        sp.cancel(value / common_denominator) for value in corner_numerators
    ]

    corner_specs = (
        ("alpha0_vertex", X1, X3, "log_x3_over_x1"),
        ("alpha1_vertex", X2, X1, "minus_log_x2_over_x1"),
        ("alpha2_vertex", X3, X2, "log_x2_over_x1_minus_log_x3_over_x1"),
    )
    corner_rows = []
    local_logs = []
    rational_total = sp.S.Zero
    for numerator_value, (corner_id, start, end, log_map) in zip(
        corner_numerators, corner_specs
    ):
        rational, local_log, coefficients = _angular_integral(
            numerator_value, start, end
        )
        rational_total += rational
        local_logs.append(local_log)
        corner_rows.append(
            {
                "corner_id": corner_id,
                "start_box": sp.sstr(start),
                "end_box": sp.sstr(end),
                "angular_numerator_coefficients": [
                    _rational_function(value) for value in coefficients
                ],
                "integrated_rational": _rational_function(rational),
                "local_log_coefficient": _rational_function(local_log),
                "local_log_map": log_map,
            }
        )
    log2 = sp.cancel(-local_logs[1] + local_logs[2])
    log3 = sp.cancel(local_logs[0] - local_logs[2])
    flux_coordinates = {
        "log_x2_over_x1": _rational_function(log2),
        "log_x3_over_x1": _rational_function(log3),
        "rational_corner": _rational_function(sp.cancel(rational_total)),
    }
    return {
        "corner_rows": corner_rows,
        "flux_coordinates": flux_coordinates,
    }


def _master_coordinate_rows(certificate: dict[str, Any]) -> list[list[sp.Expr]]:
    rows = []
    for channel_row in certificate["channel_rows"]:
        rows.append(
            [
                rational_from_data(master_row["coordinate"])
                for master_row in channel_row["master_coordinates"]
            ]
        )
    return rows


def _scalar_master_rows(certificate: dict[str, Any]) -> dict[str, dict[str, sp.Expr]]:
    return {
        master_id: {
            basis_id: rational_from_data(value)
            for basis_id, value in row.items()
        }
        for master_id, row in certificate["master_rows"].items()
    }


def _setup(
    system: dict[str, Any], coordinate_certificate: dict[str, Any]
) -> tuple[dict[str, Any], list[list[sp.Expr]], list[int]]:
    global _TANGENT_SQUARE, _RESIDUALS, _RESIDUAL_DENOMINATORS, _CORNER_WEIGHTS
    columns, vector_fields, old_masters = _pole4_system()
    tangent_indices = [index for index in system["pivot_columns"] if index < 84]
    if len(tangent_indices) != 46:
        raise ValueError("canonical tangent-column count drifted")
    tangent = _domain_matrix(
        [columns[index] for index in tangent_indices], system["basis"]
    )
    numeric = tangent.to_Matrix().subs(PIVOT_FIXTURE)
    tangent_rows = tuple(numeric.transpose().rref()[1])
    if len(tangent_rows) != 46:
        raise ValueError("canonical tangent-row count drifted")

    coordinates = _master_coordinate_rows(coordinate_certificate)
    masters = [*old_masters, *system["all_columns"][-3:]]
    residual_denominators = []
    residual_numerators = []
    for target, coordinate_row in zip(system["targets"], coordinates):
        common_denominator = sp.lcm([sp.denom(value) for value in coordinate_row])
        scaled_coordinates = [
            sp.cancel(common_denominator * value) for value in coordinate_row
        ]
        if any(sp.denom(value) != 1 for value in scaled_coordinates):
            raise ValueError("coordinate common denominator is incomplete")
        residual = sp.expand(
            common_denominator * target
            - sum(
                value * master
                for value, master in zip(scaled_coordinates, masters)
            )
        )
        residual_denominators.append(sp.factor(common_denominator))
        residual_numerators.append(residual)

    residual_matrix = _domain_matrix(
        residual_numerators, system["basis"], tangent.domain
    )
    ring = sp.QQ.poly_ring(*XS)
    _TANGENT_SQUARE = _field_to_polynomial_matrix(
        tangent.extract(tangent_rows, range(46)), ring
    )
    _RESIDUALS = _field_to_polynomial_matrix(
        residual_matrix.extract(tangent_rows, range(11)), ring
    )
    _RESIDUAL_DENOMINATORS = residual_denominators
    _CORNER_WEIGHTS = _corner_weight_rows(vector_fields, tangent_indices)
    return (
        {
            "tangent_columns": tangent_indices,
            "tangent_rows": list(tangent_rows),
            "corner_weight_nonzero_counts": [
                sum(1 for row in _CORNER_WEIGHTS if row[index] != 0)
                for index in range(3)
            ],
            "maximum_corner_weight_degree": max(
                sp.Poly(weight, sp.symbols("parameter")).degree()
                for row in _CORNER_WEIGHTS
                for weight in row
                if weight != 0
            ),
        },
        coordinates,
        tangent_indices,
    )


def build(*, jobs: int = 1) -> dict[str, Any]:
    projection = json.loads(PROJECTION.read_text())
    coordinate_certificate = json.loads(COORDINATES.read_text())
    completeness = json.loads(COMPLETENESS.read_text())
    master_values = json.loads(MASTER_VALUES.read_text())
    scalar_triangle = json.loads(SCALAR_TRIANGLE.read_text())
    volterra = json.loads(VOLTERRA.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    if (
        coordinate_certificate["claim_flags"][
            "PHYSICAL_N3_TRIANGLE_MASTER_COORDINATES_COMPUTED"
        ]
        is not True
        or master_values["claim_flags"]["RENORMALIZED_SIX_MASTER_VALUES_COMPUTED"]
        is not True
        or scalar_triangle["claim_flags"]["TWO_LOG_MASTER_REDUCTION_COMPUTED"]
        is not True
        or volterra["claim_flags"]["COMMON_MELLIN_BOUNDARY_EXTENSION_DEFINED"]
        is not True
    ):
        raise ValueError("physical triangle boundary-flux dependency gate is not closed")
    system = _system(projection)
    tangent_ledger, coordinates, _ = _setup(system, coordinate_certificate)
    if jobs <= 1:
        flux_rows = [_solve_flux(index) for index in range(11)]
    else:
        context = multiprocessing.get_context("fork")
        with ProcessPoolExecutor(max_workers=jobs, mp_context=context) as executor:
            flux_rows = list(executor.map(_solve_flux, range(11)))

    scalar_masters = _scalar_master_rows(scalar_triangle)
    master_scale = {
        row["master_id"]: sp.factor(
            sp.cancel(
                sp.sympify(
                    row["scale_derivative"],
                    locals={
                        "x1": X1,
                        "x2": X2,
                        "x3": X3,
                        "z": sp.symbols("z"),
                        "log": sp.log,
                    },
                )
            )
        )
        for row in master_values["master_rows"]
    }
    obstruction_rows = {
        row["channel_id"]: row for row in obstruction["channel_rows"]
    }
    channel_rows = []
    for projection_row, coordinate_row, flux_row in zip(
        projection["projection_rows"], coordinates, flux_rows
    ):
        c_j, c_x1, c_x2, c14, c15, c16 = coordinate_row
        flux_coordinates = {
            basis_id: rational_from_data(value)
            for basis_id, value in flux_row["flux_coordinates"].items()
        }
        integrated = {
            "J_triangle": sp.cancel(
                c_j
                + c_x1 * scalar_masters["M_x1"]["J_triangle"]
                + c_x2 * scalar_masters["M_x2"]["J_triangle"]
            ),
            "log_x2_over_x1": sp.cancel(
                c_x1 * scalar_masters["M_x1"]["log_x2_over_x1"]
                + c_x2 * scalar_masters["M_x2"]["log_x2_over_x1"]
                + flux_coordinates["log_x2_over_x1"]
            ),
            "log_x3_over_x1": sp.cancel(
                c_x1 * scalar_masters["M_x1"]["log_x3_over_x1"]
                + c_x2 * scalar_masters["M_x2"]["log_x3_over_x1"]
                + flux_coordinates["log_x3_over_x1"]
            ),
            "rational_corner": flux_coordinates["rational_corner"],
            "M14_singlet": c14,
            "M15_standard_u": c15,
            "M16_standard_v": c16,
        }
        scale_coordinates = (c14, c15, c16)
        symmetric_point = {X1: 1, X2: 1, X3: 1}
        symmetric_scale = sum(
            coordinate.subs(symmetric_point) * master_scale[master_id].subs(symmetric_point)
            for coordinate, master_id in zip(scale_coordinates, SCALE_MASTER_IDS)
        )
        expected_scale = sp.Rational(
            obstruction_rows[projection_row["channel_id"]]["log_corner_coefficient"]["numerator"],
            obstruction_rows[projection_row["channel_id"]]["log_corner_coefficient"]["denominator"],
        )
        if symmetric_scale != expected_scale:
            raise ValueError(
                f"symmetric scale-row regression failed: {projection_row['channel_id']}"
            )
        channel_rows.append(
            {
                "channel_id": projection_row["channel_id"],
                **flux_row,
                "integrated_function_basis": {
                    basis_id: _rational_function(integrated[basis_id])
                    for basis_id in INTEGRATED_BASIS
                },
                "scale_derivative": {
                    "additive_terms": [
                        {
                            "coordinate_master_id": master_id,
                            "scale_master_id": master_id,
                        }
                        for master_id in SCALE_MASTER_IDS
                    ],
                    "exact_holdouts": [
                        {
                            "box_point": list(point),
                            "value": _q(
                                sum(
                                    coordinate.subs(dict(zip(XS, point)))
                                    * master_scale[master_id].subs(dict(zip(XS, point)))
                                    for coordinate, master_id in zip(
                                        scale_coordinates, SCALE_MASTER_IDS
                                    )
                                )
                            ),
                        }
                        for point in SCALE_HOLDOUT_POINTS
                    ],
                },
                "symmetric_scale_regression": {
                    "actual": _q(symmetric_scale),
                    "expected": _q(expected_scale),
                    "status": "EXACT",
                },
            }
        )

    payload = {
        "tangent_ledger": tangent_ledger,
        "angular_moment_basis": {
            "I0": "(a+b)/(2*a^2*b^2)",
            "I1": "1/(2*a*b^2)",
            "I2_rational": "(2*a/b-a^2/(2*b^2)-3/2)/(b-a)^3",
            "I2_log": "log(b/a)/(b-a)^3",
            "global_log_basis": ["log(x2/x1)", "log(x3/x1)"],
        },
        "channel_rows": channel_rows,
        "identity_ledger": {
            "channel_count": 11,
            "tangent_identity_count": 11,
            "corner_count": 33,
            "integrated_basis_coordinate_count": 77,
            "symmetric_scale_regression_count": 11,
            "status": "ALL_EXACT",
        },
    }
    result = {
        "schema": "quantum-weyl-generic-background-physical-hessian-triangle-relative-ibp-boundary-flux-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RELATIVE_IBP_BOUNDARY_FLUX",
        "result_state": "ALL_ELEVEN_PHYSICAL_TRIANGLE_BOUNDARY_FLUXES_AND_INTEGRATED_MASTER_DECOMPOSITIONS_COMPUTED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": completeness["classical_commit"],
        "dependencies": {
            "physical_five_carrier_projection": _reference(PROJECTION),
            "six_master_completeness": _reference(COMPLETENESS),
            "six_master_coordinates": _reference(COORDINATES),
            "renormalized_master_values": _reference(MASTER_VALUES),
            "scalar_triangle_differential_system": _reference(SCALAR_TRIANGLE),
            "covariant_Volterra_carrier": _reference(VOLTERRA),
            "symmetric_integration_obstruction": _reference(OBSTRUCTION),
        },
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "kinematics": "generic nonexceptional x1,x2,x3 away from displayed chart denominators",
            "input": "eleven exact physical three-H1 triangle rows and their six-master coordinates",
            "output": "punctured-simplex corner flux and complete seven-function structured triangle decomposition",
        },
        **payload,
        "formula_digest": _canonical_digest(payload),
        "claim_flags": {
            "PHYSICAL_N3_TRIANGLE_MASTER_COORDINATES_COMPUTED": True,
            "PHYSICAL_N3_TRIANGLE_BOUNDARY_FLUX_COMPUTED": True,
            "PHYSICAL_N3_TRIANGLE_INTEGRATED": True,
            "PHYSICAL_N3_TRIANGLE_FUNCTION_BASIS_DECOMPOSITION_COMPUTED": True,
            "ALL_ELEVEN_CHANNELS_INTEGRATED": True,
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "QME_RESTORED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "next_gate": "ASSEMBLE_ELEVEN_PHYSICAL_TRIANGLE_FUNCTIONS_INTO_FIVE_REPOSITORY_THIRD_CURVATURE_FORM_FACTORS",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL certificate computes the punctured-simplex relative-IBP boundary flux of all eleven physical three-H1 triangle channels and combines it with the certified six-master coordinates, scalar-triangle differential masters and renormalized M14/M15/M16 values into a complete structured generic triangle decomposition. It does not yet assemble those eleven raw channel functions and the finite H1-H2 contact rows into the five repository third-curvature form factors, fix independent finite counterterm normalizations, supply complete Gamma1 or Q1, authorize residual transfer, or establish a Lorentzian, Hadamard, particle, positivity, scattering or unitarity theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
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
    if _canonical_digest(payload) != value["formula_digest"]:
        raise ValueError("physical triangle boundary-flux digest drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args()
    if args.fast:
        if args.emit:
            raise SystemExit("--fast cannot emit an exhaustive boundary-flux certificate")
        if not OUTPUT.exists():
            raise SystemExit(f"missing boundary-flux certificate: {OUTPUT}")
        value = json.loads(OUTPUT.read_text())
        validate(value)
    else:
        value = build(jobs=max(1, args.jobs))
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale physical triangle boundary-flux certificate: {OUTPUT}")
    print("GENERIC PHYSICAL TRIANGLE RELATIVE-IBP BOUNDARY FLUX: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
