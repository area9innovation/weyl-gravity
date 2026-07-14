"""End-to-end helpers from raw metric cohomology to weight-four vertices."""

from __future__ import annotations

from itertools import combinations_with_replacement

import sympy as sp

from bridge.bv_complex.conformal_polynomials import (
    SYMMETRIC_PAIRS,
    TRACEFREE_INCLUSION,
    TRACEFREE_PROJECTION,
    homogeneous_monomials,
)
from bridge.residual_bfv import CoefficientModule, ConformalCE
from bridge.transfer.raw_residual import RawResidualModule
from symbolic.verify_conformal_detour_polynomial import weyl_matrix


def symmetric_pairs(dimension: int) -> tuple[tuple[int, int], ...]:
    return tuple(combinations_with_replacement(range(dimension), 2))


def symmetric_square_lie_action(matrix: sp.MatrixBase) -> sp.Matrix:
    """Infinitesimal action on the unnormalized commutative-product basis."""

    dimension = matrix.rows
    pairs = symmetric_pairs(dimension)
    pair_index = {pair: index for index, pair in enumerate(pairs)}
    output = sp.zeros(len(pairs))
    for column, (first, second) in enumerate(pairs):
        for target in range(dimension):
            output[
                pair_index[tuple(sorted((target, second)))], column
            ] += matrix[target, first]
            output[
                pair_index[tuple(sorted((first, target)))], column
            ] += matrix[target, second]
    return output


def symmetric_square_finite_action(matrix: sp.MatrixBase) -> sp.Matrix:
    """Finite action on the unnormalized commutative-product basis."""

    dimension = matrix.rows
    pairs = symmetric_pairs(dimension)
    pair_index = {pair: index for index, pair in enumerate(pairs)}
    output = sp.zeros(len(pairs))
    for column, (first, second) in enumerate(pairs):
        for left in range(dimension):
            for right in range(dimension):
                coefficient = matrix[left, first] * matrix[right, second]
                if coefficient:
                    output[
                        pair_index[tuple(sorted((left, right)))], column
                    ] += coefficient
    return output


def energy_two_symmetric_module(raw: RawResidualModule) -> CoefficientModule:
    """The weight-four ``Sym^2 H_2`` coefficient module."""

    indices = raw.indices_at(2)
    compact = tuple(
        sp.Matrix(matrix).extract(indices, indices) for matrix in raw.matrices[:7]
    )
    actions = tuple(symmetric_square_lie_action(matrix) for matrix in compact)
    dimension = len(symmetric_pairs(len(indices)))
    actions += (sp.zeros(dimension),) * 8
    return CoefficientModule(actions, (4,) * dimension)


def energy_two_metric_form(raw: RawResidualModule) -> sp.Matrix:
    """Positive compact-invariant form transported through Weyl curvature.

    Gauge-dependent metric representatives are not orthogonal to gauge
    images in an arbitrary coordinate splitting, so their naive Euclidean
    coefficient norm is not a cohomological form.  At energy two the Weyl
    map is an isomorphism onto constant algebraic curvatures.  Pulling back
    the Euclidean electric/magnetic Frobenius form therefore gives the
    invariant positive form on the two E branches.
    """

    retract = raw.retracts[2]
    metric = retract.block.slice("metric")
    representatives = retract.inclusion[metric.start : metric.stop, :]
    monomial_count = len(homogeneous_monomials(2))
    tracefree_representatives = representatives[: 9 * monomial_count, :]
    tracefree_inclusion = sp.kronecker_product(
        TRACEFREE_INCLUSION, sp.eye(monomial_count)
    )
    curvature = (
        weyl_matrix(2) * tracefree_inclusion * tracefree_representatives
    )
    if curvature.rank() != 10:
        raise AssertionError("energy-two Weyl curvature map is not invertible")

    # The independent coordinates are five entries of each trace-free
    # symmetric electric/magnetic 3x3 tensor.  The missing 33 entry is minus
    # the sum of 11 and 22, giving this exact Frobenius Gram block.
    tracefree_three = sp.zeros(5)
    tracefree_three[0, 0] = tracefree_three[3, 3] = 2
    tracefree_three[0, 3] = tracefree_three[3, 0] = 1
    for index in (1, 2, 4):
        tracefree_three[index, index] = 2
    curvature_form = sp.diag(tracefree_three, tracefree_three)
    result = sp.simplify(curvature.T * curvature_form * curvature)
    for first in range(4):
        for second in range(first + 1, 4):
            rotation = retract.induced(
                retract.block.rotation(first, second), retract
            )
            if rotation.T * result + result * rotation != sp.zeros(10):
                raise AssertionError("energy-two form is not SO(4)-invariant")
    return result


def symmetric_square_form(form: sp.MatrixBase) -> sp.Matrix:
    pairs = symmetric_pairs(form.rows)
    output = sp.zeros(len(pairs))
    for row, (first, second) in enumerate(pairs):
        for column, (left, right) in enumerate(pairs):
            output[row, column] = (
                form[first, left] * form[second, right]
                + form[first, right] * form[second, left]
            )
    return output


def energy_two_parity(raw: RawResidualModule) -> sp.Matrix:
    """Orientation reversal ``x_3 -> -x_3`` induced on energy-two classes."""

    retract = raw.retracts[2]
    metric = retract.block.slice("metric")
    reflection = sp.diag(1, 1, 1, -1)
    full_component = sp.zeros(10)
    for column, (first, second) in enumerate(SYMMETRIC_PAIRS):
        tensor = sp.zeros(4)
        tensor[first, second] = tensor[second, first] = 1
        transformed = reflection * tensor * reflection.T
        for row, (left, right) in enumerate(SYMMETRIC_PAIRS):
            full_component[row, column] = transformed[left, right]
    tracefree_component = (
        TRACEFREE_PROJECTION * full_component * TRACEFREE_INCLUSION
    )
    monomials = homogeneous_monomials(2)
    monomial_parity = sp.diag(*[(-1) ** exponent[3] for exponent in monomials])
    metric_parity = sp.diag(
        sp.kronecker_product(tracefree_component, monomial_parity),
        monomial_parity,
    )
    result = sp.simplify(
        retract.projection[:, metric.start : metric.stop]
        * metric_parity
        * retract.inclusion[metric.start : metric.stop, :]
    )
    if result * result != sp.eye(result.rows):
        raise AssertionError("transferred parity is not involutive")
    return result


def induced_on_span(
    operator: sp.MatrixBase, basis: sp.MatrixBase
) -> sp.Matrix:
    """Restrict an invariant operator to a full-column-rank span."""

    pivot_rows = tuple(basis.T.rref(simplify=False, normalize_last=True)[1])
    square = basis.extract(list(pivot_rows), range(basis.cols))
    result = square.inv() * (operator * basis).extract(
        list(pivot_rows), range(basis.cols)
    )
    if operator * basis != basis * result:
        raise AssertionError("operator does not preserve the declared span")
    return result


def normalized_kernel_basis(
    basis: sp.MatrixBase, form: sp.MatrixBase
) -> tuple[sp.Matrix, sp.Matrix]:
    """Gram--Schmidt a two-column positive kernel basis exactly."""

    raw_gram = sp.simplify(basis.T * form * basis)
    first_norm = raw_gram[0, 0]
    second = basis[:, 1] - basis[:, 0] * raw_gram[0, 1] / first_norm
    second_norm = sp.simplify((second.T * form * second)[0])
    normalized = sp.Matrix.hstack(
        basis[:, 0] / sp.sqrt(first_norm), second / sp.sqrt(second_norm)
    )
    if sp.simplify(normalized.T * form * normalized) != sp.eye(2):
        raise AssertionError("weight-four kernel failed to normalize to I2")
    return normalized, raw_gram
