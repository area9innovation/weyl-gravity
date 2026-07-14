"""Canonical gauge-fermion shear of the extended tangent BV complex."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from bridge.bv_complex.polynomial_bv import PolynomialBVBlock
from field_bv_identification.gauge_fixed_equivalence.gauge_fermion import (
    CylinderGaugeFermion,
)
from field_bv_identification.gauge_fixed_equivalence.nonminimal_sector import (
    NonminimalBlock,
    NonminimalSlice,
)


def _block_diagonal(*matrices: sp.MatrixBase) -> sp.SparseMatrix:
    return sp.diag(*matrices, cls=sp.SparseMatrix)


@dataclass(frozen=True)
class GaugeFixedBVBlock:
    """One exact total-energy block before and after gauge fixing.

    ``canonical_map`` is the tangent map induced by

    ``phi_star -> phi_star + delta Psi/delta phi``.

    The fields themselves are unchanged.  Since the Hessian of the selected
    gauge fermion only mixes fields with their corresponding antifields, the
    shear is unipotent and has an explicit inverse.
    """

    energy: int
    raw: PolynomialBVBlock
    nonminimal: NonminimalBlock
    gauge_fermion: CylinderGaugeFermion
    q_unfixed: sp.SparseMatrix
    canonical_map: sp.SparseMatrix
    canonical_inverse: sp.SparseMatrix
    q_gauge_fixed: sp.SparseMatrix
    shear: sp.SparseMatrix

    @classmethod
    def at_energy(cls, energy: int) -> "GaugeFixedBVBlock":
        raw = PolynomialBVBlock.at_energy(energy)
        nonminimal = NonminimalBlock.at_energy(energy)
        fermion = CylinderGaugeFermion.at_energy(energy)
        q_unfixed = _block_diagonal(raw.q, nonminimal.tangent_q)
        total = q_unfixed.rows
        shear_entries: dict[tuple[int, int], sp.Expr] = {}
        raw_by_name = {value.name: value for value in raw.slices}
        nm_offset = raw.dimension

        def nm(name: str) -> NonminimalSlice:
            return nonminimal.field(name)

        def insert(
            target_start: int,
            source_start: int,
            matrix: sp.MatrixBase,
        ) -> None:
            for (row, column), value in matrix.todok().items():
                shear_entries[target_start + row, source_start + column] = value

        metric = raw_by_name["metric"]
        equation = raw_by_name["equation"]
        scalar_metric = nm("scalar_antighost_antifield").dimension
        scalar_equation = nm("scalar_antighost").dimension
        metric_tf = metric.dimension - scalar_metric
        equation_tf = equation.dimension - scalar_equation

        # delta Psi/delta h_0 and delta Psi/delta tau shift the metric
        # antifields.  The source antighosts carry the complementary
        # conformal weights 3 and 4.
        insert(
            equation.start,
            nm_offset + nm("vector_antighost").start,
            fermion.vector_antighost_to_equation,
        )
        insert(
            equation.start + equation_tf,
            nm_offset + nm("scalar_antighost").start,
            fermion.scalar_antighost_to_equation_trace,
        )

        # delta Psi/delta bar_c and delta Psi/delta bar_omega shift the
        # antighost antifields by the gauge conditions.
        insert(
            nm_offset + nm("vector_antighost_antifield").start,
            metric.start,
            fermion.metric_to_vector_antighost_antifield,
        )
        insert(
            nm_offset + nm("scalar_antighost_antifield").start,
            metric.start + metric_tf,
            fermion.metric_trace_to_scalar_antighost_antifield,
        )

        shear = sp.SparseMatrix(total, total, shear_entries)
        identity = sp.SparseMatrix.eye(total)
        canonical_map = identity + shear
        canonical_inverse = identity - shear
        q_gauge_fixed = sp.SparseMatrix(
            canonical_map * q_unfixed * canonical_inverse
        )
        result = cls(
            energy,
            raw,
            nonminimal,
            fermion,
            q_unfixed,
            canonical_map,
            canonical_inverse,
            q_gauge_fixed,
            shear,
        )
        result.verify()
        return result

    @property
    def dimension(self) -> int:
        return self.q_gauge_fixed.rows

    def nonminimal_global_slice(self, name: str) -> slice:
        field = self.nonminimal.field(name)
        return slice(
            self.raw.dimension + field.start,
            self.raw.dimension + field.stop,
        )

    def verify(self) -> None:
        identity = sp.SparseMatrix.eye(self.dimension)
        zero = sp.SparseMatrix(self.dimension, self.dimension, {})
        if self.shear * self.shear != zero:
            raise AssertionError("the gauge-fermion shear is not square-zero")
        if (
            self.canonical_map * self.canonical_inverse != identity
            or self.canonical_inverse * self.canonical_map != identity
        ):
            raise AssertionError("the canonical gauge-fixing shear is not invertible")
        if (
            self.q_gauge_fixed
            != self.canonical_map * self.q_unfixed * self.canonical_inverse
        ):
            raise AssertionError("Q_gf is not the canonical conjugate of Q_ext")
        if self.q_gauge_fixed * self.q_gauge_fixed != zero:
            raise AssertionError("the gauge-fixed tangent differential is not nilpotent")

        # The fermion shifts antifields only.  In particular it cannot change
        # a local gauge parameter or the metric field itself.
        gauge = self.raw.slice("gauge")
        metric = self.raw.slice("metric")
        field_rows = list(range(gauge.start, gauge.stop)) + list(
            range(metric.start, metric.stop)
        )
        if self.canonical_map.extract(field_rows, field_rows) != sp.eye(
            len(field_rows)
        ):
            raise AssertionError("gauge fixing changed a minimal field coordinate")

