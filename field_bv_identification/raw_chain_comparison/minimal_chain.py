"""Exact minimal-BV to raw-detour chain isomorphism.

The field-theoretic basis contains a full symmetric metric and its full
antifield.  The raw basis uses trace-free tensors plus scalar trace rows.
The triangular ghost change

``Omega = omega + (partial.c)/4``

and its antifield companion put the tangent differential into the certified
raw form.  No rank comparison is used: both chain maps and their inverses
are explicit exact matrices.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from bridge.bv_complex.conformal_polynomials import (
    DIMENSION,
    SYMMETRIC_PAIRS,
    TRACEFREE_INCLUSION,
    TRACEFREE_PROJECTION,
    homogeneous_monomials,
)
from bridge.bv_complex.polynomial_bv import PolynomialBVBlock
from field_bv_identification.minimal_master_action.free_master_action import (
    MinimalBVBlock,
    scalar_gradient_matrix,
    symmetric_trace_matrix,
    vector_divergence_matrix,
)


def _component_map(matrix: sp.MatrixBase, monomial_count: int) -> sp.SparseMatrix:
    return sp.SparseMatrix(sp.kronecker_product(matrix, sp.eye(monomial_count)))


def _metric_trace_vector(monomial_count: int, coefficient: sp.Expr) -> sp.SparseMatrix:
    entries: dict[tuple[int, int], sp.Expr] = {}
    for pair_index, (first, second) in enumerate(SYMMETRIC_PAIRS):
        if first != second:
            continue
        for monomial in range(monomial_count):
            entries[pair_index * monomial_count + monomial, monomial] = coefficient
    return sp.SparseMatrix(
        len(SYMMETRIC_PAIRS) * monomial_count, monomial_count, entries
    )


def _direct_sum(matrices: tuple[sp.MatrixBase, ...]) -> sp.SparseMatrix:
    if not matrices:
        return sp.SparseMatrix(0, 0, {})
    return sp.diag(*matrices, cls=sp.SparseMatrix)


def _sparse_product_dok(
    left: sp.MatrixBase, right: sp.MatrixBase
) -> dict[tuple[int, int], sp.Expr]:
    """Multiply sparse DOK maps without allocating an ambient dense block."""

    right_by_row: dict[int, list[tuple[int, sp.Expr]]] = {}
    for (row, column), value in right.todok().items():
        right_by_row.setdefault(row, []).append((column, value))
    output: dict[tuple[int, int], sp.Expr] = {}
    for (row, contracted), left_value in left.todok().items():
        for column, right_value in right_by_row.get(contracted, ()):
            key = (row, column)
            output[key] = sp.simplify(
                output.get(key, sp.Integer(0)) + left_value * right_value
            )
            if output[key] == 0:
                del output[key]
    return output


@dataclass(frozen=True)
class MinimalRawComparison:
    """An exact isomorphism of the two four-row tangent complexes."""

    energy: int
    bv: MinimalBVBlock
    raw: PolynomialBVBlock
    field_to_raw: sp.SparseMatrix
    raw_to_field: sp.SparseMatrix
    row_maps: tuple[tuple[str, sp.SparseMatrix, sp.SparseMatrix], ...]
    trace_projector: sp.SparseMatrix
    trace_homotopy: sp.SparseMatrix

    @classmethod
    def at_energy(cls, energy: int) -> "MinimalRawComparison":
        bv = MinimalBVBlock.at_energy(energy)
        raw = PolynomialBVBlock.at_energy(energy)
        if bv.dimension != raw.dimension:
            raise AssertionError("field and raw complexes have different dimensions")

        vector_ghost = DIMENSION * len(homogeneous_monomials(energy + 1))
        scalar_ghost = len(homogeneous_monomials(energy))
        metric_monomials = len(homogeneous_monomials(energy))
        equation_monomials = len(homogeneous_monomials(energy - 4))
        identity_vector = DIMENSION * len(homogeneous_monomials(energy - 5))

        # (c,omega) -> (c,Omega), Omega=omega+partial.c/4.
        f_gauge = sp.MutableSparseMatrix(
            vector_ghost + scalar_ghost, vector_ghost + scalar_ghost, {}
        )
        f_gauge[:vector_ghost, :vector_ghost] = sp.eye(vector_ghost)
        f_gauge[vector_ghost:, :vector_ghost] = (
            vector_divergence_matrix(energy + 1) / 4
        )
        f_gauge[vector_ghost:, vector_ghost:] = sp.eye(scalar_ghost)
        g_gauge = sp.MutableSparseMatrix(f_gauge)
        g_gauge[vector_ghost:, :vector_ghost] *= -1

        # h -> (h_0,tau), tau=tr(h)/8; h=h_0+2 tau eta.
        f_metric = sp.SparseMatrix.vstack(
            _component_map(TRACEFREE_PROJECTION, metric_monomials),
            symmetric_trace_matrix(energy) / 8,
        )
        g_metric = sp.SparseMatrix.hstack(
            _component_map(TRACEFREE_INCLUSION, metric_monomials),
            _metric_trace_vector(metric_monomials, sp.Integer(2)),
        )

        # hstar -> (hstar_0,tau_star), tau_star=2 tr(hstar).
        if equation_monomials:
            f_equation = sp.SparseMatrix.vstack(
                _component_map(TRACEFREE_PROJECTION, equation_monomials),
                2 * symmetric_trace_matrix(energy - 4),
            )
            g_equation = sp.SparseMatrix.hstack(
                _component_map(TRACEFREE_INCLUSION, equation_monomials),
                _metric_trace_vector(equation_monomials, sp.Rational(1, 8)),
            )
        else:
            f_equation = sp.SparseMatrix(0, 0, {})
            g_equation = sp.SparseMatrix(0, 0, {})

        # The canonical companion of Omega is
        # cstar_tilde=cstar+(partial omegastar)/4.  The raw vector identity
        # is normalized as i_star=-cstar_tilde/2, so K_0^sharp is +div.
        identity_scalar = equation_monomials
        f_identity = sp.MutableSparseMatrix(
            identity_vector + identity_scalar,
            identity_vector + identity_scalar,
            {},
        )
        g_identity = sp.MutableSparseMatrix(
            identity_vector + identity_scalar,
            identity_vector + identity_scalar,
            {},
        )
        if identity_vector:
            f_identity[:identity_vector, :identity_vector] = (
                -sp.Rational(1, 2) * sp.eye(identity_vector)
            )
            g_identity[:identity_vector, :identity_vector] = (
                -2 * sp.eye(identity_vector)
            )
            gradient = scalar_gradient_matrix(energy - 4)
            f_identity[:identity_vector, identity_vector:] = -gradient / 8
            g_identity[:identity_vector, identity_vector:] = -gradient / 4
        if identity_scalar:
            f_identity[identity_vector:, identity_vector:] = sp.eye(identity_scalar)
            g_identity[identity_vector:, identity_vector:] = sp.eye(identity_scalar)

        row_maps = (
            ("gauge", sp.SparseMatrix(f_gauge), sp.SparseMatrix(g_gauge)),
            ("metric", f_metric, g_metric),
            ("equation", f_equation, g_equation),
            ("identity", sp.SparseMatrix(f_identity), sp.SparseMatrix(g_identity)),
        )
        field_to_raw = _direct_sum(tuple(value[1] for value in row_maps))
        raw_to_field = _direct_sum(tuple(value[2] for value in row_maps))

        # The raw trace sector is the direct sum of the two unit pairs
        # Omega->tau and tau_star->Omega_star.  Record its projector and
        # contracting homotopy in the ambient raw basis rather than merely
        # observing that the corresponding blocks have rank one.
        raw_slices = {value.name: value for value in raw.slices}
        gauge_slice = raw_slices["gauge"]
        metric_slice = raw_slices["metric"]
        equation_slice = raw_slices["equation"]
        identity_slice = raw_slices["identity"]
        metric_tf = metric_slice.dimension - scalar_ghost
        equation_tf = equation_slice.dimension - equation_monomials
        trace_entries: dict[tuple[int, int], sp.Expr] = {}
        homotopy_entries: dict[tuple[int, int], sp.Expr] = {}

        def select(start: int, size: int) -> None:
            for offset in range(size):
                trace_entries[start + offset, start + offset] = 1

        select(gauge_slice.start + vector_ghost, scalar_ghost)
        select(metric_slice.start + metric_tf, scalar_ghost)
        select(equation_slice.start + equation_tf, equation_monomials)
        select(identity_slice.start + identity_vector, equation_monomials)
        for offset in range(scalar_ghost):
            homotopy_entries[
                gauge_slice.start + vector_ghost + offset,
                metric_slice.start + metric_tf + offset,
            ] = 1
        for offset in range(equation_monomials):
            homotopy_entries[
                equation_slice.start + equation_tf + offset,
                identity_slice.start + identity_vector + offset,
            ] = 1
        trace_projector = sp.SparseMatrix(
            raw.dimension, raw.dimension, trace_entries
        )
        trace_homotopy = sp.SparseMatrix(
            raw.dimension, raw.dimension, homotopy_entries
        )
        result = cls(
            energy,
            bv,
            raw,
            field_to_raw,
            raw_to_field,
            row_maps,
            trace_projector,
            trace_homotopy,
        )
        result.verify()
        return result

    def row_map(self, name: str) -> tuple[sp.SparseMatrix, sp.SparseMatrix]:
        _, forward, inverse = next(value for value in self.row_maps if value[0] == name)
        return forward, inverse

    def verify(self) -> None:
        identity = sp.SparseMatrix.eye(self.bv.dimension)
        if self.raw_to_field * self.field_to_raw != identity:
            raise AssertionError("G F != identity on the minimal BV complex")
        if self.field_to_raw * self.raw_to_field != identity:
            raise AssertionError("F G != identity on the raw detour complex")
        if self.field_to_raw * self.bv.q != self.raw.q * self.field_to_raw:
            raise AssertionError("F Q_BV != Q_raw F")
        if self.raw_to_field * self.raw.q != self.bv.q * self.raw_to_field:
            raise AssertionError("G Q_raw != Q_BV G")
        projector_entries = self.trace_projector.todok()
        if any(row != column or value != 1 for (row, column), value in projector_entries.items()):
            raise AssertionError("trace selector is not a projector")
        trace_indices = {row for row, _ in projector_entries}
        if any(
            (row in trace_indices) != (column in trace_indices)
            for row, column in self.raw.q.todok()
        ):
            raise AssertionError("raw q does not preserve the trace summand")
        qs = _sparse_product_dok(self.raw.q, self.trace_homotopy)
        sq = _sparse_product_dok(self.trace_homotopy, self.raw.q)
        contracted = dict(qs)
        for key, value in sq.items():
            contracted[key] = sp.simplify(
                contracted.get(key, sp.Integer(0)) + value
            )
            if contracted[key] == 0:
                del contracted[key]
        if contracted != dict(projector_entries):
            raise AssertionError("trace summand lacks its explicit contraction")

        # The trace/Weyl pieces are two displayed contractible pairs:
        # Omega -> tau and tau_star -> Omega_star.
        raw_slices = {value.name: value for value in self.raw.slices}
        gauge = raw_slices["gauge"]
        metric = raw_slices["metric"]
        equation = raw_slices["equation"]
        identity_slice = raw_slices["identity"]
        scalar = len(homogeneous_monomials(self.energy))
        equation_scalar = len(homogeneous_monomials(self.energy - 4))
        vector_gauge = gauge.dimension - scalar
        metric_tf = metric.dimension - scalar
        identity_vector = identity_slice.dimension - equation_scalar
        equation_tf = equation.dimension - equation_scalar
        q = self.raw.q
        if q[
            metric.start + metric_tf : metric.stop,
            gauge.start + vector_gauge : gauge.stop,
        ] != sp.SparseMatrix.eye(scalar):
            raise AssertionError("Omega -> tau is not the unit trace doublet")
        if equation_scalar and q[
            identity_slice.start + identity_vector : identity_slice.stop,
            equation.start + equation_tf : equation.stop,
        ] != sp.SparseMatrix.eye(equation_scalar):
            raise AssertionError("tau_star -> Omega_star is not the unit dual doublet")
