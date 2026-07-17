#!/usr/bin/env python3
"""Solve the global detector-rod stress against the retained Berger q1."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
import sympy as sp
from sympy import QQ
from sympy.polys.matrices import DomainMatrix

from closed_universe_observers import generate_berger_global_detector_rods as rods


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
GLOBAL_RODS = PACKAGE / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json"
RETAINED_Q1 = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
SCHEMA = PACKAGE / "schema/berger-global-rod-q1-solvability-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_GLOBAL_ROD_Q1_SOURCE_SECTOR_SOLVABILITY.json"
REPORT = PACKAGE / "reports/berger-global-rod-q1-solvability.md"
SOURCE_FILES = {
    "producer": Path(__file__),
    "independent_verifier": PACKAGE / "verify_berger_global_rod_q1_solvability.py",
    "tests": PACKAGE / "tests/test_berger_global_rod_q1_solvability.py",
    "report": REPORT,
    "certificate_schema": SCHEMA,
}

X = rods.X
C = rods.C
OMEGA = rods.OMEGA
I = sp.I
PAIRS = tuple((left, right) for left in range(4) for right in range(left, 4))
CROSS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
BASIS = (
    sp.S.One,
    X[0] ** 2 - X[3] ** 2,
    X[1] ** 2 - X[3] ** 2,
    X[2] ** 2 - X[3] ** 2,
    *(X[left] * X[right] for left, right in CROSS),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reduce_quadratic(value: sp.Expr) -> sp.Matrix:
    """Reduce degree-zero/two polynomials modulo sum x_mu^2=1."""

    output = sp.zeros(10, 1)
    for monomial, coefficient in sp.Poly(sp.expand(value), *X).terms():
        degree = sum(monomial)
        if degree == 0:
            output[0] += coefficient
            continue
        if degree != 2:
            raise AssertionError(f"rod source left the quadratic harmonic sector: {monomial}")
        indices = [axis for axis, count in enumerate(monomial) for _ in range(count)]
        left, right = indices
        if left != right:
            output[4 + CROSS.index((left, right))] += coefficient
            continue
        # x3^2=(1-d0-d1-d2)/4 and xi^2=x3^2+di for i<3.
        output[0] += coefficient / 4
        for axis in range(3):
            output[1 + axis] -= coefficient / 4
        if left < 3:
            output[1 + left] += coefficient
    return output.applyfunc(sp.simplify)


@lru_cache(maxsize=1)
def _spatial_matrices() -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    return tuple(
        sp.Matrix.hstack(*[
            _reduce_quadratic(rods._frame_derivative(basis, axis)) for basis in BASIS
        ])
        for axis in range(3)
    )


def _operator_matrix(record: dict[str, Any], frequency: sp.Expr) -> sp.Matrix:
    spatial = _spatial_matrices()
    rows, columns = record["shape"]
    blocks = [[sp.zeros(10) for _ in range(columns)] for _ in range(rows)]
    for row, column, terms in record["entries"]:
        for exponents, raw_coefficient in terms:
            coefficient = sp.sympify(
                raw_coefficient, locals={"u": C, "v": 1 / C, "alpha_B": 5}
            ) * (I * frequency) ** exponents[0]
            blocks[row][column] += coefficient * (
                spatial[0] ** exponents[1]
                * spatial[1] ** exponents[2]
                * spatial[2] ** exponents[3]
            )
    return sp.Matrix.vstack(*[sp.Matrix.hstack(*row) for row in blocks])


def _derivative_product(derivatives: list[sp.Expr], left: int, right: int, harmonic: str) -> sp.Expr:
    if harmonic == "zero":
        if left == 0 and right == 0:
            return OMEGA**2 * derivatives[0] ** 2 / 2
        if (left == 0) != (right == 0):
            return sp.S.Zero
        return derivatives[left] * derivatives[right] / 2
    if left == 0 and right == 0:
        return -OMEGA**2 * derivatives[0] ** 2 / 4
    if left == 0:
        return I * OMEGA * derivatives[0] * derivatives[right] / 4
    if right == 0:
        return I * OMEGA * derivatives[left] * derivatives[0] / 4
    return derivatives[left] * derivatives[right] / 4


def _source_at_phase(phase: sp.Expr, harmonic: str) -> sp.Matrix:
    eta = (-1, 1, 1, 1)
    stress = [[sp.S.Zero for _ in range(4)] for _ in range(4)]
    for profile in rods._profiles(phase):
        derivatives = [profile] + [rods._frame_derivative(profile, axis) for axis in range(3)]
        norm = sum(
            eta[axis] * _derivative_product(derivatives, axis, axis, harmonic)
            for axis in range(4)
        )
        for left in range(4):
            for right in range(4):
                stress[left][right] += _derivative_product(derivatives, left, right, harmonic)
                if left == right:
                    stress[left][right] -= eta[left] * norm / 2
    # The retained canonical rows use T^{ab}, hence eta_a eta_b T_ab.
    return sp.Matrix.vstack(*[
        (2 if left != right else 1)
        * eta[left]
        * eta[right]
        * _reduce_quadratic(stress[left][right])
        for left, right in PAIRS
    ]).applyfunc(sp.simplify)


@lru_cache(maxsize=None)
def _source_basis(harmonic: str) -> sp.Matrix:
    c2 = _source_at_phase(sp.S.Zero, harmonic)
    s2 = _source_at_phase(sp.pi / 2, harmonic)
    # If S(z)=cos(z)^2 A+sin(z)^2 B+cos(z)sin(z) C, then
    # C=2*(S(pi/4)-(A+B)/2).  Retain the normalized coefficient column so
    # physical detector phases synthesize without a hidden factor of two.
    cs = 2 * (_source_at_phase(sp.pi / 4, harmonic) - (c2 + s2) / 2)
    return sp.Matrix.hstack(c2, s2, cs).applyfunc(sp.simplify)


def _canonical_primitives(operator: sp.Matrix, sources: sp.Matrix) -> tuple[int, list[int], sp.Matrix]:
    """Solve H Phi=-source with all free coordinates fixed to zero."""

    field = QQ.algebraic_field(sp.sqrt(10), sp.sqrt(58), I)
    domain_matrix = DomainMatrix.from_Matrix(operator.row_join(-sources)).convert_to(field)
    domain_reduced, pivots = domain_matrix.rref()
    reduced = domain_reduced.to_Matrix()
    operator_pivots = [pivot for pivot in pivots if pivot < operator.cols]
    if len(operator_pivots) != len(pivots):
        raise AssertionError("rod source has a nonzero compact cokernel projection")
    primitives = sp.zeros(operator.cols, sources.cols)
    for row, pivot in enumerate(operator_pivots):
        for column in range(sources.cols):
            primitives[pivot, column] = reduced[row, operator.cols + column]
    if (operator * primitives + sources).applyfunc(sp.simplify) != sp.zeros(operator.rows, sources.cols):
        raise AssertionError("canonical rod backreaction primitive failed replay")
    return len(operator_pivots), operator_pivots, primitives


def _sparse_columns(matrix: sp.Matrix) -> list[list[list[Any]]]:
    return [
        [[row, sp.sstr(sp.factor(matrix[row, column]))] for row in range(matrix.rows) if matrix[row, column] != 0]
        for column in range(matrix.cols)
    ]


@lru_cache(maxsize=1)
def _exact_blocks() -> dict[str, Any]:
    q1 = json.loads(RETAINED_Q1.read_text())["q1_blocks"]
    result: dict[str, Any] = {}
    for harmonic, frequency_text, frequency in (
        ("zero", "0", sp.S.Zero),
        ("positive", "sqrt(58)/3", 2 * OMEGA),
    ):
        operator = _operator_matrix(q1["H_retained"], frequency)
        noether = _operator_matrix(q1["minus_K_spatial_sharp"], frequency)
        sources = _source_basis("zero" if harmonic == "zero" else "positive")
        closure = (noether * sources).applyfunc(sp.simplify)
        if closure != sp.zeros(30, 3):
            raise AssertionError(f"rod source Noether closure failed in {harmonic} block")
        rank, pivots, primitives = _canonical_primitives(operator, sources)
        result[harmonic] = {
            "frequency": frequency_text,
            "operator_shape": [100, 100],
            "source_basis_shape": [100, 3],
            "phase_polynomial_basis": ["cos(z)^2", "sin(z)^2", "cos(z)*sin(z)"],
            "operator_rank": rank,
            # The displayed exact primitives prove that adjoining any source
            # column does not increase rank.
            "augmented_ranks": [rank, rank, rank],
            "operator_pivot_columns": pivots,
            "noether_defect_nonzero_count": sum(value != 0 for value in closure),
            "source_nonzero_counts": [sum(value != 0 for value in sources[:, column]) for column in range(3)],
            "primitive_nonzero_counts": [sum(value != 0 for value in primitives[:, column]) for column in range(3)],
            "canonical_primitives_sparse": _sparse_columns(primitives),
            "primitive_residual_nonzero_count": 0,
        }
    return result


def build() -> dict[str, Any]:
    global_rods = json.loads(GLOBAL_RODS.read_text())
    retained = json.loads(RETAINED_Q1.read_text())
    if global_rods["flags"]["GLOBAL_COMPACT_ROD_Q0_FORMULA_EXPORTED"] is not True:
        raise AssertionError("global rod source is unavailable")
    if retained["flags"]["BERGER_RETAINED_MINIMAL_OPERATOR"] is not True:
        raise AssertionError("retained Berger q1 is unavailable")
    blocks = _exact_blocks()
    payload = {
        "schema": "closed-universe-berger-global-rod-q1-solvability-v1",
        "result_id": "BERGER_GLOBAL_ROD_Q1_SOURCE_SECTOR_SOLVABILITY",
        "setting_id": "compact_positive_berger_clock_fixed_coupling_probe_apparatus",
        "claim_status": "GLOBAL_ROD_STRESS_EXACTLY_Q1_TRIVIAL_THROUGH_SECOND_ORDER",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            "global_rods": {"path": str(GLOBAL_RODS.relative_to(ROOT)), "sha256": _sha256(GLOBAL_RODS), "result_id": global_rods["result_id"]},
            "retained_q1": {"path": str(RETAINED_Q1.relative_to(ROOT)), "sha256": _sha256(RETAINED_Q1), "result_id": retained["result_id"]},
        },
        "finite_sector": {
            "spatial_basis": ["1", "x0^2-x3^2", "x1^2-x3^2", "x2^2-x3^2", "x0*x1", "x0*x2", "x0*x3", "x1*x2", "x1*x3", "x2*x3"],
            "spatial_harmonics": ["j=0", "j=1"],
            "temporal_frequencies": ["0", "+sqrt(58)/3", "-sqrt(58)/3"],
            "phase_span_argument": "the source is quadratic in cos(z),sin(z); the three displayed phase-polynomial columns span every detector Hopf phase",
            "negative_frequency_argument": "the negative-frequency block is the complex conjugate of the positive-frequency block",
            "two_detector_argument": "each detector source is in im(q1); arbitrary time shifts multiply nonzero-frequency columns by phases, and linearity puts their sum in im(q1)",
        },
        "exact_blocks": blocks,
        "second_order_equation": {
            "equation": "H_retained Phi2=-q0^rod",
            "source_convention": "q0_(h_plus_ab)=(2-delta_ab) T_rod^{ab}",
            "verdict": "EXACTLY_SOLVABLE_ON_COMPLETE_GLOBAL_ROD_SOURCE_SECTOR",
            "cokernel_projection": "ZERO",
            "witness": "the sparse canonical primitives in exact_blocks replay with zero residual",
        },
        "flags": {
            "GLOBAL_ROD_SOURCE_Q1_CLOSED": True,
            "GLOBAL_ROD_SOURCE_COKERNEL_PROJECTION_ZERO": True,
            "GLOBAL_ROD_SECOND_ORDER_PRIMITIVES_EXPORTED": True,
            "GLOBAL_ROD_BACKREACTION_SOLVABLE_THROUGH_ORDER_EPSILON_R_SQUARED": True,
            "FULL_NONLINEAR_BACKREACTED_ROD_BRANCH_CERTIFIED": False,
            "84_ROW_INTERACTING_COMPLEX_CERTIFIED": False,
            "84_ROW_CAUSAL_GREEN_HOMOTOPY_CERTIFIED": False,
            "APPARATUS_RECOIL_INCLUDED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "IMPORT_THE_SIX_RODS_INTO_THE_84_ROW_Q1_Q2_Q3_COMPLEX_AND_TEST_NONLINEAR_OBSERVER_MORPHISM",
        "not_established": [
            "a formal all-orders backreacted rod branch",
            "the 84-row nilpotent cyclic interacting complex",
            "a retarded Green homotopy after adjoining six rods and memories",
            "apparatus recoil or nonlinear persistence of the rank-two detector map",
            "a quantum observer algebra or state",
        ],
        "provenance": {
            "source_manifest": [
                {"role": role, "path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for role, path in SOURCE_FILES.items()
            ]
        },
        "claim_boundary": "This exact LOCAL-ALGEBRAIC/REDUCED-MODE calculation evaluates the complete global six-rod stress sector against the certified retained Berger metric Hessian. Exact sparse primitives solve H_retained Phi2=-q0^rod for the full j=0,1 and temporal 0,+-sqrt(58)/3 source support, so the rod stress has no second-order compact Taub obstruction. It does not construct an all-orders branch, the corrected 84-row interacting or causal complex, apparatus recoil, nonlinear observer-map consistency, or any quantum object.",
    }
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered:
            raise AssertionError("global rod q1 solvability certificate is stale")
    else:
        CERTIFICATE.write_text(rendered)
    print("BERGER_GLOBAL_ROD_Q1_SOURCE_SECTOR_SOLVABILITY generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
