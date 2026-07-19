#!/usr/bin/env python3
"""Independent semantic replay of the physical Hessian n=3 fixture."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import sympy as sp

from spectral.euclidean.generic_background_physical_hessian_n3_triangle_fixture import (
    DEPENDENCIES,
    OUTPUT,
    ROOT,
    build,
    validate,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: object, label: str) -> Fraction:
    if (
        not isinstance(value, dict)
        or set(value) != {"numerator", "denominator"}
        or not isinstance(value["numerator"], int)
        or not isinstance(value["denominator"], int)
        or value["denominator"] <= 0
    ):
        raise ValueError(f"{label} is not an exact rational")
    return Fraction(value["numerator"], value["denominator"])


def _matrix(value: object, label: str) -> sp.Matrix:
    if not isinstance(value, list) or len(value) != 4 or any(
        not isinstance(row, list) or len(row) != 4 for row in value
    ):
        raise ValueError(f"{label} is not a four-by-four matrix")
    return sp.Matrix(
        [[sp.Rational(*_fraction(entry, label).as_integer_ratio()) for entry in row] for row in value]
    )


def _check_dependencies(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for name, expected_path in DEPENDENCIES.items():
        reference = payload["dependencies"][name]
        path = ROOT / reference["path"]
        if (
            path.resolve() != expected_path.resolve()
            or not path.is_file()
            or _sha256(path) != reference["sha256"]
        ):
            raise ValueError(f"{name} dependency path or hash drifted")
        value = json.loads(path.read_text())
        if value.get("result_id") != reference["result_id"]:
            raise ValueError(f"{name} dependency identity drifted")
        loaded[name] = value
    return loaded


def _check_source_rows(payload: dict[str, Any], parent: dict[str, Any]) -> None:
    rows = payload["scalar_flat_momentum_vertex"]["source_seed_rows"]
    coefficient_rows = parent["source_operator"]["coefficient_rows"]
    ordered_parent_rows = [
        row
        for block_name in ("V_rho_sigma", "N_lambda", "U")
        for row in coefficient_rows[block_name]
        if row["scalar_flat_survives"]
    ]
    parent_rows = {row["term_id"]: row for row in ordered_parent_rows}
    if [row["term_id"] for row in rows] != [
        row["term_id"] for row in ordered_parent_rows
    ]:
        raise ValueError("physical scalar-flat source row order drifted")
    for row in rows:
        source = parent_rows[row["term_id"]]
        source_coefficient = _fraction(source["coefficient"], row["term_id"])
        momentum_coefficient = _fraction(row["coefficient"], row["term_id"])
        # V has two right derivatives, N has one background and one right
        # derivative, and U has two background derivatives: every surviving
        # source coefficient acquires the same Fourier factor i^2=-1.
        if momentum_coefficient != -source_coefficient:
            raise ValueError(f"{row['term_id']} Fourier coefficient drifted")
    encoded = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(encoded).hexdigest() != payload["scalar_flat_momentum_vertex"][
        "source_seed_formula_sha256"
    ]:
        raise ValueError("source seed formula digest drifted")


def _check_external_geometry(fixture: dict[str, Any]) -> None:
    momenta = [sp.Matrix(row) for row in fixture["momenta"]]
    tensors = [
        _matrix(row, f"Ricci_tensors[{index}]")
        for index, row in enumerate(fixture["Ricci_tensors"])
    ]
    if sum(momenta, sp.zeros(4, 1)) != sp.zeros(4, 1):
        raise ValueError("external momentum conservation failed")
    if [int(momentum.dot(momentum)) for momentum in momenta] != fixture[
        "box_invariants"
    ]:
        raise ValueError("external box invariants drifted")
    for momentum, ricci in zip(momenta, tensors):
        if ricci != ricci.T or ricci.trace() != 0 or ricci * momentum != sp.zeros(4, 1):
            raise ValueError("external Ricci tensor is not symmetric TT")
        hessian = 2 * ricci / momentum.dot(momentum)
        riemann = [
            [
                [
                    [
                        -sp.Rational(1, 2)
                        * (
                            momentum[a] * momentum[n] * hessian[m, b]
                            + momentum[m] * momentum[b] * hessian[a, n]
                            - momentum[a] * momentum[b] * hessian[m, n]
                            - momentum[m] * momentum[n] * hessian[a, b]
                        )
                        for b in range(4)
                    ]
                    for n in range(4)
                ]
                for a in range(4)
            ]
            for m in range(4)
        ]
        contraction = sp.Matrix(
            4,
            4,
            lambda a, b: sum(riemann[m][a][m][b] for m in range(4)),
        )
        if contraction != ricci:
            raise ValueError("independent Riemann/Ricci contraction failed")
        for m in range(4):
            for a in range(4):
                for n in range(4):
                    for b in range(4):
                        value = riemann[m][a][n][b]
                        if (
                            value != -riemann[a][m][n][b]
                            or value != -riemann[m][a][b][n]
                            or value != riemann[n][b][m][a]
                            or value
                            + riemann[m][n][b][a]
                            + riemann[m][b][a][n]
                            != 0
                        ):
                            raise ValueError("independent Riemann symmetry replay failed")


def _check_parametric_arithmetic(payload: dict[str, Any]) -> None:
    fixture = payload["exact_interior_fixture"]
    alpha = [
        _fraction(fixture["alpha"][name], name)
        for name in ("alpha0", "alpha1", "alpha2")
    ]
    if sum(alpha) != 1 or any(value <= 0 for value in alpha):
        raise ValueError("fixture is not an interior simplex point")
    boxes = fixture["box_invariants"]
    delta = (
        alpha[0] * alpha[1] * boxes[0]
        + alpha[1] * alpha[2] * boxes[1]
        + alpha[2] * alpha[0] * boxes[2]
    )
    if delta != _fraction(fixture["Delta"], "Delta"):
        raise ValueError("independent Delta replay failed")

    expected_coefficients = [
        Fraction(math.factorial(3 - pair_count), 6 * 2**pair_count)
        for pair_count in range(4)
    ]
    declared_coefficients = [
        _fraction(row, "Wick coefficient")
        for row in payload["parametric_formula"][
            "Wick_coefficients_after_Feynman_and_trace_log"
        ]
    ]
    if declared_coefficients != expected_coefficients:
        raise ValueError("Feynman/Wick/trace-log coefficient drifted")
    if _fraction(
        payload["parametric_formula"]["physical_trace_log_multiplier"],
        "trace-log multiplier",
    ) != Fraction(1, 6):
        raise ValueError("bosonic n=3 trace-log multiplier drifted")

    alpha_weight = alpha[0] * alpha[1] * alpha[2]
    total = Fraction(0)
    for pair_count, row in enumerate(fixture["wick_rows"]):
        if (
            row["loop_metric_pair_count"] != pair_count
            or row["homogeneous_loop_degree"] != 2 * pair_count
        ):
            raise ValueError("Wick row grading drifted")
        raw = _fraction(row["raw_wick_contraction"], "raw Wick contraction")
        coefficient = _fraction(
            row["integrated_coefficient_after_physical_trace_log"],
            "integrated Wick coefficient",
        )
        contribution = alpha_weight * coefficient * delta**pair_count * raw
        if contribution != _fraction(
            row["common_Delta_minus4_numerator_contribution"],
            "numerator contribution",
        ):
            raise ValueError("independent Wick contribution replay failed")
        total += contribution
    if total != _fraction(
        fixture["common_Delta_minus4_numerator"], "common numerator"
    ):
        raise ValueError("common numerator sum drifted")
    if total / delta**4 != _fraction(
        fixture["kernel_without_(4pi)^-2"], "kernel value"
    ):
        raise ValueError("physical triangle kernel quotient drifted")
    if total == 0 or fixture["nonzero"] is not True:
        raise ValueError("physical triangle fixture lost its nonzero witness")


def verify(
    payload: dict[str, Any] | None = None, *, reproduce: bool = True
) -> dict[str, Any]:
    stored = json.loads(OUTPUT.read_text()) if payload is None else payload
    validate(stored)
    if reproduce and stored != build():
        raise ValueError("physical Hessian n=3 fixture does not reproduce")
    dependencies = _check_dependencies(stored)
    _check_source_rows(stored, dependencies["physical_H1"])
    _check_external_geometry(stored["exact_interior_fixture"])
    _check_parametric_arithmetic(stored)
    fixture = stored["exact_interior_fixture"]
    if (
        fixture["formal_adjoint_check"]["completed_vertex_defect_count"] != 0
        or fixture["formal_adjoint_check"]["uncompleted_seed_defect_count"] <= 0
    ):
        raise ValueError("formal-adjoint negative control drifted")
    print("physical Hessian n=3 triangle fixture independent verification: PASS")
    return stored


if __name__ == "__main__":
    verify()
