"""Arbitrary-covector symbol of the pair-(1,6) relative saddle candidate.

This module continues the temporal calculation in
``expanded_relative_witness_douglis`` without promoting it to a Green
witness.  The order-one pair map ``R6sharp`` is extended by the explicit
cylinder-time operator

``R6sharp = R6sharp_0 nabla_0``.

That is a support-local, ``SO(3)``-invariant choice, not a uniqueness or
four-dimensionally natural statement.  The first-order formal adjoint of the
curvature identity is used with its required sign

``Ncurvsharp(zeta)=-Ncurv(zeta)^T``.

For block order ``(M[24],U[26],Eqsharp[40],Usharp[26])`` the complete
Douglis symbol has orders ``(2,1;2,1)``.  Its determinant is computed over
the exact aligned polynomial ring and globalized with the coefficientwise
``SO(3)`` action.  All characteristic roots are real and causal.

The calculation also records a narrow symmetrizer boundary.  The local
polynomial field Schur symbol has only one simultaneous symmetric
pointwise multiplier; it is the rank-four Lorentz form on the vector field.
Thus neither the retained scalar diagonal nor a simple ``-2`` scalar
variant gives a positive *field-only pointwise* simultaneous symmetrizer.
This does not exclude a differential symmetrizer after a genuine
first-order reduction of the complete 116-component Douglis system.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from .conventions import SYMMETRIC_COORDINATES
from .expanded_hessian import load_coefficient_cache
from .expanded_relative_witness_commutant import (
    _block_generators,
    _intertwining_defect,
)
from .null_symbol_rank_obstruction import DEFAULT_CACHE
from .weyl_cotton_hyperbolic import ConstraintAdjustedWeylCottonEvolution


FIELD_RANK = 24
EVOLUTION_RANK = 26
CONSTRAINT_RANK = 14
CURVATURE_RANK = 92
COMPLETE_RANK = 116
VECTOR_GHOST_COLUMNS = (1, 2, 3, 5, 6, 7)
GAUGE_SCALAR_COORDINATES = (0, 10, 20)
SYMMETRIC_MONOMIALS = tuple(
    (first, second) for first in range(4) for second in range(first, 4)
)


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _table_digest(matrices: tuple[sp.Matrix, ...]) -> str:
    payload = "\n".join(
        sp.srepr(sp.ImmutableDenseMatrix(matrix)) for matrix in matrices
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _matrix_nonzero_count(matrix: sp.MatrixBase) -> int:
    return sum(int(value != 0) for value in matrix)


def _field_pairing() -> sp.Matrix:
    """Reconstruct the certified action pairing without the flat build."""

    metric = sp.diag(-1, 1, 1, 1)
    basis: list[sp.Matrix] = []
    for first, second in SYMMETRIC_COORDINATES:
        tensor = sp.zeros(4)
        tensor[first, second] = 1
        tensor[second, first] = 1
        basis.append(tensor)
    tensor_pairing = sp.Matrix(
        10,
        10,
        lambda row, column: sp.trace(
            metric * basis[row] * metric * basis[column]
        ),
    )
    trace = sp.Matrix(
        1,
        10,
        lambda _, column: sp.trace(metric * basis[column]),
    )
    de_witt = tensor_pairing - sp.Rational(1, 2) * trace.T * trace
    result = sp.zeros(FIELD_RANK)
    result[:10, 10:20] = de_witt / 2
    result[10:20, :10] = de_witt / 2
    result[20:24, 20:24] = metric
    return result


def _tensor_coordinates(tensor: sp.MatrixBase) -> sp.Matrix:
    return sp.Matrix(
        [tensor[first, second] for first, second in SYMMETRIC_COORDINATES]
    )


def _gauge_derivative_coefficients() -> tuple[sp.Matrix, ...]:
    """Exact curved K derivative table in the cylinder normal frame."""

    metric = sp.diag(-1, 1, 1, 1)
    result: list[sp.Matrix] = []
    for derivative in range(4):
        coefficient = sp.zeros(FIELD_RANK, 9)
        for column in range(4):
            xi = sp.zeros(4, 1)
            xi[column] = 1
            coefficient[:10, column] = _tensor_coordinates(
                sp.eye(4)[:, derivative] * xi.T
                + xi * sp.eye(4)[derivative, :]
            )
            # The exact cylinder auxiliary background is -2 I_covariant.
            background_xi = -2 * metric * xi
            coefficient[10:20, column] = _tensor_coordinates(
                sp.eye(4)[:, derivative] * background_xi.T
                + background_xi * sp.eye(4)[derivative, :]
            )
            kappa = sp.zeros(4, 1)
            kappa[column] = 1
            coefficient[10:20, 4 + column] = _tensor_coordinates(
                sp.eye(4)[:, derivative] * kappa.T
                + kappa * sp.eye(4)[derivative, :]
            )
        coefficient[20:24, 8] = sp.eye(4)[:, derivative]
        result.append(coefficient)
    return tuple(result)


def _gauge_zeroth_coefficient() -> sp.Matrix:
    metric = sp.diag(-1, 1, 1, 1)
    result = sp.zeros(FIELD_RANK, 9)
    result[:10, 8] = _tensor_coordinates(metric)
    result[20:24, 4:8] = -sp.eye(4)
    return result


def _homogeneous_degree_two(
    matrix: sp.MatrixBase, covector: tuple[sp.Symbol, ...]
) -> sp.Matrix:
    scale = sp.Symbol("expanded_relative_full_symbol_scale")
    return sp.Matrix(matrix).applyfunc(
        lambda value: sp.expand(
            value.subs({entry: scale * entry for entry in covector})
        ).coeff(scale, 2)
    )


def _quadratic_coefficients(
    matrix: sp.MatrixBase, covector: tuple[sp.Symbol, ...]
) -> tuple[sp.Matrix, ...]:
    return tuple(
        sp.Matrix(matrix).applyfunc(
            lambda value, first=first, second=second: sp.Poly(
                value, *covector
            ).coeff_monomial(covector[first] * covector[second])
        )
        for first, second in SYMMETRIC_MONOMIALS
    )


def _scalar_diagonal(values: sp.Matrix) -> sp.Matrix:
    if values.shape != (3, 3):
        raise ValueError("scalar diagonal must be three by three")
    result = sp.zeros(FIELD_RANK)
    for row, target in enumerate(GAUGE_SCALAR_COORDINATES):
        for column, source in enumerate(GAUGE_SCALAR_COORDINATES):
            result[target, source] = values[row, column]
    return result


def _relative_coefficients(
    gauge: tuple[sp.Matrix, ...],
) -> tuple[sp.Matrix, sp.Matrix]:
    vector_gauge = gauge[0][:, VECTOR_GHOST_COLUMNS]
    left_inverse = (vector_gauge.T * vector_gauge).inv() * vector_gauge.T
    ghost_vector = sp.zeros(9, 6)
    for column, row in enumerate(VECTOR_GHOST_COLUMNS):
        ghost_vector[row, column] = 1
    identity_vector = sp.zeros(CONSTRAINT_RANK, 6)
    identity_vector[:6, :] = sp.eye(6)
    temporal_identity = sp.zeros(CONSTRAINT_RANK, EVOLUTION_RANK).row_join(
        sp.eye(CONSTRAINT_RANK)
    )
    equation_vector = temporal_identity.T * identity_vector
    r1 = ghost_vector * equation_vector.T
    r6_sharp_zero = identity_vector * left_inverse
    return r1, r6_sharp_zero


def _identity_coefficients(
    evolution: ConstraintAdjustedWeylCottonEvolution,
) -> tuple[sp.Matrix, ...]:
    result = [
        sp.zeros(CONSTRAINT_RANK, EVOLUTION_RANK).row_join(
            sp.eye(CONSTRAINT_RANK)
        )
    ]
    result.extend(
        (-source).row_join(subsidiary)
        for source, subsidiary in zip(
            evolution.source_compatibility_spatial_coefficients,
            evolution.constraint_spatial_coefficients,
            strict=True,
        )
    )
    return tuple(result)


def _natural_schur_coefficients() -> tuple[sp.Matrix, ...]:
    """Polynomial continuation of the exact aligned curvature Schur term."""

    coefficients = {
        monomial: sp.zeros(FIELD_RANK) for monomial in SYMMETRIC_MONOMIALS
    }
    coordinate = {
        pair: index for index, pair in enumerate(SYMMETRIC_COORDINATES)
    }
    for offset in (0, 10):
        for spatial in range(1, 4):
            mixed = offset + coordinate[(0, spatial)]
            coefficients[(0, 0)][mixed, mixed] = 1
        for derivative in range(1, 4):
            for input_axis in range(1, 4):
                output = offset + coordinate[
                    (min(derivative, input_axis), max(derivative, input_axis))
                ]
                source = offset + coordinate[(0, input_axis)]
                coefficients[(0, derivative)][output, source] += (
                    2 if derivative == input_axis else 1
                )
    return tuple(coefficients[monomial] for monomial in SYMMETRIC_MONOMIALS)


def _symbol_from_quadratic_coefficients(
    coefficients: tuple[sp.Matrix, ...], values: tuple[sp.Expr, ...]
) -> sp.Matrix:
    return sum(
        (
            values[first] * values[second] * coefficient
            for (first, second), coefficient in zip(
                SYMMETRIC_MONOMIALS, coefficients, strict=True
            )
        ),
        sp.zeros(coefficients[0].rows, coefficients[0].cols),
    )


def _simultaneous_symmetric_multiplier(
    coefficients: tuple[sp.Matrix, ...],
) -> tuple[int, sp.Matrix]:
    """Solve H A^{mu nu}=(A^{mu nu})^T H with H symmetric."""

    coordinates = tuple(
        (row, column)
        for row in range(FIELD_RANK)
        for column in range(row, FIELD_RANK)
    )
    variable = {coordinate: index for index, coordinate in enumerate(coordinates)}
    rows: list[dict[int, sp.Expr]] = []
    for coefficient in coefficients:
        for row in range(FIELD_RANK):
            for column in range(row, FIELD_RANK):
                equation: dict[int, sp.Expr] = {}
                for middle in range(FIELD_RANK):
                    value = coefficient[middle, column]
                    if value:
                        key = variable[tuple(sorted((row, middle)))]
                        equation[key] = equation.get(key, 0) + value
                    value = -coefficient[middle, row]
                    if value:
                        key = variable[tuple(sorted((middle, column)))]
                        equation[key] = equation.get(key, 0) + value
                rows.append(equation)
    equations = sp.SparseMatrix(
        len(rows),
        len(coordinates),
        {
            (row, column): value
            for row, equation in enumerate(rows)
            for column, value in equation.items()
            if value
        },
    )
    rank = DomainMatrix.from_Matrix(equations).rank()
    nullspace = equations.nullspace()
    if len(nullspace) != 1:
        raise AssertionError("expected a unique simultaneous multiplier line")
    vector = nullspace[0]
    multiplier = sp.zeros(FIELD_RANK)
    for value, (row, column) in zip(vector, coordinates, strict=True):
        multiplier[row, column] = value
        multiplier[column, row] = value
    return rank, multiplier


def _connected_determinant(matrix: sp.Matrix) -> sp.Expr:
    """Exact determinant through the aligned SO(2) support components."""

    size = matrix.rows
    adjacency = [{index} for index in range(size)]
    for row in range(size):
        for column in range(size):
            if matrix[row, column] != 0 or matrix[column, row] != 0:
                adjacency[row].add(column)
                adjacency[column].add(row)
    seen: set[int] = set()
    components: list[list[int]] = []
    for root in range(size):
        if root in seen:
            continue
        seen.add(root)
        stack = [root]
        component: list[int] = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbour in adjacency[current]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
        components.append(sorted(component))
    determinant = sp.Integer(1)
    for component in components:
        determinant = sp.factor(
            determinant
            * matrix.extract(component, component).det(method="domain-ge")
        )
    return determinant


@dataclass(frozen=True)
class ExpandedRelativeFullSymbol:
    covector: tuple[sp.Symbol, ...]
    field_pairing: sp.Matrix
    paired_hessian_coefficients: tuple[sp.Matrix, ...]
    gauge_coefficients: tuple[sp.Matrix, ...]
    gauge_zeroth_coefficient: sp.Matrix
    evolution_coefficients: tuple[sp.Matrix, ...]
    subsidiary_coefficients: tuple[sp.Matrix, ...]
    identity_coefficients: tuple[sp.Matrix, ...]
    r1: sp.Matrix
    r6_sharp_temporal: sp.Matrix
    schur_coefficients: tuple[sp.Matrix, ...]
    retained_scalar_diagonal: sp.Matrix
    separated_scalar_diagonal: sp.Matrix
    aligned_retained_symbol: sp.Matrix
    aligned_separated_symbol: sp.Matrix
    aligned_retained_determinant: sp.Expr
    aligned_separated_determinant: sp.Expr
    retained_characteristic_ranks: tuple[int, ...]
    separated_characteristic_ranks: tuple[int, ...]
    retained_temporal_field_jordan_ranks: tuple[int, int, int]
    separated_temporal_field_symmetrizer: sp.Matrix
    separated_temporal_symmetrizer_defects: tuple[int, ...]
    retained_multiplier_rank: int
    separated_multiplier_rank: int
    retained_multiplier: sp.Matrix
    separated_multiplier: sp.Matrix

    @staticmethod
    def build() -> "ExpandedRelativeFullSymbol":
        covector, hessian, _ = load_coefficient_cache(DEFAULT_CACHE)
        pairing = _field_pairing()
        hessian_two = _homogeneous_degree_two(hessian, covector)
        paired_hessian = (pairing.inv() * hessian_two).applyfunc(sp.expand)
        paired_coefficients = _quadratic_coefficients(paired_hessian, covector)
        gauge = _gauge_derivative_coefficients()
        gauge_zeroth = _gauge_zeroth_coefficient()
        evolution = ConstraintAdjustedWeylCottonEvolution.build()
        evolution_coefficients = (
            sp.eye(EVOLUTION_RANK),
            *evolution.evolution_spatial_coefficients,
        )
        subsidiary_coefficients = (
            sp.eye(CONSTRAINT_RANK),
            *evolution.constraint_spatial_coefficients,
        )
        identity = _identity_coefficients(evolution)
        r1, r6_sharp_temporal = _relative_coefficients(gauge)
        schur = _natural_schur_coefficients()

        retained_scalar = _scalar_diagonal(
            sp.Matrix([[-1, 0, 0], [-4, -1, 0], [0, 0, -1]])
        )
        separated_scalar = _scalar_diagonal(-2 * sp.eye(3))

        tau, rho = sp.symbols("tau rho", real=True)
        aligned_values = (tau, rho, sp.Integer(0), sp.Integer(0))
        field_base = _symbol_from_quadratic_coefficients(
            paired_coefficients, aligned_values
        )
        gauge_symbol = tau * gauge[0] + rho * gauge[1]
        evolution_symbol = (
            tau * evolution_coefficients[0]
            + rho * evolution_coefficients[1]
        )
        subsidiary_symbol = (
            tau * subsidiary_coefficients[0]
            + rho * subsidiary_coefficients[1]
        )
        identity_symbol = tau * identity[0] + rho * identity[1]
        curvature_diagonal = sp.diag(
            evolution_symbol,
            -evolution_symbol.T,
            -subsidiary_symbol.T,
            -evolution_symbol.T,
        )
        off_diagonal_b = sp.zeros(FIELD_RANK, CURVATURE_RANK)
        off_diagonal_b[:, 26:66] = gauge_symbol * r1
        off_diagonal_c = sp.zeros(CURVATURE_RANK, FIELD_RANK)
        # Formal adjunction of a first-order identity contributes the minus.
        off_diagonal_c[26:66, :] = (
            -identity_symbol.T * (tau * r6_sharp_temporal)
        )

        def complete(scalar: sp.Matrix) -> sp.Matrix:
            field = field_base + tau**2 * scalar
            return field.row_join(off_diagonal_b).col_join(
                off_diagonal_c.row_join(curvature_diagonal)
            )

        retained_complete = complete(retained_scalar)
        separated_complete = complete(separated_scalar)
        retained_determinant = _connected_determinant(retained_complete)
        separated_determinant = _connected_determinant(separated_complete)

        characteristic_points = (
            (sp.Integer(1), sp.Integer(0)),
            (sp.Integer(0), sp.Integer(1)),
            (sp.Integer(1), sp.Integer(1)),
            (sp.Integer(1), sp.Integer(2)),
            (sp.Integer(1), sp.sqrt(3)),
            (sp.Integer(2), sp.Integer(1)),
        )
        retained_ranks = tuple(
            retained_complete.subs({tau: time, rho: space}).rank()
            for time, space in characteristic_points
        )
        separated_ranks = tuple(
            separated_complete.subs({tau: time, rho: space}).rank()
            for time, space in characteristic_points
        )

        # The exact polynomial Schur continuation is used only after its
        # aligned inverse identity and SO(3) covariance are checked below.
        schur_symbol = _symbol_from_quadratic_coefficients(
            schur, aligned_values
        )
        retained_field = field_base + tau**2 * retained_scalar - schur_symbol
        separated_field = field_base + tau**2 * separated_scalar - schur_symbol
        retained_temporal = retained_field.subs({tau: 1, rho: 0})
        separated_temporal = separated_field.subs({tau: 1, rho: 0})
        nilpotent = retained_temporal + sp.eye(FIELD_RANK)

        # A positive temporal-only multiplier exists for the separated
        # scalar choice.  It intentionally is not called a full symmetrizer.
        positive_temporal = -separated_temporal
        eigenvectors, _ = positive_temporal.diagonalize(normalize=False)
        inverse_eigenvectors = eigenvectors.inv()
        temporal_symmetrizer = (
            inverse_eigenvectors.T * inverse_eigenvectors
        ).applyfunc(sp.simplify)

        retained_field_coefficients = list(paired_coefficients)
        separated_field_coefficients = list(paired_coefficients)
        for index in range(len(SYMMETRIC_MONOMIALS)):
            retained_field_coefficients[index] -= schur[index]
            separated_field_coefficients[index] -= schur[index]
        temporal_index = SYMMETRIC_MONOMIALS.index((0, 0))
        retained_field_coefficients[temporal_index] += retained_scalar
        separated_field_coefficients[temporal_index] += separated_scalar
        retained_rank, retained_multiplier = _simultaneous_symmetric_multiplier(
            tuple(retained_field_coefficients)
        )
        separated_rank, separated_multiplier = _simultaneous_symmetric_multiplier(
            tuple(separated_field_coefficients)
        )
        temporal_defects = tuple(
            _matrix_nonzero_count(
                temporal_symmetrizer * coefficient
                - coefficient.T * temporal_symmetrizer
            )
            for coefficient in separated_field_coefficients
        )

        result = ExpandedRelativeFullSymbol(
            covector=covector,
            field_pairing=pairing,
            paired_hessian_coefficients=paired_coefficients,
            gauge_coefficients=gauge,
            gauge_zeroth_coefficient=gauge_zeroth,
            evolution_coefficients=evolution_coefficients,
            subsidiary_coefficients=subsidiary_coefficients,
            identity_coefficients=identity,
            r1=r1,
            r6_sharp_temporal=r6_sharp_temporal,
            schur_coefficients=schur,
            retained_scalar_diagonal=retained_scalar,
            separated_scalar_diagonal=separated_scalar,
            aligned_retained_symbol=retained_complete,
            aligned_separated_symbol=separated_complete,
            aligned_retained_determinant=retained_determinant,
            aligned_separated_determinant=separated_determinant,
            retained_characteristic_ranks=retained_ranks,
            separated_characteristic_ranks=separated_ranks,
            retained_temporal_field_jordan_ranks=(
                nilpotent.rank(),
                (nilpotent**2).rank(),
                (nilpotent**3).rank(),
            ),
            separated_temporal_field_symmetrizer=temporal_symmetrizer,
            separated_temporal_symmetrizer_defects=temporal_defects,
            retained_multiplier_rank=retained_rank,
            separated_multiplier_rank=separated_rank,
            retained_multiplier=retained_multiplier,
            separated_multiplier=separated_multiplier,
        )
        result.verify()
        return result

    def symbol(
        self, values: tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr], *, separated: bool
    ) -> sp.Matrix:
        """Return the complete 116-square weighted symbol at any covector."""

        if len(values) != 4:
            raise ValueError("a cylinder covector has four components")
        field = _symbol_from_quadratic_coefficients(
            self.paired_hessian_coefficients, values
        ) + values[0] ** 2 * (
            self.separated_scalar_diagonal
            if separated
            else self.retained_scalar_diagonal
        )
        gauge = sum(
            (value * coefficient for value, coefficient in zip(
                values, self.gauge_coefficients, strict=True
            )),
            sp.zeros(FIELD_RANK, 9),
        )
        evolution = sum(
            (value * coefficient for value, coefficient in zip(
                values, self.evolution_coefficients, strict=True
            )),
            sp.zeros(EVOLUTION_RANK),
        )
        subsidiary = sum(
            (value * coefficient for value, coefficient in zip(
                values, self.subsidiary_coefficients, strict=True
            )),
            sp.zeros(CONSTRAINT_RANK),
        )
        identity = sum(
            (value * coefficient for value, coefficient in zip(
                values, self.identity_coefficients, strict=True
            )),
            sp.zeros(CONSTRAINT_RANK, 40),
        )
        diagonal = sp.diag(
            evolution, -evolution.T, -subsidiary.T, -evolution.T
        )
        b = sp.zeros(FIELD_RANK, CURVATURE_RANK)
        b[:, 26:66] = gauge * self.r1
        c = sp.zeros(CURVATURE_RANK, FIELD_RANK)
        c[26:66, :] = -identity.T * (
            values[0] * self.r6_sharp_temporal
        )
        return field.row_join(b).col_join(c.row_join(diagonal))

    def verify(self) -> None:
        tau, rho = sp.symbols("tau rho", real=True)
        expected_retained = sp.factor(
            tau**48
            * (rho - 2 * tau) ** 8
            * (rho - tau) ** 30
            * (rho + tau) ** 30
            * (rho + 2 * tau) ** 8
            * (rho**2 - 3 * tau**2) ** 8
            / (2**16 * 3**8)
        )
        expected_separated = sp.factor(8 * expected_retained)
        if self.aligned_retained_determinant != expected_retained:
            raise AssertionError("retained-scalar characteristic drifted")
        if self.aligned_separated_determinant != expected_separated:
            raise AssertionError("separated-scalar characteristic drifted")
        expected_ranks = (116, 85, 88, 110, 108, 116)
        if self.retained_characteristic_ranks != expected_ranks:
            raise AssertionError("retained characteristic ranks drifted")
        if self.separated_characteristic_ranks != expected_ranks:
            raise AssertionError("separated characteristic ranks drifted")
        if self.retained_temporal_field_jordan_ranks != (2, 1, 0):
            raise AssertionError("retained scalar Jordan chain drifted")

        # Exact aligned Schur inverse identity with the corrected N# sign.
        evolution = (
            tau * self.evolution_coefficients[0]
            + rho * self.evolution_coefficients[1]
        )
        subsidiary = (
            tau * self.subsidiary_coefficients[0]
            + rho * self.subsidiary_coefficients[1]
        )
        identity = tau * self.identity_coefficients[0] + rho * self.identity_coefficients[1]
        equation_dual = -sp.diag(evolution.T, subsidiary.T)
        gauge = tau * self.gauge_coefficients[0] + rho * self.gauge_coefficients[1]
        aligned_schur = (
            gauge
            * self.r1
            * equation_dual.inv()
            * (-identity.T * (tau * self.r6_sharp_temporal))
        ).applyfunc(sp.factor)
        expected_schur = _symbol_from_quadratic_coefficients(
            self.schur_coefficients, (tau, rho, 0, 0)
        )
        if aligned_schur != expected_schur:
            raise AssertionError("aligned curvature Schur identity failed")

        # Globalization of that aligned formula: the constant part is an
        # intertwiner and the three mixed tables transform as a spatial
        # covector under every infinitesimal rotation.
        field_generators = _block_generators()[1]
        from .invariant_pairings import _rotation_generators

        spatial_rotations = tuple(
            generator[1:, 1:] for generator in _rotation_generators()
        )
        temporal_schur = self.schur_coefficients[
            SYMMETRIC_MONOMIALS.index((0, 0))
        ]
        mixed_schur = tuple(
            self.schur_coefficients[SYMMETRIC_MONOMIALS.index((0, axis))]
            for axis in range(1, 4)
        )
        for field_generator, rotation in zip(
            field_generators, spatial_rotations, strict=True
        ):
            if field_generator * temporal_schur != temporal_schur * field_generator:
                raise AssertionError("temporal Schur table is not SO(3)-invariant")
            for input_axis in range(3):
                right = sum(
                    (
                        rotation[output_axis, input_axis]
                        * mixed_schur[output_axis]
                        for output_axis in range(3)
                    ),
                    sp.zeros(FIELD_RANK),
                )
                if (
                    field_generator * mixed_schur[input_axis]
                    - mixed_schur[input_axis] * field_generator
                    != right
                ):
                    raise AssertionError("mixed Schur tables are not an SO(3) vector")

        # The selected time-only R6sharp and constant R1 are actual
        # coefficientwise intertwiners, but the extension is a choice.
        generators = _block_generators()
        if _intertwining_defect(generators[0], self.r1, generators[11]):
            raise AssertionError("R1 lost SO(3) equivariance")
        if _intertwining_defect(
            generators[10], self.r6_sharp_temporal, generators[1]
        ):
            raise AssertionError("R6sharp_0 lost SO(3) equivariance")

        # Positive temporal-only multiplier for the separated scalar block.
        h = self.separated_temporal_field_symmetrizer
        separated_field = _symbol_from_quadratic_coefficients(
            tuple(
                paired - schur
                for paired, schur in zip(
                    self.paired_hessian_coefficients,
                    self.schur_coefficients,
                    strict=True,
                )
            ),
            (1, 0, 0, 0),
        ) + self.separated_scalar_diagonal
        positive_temporal = -separated_field
        if h != h.T or h * positive_temporal != positive_temporal.T * h:
            raise AssertionError("separated temporal multiplier identity failed")
        if any(sp.factor(h[:size, :size].det()) <= 0 for size in range(1, 25)):
            raise AssertionError("separated temporal multiplier is not positive")
        weighted = h * positive_temporal
        if any(
            sp.factor(weighted[:size, :size].det()) <= 0
            for size in range(1, 25)
        ):
            raise AssertionError("separated temporal coefficient is not positive")
        if self.separated_temporal_symmetrizer_defects != (
            0, 26, 26, 26, 30, 30, 30, 30, 30, 30
        ):
            raise AssertionError("temporal-only multiplier defect ledger drifted")

        # The complete field-Schur simultaneous multiplier line is singular
        # and indefinite for both scalar choices.
        expected_multiplier = sp.zeros(FIELD_RANK)
        expected_multiplier[20:24, 20:24] = sp.diag(-1, 1, 1, 1)
        if (self.retained_multiplier_rank, self.separated_multiplier_rank) != (
            299,
            299,
        ):
            raise AssertionError("simultaneous multiplier rank drifted")
        for multiplier in (self.retained_multiplier, self.separated_multiplier):
            if multiplier != expected_multiplier:
                raise AssertionError("unique simultaneous multiplier drifted")
            if multiplier.rank() != 4:
                raise AssertionError("simultaneous multiplier rank is not four")

    def certificate(self) -> dict[str, object]:
        self.verify()
        tau, rho = sp.symbols("tau rho", real=True)
        h = self.separated_temporal_field_symmetrizer
        paired_hash = _digest(
            _symbol_from_quadratic_coefficients(
                self.paired_hessian_coefficients, self.covector
            )
        )
        return {
            "schema": "pure-weyl-expanded-relative-witness-full-symbol-v1",
            "block_order": [
                "M_aux[24]",
                "X_U[26]",
                "X_Eq_sharp[40]",
                "Y_U_sharp[26]",
            ],
            "exact_inputs": {
                "paired_action_Hessian_E2_sha256": paired_hash,
                "field_pairing_sha256": _digest(self.field_pairing),
                "gauge_K1_sha256": [
                    _digest(coefficient) for coefficient in self.gauge_coefficients
                ],
                "gauge_K_full_coefficient_sha256": _table_digest(
                    self.gauge_coefficients + (self.gauge_zeroth_coefficient,)
                ),
                "curvature_L1_sha256": [
                    _digest(coefficient)
                    for coefficient in self.evolution_coefficients
                ],
                "subsidiary_S1_sha256": [
                    _digest(coefficient)
                    for coefficient in self.subsidiary_coefficients
                ],
                "identity_N1_sha256": [
                    _digest(coefficient)
                    for coefficient in self.identity_coefficients
                ],
            },
            "pair_1_plus_6_extension": {
                "R1_order": 0,
                "R6sharp_formula": "R6sharp_0 nabla_0",
                "R6sharp_order": 1,
                "R1_sha256": _digest(self.r1),
                "R6sharp_0_sha256": _digest(self.r6_sharp_temporal),
                "coefficientwise_SO3_equivariant": True,
                "support_local": True,
                "spatial_coefficients_zero": True,
                "uniquely_derived_from_temporal_data": False,
                "four_dimensionally_natural": False,
            },
            "authoritative_provenance_bindings": {
                "field_pairing_certificate": (
                    "ordinary_derivative_auxiliary_system.json:"
                    "matrix_sha256.field_fibre_pairing"
                ),
                "gauge_generator_certificate": (
                    "curved_bv_conventions.json:"
                    "gauge_generator.coefficient_sha256"
                ),
                "hashes_compared_by_verifier": True,
            },
            "formal_adjoint_correction": {
                "identity": "Ncurvsharp(zeta)=-Ncurv(zeta)^T",
                "temporal_pair16_Schur": "+Pi_vector",
                "temporal_field_Schur": "J^-1 E2+Dscalar-Pi_vector",
                "old_coordinate_transpose_without_minus_rejected": True,
            },
            "complete_arbitrary_covector_symbol": {
                "shape": [COMPLETE_RANK, COMPLETE_RANK],
                "Douglis_orders": {"A": 2, "B": 1, "C": 2, "D": 1},
                "coefficient_tables_complete": True,
                "inverse_covector_used_in_definition": False,
                "SO3_globalization_exact": True,
                "aligned_covector": "(tau,rho,0,0)",
            },
            "curvature_Schur_polynomial": {
                "formula": "B D^-1 C=Z2(zeta)",
                "aligned_rational_identity_exact": True,
                "SO3_covariance_defect": 0,
                "Z2_nonzero_coefficients": [
                    _matrix_nonzero_count(coefficient)
                    for coefficient in self.schur_coefficients
                ],
                "Z2_sha256": [
                    _digest(coefficient) for coefficient in self.schur_coefficients
                ],
            },
            "retained_scalar_candidate": {
                "scalar_matrix": [[-1, 0, 0], [-4, -1, 0], [0, 0, -1]],
                "aligned_determinant": str(self.aligned_retained_determinant),
                "temporal_rank": self.retained_characteristic_ranks[0],
                "characteristic_ranks_at_tau_rho": {
                    "(0,1)": self.retained_characteristic_ranks[1],
                    "(1,1)": self.retained_characteristic_ranks[2],
                    "(1,2)": self.retained_characteristic_ranks[3],
                    "(1,sqrt(3))": self.retained_characteristic_ranks[4],
                    "(2,1)_generic": self.retained_characteristic_ranks[5],
                },
                "temporal_field_charpoly": "(lambda+1)^24",
                "temporal_field_diagonalizable": False,
                "nilpotent_ranks_N_N2_N3": list(
                    self.retained_temporal_field_jordan_ranks
                ),
                "pointwise_positive_temporal_field_symmetrizer_exists": False,
            },
            "separated_scalar_candidate": {
                "scalar_matrix": "-2 I_3 on (h00,f00,v0)",
                "aligned_determinant": str(self.aligned_separated_determinant),
                "same_characteristic_variety_as_retained": True,
                "characteristic_ranks": list(self.separated_characteristic_ranks),
                "temporal_field_charpoly": "(lambda+1)^21(lambda+2)^3",
                "temporal_field_diagonalizable": True,
                "temporal_positive_multiplier_sha256": _digest(h),
                "temporal_positive_multiplier_leading_minors": [
                    str(sp.factor(h[:size, :size].det()))
                    for size in range(1, 25)
                ],
                "weighted_temporal_leading_minors": [
                    str(
                        sp.factor(
                            (
                                h
                                * -(
                                    _symbol_from_quadratic_coefficients(
                                        tuple(
                                            paired - schur
                                            for paired, schur in zip(
                                                self.paired_hessian_coefficients,
                                                self.schur_coefficients,
                                                strict=True,
                                            )
                                        ),
                                        (1, 0, 0, 0),
                                    )
                                    + self.separated_scalar_diagonal
                                )
                            )[:size, :size].det()
                        )
                    )
                    for size in range(1, 25)
                ],
                "full_spatial_symmetrizer_defects": list(
                    self.separated_temporal_symmetrizer_defects
                ),
                "cyclic_scalar_lift_cross_certificate": (
                    "curved_expanded_relative_witness_scalar_cyclic_lift.json"
                ),
                "cyclic_scalar_lift_claimed_in_this_certificate": False,
            },
            "characteristic_conclusion": {
                "speeds": [
                    "-1",
                    "-1/sqrt(3)",
                    "-1/2",
                    "0",
                    "+1/2",
                    "+1/sqrt(3)",
                    "+1",
                ],
                "all_roots_real": True,
                "all_speeds_causal": True,
                "generic_covector_invertible": True,
                "characteristic_polynomial_total_Douglis_degree": 140,
            },
            "field_Schur_simultaneous_multiplier_no_go": {
                "equations": "H F2^{mu nu}=(F2^{mu nu})^T H, H=H^T",
                "unknown_symmetric_entries": 300,
                "retained_equation_rank": self.retained_multiplier_rank,
                "separated_equation_rank": self.separated_multiplier_rank,
                "solution_dimension": 1,
                "unique_generator": "diag(0_20,-1,+1,+1,+1)",
                "generator_rank": 4,
                "generator_inertia": {"positive": 3, "negative": 1, "zero": 20},
                "nondegenerate_pointwise_field_multiplier_exists": False,
                "positive_pointwise_field_symmetrizer_exists": False,
                "scope": (
                    "the local 24-component polynomial field Schur symbol only; "
                    "a differential symmetrizer after first-order reduction or a "
                    "full 116-component multiplier mixing curvature blocks is not ruled out"
                ),
            },
            "scope_and_open_work": {
                "arbitrary_covector_characteristic_certified_for_candidate": True,
                "positive_full_Douglis_symmetrizer_certified": False,
                "first_order_reduction_constructed": False,
                "cyclic_scalar_lift_cross_certificate_required": True,
                "lower_order_completion_certified": False,
                "all_BV_degrees_certified": False,
            },
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
