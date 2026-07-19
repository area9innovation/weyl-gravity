#!/usr/bin/env python3
"""Certify the logarithmic corner obstruction of the isolated three-H1 row."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from .generic_background_ghost_n3_i29_integrated_function import _pole4_system
from .generic_background_ghost_n3_pole3_relative_ibp import (
    A,
    B,
    C,
    X1,
    X2,
    X3,
    _domain_matrix,
    _monomials,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_INTEGRATION_OBSTRUCTION.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-n3-integration-obstruction-v1.schema.json"
PROJECTION = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_FIVE_CARRIER_PROJECTION.json"
POLE4 = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_I29_INTEGRATED_FUNCTION.json"

CF = 1 - A - B
E2 = sp.expand(A * B + B * CF + CF * A)
E3 = sp.expand(A * B * CF)
INVARIANT_SIGNATURES = tuple(
    (e2_power, e3_power)
    for e3_power in range(4)
    for e2_power in range(5)
    if 2 * e2_power + 3 * e3_power <= 9
)
AFFINE_MONOMIALS = tuple(
    A**i * B**j for i in range(10) for j in range(10 - i)
)


def _q(value: Any) -> dict[str, int]:
    rational = sp.Rational(value)
    return {"numerator": int(rational.p), "denominator": int(rational.q)}


def _from_q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


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


def _symmetric_invariant_solver() -> tuple[sp.Matrix, tuple[int, ...]]:
    invariant_basis = [
        sp.expand(E2**e2_power * E3**e3_power)
        for e2_power, e3_power in INVARIANT_SIGNATURES
    ]
    matrix = sp.Matrix(
        [
            [
                sp.Poly(value, A, B).coeff_monomial(monomial)
                for value in invariant_basis
            ]
            for monomial in AFFINE_MONOMIALS
        ]
    )
    pivot_rows = matrix.T.rref()[1]
    if matrix.rank() != len(INVARIANT_SIGNATURES):
        raise ValueError("symmetric invariant basis lost rank")
    return matrix.extract(pivot_rows, range(len(INVARIANT_SIGNATURES))).inv(), pivot_rows


def _row_at_symmetric_boxes(row: dict[str, Any]) -> sp.Expr:
    return sp.expand(
        sum(
            _from_q(term["coefficient"])
            * A ** term["alpha_exponents"][0]
            * B ** term["alpha_exponents"][1]
            for term in row["terms"]
        )
    )


def _symmetric_average(expression: sp.Expr) -> sp.Expr:
    return sp.expand(
        sum(
            expression.subs({A: permutation[0], B: permutation[1]}, simultaneous=True)
            for permutation in itertools.permutations((A, B, CF), 3)
        )
        / 6
    )


def _invariant_coordinates(
    expression: sp.Expr, inverse: sp.Matrix, pivot_rows: tuple[int, ...]
) -> list[sp.Rational]:
    polynomial = sp.Poly(expression, A, B, domain=sp.QQ)
    right = sp.Matrix(
        [polynomial.coeff_monomial(AFFINE_MONOMIALS[index]) for index in pivot_rows]
    )
    coordinates = list(inverse * right)
    reconstructed = sp.expand(
        sum(
            coefficient * E2**signature[0] * E3**signature[1]
            for signature, coefficient in zip(INVARIANT_SIGNATURES, coordinates)
        )
    )
    if sp.expand(reconstructed - expression) != 0:
        raise ValueError("symmetric invariant reconstruction failed")
    return [sp.Rational(value) for value in coordinates]


def _coefficient_vector(expression: sp.Expr) -> sp.Matrix:
    polynomial = sp.Poly(sp.expand(expression), A, B, domain=sp.QQ)
    return sp.Matrix(
        [polynomial.coeff_monomial(monomial) for monomial in AFFINE_MONOMIALS]
    )


def _relative_quotient_ranks() -> tuple[
    int, dict[tuple[int, int], int], dict[str, Any]
]:
    columns, _, masters = _pole4_system()
    basis = _monomials(9)
    substitution = {X1: 1, X2: 1, X3: 1}
    relative = _domain_matrix(
        [
            *(column.subs(substitution) for column in columns),
            *(master.subs(substitution) for master in masters),
        ],
        basis,
    )
    base_rank = relative.rank()
    augmented = {}
    for signature in INVARIANT_SIGNATURES:
        target = _domain_matrix(
            [E2 ** signature[0] * E3 ** signature[1]],
            basis,
            relative.domain,
        )
        augmented[signature] = relative.hstack(target).rank()
    relative_matrix = relative.to_Matrix()
    target_vector = _coefficient_vector(E3)
    candidates = relative_matrix.T.nullspace()
    witness = next(
        (candidate for candidate in candidates if (candidate.T * target_vector)[0]),
        None,
    )
    if witness is None:
        raise ValueError("M14 dual nonmembership witness was not found")
    witness = witness / (witness.T * target_vector)[0]
    if relative_matrix.T * witness != sp.zeros(relative_matrix.cols, 1):
        raise ValueError("M14 dual witness does not annihilate the relative span")
    return base_rank, augmented, {
        "witness_type": "COMPLETE_NONMEMBERSHIP_WITNESS_IN_DECLARED_SYMMETRIC_POINT_POLE4_AMBIENT",
        "ambient_alpha_monomial_count": len(AFFINE_MONOMIALS),
        "relative_span_annihilation": "ZERO",
        "M14_normalization": _q((witness.T * target_vector)[0]),
        "nonzero_coordinates": [
            {
                "alpha1_power": sp.Poly(monomial, A, B).degree(A),
                "alpha2_power": sp.Poly(monomial, A, B).degree(B),
                "coefficient": _q(coefficient),
            }
            for monomial, coefficient in zip(AFFINE_MONOMIALS, witness)
            if coefficient
        ],
    }


def _corner_asymptotic() -> dict[str, Any]:
    epsilon, parameter = sp.symbols("epsilon parameter", positive=True)
    substitutions = (
        {A: 1 - epsilon, B: epsilon * (1 - parameter)},
        {A: epsilon * (1 - parameter), B: 1 - epsilon},
        {A: epsilon * parameter, B: epsilon * (1 - parameter)},
    )
    densities = []
    for substitution in substitutions:
        # One epsilon is the simplex Jacobian; the second extracts the
        # coefficient of d epsilon / epsilon.
        scaled_density = sp.cancel(
            epsilon**2 * (E3 / E2**4).subs(substitution, simultaneous=True)
        )
        leading = sp.cancel(sp.limit(scaled_density, epsilon, 0, dir="+"))
        if sp.expand(leading - parameter * (1 - parameter)) != 0:
            raise ValueError("M14 corner leading density drifted")
        densities.append(leading)
    per_corner = sp.integrate(densities[0], (parameter, 0, 1))
    total = sp.cancel(3 * per_corner)
    if per_corner != sp.Rational(1, 6) or total != sp.Rational(1, 2):
        raise ValueError("M14 logarithmic corner coefficient drifted")
    return {
        "corner_coordinates": "one dominant alpha=1-epsilon; two small alphas split as epsilon*t and epsilon*(1-t)",
        "simplex_Jacobian": "epsilon",
        "leading_density_after_Jacobian": "t*(1-t)/epsilon",
        "angular_integral_per_corner": _q(per_corner),
        "corner_count": 3,
        "total_log_1_over_epsilon_coefficient": _q(total),
    }


def build() -> dict[str, Any]:
    projection = json.loads(PROJECTION.read_text())
    pole4 = json.loads(POLE4.read_text())
    if (
        projection.get("claim_flags", {}).get(
            "PHYSICAL_N3_FIVE_CARRIER_PROJECTION_COMPUTED"
        )
        is not True
        or projection.get("claim_flags", {}).get("PHYSICAL_N3_TRIANGLE_INTEGRATED")
        is not False
        or pole4.get("rank_ledger", {}).get("tangent_plus_masters_rank") != 49
    ):
        raise ValueError("physical integration-obstruction dependency drifted")

    inverse, pivot_rows = _symmetric_invariant_solver()
    channel_rows = []
    for row in projection["projection_rows"]:
        averaged = _symmetric_average(_row_at_symmetric_boxes(row))
        coordinates = _invariant_coordinates(averaged, inverse, pivot_rows)
        coordinate_rows = [
            {
                "e2_power": signature[0],
                "e3_power": signature[1],
                "coefficient": _q(coefficient),
            }
            for signature, coefficient in zip(INVARIANT_SIGNATURES, coordinates)
            if coefficient
        ]
        obstruction = coordinates[INVARIANT_SIGNATURES.index((0, 1))]
        channel_rows.append(
            {
                "channel_id": row["channel_id"],
                "symmetric_invariant_coordinates": coordinate_rows,
                "M14_e3_over_e2_power4_coefficient": _q(obstruction),
                "log_corner_coefficient": _q(obstruction / 2),
                "obstruction_status": "NONZERO" if obstruction else "ZERO",
            }
        )

    base_rank, augmented_ranks, dual_witness = _relative_quotient_ranks()
    if base_rank != 49 or augmented_ranks[(0, 1)] != 50 or any(
        rank != 49
        for signature, rank in augmented_ranks.items()
        if signature != (0, 1) and any(
            coordinate["e2_power"] == signature[0]
            and coordinate["e3_power"] == signature[1]
            for row in channel_rows
            for coordinate in row["symmetric_invariant_coordinates"]
        )
    ):
        raise ValueError("physical symmetric quotient-rank classification drifted")

    nonzero_channels = [
        row["channel_id"]
        for row in channel_rows
        if row["obstruction_status"] == "NONZERO"
    ]
    if nonzero_channels != [
        "I10_123",
        "I24_123",
        "I24_213",
        "I24_312",
        "I25_123",
        "I25_213",
        "I25_312",
        "I29_123",
    ]:
        raise ValueError("physical logarithmic obstruction channel set drifted")

    payload = {
        "relative_quotient": {
            "symmetric_point_relative_IBP_plus_master_rank": base_rank,
            "M14_augmented_rank": augmented_ranks[(0, 1)],
            "M14_rank_jump": augmented_ranks[(0, 1)] - base_rank,
            "other_occupied_signature_augmented_ranks": [
                {
                    "e2_power": signature[0],
                    "e3_power": signature[1],
                    "augmented_rank": augmented_ranks[signature],
                }
                for signature in INVARIANT_SIGNATURES
                if signature != (0, 1)
                and any(
                    coordinate["e2_power"] == signature[0]
                    and coordinate["e3_power"] == signature[1]
                    for row in channel_rows
                    for coordinate in row["symmetric_invariant_coordinates"]
                )
            ],
            "M14_dual_nonmembership_witness": dual_witness,
        },
        "corner_asymptotic": _corner_asymptotic(),
        "channel_rows": channel_rows,
        "nonzero_obstruction_channels": nonzero_channels,
    }
    return {
        "schema": "quantum-weyl-generic-background-physical-hessian-n3-integration-obstruction-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_INTEGRATION_OBSTRUCTION",
        "result_state": "ISOLATED_PHYSICAL_THREE_H1_TRIANGLE_HAS_LOGARITHMIC_SIMPLEX_CORNER_OBSTRUCTION",
        "lifecycle_state": "PHYSICAL_H1_PARAMETRIC_PROJECTION_COMPUTED_H2_CONTACT_COMPLETION_OR_SUBTRACTION_REQUIRED_BEFORE_INTEGRATION",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": projection["classical_commit"],
        "dependencies": {
            "physical_five_carrier_projection": _reference(PROJECTION),
            "pole4_relative_IBP_architecture": _reference(POLE4),
        },
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "kinematic_fixture": "x1=x2=x3=1 with an S3-symmetric corner cutoff",
            "input": "isolated bosonic +(1/6) Tr[(H0^-1 H1)^3] five-carrier projection",
            "output": "exact logarithmic corner obstruction and minimal missing completion",
        },
        "convention": {
            "e2": "alpha0*alpha1+alpha1*alpha2+alpha2*alpha0",
            "e3": "alpha0*alpha1*alpha2",
            "M14": "integral_simplex e3/e2^4",
            "overall_loop_prefactor": "(4*pi)^-2 excluded",
            "external_box_denominator_at_fixture": "x1*x2*x3=1",
        },
        **payload,
        "formula_digest": _canonical_digest(payload),
        "claim_flags": {
            "PHYSICAL_H1_ONLY_SYMMETRIC_POINT_INTEGRATION_OBSTRUCTED": True,
            "LOGARITHMIC_SIMPLEX_CORNER_CLASS_IDENTIFIED": True,
            "M14_RAISES_RELATIVE_QUOTIENT_RANK_BY_ONE": True,
            "EIGHT_RAW_CARRIER_ORIENTATIONS_HAVE_NONZERO_OBSTRUCTION": True,
            "CURVATURE_SQUARED_H2_IMPORTED": False,
            "H1_H2_MIXED_ROWS_COMPUTED": False,
            "H2_CANCELLATION_OF_CORNER_CLASS_PROVED": False,
            "RENORMALIZED_SUBTRACTION_PRESCRIPTION_FIXED": False,
            "PHYSICAL_N3_TRIANGLE_INTEGRATED": False,
            "COMPLETE_REPOSITORY_CUBIC_FORM_FACTORS_ASSEMBLED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "LORENTZIAN_CERTIFIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
        },
        "next_gate": "IMPORT_PHYSICAL_H2_AND_MIXED_ROWS_THEN_TEST_CORNER_CLASS_CANCELLATION_OR_FIX_A_RENORMALIZED_SUBTRACTION",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate proves that the isolated physical three-H1 triangle cannot be promoted to a finite integrated form factor. At the symmetric point its S3-averaged numerator contains the M14=e3/e2^4 carrier in eight raw orientations; M14 raises the exact pole-four relative-IBP-plus-master rank from 49 to 50 and has total logarithmic corner coefficient one half. The certificate therefore names the curvature-squared H2/mixed contact completion or an explicit renormalized subtraction as the minimal missing input. It does not assert that H2 cancels the class, choose a subtraction, integrate the physical triangle, assemble the complete repository form factors, supply Gamma1 or Q1, authorize residual transfer, or establish any Lorentzian, Hadamard, particle, positivity, scattering, or unitarity theorem."
        ),
    }


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    payload = {
        key: value[key]
        for key in (
            "relative_quotient",
            "corner_asymptotic",
            "channel_rows",
            "nonzero_obstruction_channels",
        )
    }
    if value["formula_digest"] != _canonical_digest(payload):
        raise ValueError("physical integration-obstruction formula digest drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale physical integration-obstruction certificate: {OUTPUT}")
    print(
        "PHYSICAL HESSIAN N3 INTEGRATION: LOGARITHMIC M14 CORNER OBSTRUCTION PASS; H2 OR SUBTRACTION REQUIRED"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
