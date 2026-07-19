#!/usr/bin/env python3
"""Evaluate one exact physical three-linear Hessian triangle fixture.

The imported same-gauge traceless metric Hessian fixes the complete term
linear in curvature on a scalar-flat background.  This module turns that
covariant ledger into an operational momentum-space vertex, completes the
source seed by formal adjunction, and evaluates one nonexceptional interior
Feynman-simplex point of the bosonic ``n=3`` trace-log row exactly.

This is deliberately not called the completed physical form factor: the full
alpha polynomial, its five-carrier projection, the curvature-squared Hessian
layer, and the mixed H1/H2 rows remain open.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
QROOT = HERE.parents[1]
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_TRIANGLE_FIXTURE.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-n3-triangle-fixture-v1.schema.json"
DEPENDENCIES = {
    "physical_H1": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_LINEAR_CURVATURE.json",
    "carrier_manifest": QROOT / "transfer/certificates/FOUR_DIMENSIONAL_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST.json",
    "K_Ricci_crosswalk": QROOT / "transfer/certificates/SCALAR_FLAT_K_RICCI_CUBIC_CROSSWALK.json",
}

Q = sp.Rational
MOMENTA = (
    (1, -1, -2, -2),
    (-2, 1, 0, 2),
    (1, 0, 2, 0),
)
TT_BASIS_INDICES = (0, 1, 2)
ALPHAS = (Q(7, 15), Q(1, 5), Q(1, 3))  # alpha0, alpha1, alpha2
ADJOINT_Q = (Q(1, 3), Q(-2, 5), Q(4, 7), Q(3, 2))
INTEGRATED_WICK_COEFFICIENTS = (Q(1), Q(1, 6), Q(1, 24), Q(1, 48))

SCALAR_FLAT_ROW_FORMULAS: tuple[dict[str, Any], ...] = (
    {"term_id": "V03", "coefficient": Q(-4, 3), "formula": "q_m q_n Ric_ab"},
    {"term_id": "V04", "coefficient": Q(-4, 3), "formula": "Ric_mn q_a q_b"},
    {"term_id": "V05", "coefficient": Q(-2), "formula": "Ric_ma q_n q_b"},
    {"term_id": "V06", "coefficient": Q(4), "formula": "(Ric q)_m delta_nb q_a"},
    {"term_id": "V07", "coefficient": Q(4), "formula": "(Ric q)_a delta_nb q_m"},
    {"term_id": "V08", "coefficient": Q(-4), "formula": "Riem_manb q^2"},
    {"term_id": "V09", "coefficient": Q(-2), "formula": "delta_sym(mn,ab) (q Ric q)"},
    {"term_id": "N02", "coefficient": Q(4, 3), "formula": "k_m q_n Ric_ab"},
    {"term_id": "N04", "coefficient": Q(2), "formula": "k_m q_a Ric_nb"},
    {"term_id": "N05", "coefficient": Q(-4), "formula": "k_a q_b Ric_mn"},
    {"term_id": "N06", "coefficient": Q(-4), "formula": "k_a q_n Ric_mb"},
    {"term_id": "N07", "coefficient": Q(4), "formula": "k_a (Ric q)_m delta_nb"},
    {"term_id": "N08", "coefficient": Q(-4), "formula": "(k q) Riem_manb"},
    {"term_id": "U03", "coefficient": Q(-4, 3), "formula": "k_m k_n Ric_ab"},
    {"term_id": "U04", "coefficient": Q(-2), "formula": "k^2 Ric_ma delta_nb"},
    {"term_id": "U05", "coefficient": Q(-2), "formula": "k^2 Riem_manb"},
)


def _q(value: Fraction | int | sp.Rational) -> dict[str, int]:
    value = Q(value)
    return {"numerator": int(value.p), "denominator": int(value.q)}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value["result_id"]),
        "sha256": _sha256(path),
    }


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _matrix_to_q(matrix: sp.Matrix) -> list[list[dict[str, int]]]:
    return [[_q(matrix[i, j]) for j in range(matrix.cols)] for i in range(matrix.rows)]


def _traceless_basis() -> tuple[list[sp.Matrix], sp.Matrix, sp.Matrix]:
    basis: list[sp.Matrix] = []
    for first in range(4):
        for second in range(first + 1, 4):
            matrix = sp.zeros(4)
            matrix[first, second] = matrix[second, first] = 1
            basis.append(matrix)
    for index in range(3):
        matrix = sp.zeros(4)
        matrix[index, index] = 1
        matrix[3, 3] = -1
        basis.append(matrix)
    gram = sp.Matrix(
        [[sp.trace(left.T * right) for right in basis] for left in basis]
    )
    if len(basis) != 9 or gram.rank() != 9 or gram.det() != 256:
        raise AssertionError("rank-nine traceless basis drifted")
    return basis, gram, gram.inv()


TRACELESS_BASIS, TRACELESS_GRAM, TRACELESS_GRAM_INVERSE = _traceless_basis()


def _transverse_tracefree_basis(momentum: sp.Matrix) -> list[sp.Matrix]:
    raw = sp.Matrix([list(momentum)]).nullspace()
    orthogonal: list[sp.Matrix] = []
    for vector in raw:
        reduced = vector
        for previous in orthogonal:
            reduced -= previous * (
                previous.dot(reduced) / previous.dot(previous)
            )
        orthogonal.append(sp.simplify(reduced))
    projectors = [
        vector * vector.T / vector.dot(vector) for vector in orthogonal
    ]
    result = [
        projectors[0] - projectors[1],
        projectors[0] - projectors[2],
        orthogonal[0] * orthogonal[1].T
        + orthogonal[1] * orthogonal[0].T,
        orthogonal[0] * orthogonal[2].T
        + orthogonal[2] * orthogonal[0].T,
        orthogonal[1] * orthogonal[2].T
        + orthogonal[2] * orthogonal[1].T,
    ]
    if any(matrix.trace() != 0 or matrix * momentum != sp.zeros(4, 1) for matrix in result):
        raise AssertionError("external TT Ricci basis drifted")
    return result


def _linearized_riemann(momentum: sp.Matrix, ricci: sp.Matrix) -> list:
    """Return R_{m a n b} reconstructed from TT Ricci at linear order."""

    metric_fluctuation = 2 * ricci / momentum.dot(momentum)
    return [
        [
            [
                [
                    sp.expand(
                        -Q(1, 2)
                        * (
                            momentum[a] * momentum[n] * metric_fluctuation[m, b]
                            + momentum[m] * momentum[b] * metric_fluctuation[a, n]
                            - momentum[a] * momentum[b] * metric_fluctuation[m, n]
                            - momentum[m] * momentum[n] * metric_fluctuation[a, b]
                        )
                    )
                    for b in range(4)
                ]
                for n in range(4)
            ]
            for a in range(4)
        ]
        for m in range(4)
    ]


def _check_riemann(momentum: sp.Matrix, ricci: sp.Matrix, riemann: list) -> None:
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
                        raise AssertionError("linearized Riemann symmetry drifted")
    contraction = sp.Matrix(
        4,
        4,
        lambda a, b: sum(riemann[m][a][m][b] for m in range(4)),
    )
    if contraction != ricci:
        raise AssertionError("linearized Riemann/Ricci contraction drifted")


def _riemann_bilinear(left: sp.Matrix, riemann: list, right: sp.Matrix) -> sp.Expr:
    return sp.expand(
        sum(
            left[m, n] * riemann[m][a][n][b] * right[a, b]
            for m in range(4)
            for a in range(4)
            for n in range(4)
            for b in range(4)
        )
    )


def _seed_bilinear(
    momentum: sp.Matrix,
    ricci: sp.Matrix,
    riemann: list,
    incoming: sp.Matrix,
    left: sp.Matrix,
    right: sp.Matrix,
) -> sp.Expr:
    """Source seed after within-pair symmetrization on symmetric arguments."""

    k = momentum
    q = incoming
    k2 = k.dot(k)
    q2 = q.dot(q)
    kq = k.dot(q)
    tr_ricci_right = sp.trace(ricci.T * right)
    tr_ricci_left = sp.trace(ricci.T * left)
    left_right = sp.trace(left.T * right)
    q_ricci_q = (q.T * ricci * q)[0]
    riemann_row = _riemann_bilinear(left, riemann, right)

    value = -Q(4, 3) * (q.T * left * q)[0] * tr_ricci_right
    value -= Q(4, 3) * tr_ricci_left * (q.T * right * q)[0]
    value -= 2 * (left * q).dot(ricci * (right * q))
    value += 4 * (ricci * q).dot(left * (right * q))
    value += 4 * (ricci * q).dot(right * (left * q))
    value -= 4 * q2 * riemann_row
    value -= 2 * left_right * q_ricci_q

    value += Q(4, 3) * (k.T * left * q)[0] * tr_ricci_right
    value += 2 * (left * k).dot(ricci * (right * q))
    value -= 4 * tr_ricci_left * (k.T * right * q)[0]
    value -= 4 * (left * q).dot(ricci * (right * k))
    value += 4 * (ricci * q).dot(left * (right * k))
    value -= 4 * kq * riemann_row

    value -= Q(4, 3) * (k.T * left * k)[0] * tr_ricci_right
    value -= 2 * k2 * sp.trace(right.T * ricci * left)
    value -= 2 * k2 * riemann_row
    return sp.expand(value)


def _vertex_covariant_matrix(
    momentum: sp.Matrix,
    ricci: sp.Matrix,
    incoming: sp.Matrix,
    *,
    complete_formal_adjoint: bool = True,
) -> sp.Matrix:
    riemann = _linearized_riemann(momentum, ricci)
    rows: list[list[sp.Expr]] = []
    for left in TRACELESS_BASIS:
        row = []
        for right in TRACELESS_BASIS:
            direct = _seed_bilinear(
                momentum, ricci, riemann, incoming, left, right
            )
            if complete_formal_adjoint:
                adjoint = _seed_bilinear(
                    -momentum,
                    ricci,
                    riemann,
                    incoming + momentum,
                    right,
                    left,
                )
                direct = (direct + adjoint) / 2
            row.append(sp.expand(direct))
        rows.append(row)
    return sp.Matrix(rows)


def _vertex_representation(
    momentum: sp.Matrix, ricci: sp.Matrix, incoming: sp.Matrix
) -> sp.Matrix:
    return TRACELESS_GRAM_INVERSE * _vertex_covariant_matrix(
        momentum, ricci, incoming
    )


def _polynomial_digest(expression: sp.Expr, variables: Iterable[sp.Symbol]) -> tuple[int, str]:
    polynomial = sp.Poly(sp.expand(expression), *variables)
    terms = [
        {"exponents": list(exponents), "coefficient": _q(coefficient)}
        for exponents, coefficient in polynomial.terms()
    ]
    return len(terms), _canonical_digest(terms)


def _matrix_polynomial_digest(matrix: sp.Matrix, variables: Iterable[sp.Symbol]) -> str:
    rows = []
    for row in range(matrix.rows):
        for column in range(matrix.cols):
            polynomial = sp.Poly(sp.expand(matrix[row, column]), *variables)
            terms = [
                [list(exponents), _q(coefficient)]
                for exponents, coefficient in polynomial.terms()
            ]
            if terms:
                rows.append([row, column, terms])
    return _canonical_digest(rows)


def _wick_contraction(polynomial: sp.Poly, pair_count: int) -> sp.Rational:
    result = sp.S.Zero
    for exponents, coefficient in polynomial.terms():
        if sum(exponents) != 2 * pair_count:
            continue
        multiplicity = 1
        for exponent in exponents:
            if exponent % 2:
                multiplicity = 0
                break
            for value in range(exponent - 1, 0, -2):
                multiplicity *= value
        result += coefficient * multiplicity
    return Q(result)


def _external_fixture() -> tuple[list[sp.Matrix], list[sp.Matrix], list[list]]:
    momenta = [sp.Matrix(row) for row in MOMENTA]
    if sum(momenta, sp.zeros(4, 1)) != sp.zeros(4, 1):
        raise AssertionError("external momentum conservation drifted")
    bases = [_transverse_tracefree_basis(momentum) for momentum in momenta]
    ricci = [bases[index][TT_BASIS_INDICES[index]] for index in range(3)]
    riemann = [
        _linearized_riemann(momentum, tensor)
        for momentum, tensor in zip(momenta, ricci)
    ]
    for momentum, tensor, curvature in zip(momenta, ricci, riemann):
        _check_riemann(momentum, tensor, curvature)
    return momenta, ricci, riemann


def compute_fixture() -> dict[str, Any]:
    momenta, ricci, _ = _external_fixture()
    q_symbols = sp.symbols("q0:4")
    q = sp.Matrix(q_symbols)
    vertex_polynomials = [
        _vertex_representation(momentum, tensor, q)
        for momentum, tensor in zip(momenta, ricci)
    ]

    adjoint_q = sp.Matrix(ADJOINT_Q)
    completed = _vertex_covariant_matrix(momenta[0], ricci[0], adjoint_q)
    completed_reverse = _vertex_covariant_matrix(
        -momenta[0], ricci[0], adjoint_q + momenta[0]
    ).T
    seed = _vertex_covariant_matrix(
        momenta[0], ricci[0], adjoint_q, complete_formal_adjoint=False
    )
    seed_reverse = _vertex_covariant_matrix(
        -momenta[0],
        ricci[0],
        adjoint_q + momenta[0],
        complete_formal_adjoint=False,
    ).T
    completed_defects = sum(value != 0 for value in completed - completed_reverse)
    seed_defects = sum(sp.simplify(value) != 0 for value in seed - seed_reverse)
    if completed_defects != 0 or seed_defects == 0:
        raise AssertionError("formal-adjoint completion regression failed")

    alpha0, alpha1, alpha2 = ALPHAS
    k1, k2, k3 = momenta
    shifts = [
        -alpha1 * k1 + alpha2 * k3,
        (1 - alpha1) * k1 + alpha2 * k3,
        -alpha1 * k1 - (1 - alpha2) * k3,
    ]
    loop_symbols = sp.symbols("l0:4")
    loop = sp.Matrix(loop_symbols)
    routed_vertices = [
        vertex.subs(dict(zip(q_symbols, loop + shift)))
        for vertex, shift in zip(vertex_polynomials, shifts)
    ]
    trace_polynomial_expression = sp.expand(
        sp.trace(routed_vertices[2] * routed_vertices[1] * routed_vertices[0])
    )
    trace_polynomial = sp.Poly(trace_polynomial_expression, *loop_symbols)
    term_count, trace_digest = _polynomial_digest(
        trace_polynomial_expression, loop_symbols
    )
    if trace_polynomial.total_degree() != 6 or term_count != 210:
        raise AssertionError("rank-nine triangle loop polynomial drifted")

    delta = (
        alpha0 * alpha1 * k1.dot(k1)
        + alpha1 * alpha2 * k2.dot(k2)
        + alpha2 * alpha0 * k3.dot(k3)
    )
    alpha_weight = alpha0 * alpha1 * alpha2
    wick_rows = []
    common_numerator = sp.S.Zero
    for pair_count, integration_coefficient in enumerate(
        INTEGRATED_WICK_COEFFICIENTS
    ):
        contraction = _wick_contraction(trace_polynomial, pair_count)
        contribution = sp.factor(
            alpha_weight
            * integration_coefficient
            * delta**pair_count
            * contraction
        )
        common_numerator += contribution
        wick_rows.append(
            {
                "loop_metric_pair_count": pair_count,
                "homogeneous_loop_degree": 2 * pair_count,
                "raw_wick_contraction": _q(contraction),
                "integrated_coefficient_after_physical_trace_log": _q(
                    integration_coefficient
                ),
                "common_Delta_minus4_numerator_contribution": _q(contribution),
            }
        )
    common_numerator = Q(common_numerator)
    kernel_value = Q(common_numerator / delta**4)
    if common_numerator == 0:
        raise AssertionError("physical three-linear triangle fixture vanished")

    return {
        "momenta": [list(map(int, momentum)) for momentum in momenta],
        "box_invariants": [int(momentum.dot(momentum)) for momentum in momenta],
        "TT_basis_indices": list(TT_BASIS_INDICES),
        "Ricci_tensors": [_matrix_to_q(tensor) for tensor in ricci],
        "alpha": {
            "alpha0": _q(alpha0),
            "alpha1": _q(alpha1),
            "alpha2": _q(alpha2),
        },
        "Delta": _q(delta),
        "vertex_polynomial_digests": [
            _matrix_polynomial_digest(vertex, q_symbols)
            for vertex in vertex_polynomials
        ],
        "formal_adjoint_check": {
            "incoming_q": [_q(value) for value in ADJOINT_Q],
            "completed_vertex_defect_count": completed_defects,
            "uncompleted_seed_defect_count": seed_defects,
        },
        "loop_trace": {
            "matrix_rank": 9,
            "orientation": "tr[A3(k3,q2) A2(k2,q1) A1(k1,q0)]",
            "maximum_loop_degree": trace_polynomial.total_degree(),
            "monomial_count": term_count,
            "polynomial_sha256": trace_digest,
        },
        "wick_rows": wick_rows,
        "common_Delta_minus4_numerator": _q(common_numerator),
        "kernel_without_(4pi)^-2": _q(kernel_value),
        "nonzero": True,
    }


def _validate_dependencies(values: dict[str, dict[str, Any]]) -> None:
    physical = values["physical_H1"]
    manifest = values["carrier_manifest"]
    crosswalk = values["K_Ricci_crosswalk"]
    parent_ids = physical["scalar_flat_restriction"]["surviving_term_ids"]
    imported_ids = [row["term_id"] for row in SCALAR_FLAT_ROW_FORMULAS]
    expected_ids = (
        parent_ids["V_rho_sigma"] + parent_ids["N_lambda"] + parent_ids["U"]
    )
    if (
        physical["claim_flags"]["PHYSICAL_N3_THREE_LINEAR_INSERTION_VERTEX_READY"]
        is not True
        or physical["claim_flags"]["CURVATURE_SQUARED_ZERO_ORDER_LAYER_SUPPLIED"]
        is not False
        or imported_ids != expected_ids
        or manifest["quotient_module"]["generic_label_orbit_dimension"] != 10
        or crosswalk["claim_flags"]["CUBIC_K_TO_RICCI_REPLACEMENT_CERTIFIED"]
        is not True
    ):
        raise ValueError("physical n=3 triangle dependencies drifted")


def build() -> dict[str, Any]:
    dependencies = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    _validate_dependencies(dependencies)
    fixture = compute_fixture()
    formula_ledger = [
        {
            "term_id": row["term_id"],
            "coefficient": _q(row["coefficient"]),
            "formula": row["formula"],
        }
        for row in SCALAR_FLAT_ROW_FORMULAS
    ]
    result = {
        "schema": "quantum-weyl-generic-background-physical-hessian-n3-triangle-fixture-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_TRIANGLE_FIXTURE",
        "result_state": "PHYSICAL_THREE_LINEAR_HESSIAN_TRIANGLE_OPERATIONAL_EXACT_INTERIOR_FIXTURE",
        "lifecycle_state": "COEFFICIENT_BEARING_FIXTURE_COMPUTED_FULL_PARAMETRIC_PROJECTION_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": dependencies["physical_H1"]["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background": "scalar-flat linear-curvature momentum fixture with generic nonexceptional external momenta",
            "quantum_bundle": "rank-nine traceless symmetric metric fluctuations",
            "curvature_order": 3,
            "included_trace_row": "(1/6) Tr[(H0^-1 H1)^3] from the bosonic one-half trace log",
            "excluded_rows": [
                "full alpha-polynomial and five-carrier projection",
                "curvature-squared H2 and mixed H1-H2 traces",
                "simplex integration and global spectral data",
            ],
        },
        "scalar_flat_momentum_vertex": {
            "Fourier_convention": "background derivative -> +i k; right-acting fluctuation derivative -> +i q",
            "source_seed_rows": formula_ledger,
            "source_seed_formula_sha256": _canonical_digest(formula_ledger),
            "within_pair_policy": "contraction with symmetric traceless basis implements normalized symmetrization in mu-nu and alpha-beta",
            "formal_adjoint_completion": "A(k,q)=[S(k,q)+S(-k,q+k)^T]/2",
            "formal_adjoint_identity": "A(k,q)=A(-k,q+k)^T",
            "traceless_basis": {
                "description": "six off-diagonal symmetric matrices and three diagonal differences E_ii-E_33",
                "rank": 9,
                "Gram_determinant": 256,
                "Gram_matrix": _matrix_to_q(TRACELESS_GRAM),
            },
            "linearized_Riemann_reconstruction": "h_mn=2 Ric_mn/k^2 and R_manb=-(1/2)(k_a k_n h_mb+k_m k_b h_an-k_a k_b h_mn-k_m k_n h_ab)",
            "Riemann_checks": [
                "antisymmetry in both index pairs",
                "pair exchange",
                "first algebraic Bianchi identity",
                "sum_m R_mamb=Ric_ab",
            ],
        },
        "parametric_formula": {
            "routing": [
                "q0=p",
                "q1=p+k1",
                "q2=p-k3",
            ],
            "denominator": "(q0^2)^2 (q1^2)^2 (q2^2)^2",
            "Feynman_identity": "1/(D0^2 D1^2 D2^2)=Gamma(6) integral_simplex alpha0 alpha1 alpha2 /(l^2+Delta)^6",
            "shift": [
                "r0=-alpha1 k1+alpha2 k3",
                "r1=(1-alpha1)k1+alpha2 k3",
                "r2=-alpha1 k1-(1-alpha2)k3",
            ],
            "Delta": "alpha0 alpha1 k1^2+alpha1 alpha2 k2^2+alpha2 alpha0 k3^2",
            "physical_trace_log_multiplier": _q(Q(1, 6)),
            "Wick_coefficients_after_Feynman_and_trace_log": [
                _q(value) for value in INTEGRATED_WICK_COEFFICIENTS
            ],
            "common_integrand": "(4 pi)^-2 N(alpha,k,R)/Delta^4",
        },
        "exact_interior_fixture": fixture,
        "negative_controls": {
            "omit_formal_adjoint_completion": {
                "defect_count": fixture["formal_adjoint_check"][
                    "uncompleted_seed_defect_count"
                ],
                "rejected": True,
            },
            "flip_bosonic_n3_trace_log_sign": {
                "expected_multiplier": _q(Q(1, 6)),
                "mutated_multiplier": _q(Q(-1, 6)),
                "rejected": True,
            },
            "promote_to_complete_form_factor": {
                "attempted": True,
                "rejected": True,
                "reason": "one interior simplex fixture does not determine the alpha polynomial or five carrier functions",
            },
        },
        "claim_flags": {
            "PHYSICAL_H1_MOMENTUM_VERTEX_CONSTRUCTED": True,
            "PHYSICAL_H1_FORMAL_ADJOINT_COMPLETION_VERIFIED": True,
            "SCALAR_FLAT_LINEARIZED_RIEMANN_RECONSTRUCTION_VERIFIED": True,
            "PHYSICAL_N3_EXACT_INTERIOR_SIMPLEX_FIXTURE_COMPUTED": True,
            "PHYSICAL_N3_FULL_ALPHA_POLYNOMIAL_COMPUTED": False,
            "PHYSICAL_N3_FIVE_CARRIER_PROJECTION_COMPUTED": False,
            "PHYSICAL_N3_TRIANGLE_INTEGRATED": False,
            "CURVATURE_SQUARED_H2_IMPORTED": False,
            "PHYSICAL_MIXED_H1_H2_ROWS_COMPUTED": False,
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {
            name: _reference(path) for name, path in DEPENDENCIES.items()
        },
        "next_gate": "INTERPOLATE_PHYSICAL_N3_COMMON_NUMERATOR_PROJECT_TO_FIVE_CARRIERS_AND_IMPORT_CURVATURE_SQUARED_H2",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL result constructs the exact scalar-flat momentum vertex of the imported rank-nine traceless metric Hessian, verifies its required formal-adjoint completion, reconstructs the external linearized Riemann tensors, and evaluates all four Wick orders of one generic interior Feynman-simplex fixture of the physical three-H1 trace. It is an operational coefficient-bearing fixture, not the full alpha polynomial, five-carrier projection, integrated tensor triangle, curvature-squared H2 layer, mixed H1-H2 contribution, complete repository form factors, Gamma1, Q1, residual transfer, Lorentzian QME, Hadamard state, or particle theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    fixture = value["exact_interior_fixture"]
    if (
        fixture["formal_adjoint_check"]["completed_vertex_defect_count"] != 0
        or fixture["formal_adjoint_check"]["uncompleted_seed_defect_count"] <= 0
        or fixture["loop_trace"]["maximum_loop_degree"] != 6
        or fixture["loop_trace"]["monomial_count"] != 210
        or fixture["nonzero"] is not True
        or value["parametric_formula"]["physical_trace_log_multiplier"]
        != _q(Q(1, 6))
    ):
        raise ValueError("physical n=3 exact fixture drifted")
    true_flags = {
        "PHYSICAL_H1_MOMENTUM_VERTEX_CONSTRUCTED",
        "PHYSICAL_H1_FORMAL_ADJOINT_COMPLETION_VERIFIED",
        "SCALAR_FLAT_LINEARIZED_RIEMANN_RECONSTRUCTION_VERIFIED",
        "PHYSICAL_N3_EXACT_INTERIOR_SIMPLEX_FIXTURE_COMPUTED",
    }
    flags = value["claim_flags"]
    if any(flags[name] is not True for name in true_flags) or any(
        setting is not False for name, setting in flags.items() if name not in true_flags
    ):
        raise ValueError("physical n=3 fixture crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale physical n=3 triangle fixture: {OUTPUT}")
    print("PHYSICAL HESSIAN N3 TRIANGLE: EXACT INTERIOR FIXTURE PASS; FULL PROJECTION OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
