"""Explicit contraction and conformal-Killing preservation certificates."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import factorial

import sympy as sp

from bridge.zero_modes import conformal_killing_projector
from field_bv_identification.gauge_fixed_equivalence.canonical_transformation import (
    GaugeFixedBVBlock,
)


def _identity_entries(row: int, column: int, size: int):
    return {(row + offset, column + offset): sp.Integer(1) for offset in range(size)}


@dataclass(frozen=True)
class GaugeFixedContraction:
    block: GaugeFixedBVBlock
    projection: sp.SparseMatrix
    inclusion: sp.SparseMatrix
    homotopy: sp.SparseMatrix

    @classmethod
    def at_energy(cls, energy: int) -> "GaugeFixedContraction":
        block = GaugeFixedBVBlock.at_energy(energy)
        raw_dimension = block.raw.dimension
        full_dimension = block.dimension
        inclusion_unfixed = sp.SparseMatrix(
            full_dimension,
            raw_dimension,
            _identity_entries(0, 0, raw_dimension),
        )
        projection_unfixed = sp.SparseMatrix(
            raw_dimension,
            full_dimension,
            _identity_entries(0, 0, raw_dimension),
        )
        homotopy_unfixed = sp.MutableSparseMatrix(full_dimension, full_dimension, {})
        start = raw_dimension
        homotopy_unfixed[start:, start:] = block.nonminimal.tangent_homotopy
        homotopy_unfixed = sp.SparseMatrix(homotopy_unfixed)

        # Transport the obvious direct-sum contraction through the canonical
        # gauge-fixing shear.
        inclusion = sp.SparseMatrix(block.canonical_map * inclusion_unfixed)
        projection = sp.SparseMatrix(projection_unfixed * block.canonical_inverse)
        homotopy = sp.SparseMatrix(
            block.canonical_map * homotopy_unfixed * block.canonical_inverse
        )
        result = cls(block, projection, inclusion, homotopy)
        result.verify()
        return result

    def verify(self) -> None:
        raw_identity = sp.SparseMatrix.eye(self.block.raw.dimension)
        full_identity = sp.SparseMatrix.eye(self.block.dimension)
        if self.projection * self.inclusion != raw_identity:
            raise AssertionError("p_gf j_gf != identity")
        if (
            self.inclusion * self.projection
            != full_identity
            - self.block.q_gauge_fixed * self.homotopy
            - self.homotopy * self.block.q_gauge_fixed
        ):
            raise AssertionError("j_gf p_gf != 1-Q_gf s_gf-s_gf Q_gf")
        if self.projection * self.block.q_gauge_fixed != self.block.raw.q * self.projection:
            raise AssertionError("p_gf is not a chain map")
        if self.block.q_gauge_fixed * self.inclusion != self.inclusion * self.block.raw.q:
            raise AssertionError("j_gf is not a chain map")


def _image_basis_and_left_inverse(projector: sp.MatrixBase):
    _, pivot_columns = projector.rref()
    basis = sp.Matrix(projector[:, list(pivot_columns)])
    if basis.cols != projector.rank():
        raise AssertionError("projector image basis has the wrong rank")
    _, pivot_rows = basis.T.rref()
    selection = sp.zeros(basis.cols, basis.rows)
    for row, source in enumerate(pivot_rows):
        selection[row, source] = 1
    # Compose the coordinate chart with the given projector.  The bare row
    # selection is a left inverse of ``basis`` but would generally define a
    # different projector onto the same image; this composition reproduces
    # the specified complementary projector exactly.
    left_inverse = (selection * basis).inv() * selection * projector
    return basis, left_inverse


def _low_parameter_data():
    vector_exponents = tuple(
        exponent
        for degree in range(3)
        for exponent in product(range(degree + 1), repeat=4)
        if sum(exponent) == degree
    )
    scalar_exponents = tuple(
        exponent
        for degree in range(2)
        for exponent in product(range(degree + 1), repeat=4)
        if sum(exponent) == degree
    )
    vector_index = {
        (component, exponent): index
        for index, (component, exponent) in enumerate(
            product(range(4), vector_exponents)
        )
    }
    scalar_offset = len(vector_index)
    scalar_index = {
        exponent: scalar_offset + index
        for index, exponent in enumerate(scalar_exponents)
    }
    return vector_exponents, scalar_exponents, vector_index, scalar_index


def _compact_parameter_generators():
    """Exact D and SO(4) action on the 65 low gauge coefficients."""

    vector_exponents, scalar_exponents, vector_index, scalar_index = (
        _low_parameter_data()
    )
    dilation = sp.zeros(65)
    for (component, exponent), index in vector_index.items():
        dilation[index, index] = sum(exponent) - 1
    for exponent, index in scalar_index.items():
        dilation[index, index] = sum(exponent)

    rotations = []
    for first in range(4):
        for second in range(first + 1, 4):
            matrix = sp.zeros(65)
            for (component, exponent), column in vector_index.items():
                # Vector spin action.
                if component == second:
                    matrix[vector_index[(first, exponent)], column] += 1
                if component == first:
                    matrix[vector_index[(second, exponent)], column] -= 1
                # Polynomial orbital action x_first d_second-x_second d_first.
                for sign, multiply_axis, derivative_axis in (
                    (1, first, second),
                    (-1, second, first),
                ):
                    if exponent[derivative_axis] == 0:
                        continue
                    output = list(exponent)
                    coefficient = output[derivative_axis]
                    output[derivative_axis] -= 1
                    output[multiply_axis] += 1
                    matrix[
                        vector_index[(component, tuple(output))], column
                    ] += sign * coefficient
            for exponent, column in scalar_index.items():
                for sign, multiply_axis, derivative_axis in (
                    (1, first, second),
                    (-1, second, first),
                ):
                    if exponent[derivative_axis] == 0:
                        continue
                    output = list(exponent)
                    coefficient = output[derivative_axis]
                    output[derivative_axis] -= 1
                    output[multiply_axis] += 1
                    matrix[scalar_index[tuple(output)], column] += sign * coefficient
            rotations.append(matrix)
    return dilation, tuple(rotations)


def _compact_equivariant_projector(basis: sp.MatrixBase):
    """Fischer-orthogonal projector onto the CKV representation."""

    vector_exponents, scalar_exponents, vector_index, scalar_index = (
        _low_parameter_data()
    )
    weights = [sp.Integer(0)] * 65
    for (_, exponent), index in vector_index.items():
        weights[index] = sp.prod(factorial(power) for power in exponent)
    for exponent, index in scalar_index.items():
        weights[index] = sp.prod(factorial(power) for power in exponent)
    gram = sp.diag(*weights)
    projector = sp.simplify(
        basis * (basis.T * gram * basis).inv() * basis.T * gram
    )
    dilation, rotations = _compact_parameter_generators()
    if any(rotation.T * gram + gram * rotation != sp.zeros(65) for rotation in rotations):
        raise AssertionError("Fischer form is not SO(4)-invariant")
    if projector * dilation != dilation * projector:
        raise AssertionError("CKV projector is not D-equivariant")
    if any(projector * rotation != rotation * projector for rotation in rotations):
        raise AssertionError("CKV projector is not SO(4)-equivariant")
    return sp.Matrix(projector), sp.Matrix(gram), dilation, rotations


@dataclass(frozen=True)
class ZeroModePreservation:
    projector: sp.Matrix
    complement_projector: sp.Matrix
    complement_basis: sp.Matrix
    complement_left_inverse: sp.Matrix
    local_gauge_map: sp.Matrix
    q_gauge_fixed_model: sp.Matrix
    extended_projector: sp.Matrix
    labels: tuple[str, ...]
    compact_degrees: tuple[int, ...]
    compact_gram: sp.Matrix
    compact_dilation: sp.Matrix
    compact_rotations: tuple[sp.Matrix, ...]

    @classmethod
    def build(cls) -> "ZeroModePreservation":
        ckv = conformal_killing_projector()
        projector, gram, dilation, rotations = _compact_equivariant_projector(
            ckv.basis
        )
        identity = sp.eye(projector.rows)
        complement = identity - projector
        basis, left_inverse = _image_basis_and_left_inverse(complement)
        local_gauge = sp.Matrix(ckv.gauge_map * basis)
        if local_gauge.det() == 0:
            raise AssertionError("K is not invertible on the selected CKV complement")

        # On the low inhomogeneous block the auxiliary stationary inner
        # product gives chi=(K|_perp)^T.  The gauge-fixed column of a gauge
        # parameter contains K epsilon and chi K epsilon.  Both vanish on Z.
        chi = local_gauge.T
        gauge_dimension = projector.rows
        metric_dimension = ckv.gauge_map.rows
        condition_dimension = basis.cols
        total = gauge_dimension + metric_dimension + condition_dimension
        q = sp.zeros(total)
        q[
            gauge_dimension : gauge_dimension + metric_dimension,
            :gauge_dimension,
        ] = ckv.gauge_map
        q[
            gauge_dimension + metric_dimension :,
            :gauge_dimension,
        ] = chi * ckv.gauge_map
        extended = sp.zeros(total)
        extended[:gauge_dimension, :gauge_dimension] = projector
        result = cls(
            projector,
            sp.Matrix(complement),
            basis,
            left_inverse,
            local_gauge,
            sp.Matrix(q),
            sp.Matrix(extended),
            ckv.labels,
            ckv.compact_degrees,
            gram,
            dilation,
            rotations,
        )
        result.verify()
        return result

    def verify(self) -> None:
        identity = sp.eye(self.projector.rows)
        if self.projector * self.projector != self.projector:
            raise AssertionError("P_Z is not idempotent")
        if self.complement_projector * self.complement_projector != self.complement_projector:
            raise AssertionError("P_perp is not idempotent")
        if self.projector + self.complement_projector != identity:
            raise AssertionError("Z plus its local complement does not exhaust ghosts")
        if self.complement_left_inverse * self.complement_basis != sp.eye(50):
            raise AssertionError("local ghost complement has no exact coordinate inverse")
        if self.complement_basis * self.complement_left_inverse != self.complement_projector:
            raise AssertionError("local ghost complement does not reproduce P_perp")
        if self.local_gauge_map.rank() != 50:
            raise AssertionError("nonzero-mode gauge map is not injective")
        if self.q_gauge_fixed_model * self.q_gauge_fixed_model != sp.zeros(
            self.q_gauge_fixed_model.rows
        ):
            raise AssertionError("low-mode gauge-fixed model is not nilpotent")
        if (
            self.extended_projector * self.q_gauge_fixed_model
            != self.q_gauge_fixed_model * self.extended_projector
        ):
            raise AssertionError("P_Z Q_gf != Q_gf P_Z")
        if self.q_gauge_fixed_model * self.extended_projector != sp.zeros(
            self.q_gauge_fixed_model.rows
        ):
            raise AssertionError("a conformal-Killing mode was absorbed by gauge fixing")
        if self.extended_projector.rank() != 15:
            raise AssertionError("the preserved zero-mode kernel is not 15-dimensional")
        if self.compact_degrees != (-1,) * 4 + (0,) * 7 + (1,) * 4:
            raise AssertionError("the zero-mode compact grading changed")
        if self.projector * self.compact_dilation != self.compact_dilation * self.projector:
            raise AssertionError("P_Z is not D-equivariant")
        if any(
            self.projector * rotation != rotation * self.projector
            for rotation in self.compact_rotations
        ):
            raise AssertionError("P_Z is not SO(4)-equivariant")
