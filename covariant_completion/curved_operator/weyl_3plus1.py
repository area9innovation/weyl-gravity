"""Exact algebraic 3+1 decomposition of Weyl and Cotton tensors.

The module contains no evolution ansatz.  It constructs the ten-dimensional
four-dimensional algebraic Weyl bundle from its electric and magnetic STF
parts in a normal orthonormal cylinder frame and derives the algebraic bundle
of its first divergence directly from the covariant symbol

``V_{mu,nu,sigma} = nabla^rho Psi_{mu,rho,nu,sigma}``.

The latter calculation is deliberately included here: the span of first
divergences is sixteen-dimensional, and its natural spatial coordinates are
two trace-free (not necessarily symmetric) three-by-three tensors.  Thus a
first-order Bach prolongation must retain a Cotton-type 16-component slot;
the ten electric/magnetic Weyl components alone cannot be assumed to close.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import sympy as sp


SPACETIME_DIMENSION = 4
SPATIAL_DIMENSION = 3
WEYL_DIMENSION = 10
COTTON_DIMENSION = 16


def _matrix_rows(matrix: sp.Matrix) -> list[list[str]]:
    """Serialize an exact rational matrix without losing normalization data."""

    return [[str(value) for value in row] for row in matrix.tolist()]


def epsilon(i: int, j: int, k: int) -> sp.Integer:
    """The positively oriented spatial Levi-Civita symbol."""

    return sp.Integer(sp.LeviCivita(i, j, k))


def stf_basis() -> tuple[sp.Matrix, ...]:
    """A rational basis of symmetric trace-free three-by-three tensors."""

    return (
        sp.diag(1, -1, 0),
        sp.diag(1, 1, -2),
        sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 0]]),
        sp.Matrix([[0, 0, 1], [0, 0, 0], [1, 0, 0]]),
        sp.Matrix([[0, 0, 0], [0, 0, 1], [0, 1, 0]]),
    )


def tracefree_matrix_basis() -> tuple[sp.Matrix, ...]:
    """STF(5) plus antisymmetric-vector(3) basis of ``sl(3)``."""

    antisymmetric = tuple(
        sp.Matrix(
            3,
            3,
            lambda i, j, axis=axis: epsilon(i, j, axis),
        )
        for axis in range(3)
    )
    return stf_basis() + antisymmetric


def _ordered_pair(first: int, second: int) -> tuple[tuple[int, int] | None, int]:
    if first == second:
        return None, 0
    if first < second:
        return (first, second), 1
    return (second, first), -1


def weyl_component(
    electric: sp.Matrix,
    magnetic: sp.Matrix,
    a: int,
    b: int,
    c: int,
    d: int,
) -> sp.Expr:
    """Return ``Psi_abcd`` from electric and magnetic STF components.

    The conventions are

    ``E_ij = Psi_0i0j`` and
    ``B_ij = (1/2) epsilon_i^kl Psi_0jkl``

    with all spacetime indices lowered and signature ``(-,+,+,+)``.
    """

    first_pair, first_sign = _ordered_pair(a, b)
    second_pair, second_sign = _ordered_pair(c, d)
    if first_pair is None or second_pair is None:
        return sp.Integer(0)
    if first_pair > second_pair:
        first_pair, second_pair = second_pair, first_pair
    sign = first_sign * second_sign
    zero_count = int(0 in first_pair) + int(0 in second_pair)
    if zero_count == 2:
        return sp.expand(
            sign * electric[first_pair[1] - 1, second_pair[1] - 1]
        )
    if zero_count == 1:
        # Pair ordering puts the time-containing pair first.
        spatial = first_pair[1] - 1
        return sp.expand(
            sign
            * sum(
                epsilon(axis, second_pair[0] - 1, second_pair[1] - 1)
                * magnetic[axis, spatial]
                for axis in range(3)
            )
        )
    if zero_count == 0:
        i, j = first_pair[0] - 1, first_pair[1] - 1
        k, l = second_pair[0] - 1, second_pair[1] - 1
        return sp.expand(
            -sign
            * sum(
                epsilon(i, j, left)
                * epsilon(k, l, right)
                * electric[left, right]
                for left in range(3)
                for right in range(3)
            )
        )
    return sp.Integer(0)


def _rank4_row(a: int, b: int, c: int, d: int) -> int:
    return ((a * 4 + b) * 4 + c) * 4 + d


def _rank3_row(a: int, b: int, c: int) -> int:
    return (a * 4 + b) * 4 + c


def _rank2_row(a: int, b: int) -> int:
    return 4 * a + b


def tracefree_symmetric_spacetime_basis() -> tuple[sp.Matrix, ...]:
    """SO(3)-adapted basis ``scalar(1)+mixed vector(3)+spatial STF(5)``."""

    scalar = sp.diag(3, 1, 1, 1)
    mixed = []
    for spatial in range(1, 4):
        tensor = sp.zeros(4)
        tensor[0, spatial] = tensor[spatial, 0] = 1
        mixed.append(tensor)
    spatial_stf = []
    for source in stf_basis():
        tensor = sp.zeros(4)
        tensor[1:, 1:] = source
        spatial_stf.append(tensor)
    return (scalar,) + tuple(mixed) + tuple(spatial_stf)


@dataclass(frozen=True)
class WeylCottonThreePlusOne:
    """Exact fibre matrices for the Weyl/Cotton 3+1 decomposition."""

    weyl_reconstruction: sp.Matrix
    electric_magnetic_extraction: sp.Matrix
    weyl_hodge: sp.Matrix
    divergence_symbols: tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix]
    cotton_span: sp.Matrix
    cotton_xy_extraction: sp.Matrix
    cotton_xy_reconstruction: sp.Matrix
    cotton_hodge: sp.Matrix
    cotton_coordinate_inclusion: sp.Matrix
    cotton_coordinate_extraction: sp.Matrix
    cotton_reconstruction: sp.Matrix
    cotton_divergence_coefficients: tuple[
        sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix
    ]
    cotton_coordinate_hodge: sp.Matrix

    @staticmethod
    def build(*, verify: bool = True) -> "WeylCottonThreePlusOne":
        basis = stf_basis()
        reconstruction = sp.zeros(4**4, WEYL_DIMENSION)
        for column in range(WEYL_DIMENSION):
            electric = basis[column] if column < 5 else sp.zeros(3)
            magnetic = basis[column - 5] if column >= 5 else sp.zeros(3)
            for a, b, c, d in product(range(4), repeat=4):
                reconstruction[_rank4_row(a, b, c, d), column] = weyl_component(
                    electric, magnetic, a, b, c, d
                )

        gram = sp.diag(2, 6, 2, 2, 2)
        extraction = sp.zeros(WEYL_DIMENSION, 4**4)
        # Extract E and B as spatial matrices, then resolve them in the STF basis.
        gram_inverse = gram.inv()
        for column in range(5):
            for i, j in product(range(3), repeat=2):
                coefficient = sum(
                    gram_inverse[column, row] * basis[row][i, j]
                    for row in range(5)
                )
                extraction[column, _rank4_row(0, i + 1, 0, j + 1)] += coefficient
                for k, l in product(range(3), repeat=2):
                    extraction[5 + column, _rank4_row(0, j + 1, k + 1, l + 1)] += (
                        sp.Rational(1, 2)
                        * epsilon(i, k, l)
                        * coefficient
                    )

        # Lorentzian Hodge star on the first antisymmetric pair.  In the
        # chosen orientation it acts on E/B coordinates as (E,B)->(B,-E).
        inverse_metric = sp.diag(-1, 1, 1, 1)
        ambient_hodge = sp.zeros(4**4)
        for a, b, c, d in product(range(4), repeat=4):
            for raised_first, raised_second, lower_first, lower_second in product(
                range(4), repeat=4
            ):
                ambient_hodge[
                    _rank4_row(a, b, c, d),
                    _rank4_row(lower_first, lower_second, c, d),
                ] += (
                    sp.Rational(1, 2)
                    * sp.LeviCivita(a, b, raised_first, raised_second)
                    * inverse_metric[raised_first, lower_first]
                    * inverse_metric[raised_second, lower_second]
                )
        weyl_hodge = extraction * ambient_hodge * reconstruction

        # V_{mu,nu,sigma}=nabla^rho Psi_{mu,rho,nu,sigma}.  At a normal
        # frame the four symbol matrices differ only by the raised-derivative
        # signature sign.
        divergence_symbols: list[sp.Matrix] = []
        for derivative in range(4):
            raised_sign = -1 if derivative == 0 else 1
            symbol = sp.zeros(4**3, WEYL_DIMENSION)
            for mu, nu, sigma in product(range(4), repeat=3):
                symbol[_rank3_row(mu, nu, sigma), :] = (
                    raised_sign
                    * reconstruction[_rank4_row(mu, derivative, nu, sigma), :]
                )
            divergence_symbols.append(symbol)
        divergence_span = sp.Matrix.hstack(*divergence_symbols)
        cotton_columns = sp.Matrix.hstack(*divergence_span.columnspace())

        # Divergence after Hodge dualization contains no second independent
        # 16-component slot: it is an algebraic complex structure on the
        # same Cotton bundle.
        cotton_left_inverse = (
            (cotton_columns.T * cotton_columns).inv() * cotton_columns.T
        )
        divergence_coordinates = cotton_left_inverse * divergence_span
        dual_divergence_span = sp.Matrix.hstack(
            *(symbol * weyl_hodge for symbol in divergence_symbols)
        )
        dual_divergence_coordinates = cotton_left_inverse * dual_divergence_span
        divergence_right_inverse = (
            divergence_coordinates.T
            * (divergence_coordinates * divergence_coordinates.T).inv()
        )
        cotton_hodge = dual_divergence_coordinates * divergence_right_inverse

        # X_ij=V_i0j and Y_ij=(1/2) eps_j^kl V_ikl.  Both are trace-free;
        # these two sl(3) matrices are exact coordinates on the Cotton span.
        xy = sp.zeros(18, 4**3)
        for i, j in product(range(3), repeat=2):
            xy[3 * i + j, _rank3_row(i + 1, 0, j + 1)] = 1
            for k, l in product(range(3), repeat=2):
                xy[9 + 3 * i + j, _rank3_row(i + 1, k + 1, l + 1)] += (
                    sp.Rational(1, 2) * epsilon(j, k, l)
                )
        restricted_xy = xy * cotton_columns
        left_inverse = (restricted_xy.T * restricted_xy).inv() * restricted_xy.T
        xy_reconstruction = cotton_columns * left_inverse

        tracefree_basis = tracefree_matrix_basis()
        coordinate_inclusion = sp.zeros(18, COTTON_DIMENSION)
        for block in range(2):
            for column, matrix in enumerate(tracefree_basis):
                for i, j in product(range(3), repeat=2):
                    coordinate_inclusion[
                        9 * block + 3 * i + j, 8 * block + column
                    ] = matrix[i, j]
        coordinate_extraction = (
            (coordinate_inclusion.T * coordinate_inclusion).inv()
            * coordinate_inclusion.T
        )
        cotton_reconstruction = xy_reconstruction * coordinate_inclusion
        cotton_divergence_coefficients = tuple(
            coordinate_extraction * xy * symbol for symbol in divergence_symbols
        )
        coordinate_divergence = sp.Matrix.hstack(*cotton_divergence_coefficients)
        coordinate_dual_divergence = sp.Matrix.hstack(
            *(
                coordinate_extraction * xy * symbol * weyl_hodge
                for symbol in divergence_symbols
            )
        )
        coordinate_hodge = (
            coordinate_dual_divergence
            * coordinate_divergence.T
            * (coordinate_divergence * coordinate_divergence.T).inv()
        )

        result = WeylCottonThreePlusOne(
            weyl_reconstruction=reconstruction,
            electric_magnetic_extraction=extraction,
            weyl_hodge=weyl_hodge,
            divergence_symbols=tuple(divergence_symbols),
            cotton_span=cotton_columns,
            cotton_xy_extraction=xy,
            cotton_xy_reconstruction=xy_reconstruction,
            cotton_hodge=cotton_hodge,
            cotton_coordinate_inclusion=coordinate_inclusion,
            cotton_coordinate_extraction=coordinate_extraction,
            cotton_reconstruction=cotton_reconstruction,
            cotton_divergence_coefficients=cotton_divergence_coefficients,
            cotton_coordinate_hodge=coordinate_hodge,
        )
        if verify:
            result.verify()
        return result

    def verify(self) -> None:
        reconstruction = self.weyl_reconstruction
        if reconstruction.shape != (256, WEYL_DIMENSION):
            raise AssertionError("wrong Weyl reconstruction shape")
        if reconstruction.rank() != WEYL_DIMENSION:
            raise AssertionError("electric/magnetic Weyl reconstruction is singular")
        if self.electric_magnetic_extraction * reconstruction != sp.eye(10):
            raise AssertionError("electric/magnetic extraction is not inverse")
        if self.weyl_hodge != sp.zeros(5).row_join(sp.eye(5)).col_join(
            (-sp.eye(5)).row_join(sp.zeros(5))
        ):
            raise AssertionError("Lorentzian Weyl Hodge convention drifted")
        if self.weyl_hodge**2 != -sp.eye(WEYL_DIMENSION):
            raise AssertionError("Lorentzian Weyl Hodge star does not square to -1")

        metric_inverse = sp.diag(-1, 1, 1, 1)
        for column in range(WEYL_DIMENSION):
            component = lambda a, b, c, d: reconstruction[
                _rank4_row(a, b, c, d), column
            ]
            for a, b, c, d in product(range(4), repeat=4):
                if component(a, b, c, d) + component(b, a, c, d) != 0:
                    raise AssertionError("Weyl first-pair antisymmetry failed")
                if component(a, b, c, d) + component(a, b, d, c) != 0:
                    raise AssertionError("Weyl second-pair antisymmetry failed")
                if component(a, b, c, d) - component(c, d, a, b) != 0:
                    raise AssertionError("Weyl pair symmetry failed")
                if (
                    component(a, b, c, d)
                    + component(a, c, d, b)
                    + component(a, d, b, c)
                    != 0
                ):
                    raise AssertionError("Weyl algebraic Bianchi identity failed")
            for b, d in product(range(4), repeat=2):
                trace = sum(
                    metric_inverse[a, c] * component(a, b, c, d)
                    for a, c in product(range(4), repeat=2)
                )
                if sp.expand(trace) != 0:
                    raise AssertionError("Weyl trace failed")

        if any(symbol.rank() != WEYL_DIMENSION for symbol in self.divergence_symbols):
            raise AssertionError("nonzero directional Weyl divergence lost rank")
        if self.cotton_span.shape != (64, COTTON_DIMENSION):
            raise AssertionError("first-divergence span is not the Cotton-16 bundle")
        if self.cotton_span.rank() != COTTON_DIMENSION:
            raise AssertionError("Cotton basis is singular")
        divergence_span = sp.Matrix.hstack(*self.divergence_symbols)
        dual_divergence_span = sp.Matrix.hstack(
            *(symbol * self.weyl_hodge for symbol in self.divergence_symbols)
        )
        if sp.Matrix.vstack(divergence_span, dual_divergence_span).rank() != 16:
            raise AssertionError("dual divergence introduced a spurious Cotton slot")
        cotton_left_inverse = (
            (self.cotton_span.T * self.cotton_span).inv() * self.cotton_span.T
        )
        if self.cotton_span * cotton_left_inverse * dual_divergence_span != (
            dual_divergence_span
        ):
            raise AssertionError("dual divergence escaped the Cotton bundle")
        if (
            self.cotton_hodge * cotton_left_inverse * divergence_span
            != cotton_left_inverse * dual_divergence_span
        ):
            raise AssertionError("Cotton Hodge action does not intertwine divergence")
        if self.cotton_hodge**2 != -sp.eye(COTTON_DIMENSION):
            raise AssertionError("Cotton Hodge action does not square to -1")
        restricted = self.cotton_xy_extraction * self.cotton_span
        if restricted.rank() != COTTON_DIMENSION:
            raise AssertionError("X/Y coordinates do not separate Cotton tensors")
        if self.cotton_xy_reconstruction * restricted != self.cotton_span:
            raise AssertionError("Cotton X/Y reconstruction is not inverse on the span")
        trace_x = sum(
            (self.cotton_xy_extraction[3 * i + i, :] for i in range(3)),
            sp.zeros(1, 64),
        )
        trace_y = sum(
            (self.cotton_xy_extraction[9 + 3 * i + i, :] for i in range(3)),
            sp.zeros(1, 64),
        )
        if trace_x * self.cotton_span != sp.zeros(1, COTTON_DIMENSION):
            raise AssertionError("Cotton X is not trace-free")
        if trace_y * self.cotton_span != sp.zeros(1, COTTON_DIMENSION):
            raise AssertionError("Cotton Y is not trace-free")
        if (
            self.cotton_coordinate_extraction * self.cotton_coordinate_inclusion
            != sp.eye(COTTON_DIMENSION)
        ):
            raise AssertionError("natural Cotton coordinate extraction is not inverse")
        if self.cotton_reconstruction.rank() != COTTON_DIMENSION:
            raise AssertionError("natural Cotton reconstruction is singular")
        for symbol, coefficient in zip(
            self.divergence_symbols,
            self.cotton_divergence_coefficients,
            strict=True,
        ):
            if self.cotton_reconstruction * coefficient != symbol:
                raise AssertionError("3+1 Cotton coefficient table lost divergence data")
        coordinate_divergence = sp.Matrix.hstack(
            *self.cotton_divergence_coefficients
        )
        coordinate_dual_divergence = sp.Matrix.hstack(
            *(
                self.cotton_coordinate_extraction
                * self.cotton_xy_extraction
                * symbol
                * self.weyl_hodge
                for symbol in self.divergence_symbols
            )
        )
        if self.cotton_coordinate_hodge * coordinate_divergence != (
            coordinate_dual_divergence
        ):
            raise AssertionError("natural Cotton Hodge table does not intertwine")
        if self.cotton_coordinate_hodge**2 != -sp.eye(COTTON_DIMENSION):
            raise AssertionError("natural Cotton Hodge table does not square to -1")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-cotton-3plus1-algebra-v1",
            "frame": "normal orthonormal (-,+,+,+), spatial orientation +123",
            "weyl_bundle_dimension": WEYL_DIMENSION,
            "weyl_coordinates": "E_STF(5) + B_STF(5)",
            "weyl_reconstruction_rank": self.weyl_reconstruction.rank(),
            "electric_magnetic_extraction_inverse": True,
            "weyl_symmetries_trace_and_bianchi": True,
            "weyl_hodge_on_EB": "(E,B)->(B,-E)",
            "weyl_hodge_square": "-I_10",
            "first_divergence": "V_mu,nu,sigma=nabla^rho Psi_mu,rho,nu,sigma",
            "directional_divergence_ranks": [
                symbol.rank() for symbol in self.divergence_symbols
            ],
            "cotton_bundle_dimension": self.cotton_span.rank(),
            "dual_divergence_joint_dimension": 16,
            "cotton_hodge_square": "-I_16",
            "cotton_coordinates": (
                "X_ij=V_i0j and Y_ij=(1/2)epsilon_j^kl V_ikl; "
                "each is a trace-free 3x3 matrix"
            ),
            "cotton_first_order_table_shapes": [
                list(matrix.shape) for matrix in self.cotton_divergence_coefficients
            ],
            "weyl_hodge_matrix": _matrix_rows(self.weyl_hodge),
            "cotton_hodge_matrix": _matrix_rows(self.cotton_coordinate_hodge),
            "cotton_first_order_tables": [
                _matrix_rows(matrix)
                for matrix in self.cotton_divergence_coefficients
            ],
            "cotton_first_order_identity": (
                "c=sum_alpha L^alpha nabla_alpha(E,B), derived by exact contraction"
            ),
            "dual_cotton_is_algebraic": True,
            "SO3_decomposition": "2 x (STF_2[5] + vector[3])",
            "ten_component_EB_first_order_closure_assumed": False,
            "minimal_first_divergence_slot_required": COTTON_DIMENSION,
            "derivation": "exact covariant divergence symbol of reconstructed Weyl tensor",
            "fitted_coefficients": False,
        }


@dataclass(frozen=True)
class WeylCottonBachFirstOrder:
    """Exact first-order curvature/Cotton form of Bach plus compatibility.

    With ``u=(E,B)`` and the natural sixteen Cotton coordinates ``c``, the
    system is

    ``c-L^alpha nabla_alpha u=0``,
    ``M^alpha nabla_alpha c+N u=0``,
    ``M^alpha J_C nabla_alpha c+N J_W u=0``.

    The last row is ``C_1^sharp star Psi=0``.  Every coefficient follows by
    contraction from the covariant Weyl tensor; no spectral data or fitted
    lower-order term enters.
    """

    decomposition: WeylCottonThreePlusOne
    bach_derivative_coefficients: tuple[
        sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix
    ]
    bach_zeroth_coefficient: sp.Matrix
    compatibility_derivative_coefficients: tuple[
        sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix
    ]
    compatibility_zeroth_coefficient: sp.Matrix
    temporal_matrix: sp.Matrix
    evolution_coefficients: tuple[sp.Matrix, sp.Matrix, sp.Matrix]

    @staticmethod
    def build(*, verify: bool = True) -> "WeylCottonBachFirstOrder":
        decomposition = WeylCottonThreePlusOne.build()
        inverse_metric = sp.diag(-1, 1, 1, 1)
        ricci_up = sp.diag(0, 2, 2, 2)

        # Full rank-two derivative coefficients of
        # nabla^sigma V_{mu,nu,sigma}.
        full_derivatives: list[sp.Matrix] = []
        for derivative in range(4):
            coefficient = sp.zeros(16, COTTON_DIMENSION)
            for mu, nu in product(range(4), repeat=2):
                for sigma in range(4):
                    coefficient[_rank2_row(mu, nu), :] += (
                        inverse_metric[sigma, derivative]
                        * decomposition.cotton_reconstruction[
                            _rank3_row(mu, nu, sigma), :
                        ]
                    )
            full_derivatives.append(coefficient)

        # The algebraic cylinder-curvature term
        # (1/2) Ric^{rho sigma} Psi_{mu rho nu sigma}.
        full_zeroth = sp.zeros(16, WEYL_DIMENSION)
        for mu, nu in product(range(4), repeat=2):
            for rho, sigma in product(range(4), repeat=2):
                full_zeroth[_rank2_row(mu, nu), :] += (
                    sp.Rational(1, 2)
                    * ricci_up[rho, sigma]
                    * decomposition.weyl_reconstruction[
                        _rank4_row(mu, rho, nu, sigma), :
                    ]
                )

        # Project to the nine-component symmetric trace-free Bach target.
        stf_basis_4 = tracefree_symmetric_spacetime_basis()
        inclusion = sp.zeros(16, 9)
        for column, tensor in enumerate(stf_basis_4):
            for a, b in product(range(4), repeat=2):
                inclusion[_rank2_row(a, b), column] = tensor[a, b]
        extraction = (inclusion.T * inclusion).inv() * inclusion.T
        projector = sp.zeros(16)
        metric = inverse_metric
        for a, b, c, d in product(range(4), repeat=4):
            projector[_rank2_row(a, b), _rank2_row(c, d)] = (
                sp.Rational(1, 2)
                * (int(a == c and b == d) + int(a == d and b == c))
                - sp.Rational(1, 4) * metric[a, b] * inverse_metric[c, d]
            )
        projection_coordinates = extraction * projector
        bach_derivatives = tuple(
            projection_coordinates * coefficient for coefficient in full_derivatives
        )
        bach_zeroth = projection_coordinates * full_zeroth
        compatibility_derivatives = tuple(
            coefficient * decomposition.cotton_coordinate_hodge
            for coefficient in bach_derivatives
        )
        compatibility_zeroth = bach_zeroth * decomposition.weyl_hodge

        # Principal temporal table on state (u[10],c[16]).  Algebraic c in
        # the defining equation is lower order and therefore absent here.
        zero_16 = sp.zeros(16, 16)
        zero_9_10 = sp.zeros(9, 10)
        temporal = (
            (-decomposition.cotton_divergence_coefficients[0]).row_join(zero_16)
            .col_join(zero_9_10.row_join(bach_derivatives[0]))
            .col_join(zero_9_10.row_join(compatibility_derivatives[0]))
        )
        independent_rows = tuple(temporal.T.rref()[1])
        evolution_temporal = temporal[list(independent_rows), :]
        evolution_coefficients: list[sp.Matrix] = []
        for spatial_axis in range(1, 4):
            spatial = (
                (-decomposition.cotton_divergence_coefficients[spatial_axis])
                .row_join(zero_16)
                .col_join(
                    zero_9_10.row_join(bach_derivatives[spatial_axis])
                )
                .col_join(
                    zero_9_10.row_join(
                        compatibility_derivatives[spatial_axis]
                    )
                )
            )
            evolution_coefficients.append(
                evolution_temporal.inv() * spatial[list(independent_rows), :]
            )

        result = WeylCottonBachFirstOrder(
            decomposition=decomposition,
            bach_derivative_coefficients=bach_derivatives,
            bach_zeroth_coefficient=bach_zeroth,
            compatibility_derivative_coefficients=compatibility_derivatives,
            compatibility_zeroth_coefficient=compatibility_zeroth,
            temporal_matrix=temporal,
            evolution_coefficients=tuple(evolution_coefficients),
        )
        if verify:
            result.verify()
        return result

    def verify(self) -> None:
        expected_bach_shape = (9, COTTON_DIMENSION)
        if any(
            matrix.shape != expected_bach_shape
            for matrix in self.bach_derivative_coefficients
        ):
            raise AssertionError("wrong first-order Bach derivative shape")
        if self.bach_zeroth_coefficient.shape != (9, WEYL_DIMENSION):
            raise AssertionError("wrong Bach curvature-coefficient shape")
        if any(
            matrix.shape != expected_bach_shape
            for matrix in self.compatibility_derivative_coefficients
        ):
            raise AssertionError("wrong dual-compatibility derivative shape")
        if self.compatibility_zeroth_coefficient.shape != (9, WEYL_DIMENSION):
            raise AssertionError("wrong dual-compatibility curvature shape")
        for bach, compatibility in zip(
            self.bach_derivative_coefficients,
            self.compatibility_derivative_coefficients,
            strict=True,
        ):
            if compatibility != bach * self.decomposition.cotton_coordinate_hodge:
                raise AssertionError("dual Cotton row was not induced by Hodge")
        if self.compatibility_zeroth_coefficient != (
            self.bach_zeroth_coefficient * self.decomposition.weyl_hodge
        ):
            raise AssertionError("dual Weyl lower term was not induced by Hodge")
        if self.temporal_matrix.shape != (34, 26):
            raise AssertionError("wrong curvature/Cotton temporal table shape")
        if self.temporal_matrix.rank() != 26:
            raise AssertionError("curvature/Cotton equations do not determine all time derivatives")
        independent_rows = tuple(self.temporal_matrix.T.rref()[1])
        constraint_rows = tuple(
            row for row in range(self.temporal_matrix.rows) if row not in independent_rows
        )
        if constraint_rows != (5, 6, 7, 13, 14, 15, 16, 25):
            raise AssertionError("curvature/Cotton evolution-constraint split drifted")
        spectral_parameter = sp.Symbol("lambda")
        expected_characteristic = (
            spectral_parameter**2
            * (spectral_parameter**2 - 1) ** 8
            * (4 * spectral_parameter**2 - 1) ** 2
            * (3 * spectral_parameter**2 + 1) ** 2
            / 144
        )
        for evolution in self.evolution_coefficients:
            if sp.factor(evolution.charpoly().as_expr()) != sp.factor(
                expected_characteristic
            ):
                raise AssertionError("SO(3)-adapted unadjusted characteristic drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        nonzero_lower = sum(
            int(value != 0) for value in self.bach_zeroth_coefficient
        )
        independent_rows = tuple(self.temporal_matrix.T.rref()[1])
        constraint_rows = tuple(
            row for row in range(self.temporal_matrix.rows) if row not in independent_rows
        )
        return {
            "schema": "pure-weyl-cotton-bach-first-order-v1",
            "derivation": (
                "exact contraction of V=nabla^rho Psi_mu,rho,nu,sigma, "
                "B=nabla^sigma V_mu,nu,sigma+(1/2)Ric^rho,sigma "
                "Psi_mu,rho,nu,sigma, and its Hodge dual"
            ),
            "state_bundle": {
                "Weyl_EB": WEYL_DIMENSION,
                "Cotton_XY": COTTON_DIMENSION,
                "total": 26,
            },
            "equation_rows": {
                "Cotton_definition": 16,
                "Bach_STF": 9,
                "dual_compatibility_STF": 9,
                "total": 34,
            },
            "temporal_matrix_shape": list(self.temporal_matrix.shape),
            "temporal_matrix_rank": self.temporal_matrix.rank(),
            "principal_constraint_count": 34 - self.temporal_matrix.rank(),
            "independent_temporal_rows": list(independent_rows),
            "constraint_rows": list(constraint_rows),
            "evolution_row_decomposition": {
                "Cotton_definition_STF": 10,
                "Bach": 8,
                "dual_compatibility": 8,
            },
            "constraint_row_decomposition": {
                "Cotton_definition_vectors": 6,
                "Bach_scalar": 1,
                "dual_compatibility_scalar": 1,
            },
            "canonical_unadjusted_characteristic": (
                "lambda^2 (lambda^2-1)^8 (4lambda^2-1)^2 "
                "(3lambda^2+1)^2 / 144"
            ),
            "canonical_unadjusted_speeds": {
                "0": 2,
                "+1": 8,
                "-1": 8,
                "+1/2": 2,
                "-1/2": 2,
                "+i/sqrt(3)": 2,
                "-i/sqrt(3)": 2,
            },
            "canonical_unadjusted_reduction_hyperbolic": False,
            "constraint_addition_required_for_hyperbolic_reduction": True,
            "bach_derivative_table_shapes": [
                list(matrix.shape) for matrix in self.bach_derivative_coefficients
            ],
            "bach_zeroth_table_shape": list(self.bach_zeroth_coefficient.shape),
            "bach_derivative_tables": [
                _matrix_rows(matrix)
                for matrix in self.bach_derivative_coefficients
            ],
            "bach_zeroth_table": _matrix_rows(self.bach_zeroth_coefficient),
            "compatibility_derivative_tables": [
                _matrix_rows(matrix)
                for matrix in self.compatibility_derivative_coefficients
            ],
            "compatibility_zeroth_table": _matrix_rows(
                self.compatibility_zeroth_coefficient
            ),
            "bach_zeroth_nonzero_entries": nonzero_lower,
            "cylinder_Ricci_lower_term_included": True,
            "dual_rows_induced_by_exact_Hodge": True,
            "fitted_coefficients": False,
            "first_order_covariant_closure_table_derived": True,
            "evolution_constraint_split_derived": False,
            "symmetric_hyperbolicity_proved": False,
            "sourced_constraint_identity_proved": False,
            "exhaustive_curved_jet_comparison_proved": False,
            "fail_closed": True,
        }
