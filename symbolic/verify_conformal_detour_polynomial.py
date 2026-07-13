#!/usr/bin/env python3
"""C2h-L: finite exact local detour-complex certificate for pure Weyl gravity.

This is deliberately a *Euclidean homogeneous-polynomial jet* certificate, not an
all-level theorem about Lorentzian cylinder BRST cohomology.  On flat
``R^4`` (conformally equivalent locally to the Einstein cylinder) it builds
the actual finite matrices

    (xi, sigma) --K--> h --C1--> C1[h] --div div--> B1[h]

where ``K`` is the linear Diff x Weyl generator, ``C1`` is the linearized
Weyl tensor, and ``B1`` is the linearized Bach tensor.  Homogeneous metric
polynomials of degree ``n`` map to Weyl polynomials of degree ``n-2`` and
to Bach polynomials of degree ``n-4``.  The first five nontrivial homogeneous
levels, ``n=2,...,6``, are small enough for exact rational rank calculations.

The certificate separately treats the low-degree gauge block.  Vector
parameters of degree at most two and Weyl parameters of degree at most one
have the complete fifteen-dimensional conformal-Killing kernel

    4 translations + (6 rotations + 1 dilation) + 4 special conformal.

At levels 2--6 the script checks operator identities, exactness at the
potential-Weyl slot, and the finite quotient ranks.  Their values ``10, 40,
82, 136, 202`` agree with the two-chirality E/A/L character at the corresponding
compact weights.  That agreement is recorded only as a finite
representation-count match: no Cartesian-jet-to-cylinder harmonic intertwiner is
constructed here.

Fail-closed switches make the boundary explicit::

    python3 symbolic/verify_conformal_detour_polynomial.py
    python3 symbolic/verify_conformal_detour_polynomial.py --claim-all-levels
    python3 symbolic/verify_conformal_detour_polynomial.py --claim-lorentzian-eal
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from itertools import product

import sympy as sp

try:
    from symbolic.verify_conformal_weyl_module import (
        expected_towers,
        irrep_dimension,
    )
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    from verify_conformal_weyl_module import expected_towers, irrep_dimension


R = sp.Rational
DIMENSION = 4
SYMMETRIC_PAIRS = tuple(
    (first, second)
    for first in range(DIMENSION)
    for second in range(first, DIMENSION)
)


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def homogeneous_monomials(degree: int) -> tuple[tuple[int, ...], ...]:
    """Exponent tuples of total degree ``degree`` in four variables."""

    if degree < 0:
        return ()
    return tuple(
        exponent
        for exponent in product(range(degree + 1), repeat=DIMENSION)
        if sum(exponent) == degree
    )


def canonical_pair(first: int, second: int) -> tuple[int, int]:
    return (first, second) if first <= second else (second, first)


def differentiated_monomial(
    exponent: tuple[int, ...], derivatives: tuple[int, ...]
) -> tuple[sp.Integer, tuple[int, ...]] | None:
    """Apply ordered coordinate derivatives to one monomial exactly."""

    remaining = list(exponent)
    coefficient = sp.Integer(1)
    for derivative in derivatives:
        if remaining[derivative] == 0:
            return None
        coefficient *= remaining[derivative]
        remaining[derivative] -= 1
    return coefficient, tuple(remaining)


OperatorTerm = tuple[sp.Rational, tuple[int, ...], tuple[int, int]]


def collect_terms(terms: list[OperatorTerm]) -> tuple[OperatorTerm, ...]:
    output: defaultdict[tuple[tuple[int, ...], tuple[int, int]], sp.Expr] = (
        defaultdict(lambda: sp.Integer(0))
    )
    for coefficient, derivatives, pair in terms:
        output[derivatives, canonical_pair(*pair)] += coefficient
    return tuple(
        (sp.Rational(coefficient), derivatives, pair)
        for (derivatives, pair), coefficient in output.items()
        if coefficient != 0
    )


def scaled_terms(
    coefficient: sp.Rational, terms: tuple[OperatorTerm, ...]
) -> list[OperatorTerm]:
    return [
        (sp.Rational(coefficient * value), derivatives, pair)
        for value, derivatives, pair in terms
    ]


def riemann_terms(
    first: int, second: int, third: int, fourth: int
) -> tuple[OperatorTerm, ...]:
    """Terms in ``R^(1)_{first second third fourth}``.

    The overall Riemann-sign convention is irrelevant to ranks, but this
    convention is used consistently in ``C1`` and ``B1``.
    """

    return collect_terms(
        [
            (R(1, 2), (first, third), (second, fourth)),
            (R(1, 2), (second, fourth), (first, third)),
            (-R(1, 2), (second, third), (first, fourth)),
            (-R(1, 2), (first, fourth), (second, third)),
        ]
    )


def ricci_terms(first: int, second: int) -> tuple[OperatorTerm, ...]:
    terms: list[OperatorTerm] = []
    for contracted in range(DIMENSION):
        terms.extend(riemann_terms(contracted, first, contracted, second))
    return collect_terms(terms)


def scalar_terms() -> tuple[OperatorTerm, ...]:
    terms: list[OperatorTerm] = []
    for index in range(DIMENSION):
        terms.extend(ricci_terms(index, index))
    return collect_terms(terms)


def weyl_terms(
    first: int, second: int, third: int, fourth: int
) -> tuple[OperatorTerm, ...]:
    """Terms in the four-dimensional Euclidean linearized Weyl tensor."""

    delta = lambda left, right: sp.Integer(left == right)
    terms = list(riemann_terms(first, second, third, fourth))
    trace_terms = (
        (delta(first, third), ricci_terms(second, fourth)),
        (-delta(first, fourth), ricci_terms(second, third)),
        (-delta(second, third), ricci_terms(first, fourth)),
        (delta(second, fourth), ricci_terms(first, third)),
    )
    for coefficient, source in trace_terms:
        terms.extend(scaled_terms(-R(1, 2) * coefficient, source))
    scalar_coefficient = R(1, 6) * (
        delta(first, third) * delta(second, fourth)
        - delta(first, fourth) * delta(second, third)
    )
    terms.extend(scaled_terms(scalar_coefficient, scalar_terms()))
    return collect_terms(terms)


# Five electric and five magnetic components are independent coordinates on
# a four-dimensional Weyl tensor.  The magnetic entries use
# B_ij=(1/2) epsilon_i^kl C_0jkl and the pair antisymmetry of C.
WEYL_COORDINATES = (
    (0, 1, 0, 1),
    (0, 1, 0, 2),
    (0, 1, 0, 3),
    (0, 2, 0, 2),
    (0, 2, 0, 3),
    (0, 1, 2, 3),
    (0, 2, 2, 3),
    (0, 3, 2, 3),
    (0, 2, 3, 1),
    (0, 3, 3, 1),
)


@dataclass(frozen=True)
class FiniteLevel:
    degree: int
    gauge: sp.SparseMatrix
    weyl: sp.SparseMatrix
    bach: sp.SparseMatrix
    metric_dimension: int
    gauge_dimension: int
    weyl_dimension: int
    bach_dimension: int


def gauge_matrix(degree: int) -> sp.SparseMatrix:
    """Matrix of ``K(xi,sigma)=2 d_(a xi_b)+2 sigma delta_ab``."""

    metric_monomials = homogeneous_monomials(degree)
    vector_monomials = homogeneous_monomials(degree + 1)
    scalar_monomials = homogeneous_monomials(degree)
    row_index = {
        (pair, exponent): row
        for row, (pair, exponent) in enumerate(
            product(SYMMETRIC_PAIRS, metric_monomials)
        )
    }
    vector_columns = {
        (component, exponent): column
        for column, (component, exponent) in enumerate(
            product(range(DIMENSION), vector_monomials)
        )
    }
    scalar_offset = len(vector_columns)
    scalar_columns = {
        exponent: scalar_offset + column
        for column, exponent in enumerate(scalar_monomials)
    }
    entries: defaultdict[tuple[int, int], sp.Expr] = defaultdict(
        lambda: sp.Integer(0)
    )
    for (component, exponent), column in vector_columns.items():
        for first, second in SYMMETRIC_PAIRS:
            for derivative, target_component in (
                (first, second),
                (second, first),
            ):
                if component != target_component:
                    continue
                result = differentiated_monomial(exponent, (derivative,))
                if result is None:
                    continue
                coefficient, output_exponent = result
                entries[row_index[((first, second), output_exponent)], column] += (
                    coefficient
                )
    for exponent, column in scalar_columns.items():
        for index in range(DIMENSION):
            entries[row_index[((index, index), exponent)], column] += 2
    return sp.SparseMatrix(
        len(row_index), len(vector_columns) + len(scalar_columns), dict(entries)
    )


def differential_matrix(
    input_degree: int,
    output_degree: int,
    output_components: tuple[object, ...],
    terms_for_component,
) -> sp.SparseMatrix:
    input_monomials = homogeneous_monomials(input_degree)
    output_monomials = homogeneous_monomials(output_degree)
    input_columns = {
        (pair, exponent): column
        for column, (pair, exponent) in enumerate(
            product(SYMMETRIC_PAIRS, input_monomials)
        )
    }
    output_rows = {
        (component, exponent): row
        for row, (component, exponent) in enumerate(
            product(output_components, output_monomials)
        )
    }
    entries: defaultdict[tuple[int, int], sp.Expr] = defaultdict(
        lambda: sp.Integer(0)
    )
    for component in output_components:
        for coefficient, derivatives, pair in terms_for_component(component):
            for exponent in input_monomials:
                result = differentiated_monomial(exponent, derivatives)
                if result is None:
                    continue
                derivative_coefficient, output_exponent = result
                row = output_rows[(component, output_exponent)]
                column = input_columns[(pair, exponent)]
                entries[row, column] += coefficient * derivative_coefficient
    return sp.SparseMatrix(
        len(output_rows), len(input_columns), dict(entries)
    )


def weyl_matrix(degree: int) -> sp.SparseMatrix:
    return differential_matrix(
        degree,
        degree - 2,
        WEYL_COORDINATES,
        lambda component: weyl_terms(*component),
    )


def bach_component_terms(component: tuple[int, int]) -> tuple[OperatorTerm, ...]:
    first, second = component
    terms: list[OperatorTerm] = []
    for left in range(DIMENSION):
        for right in range(DIMENSION):
            for coefficient, derivatives, pair in weyl_terms(
                left, first, right, second
            ):
                terms.append(
                    (coefficient, (left, right, *derivatives), pair)
                )
    return collect_terms(terms)


def bach_matrix(degree: int) -> sp.SparseMatrix:
    if degree < 4:
        metric_dimension = len(SYMMETRIC_PAIRS) * len(
            homogeneous_monomials(degree)
        )
        return sp.SparseMatrix(0, metric_dimension, {})
    return differential_matrix(
        degree,
        degree - 4,
        SYMMETRIC_PAIRS,
        bach_component_terms,
    )


def finite_level(degree: int) -> FiniteLevel:
    gauge = gauge_matrix(degree)
    weyl = weyl_matrix(degree)
    bach = bach_matrix(degree)
    return FiniteLevel(
        degree=degree,
        gauge=gauge,
        weyl=weyl,
        bach=bach,
        metric_dimension=gauge.rows,
        gauge_dimension=gauge.cols,
        weyl_dimension=weyl.rows,
        bach_dimension=bach.rows,
    )


def inhomogeneous_gauge_matrix() -> tuple[sp.SparseMatrix, dict, dict]:
    """Gauge map on ``xi_{<=2}, sigma_{<=1} -> h_{<=1}``.

    The returned column dictionaries are also used to construct the standard
    fifteen conformal-Killing parameters independently of a nullspace basis.
    """

    vector_exponents = tuple(
        exponent
        for degree in range(3)
        for exponent in homogeneous_monomials(degree)
    )
    scalar_exponents = tuple(
        exponent
        for degree in range(2)
        for exponent in homogeneous_monomials(degree)
    )
    metric_exponents = tuple(
        exponent
        for degree in range(2)
        for exponent in homogeneous_monomials(degree)
    )
    vector_columns = {
        (component, exponent): column
        for column, (component, exponent) in enumerate(
            product(range(DIMENSION), vector_exponents)
        )
    }
    scalar_offset = len(vector_columns)
    scalar_columns = {
        exponent: scalar_offset + column
        for column, exponent in enumerate(scalar_exponents)
    }
    rows = {
        (pair, exponent): row
        for row, (pair, exponent) in enumerate(
            product(SYMMETRIC_PAIRS, metric_exponents)
        )
    }
    entries: defaultdict[tuple[int, int], sp.Expr] = defaultdict(
        lambda: sp.Integer(0)
    )
    for (component, exponent), column in vector_columns.items():
        for first, second in SYMMETRIC_PAIRS:
            for derivative, target_component in (
                (first, second),
                (second, first),
            ):
                if component != target_component:
                    continue
                result = differentiated_monomial(exponent, (derivative,))
                if result is None:
                    continue
                coefficient, output_exponent = result
                entries[rows[((first, second), output_exponent)], column] += (
                    coefficient
                )
    for exponent, column in scalar_columns.items():
        for index in range(DIMENSION):
            entries[rows[((index, index), exponent)], column] += 2
    matrix = sp.SparseMatrix(
        len(rows), len(vector_columns) + len(scalar_columns), dict(entries)
    )
    return matrix, vector_columns, scalar_columns


def parameter_vector(
    vector_columns: dict,
    scalar_columns: dict,
    vector_terms: dict[tuple[int, tuple[int, ...]], sp.Expr],
    scalar_terms_map: dict[tuple[int, ...], sp.Expr],
) -> sp.Matrix:
    output = sp.zeros(len(vector_columns) + len(scalar_columns), 1)
    for key, coefficient in vector_terms.items():
        output[vector_columns[key]] += coefficient
    for exponent, coefficient in scalar_terms_map.items():
        output[scalar_columns[exponent]] += coefficient
    return output


def expected_conformal_killing_vectors(
    vector_columns: dict, scalar_columns: dict
) -> sp.Matrix:
    zero = (0, 0, 0, 0)
    unit = tuple(
        tuple(1 if coordinate == axis else 0 for coordinate in range(DIMENSION))
        for axis in range(DIMENSION)
    )
    vectors: list[sp.Matrix] = []

    # Four translations.
    for component in range(DIMENSION):
        vectors.append(
            parameter_vector(
                vector_columns,
                scalar_columns,
                {(component, zero): sp.Integer(1)},
                {},
            )
        )

    # Six rotations xi_a = x_b, xi_b = -x_a.
    for first in range(DIMENSION):
        for second in range(first + 1, DIMENSION):
            vectors.append(
                parameter_vector(
                    vector_columns,
                    scalar_columns,
                    {
                        (first, unit[second]): sp.Integer(1),
                        (second, unit[first]): sp.Integer(-1),
                    },
                    {},
                )
            )

    # Dilation xi_a=x_a, sigma=-1.
    vectors.append(
        parameter_vector(
            vector_columns,
            scalar_columns,
            {(axis, unit[axis]): sp.Integer(1) for axis in range(DIMENSION)},
            {zero: sp.Integer(-1)},
        )
    )

    # Four special conformal generators
    # xi_a=2(b.x)x_a-x^2 b_a, sigma=-2(b.x).
    for direction in range(DIMENSION):
        vector_terms: defaultdict[tuple[int, tuple[int, ...]], sp.Expr] = (
            defaultdict(lambda: sp.Integer(0))
        )
        for component in range(DIMENSION):
            exponent = list(unit[direction])
            exponent[component] += 1
            vector_terms[component, tuple(exponent)] += 2
        for axis in range(DIMENSION):
            exponent = [0] * DIMENSION
            exponent[axis] = 2
            vector_terms[direction, tuple(exponent)] -= 1
        vectors.append(
            parameter_vector(
                vector_columns,
                scalar_columns,
                dict(vector_terms),
                {unit[direction]: sp.Integer(-2)},
            )
        )
    return sp.Matrix.hstack(*vectors)


def parity_completed_eal_dimension(energy: int) -> int:
    return 2 * sum(
        multiplicity * irrep_dimension(*highest_weight)
        for highest_weight, multiplicity in expected_towers(energy).items()
    )


def predicted_ranks(degree: int) -> tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr]:
    """Closed rank predictions checked only on the finite default buffer.

    Agreement for degrees two through six is not used as an all-degree proof.
    """

    rank_gauge = 4 * sp.binomial(degree + 4, 3) + sp.binomial(degree + 3, 3)
    rank_weyl = R(1, 6) * (degree + 2) * (degree + 3) * (5 * degree - 7)
    rank_bach = R(1, 6) * (degree - 2) * (degree - 3) * (5 * degree + 7)
    quotient = 6 * degree**2 - 14
    return rank_gauge, rank_weyl, rank_bach, sp.Integer(quotient)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--claim-all-levels",
        action="store_true",
        help="fail closed: degrees 2--6 do not prove exactness at all levels",
    )
    parser.add_argument(
        "--claim-lorentzian-eal",
        action="store_true",
        help=(
            "fail closed: Euclidean homogeneous-polynomial jet ranks do not construct "
            "the Lorentzian cylinder harmonic/BRST intertwiner"
        ),
    )
    args = parser.parse_args()

    print("=== C2h-L0: conformal-Killing zero-mode split ===")
    low_gauge, vector_columns, scalar_columns = inhomogeneous_gauge_matrix()
    expected_kernel = expected_conformal_killing_vectors(
        vector_columns, scalar_columns
    )
    low_rank = low_gauge.rank()
    check(
        "C2h-L0: affine metric gauge map has dimensions 50 x 65 and rank 50",
        low_gauge.shape == (50, 65) and low_rank == 50,
    )
    check(
        "C2h-L0: the independently constructed 4+7+4 CK parameters are linearly independent",
        expected_kernel.shape == (65, 15) and expected_kernel.rank() == 15,
    )
    check(
        "C2h-L0: all fifteen CK parameters lie in ker K",
        low_gauge * expected_kernel == sp.zeros(50, 15),
    )
    check(
        "C2h-L0: the CK span exhausts ker K exactly",
        low_gauge.cols - low_rank == 15,
    )

    print("\n=== C2h-L1: finite Euclidean homogeneous-polynomial jet levels ===")
    rank_rows: list[tuple[int, ...]] = []
    for degree in range(2, 7):
        level = finite_level(degree)
        rank_gauge = level.gauge.rank()
        rank_weyl = level.weyl.rank()
        rank_bach = level.bach.rank()
        quotient_dimension = (
            level.metric_dimension - rank_bach - rank_gauge
        )
        rank_predictions = predicted_ranks(degree)
        check(
            f"C2h-L1[{degree}]: C1 K=0 exactly",
            level.weyl * level.gauge
            == sp.zeros(level.weyl.rows, level.gauge.cols),
        )
        check(
            f"C2h-L1[{degree}]: B1 K=0 exactly",
            level.bach * level.gauge
            == sp.zeros(level.bach.rows, level.gauge.cols),
        )
        check(
            f"C2h-L1[{degree}]: ker C1=im K at this finite homogeneous level",
            rank_weyl == level.metric_dimension - rank_gauge,
        )
        check(
            f"C2h-L1[{degree}]: C1 injects ker B1/im K into on-shell Weyl polynomials",
            rank_weyl - rank_bach == quotient_dimension,
        )
        expected_eal = parity_completed_eal_dimension(degree)
        check(
            f"C2h-L1[{degree}]: finite quotient rank matches the two-chirality E/A/L count",
            quotient_dimension == expected_eal,
        )
        check(
            f"C2h-L1[{degree}]: observed ranks match the closed finite-buffer predictions",
            (rank_gauge, rank_weyl, rank_bach, quotient_dimension)
            == rank_predictions,
        )
        rank_rows.append(
            (
                degree,
                level.gauge_dimension,
                level.metric_dimension,
                level.weyl_dimension,
                level.bach_dimension,
                rank_gauge,
                rank_weyl,
                rank_bach,
                quotient_dimension,
            )
        )

    check(
        "C2h-L2: quotient ranks through degree six are 10, 40, 82, 136, 202",
        tuple(row[-1] for row in rank_rows) == (10, 40, 82, 136, 202),
    )
    print(
        "degree | dim gauge | dim h | dim Ccoords | dim Bach | "
        "rank K | rank C1 | rank B1 | quotient"
    )
    for row in rank_rows:
        print("%6d | %9d | %5d | %11d | %8d | %6d | %7d | %7d | %8d" % row)
    print(
        "finite-buffer rank predictions: rank K=4*C(n+4,3)+C(n+3,3), "
        "rank C1=(n+2)(n+3)(5n-7)/6, "
        "rank B1=(n-2)(n-3)(5n+7)/6, quotient=6n^2-14"
    )

    print(
        "C2h-L STATUS: EXACT EUCLIDEAN HOMOGENEOUS-POLYNOMIAL JET DETOUR "
        "MATRICES AT DEGREES 2--6, WITH THE FIFTEEN CONFORMAL-KILLING ZERO MODES "
        "SEPARATED. The 10/40/82/136/202 quotient ranks match the finite E/A/L "
        "character counts. This is not an all-level exactness theorem and "
        "does not construct the Lorentzian cylinder harmonic/BRST map."
    )
    if args.claim_all_levels:
        raise SystemExit(
            "finite degrees 2--6 do not prove the all-level local detour exactness theorem"
        )
    if args.claim_lorentzian_eal:
        raise SystemExit(
            "the Euclidean homogeneous-polynomial jet certificate does not construct the "
            "Lorentzian on-shell E/A/L harmonic/BRST intertwiner"
        )


if __name__ == "__main__":
    main()
