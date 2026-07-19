#!/usr/bin/env python3
"""Compare the physical three-H1 corners with the mixed H1-H2 endpoints.

The algebraic ``H2`` import turns the next physical trace-log row into a
two-propagator bubble.  Its endpoint logarithms cannot be added to the
three-propagator numerator before integration.  This module instead uses one
common dimensionless Feynman-parameter cutoff on a rational equal-box TT
fixture and compares all six labelled ``H1^3`` orderings with all three
polarized ``H1 H2`` bubbles exactly.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from .generic_background_physical_hessian_n3_five_carrier_projection import (
    A1,
    A2,
    _common_numerator,
    _route_matrix,
    _routing_coordinates,
    _to_sympy_poly,
    _vertex_q_matrix,
)
from .generic_background_physical_hessian_n3_triangle_fixture import (
    TRACELESS_BASIS,
    TRACELESS_GRAM_INVERSE,
    _linearized_riemann,
    _transverse_tracefree_basis,
    _vertex_representation,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MIXED_H1_H2_CORNER_FIXTURE.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-mixed-h1-h2-corner-fixture-v1.schema.json"
DEPENDENCIES = {
    "physical_H1": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_LINEAR_CURVATURE.json",
    "physical_H2": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_CURVATURE_SQUARED.json",
    "three_H1_projection": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_FIVE_CARRIER_PROJECTION.json",
    "three_H1_corner_obstruction": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_INTEGRATION_OBSTRUCTION.json",
}

RANGE4 = range(4)
MOMENTA = (
    (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
    (Fraction(-1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)),
    (Fraction(-1, 2), Fraction(-1, 2), Fraction(-1, 2), Fraction(-1, 2)),
)
TT_BASIS_INDICES = (0, 1, 2)


def _q(value: Any) -> dict[str, int]:
    rational = sp.Rational(value)
    return {"numerator": int(rational.p), "denominator": int(rational.q)}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value["result_id"]),
        "sha256": _sha256(path),
    }


def _external_fixture() -> tuple[list[sp.Matrix], list[sp.Matrix], list[list]]:
    momenta = [sp.Matrix(row) for row in MOMENTA]
    if sum(momenta, sp.zeros(4, 1)) != sp.zeros(4, 1):
        raise ValueError("equal-box fixture lost momentum conservation")
    if [momentum.dot(momentum) for momentum in momenta] != [1, 1, 1]:
        raise ValueError("equal-box fixture drifted")
    ricci = [
        _transverse_tracefree_basis(momentum)[basis_index]
        for momentum, basis_index in zip(momenta, TT_BASIS_INDICES)
    ]
    riemann = [
        _linearized_riemann(momentum, tensor)
        for momentum, tensor in zip(momenta, ricci)
    ]
    return momenta, ricci, riemann


def _corner_weights(
    momenta: list[sp.Matrix],
    vertex_matrices: list[list[list[dict[tuple[int, ...], Fraction]]]],
    order: tuple[int, int, int],
) -> list[sp.Rational]:
    ordered_momenta = [momenta[index] for index in order]
    ordered_vertices = [vertex_matrices[index] for index in order]
    routed = [
        _route_matrix(vertex, _routing_coordinates(ordered_momenta, leg))
        for leg, vertex in enumerate(ordered_vertices)
    ]
    numerator = _to_sympy_poly(
        _common_numerator(routed[2], routed[1], routed[0], (1, 1, 1))
    ).as_expr()
    alpha0 = 1 - A1 - A2
    delta = sp.expand(A1 * A2 + A2 * alpha0 + alpha0 * A1)
    density = sp.cancel(numerator / delta**4)
    epsilon, tangent = sp.symbols("epsilon tangent", positive=True)
    substitutions = (
        {A1: 1 - epsilon, A2: epsilon * (1 - tangent)},
        {A1: epsilon * (1 - tangent), A2: 1 - epsilon},
        {A1: epsilon * tangent, A2: epsilon * (1 - tangent)},
    )
    return [
        sp.Rational(
            sp.integrate(
                sp.cancel(
                    sp.limit(
                        epsilon**2
                        * density.subs(substitution, simultaneous=True),
                        epsilon,
                        0,
                        dir="+",
                    )
                ),
                (tangent, 0, 1),
            )
        )
        for substitution in substitutions
    ]


def _dot_ricci(left: sp.Matrix, right: sp.Matrix) -> sp.Expr:
    return sum(left[i, j] * right[i, j] for i in RANGE4 for j in RANGE4)


def _dot_riemann(left: list, right: list) -> sp.Expr:
    return sum(
        left[i][j][k][ell] * right[i][j][k][ell]
        for i in RANGE4
        for j in RANGE4
        for k in RANGE4
        for ell in RANGE4
    )


def _h2_seed_tensor(
    ricci1: sp.Matrix, riemann1: list, ricci2: sp.Matrix, riemann2: list
) -> dict[tuple[int, int, int, int], sp.Expr]:
    """Coefficient tensor of the nine scalar-flat projected monic H2 rows."""

    ricci_dot = _dot_ricci(ricci1, ricci2)
    riemann_dot = _dot_riemann(riemann1, riemann2)
    tensor: dict[tuple[int, int, int, int], sp.Expr] = {}
    for m in RANGE4:
        for n in RANGE4:
            for a in RANGE4:
                for b in RANGE4:
                    value = (-2 * ricci_dot + riemann_dot) * (
                        int(m == n) * int(a == b) - int(m == a) * int(n == b)
                    )
                    value += sp.Rational(2, 3) * ricci1[m, n] * ricci2[a, b]
                    value -= 2 * int(n == b) * sum(
                        ricci1[m, r] * ricci2[r, a] for r in RANGE4
                    )
                    value -= 4 * int(n == b) * sum(
                        ricci1[r, ell] * riemann2[m][r][a][ell]
                        for r in RANGE4
                        for ell in RANGE4
                    )
                    value += 12 * sum(
                        ricci1[r, m] * riemann2[r][a][b][n] for r in RANGE4
                    )
                    value += 8 * sum(
                        riemann1[r][a][m][ell] * riemann2[n][b][r][ell]
                        for r in RANGE4
                        for ell in RANGE4
                    )
                    value -= 2 * sum(
                        riemann1[r][a][m][ell] * riemann2[r][n][b][ell]
                        for r in RANGE4
                        for ell in RANGE4
                    )
                    value += 6 * sum(
                        riemann1[r][m][ell][n] * riemann2[r][a][ell][b]
                        for r in RANGE4
                        for ell in RANGE4
                    )
                    value += 3 * int(n == b) * sum(
                        riemann1[m][r][ell][sigma]
                        * riemann2[a][r][ell][sigma]
                        for r in RANGE4
                        for ell in RANGE4
                        for sigma in RANGE4
                    )
                    tensor[m, n, a, b] = sp.expand(value)
    return tensor


def _polarized_h2_representation(
    ricci1: sp.Matrix, riemann1: list, ricci2: sp.Matrix, riemann2: list
) -> tuple[sp.Matrix, sp.Matrix]:
    direct = _h2_seed_tensor(ricci1, riemann1, ricci2, riemann2)
    exchanged = _h2_seed_tensor(ricci2, riemann2, ricci1, riemann1)
    covariant = sp.zeros(9)
    for row, left in enumerate(TRACELESS_BASIS):
        for column, right in enumerate(TRACELESS_BASIS):
            covariant[row, column] = sp.expand(
                sum(
                    left[m, n]
                    * right[a, b]
                    * (
                        direct[m, n, a, b]
                        + exchanged[m, n, a, b]
                        + direct[a, b, m, n]
                        + exchanged[a, b, m, n]
                    )
                    / 2
                    for m in RANGE4
                    for n in RANGE4
                    for a in RANGE4
                    for b in RANGE4
                )
            )
    if covariant != covariant.T:
        raise ValueError("polarized H2 lost formal self-adjointness")
    return TRACELESS_GRAM_INVERSE * covariant, covariant


def _wick(polynomial: sp.Poly, pair_count: int) -> sp.Expr:
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
    return sp.expand(result)


def _bubble_endpoint_weights(
    singled_leg: int,
    momenta: list[sp.Matrix],
    ricci: list[sp.Matrix],
    riemann: list[list],
) -> tuple[sp.Rational, sp.Rational, dict[str, Any]]:
    paired = [index for index in range(3) if index != singled_leg]
    h2, covariant = _polarized_h2_representation(
        ricci[paired[0]],
        riemann[paired[0]],
        ricci[paired[1]],
        riemann[paired[1]],
    )
    parameter = sp.symbols("parameter", positive=True)
    loop_symbols = sp.symbols("loop0:4")
    loop = sp.Matrix(loop_symbols)
    momentum = momenta[singled_leg]
    incoming = loop - (1 - parameter) * momentum
    trace = sp.expand(
        sp.trace(
            h2
            * _vertex_representation(
                momentum, ricci[singled_leg], incoming
            )
        )
    )
    polynomial = sp.Poly(trace, *loop_symbols)
    constant = _wick(polynomial, 0)
    pair = _wick(polynomial, 1)
    delta = parameter * (1 - parameter) * momentum.dot(momentum)
    # 6*x*(1-x) is the Feynman prefactor for two squared propagators;
    # the d=4 scalar/pair loop integrals are 1/(6 Delta^2) and
    # 1/(12 Delta), and -1/2 is the labelled mixed trace-log coefficient.
    density = sp.factor(
        -sp.Rational(1, 2)
        * parameter
        * (1 - parameter)
        * (constant / delta**2 + sp.Rational(1, 2) * pair / delta)
    )
    left = sp.Rational(sp.limit(parameter * density, parameter, 0, dir="+"))
    right = sp.Rational(
        sp.limit((1 - parameter) * density, parameter, 1, dir="-")
    )
    return left, right, {
        "singled_H1_leg": singled_leg,
        "polarized_H2_legs": paired,
        "H2_covariant_rank": covariant.rank(),
        "H2_representation_rank": h2.rank(),
        "H1_loop_polynomial_degree": polynomial.total_degree(),
        "H1_loop_polynomial_term_count": len(polynomial.terms()),
        "left_endpoint_log_coefficient": _q(left),
        "right_endpoint_log_coefficient": _q(right),
    }


def _round_row_regression() -> dict[str, Any]:
    # These are the nine rows used by the scalar-flat vertex, evaluated with
    # the full C^2 scalar in H201. They replay the corresponding entries of
    # the imported thirteen-row source-W round ledger.
    expected = [18, -8, -6, 6, 36, 0, 0, -18, -36]
    source_ids = ["H217", "H213", "H215", "H216", "H212", "H208", "H201", "H209", "H211"]
    delta = lambda left, right: sp.Integer(left == right)
    ricci = 3 * sp.eye(4)
    riemann = [
        [
            [
                [
                    delta(m, n) * delta(a, b) - delta(m, b) * delta(a, n)
                    for b in RANGE4
                ]
                for n in RANGE4
            ]
            for a in RANGE4
        ]
        for m in RANGE4
    ]
    left = TRACELESS_BASIS[0]
    right = left
    norm = sp.trace(left.T * right)
    scalar = (
        sp.Rational(1, 6) * 12**2
        - _dot_ricci(ricci, ricci)
        + sp.Rational(1, 2) * _dot_riemann(riemann, riemann)
    )
    calculated = [
        3
        * sum(
            left[m, n]
            * right[a, n]
            * riemann[m][r][ell][sigma]
            * riemann[a][r][ell][sigma]
            for m in RANGE4
            for n in RANGE4
            for a in RANGE4
            for r in RANGE4
            for ell in RANGE4
            for sigma in RANGE4
        ),
        8
        * sum(
            left[m, n]
            * right[a, b]
            * riemann[r][a][m][ell]
            * riemann[n][b][r][ell]
            for m in RANGE4
            for n in RANGE4
            for a in RANGE4
            for b in RANGE4
            for r in RANGE4
            for ell in RANGE4
        ),
        -2
        * sum(
            left[m, n]
            * right[a, b]
            * riemann[r][a][m][ell]
            * riemann[r][n][b][ell]
            for m in RANGE4
            for n in RANGE4
            for a in RANGE4
            for b in RANGE4
            for r in RANGE4
            for ell in RANGE4
        ),
        6
        * sum(
            left[m, n]
            * right[a, b]
            * riemann[r][m][ell][n]
            * riemann[r][a][ell][b]
            for m in RANGE4
            for n in RANGE4
            for a in RANGE4
            for b in RANGE4
            for r in RANGE4
            for ell in RANGE4
        ),
        12
        * sum(
            left[m, n]
            * right[a, b]
            * ricci[r, m]
            * riemann[r][a][b][n]
            for m in RANGE4
            for n in RANGE4
            for a in RANGE4
            for b in RANGE4
            for r in RANGE4
        ),
        sp.Rational(2, 3)
        * sp.trace(left.T * ricci)
        * sp.trace(right.T * ricci),
        scalar
        * (sp.trace(left) * sp.trace(right) - sp.trace(left.T * right)),
        -2
        * sum(
            left[m, n]
            * right[a, n]
            * ricci[m, r]
            * ricci[r, a]
            for m in RANGE4
            for n in RANGE4
            for a in RANGE4
            for r in RANGE4
        ),
        -4
        * sum(
            left[m, n]
            * right[a, n]
            * ricci[r, ell]
            * riemann[m][r][a][ell]
            for m in RANGE4
            for n in RANGE4
            for a in RANGE4
            for r in RANGE4
            for ell in RANGE4
        ),
    ]
    calculated = [sp.Rational(value / norm) for value in calculated]
    if calculated != expected:
        raise ValueError("operational H2 round-row regression failed")
    return {
        "term_ids": source_ids,
        "TT_eigenvalue_contributions": [_q(value) for value in calculated],
        "sum_without_R_dependent_H1_rows": _q(sum(calculated)),
        "source_crosscheck": "entries agree termwise with the imported +24 K^2 source-W ledger; the omitted R-dependent row contributes +32 K^2",
    }


def build() -> dict[str, Any]:
    dependencies = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if dependencies["physical_H2"]["claim_flags"]["ALGEBRAIC_CURVATURE_SQUARED_H2_IMPORTED"] is not True:
        raise ValueError("physical H2 import gate is not satisfied")
    if dependencies["three_H1_corner_obstruction"]["claim_flags"]["H2_CANCELLATION_OF_CORNER_CLASS_PROVED"] is not False:
        raise ValueError("upstream H1 corner boundary drifted")

    momenta, ricci, riemann = _external_fixture()
    vertex_matrices = [
        _vertex_q_matrix(momentum, tensor)
        for momentum, tensor in zip(momenta, ricci)
    ]
    orientation_a = _corner_weights(momenta, vertex_matrices, (0, 1, 2))
    orientation_b = _corner_weights(momenta, vertex_matrices, (0, 2, 1))
    one_orientation_sum = sp.Rational(sum(orientation_a))
    if one_orientation_sum != sum(orientation_b):
        raise ValueError("the two cyclic H1 orientation sums disagree")
    full_h1 = sp.Rational(3 * (sum(orientation_a) + sum(orientation_b)))

    bubble_rows = []
    full_h2 = sp.S.Zero
    for singled_leg in range(3):
        left, right, row = _bubble_endpoint_weights(
            singled_leg, momenta, ricci, riemann
        )
        bubble_rows.append(row)
        full_h2 += left + right
    full_h2 = sp.Rational(full_h2)
    combined = sp.Rational(full_h1 + full_h2)
    if combined == 0:
        raise ValueError("raw H1/H2 logarithmic fixture unexpectedly cancelled")

    result = {
        "schema": "quantum-weyl-generic-background-physical-hessian-mixed-h1-h2-corner-fixture-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MIXED_H1_H2_CORNER_FIXTURE",
        "result_state": "RAW_MIXED_PHYSICAL_LOG_COEFFICIENT_NONZERO_SUBTRACTION_REQUIRED",
        "lifecycle_state": "COEFFICIENT_COMPUTED_RAW_RENORMALIZED_DISTRIBUTION_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": dependencies["physical_H2"]["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background": "scalar-flat rational equal-box local TT curvature fixture",
            "operator": "same-gauge rank-nine monic traceless physical Hessian H0+H1+H2",
            "regulator": "common dimensionless Feynman-parameter endpoint cutoff epsilon",
            "included": [
                "all six labelled H1-cubed trace-log orderings",
                "all three labelled polarized mixed H1-H2 bubbles",
                "both endpoints of every bubble",
            ],
            "excluded": [
                "a fixed covariant subtraction or renormalized distribution extension",
                "generic momentum form-factor integration",
                "ghost, nonminimal and complete repository sector assembly",
            ],
        },
        "equal_box_fixture": {
            "momenta": [[_q(component) for component in momentum] for momentum in momenta],
            "box_invariants": [_q(momentum.dot(momentum)) for momentum in momenta],
            "TT_basis_indices": list(TT_BASIS_INDICES),
            "momentum_conservation": "ZERO",
        },
        "operational_H2": {
            "source_row_ids": ["H201", "H208", "H209", "H211", "H212", "H213", "H215", "H216", "H217"],
            "polarization": "coefficient of epsilon_j epsilon_k, including external-curvature exchange",
            "field_slot_symmetrization": "formal self-adjoint average followed by the traceless Gram inverse",
            "round_row_regression": _round_row_regression(),
            "bubble_rows": bubble_rows,
        },
        "three_H1_corner": {
            "single_ordering_trace_log_coefficient": _q(sp.Rational(1, 6)),
            "cyclic_multiplicity_per_orientation": 3,
            "orientation_A_corner_weights": [_q(value) for value in orientation_a],
            "orientation_B_corner_weights": [_q(value) for value in orientation_b],
            "orientation_A_sum": _q(one_orientation_sum),
            "orientation_B_sum": _q(one_orientation_sum),
            "full_six_ordering_log_coefficient": _q(full_h1),
        },
        "mixed_H1_H2_endpoint": {
            "labelled_trace_log_coefficient_per_bubble": _q(sp.Rational(-1, 2)),
            "bubble_count": 3,
            "endpoint_count": 6,
            "full_endpoint_log_coefficient": _q(full_h2),
        },
        "combined_raw_logarithm": {
            "three_H1_corner_coefficient": _q(full_h1),
            "mixed_H1_H2_endpoint_coefficient": _q(full_h2),
            "sum": _q(combined),
            "common_factor_not_included": "(4 pi)^-2",
            "verdict": "NONZERO_RAW_LOG_COEFFICIENT_ALGEBRAIC_H2_DOES_NOT_CANCEL_THE_H1_CORNER_ON_THIS_FIXTURE",
        },
        "claim_flags": {
            "OPERATIONAL_SCALAR_FLAT_H2_POLARIZATION_CONSTRUCTED": True,
            "ALL_SIX_LABELLED_H1_CUBED_ORDERINGS_INCLUDED": True,
            "ALL_THREE_MIXED_H1_H2_BUBBLES_INCLUDED": True,
            "RAW_ALGEBRAIC_H2_CANCELLATION_IDENTITY_REFUTED_BY_FIXTURE": True,
            "RENORMALIZED_SUBTRACTION_FIXED": False,
            "PHYSICAL_M14_CORNER_CLASS_DISPOSED": False,
            "PHYSICAL_THIRD_CURVATURE_FORM_FACTORS_COMPLETE": False,
            "QME_OR_ANOMALY_STATUS_CHANGED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "negative_controls": {
            "interior_numerator_addition": {
                "rejected": True,
                "reason": "H1 cubed is a two-dimensional triangle density whereas H1-H2 is a one-dimensional bubble density with endpoint logarithms",
            },
            "renormalized_promotion": {
                "rejected": True,
                "reason": "a nonzero raw logarithmic coefficient requires a declared local covariant subtraction and distribution extension before a finite form factor exists",
            },
            "universal_cancellation": {
                "rejected": True,
                "reason": "the exact same-background equal-box TT fixture has nonzero combined raw coefficient 15707/216",
            },
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "FIX_COVARIANT_SUBTRACTION_AND_ASSEMBLE_RENORMALIZED_MIXED_PHYSICAL_ROWS",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL fixture rejects a universal raw algebraic-H2 cancellation of the physical H1 corner. It does not yet define the renormalized distribution, complete a form factor, change the anomaly/QME disposition, or establish a Lorentzian result.",
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text() != encoded:
            raise SystemExit("stored mixed H1-H2 corner fixture is stale")
        print("generic physical mixed H1-H2 corner fixture: PASS")
        return 0
    OUTPUT.write_text(encoded)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
