#!/usr/bin/env python3
"""Independent replay of the physical three-H1 corner obstruction."""

from __future__ import annotations

import hashlib
import itertools
import json
import gc
from pathlib import Path
from typing import Any

import sympy as sp

from spectral.euclidean.generic_background_ghost_n3_i29_integrated_function import (
    _pole4_system,
)
from spectral.euclidean.generic_background_ghost_n3_pole3_relative_ibp import (
    A,
    B,
    X1,
    X2,
    X3,
    _domain_matrix,
    _monomials,
)
from spectral.euclidean.generic_background_physical_hessian_n3_integration_obstruction import (
    AFFINE_MONOMIALS,
    OUTPUT,
    POLE4,
    PROJECTION,
    ROOT,
    validate,
)


CF = 1 - A - B
E2 = sp.expand(A * B + B * CF + CF * A)
E3 = sp.expand(A * B * CF)
SIGNATURES = tuple(
    (i, j) for j in range(4) for i in range(5) if 2 * i + 3 * j <= 9
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q_value(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _check_dependencies(payload: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "physical_five_carrier_projection": PROJECTION,
        "pole4_relative_IBP_architecture": POLE4,
    }
    loaded = {}
    for name, expected_path in expected.items():
        reference = payload["dependencies"][name]
        path = ROOT / reference["path"]
        if (
            path.resolve() != expected_path.resolve()
            or not path.is_file()
            or _sha256(path) != reference["sha256"]
        ):
            raise ValueError(f"{name} dependency path or hash drifted")
        loaded[name] = json.loads(path.read_text())
        if loaded[name].get("result_id") != reference["result_id"]:
            raise ValueError(f"{name} dependency identity drifted")
    return loaded


def _row_expression(row: dict[str, Any]) -> sp.Expr:
    return sp.expand(
        sum(
            _q_value(term["coefficient"])
            * A ** term["alpha_exponents"][0]
            * B ** term["alpha_exponents"][1]
            for term in row["terms"]
        )
    )


def _coordinate_map(expression: sp.Expr) -> dict[tuple[int, int], sp.Rational]:
    average = sp.expand(
        sum(
            expression.subs({A: p[0], B: p[1]}, simultaneous=True)
            for p in itertools.permutations((A, B, CF), 3)
        )
        / 6
    )
    basis = [sp.expand(E2**i * E3**j) for i, j in SIGNATURES]
    matrix = sp.Matrix(
        [
            [sp.Poly(value, A, B).coeff_monomial(m) for value in basis]
            for m in AFFINE_MONOMIALS
        ]
    )
    pivots = matrix.T.rref()[1]
    right = sp.Matrix(
        [sp.Poly(average, A, B).coeff_monomial(AFFINE_MONOMIALS[i]) for i in pivots]
    )
    coordinates = list(matrix.extract(pivots, range(12)).inv() * right)
    if matrix * sp.Matrix(coordinates) != sp.Matrix(
        [sp.Poly(average, A, B).coeff_monomial(m) for m in AFFINE_MONOMIALS]
    ):
        raise ValueError("independent symmetric-coordinate reconstruction failed")
    return {
        signature: sp.Rational(value)
        for signature, value in zip(SIGNATURES, coordinates)
        if value
    }


def _check_channel_rows(payload: dict[str, Any], projection: dict[str, Any]) -> None:
    for stored, source in zip(payload["channel_rows"], projection["projection_rows"]):
        coordinates = _coordinate_map(_row_expression(source))
        declared = {
            (row["e2_power"], row["e3_power"]): _q_value(row["coefficient"])
            for row in stored["symmetric_invariant_coordinates"]
        }
        obstruction = coordinates.get((0, 1), sp.S.Zero)
        if (
            stored["channel_id"] != source["channel_id"]
            or coordinates != declared
            or _q_value(stored["M14_e3_over_e2_power4_coefficient"])
            != obstruction
            or _q_value(stored["log_corner_coefficient"]) != obstruction / 2
        ):
            raise ValueError(f"independent channel replay failed: {stored['channel_id']}")


def _check_dual_witness(payload: dict[str, Any]) -> None:
    columns, _, masters = _pole4_system()
    basis = _monomials(9)
    substitution = {X1: 1, X2: 1, X3: 1}
    relative_domain = _domain_matrix(
        [
            *(column.subs(substitution) for column in columns),
            *(master.subs(substitution) for master in masters),
        ],
        basis,
    )
    relative_rank = relative_domain.rank()
    relative = relative_domain.to_Matrix()
    witness_data = payload["relative_quotient"]["M14_dual_nonmembership_witness"]
    coordinate_map = {
        (row["alpha1_power"], row["alpha2_power"]): _q_value(row["coefficient"])
        for row in witness_data["nonzero_coordinates"]
    }
    witness = sp.Matrix(
        [
            coordinate_map.get(
                (sp.Poly(m, A, B).degree(A), sp.Poly(m, A, B).degree(B)),
                sp.S.Zero,
            )
            for m in AFFINE_MONOMIALS
        ]
    )
    target = sp.Matrix(
        [sp.Poly(E3, A, B).coeff_monomial(m) for m in AFFINE_MONOMIALS]
    )
    if relative_rank != 49 or relative.T * witness != sp.zeros(relative.cols, 1):
        raise ValueError("independent dual-witness annihilation failed")
    if (witness.T * target)[0] != 1:
        raise ValueError("independent dual-witness normalization failed")


def _check_corner_asymptotic(payload: dict[str, Any]) -> None:
    epsilon, t = sp.symbols("epsilon t", positive=True)
    substitution = {A: 1 - epsilon, B: epsilon * (1 - t)}
    coefficient = sp.limit(
        sp.cancel(epsilon**2 * (E3 / E2**4).subs(substitution, simultaneous=True)),
        epsilon,
        0,
        dir="+",
    )
    per_corner = sp.integrate(coefficient, (t, 0, 1))
    declared = payload["corner_asymptotic"]
    if (
        sp.expand(coefficient - t * (1 - t)) != 0
        or per_corner != sp.Rational(1, 6)
        or _q_value(declared["total_log_1_over_epsilon_coefficient"])
        != 3 * per_corner
    ):
        raise ValueError("independent logarithmic corner asymptotic failed")


def verify(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    stored = json.loads(OUTPUT.read_text()) if payload is None else payload
    validate(stored)
    dependencies = _check_dependencies(stored)
    # Replay the sparse pole-four witness before materializing the much larger
    # carrier polynomials.  Keeping both SymPy object graphs live at once can
    # exceed the bounded-memory verification rail without adding scrutiny.
    _check_dual_witness(stored)
    gc.collect()
    _check_channel_rows(stored, dependencies["physical_five_carrier_projection"])
    _check_corner_asymptotic(stored)
    print("physical Hessian n=3 integration-obstruction independent verification: PASS")
    return stored


if __name__ == "__main__":
    verify()
