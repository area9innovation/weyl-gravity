"""Exact conformal generalized-Verma realization of the free BV detour row.

Unlike the split normal form, this module retains the raw homogeneous
polynomial bases.  It is the machine rail for noncompact conformal
equivariance.  Total cylinder energy is primary dimension plus polynomial
level, so every differential preserves the energy label.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from bridge.bv_complex.conformal_polynomials import (
    DIMENSION,
    ROTATION_PAIRS,
    SYMMETRIC_PAIRS,
    PolynomialConformalModule,
    TRACEFREE_INCLUSION,
    TRACEFREE_PROJECTION,
    homogeneous_monomials,
)

# The operator engine predates the bridge package and is independently
# certified.  It supplies the raw rational K and Bach matrices; this module
# adds the complete BV rows and conformal action around them.
from symbolic.verify_conformal_detour_polynomial import bach_matrix, gauge_matrix


GAUGE_VECTOR = PolynomialConformalModule(sp.Integer(-1), "vector")
GAUGE_WEYL = PolynomialConformalModule(sp.Integer(0), "scalar")
METRIC = PolynomialConformalModule(sp.Integer(0), "symmetric_tf")
METRIC_TRACE = PolynomialConformalModule(sp.Integer(0), "scalar")
EQUATION = PolynomialConformalModule(sp.Integer(4), "symmetric_tf")
EQUATION_TRACE = PolynomialConformalModule(sp.Integer(4), "scalar")
IDENTITY_VECTOR = PolynomialConformalModule(sp.Integer(5), "vector")
IDENTITY_WEYL = PolynomialConformalModule(sp.Integer(4), "scalar")


@dataclass(frozen=True)
class ChainSlice:
    name: str
    start: int
    stop: int
    modules: tuple[tuple[PolynomialConformalModule, int], ...]

    @property
    def dimension(self) -> int:
        return self.stop - self.start


def _level(module: PolynomialConformalModule, energy: int) -> int:
    return int(energy - module.dimension_primary)


def _module_dimension(module: PolynomialConformalModule, energy: int) -> int:
    return module.dimension(_level(module, energy))


def _direct_sum(matrices: tuple[sp.MatrixBase, ...]) -> sp.SparseMatrix:
    if not matrices:
        return sp.SparseMatrix(0, 0, {})
    return sp.diag(*matrices, cls=sp.SparseMatrix)


def _component_map(component_matrix: sp.MatrixBase, monomial_count: int) -> sp.SparseMatrix:
    """Apply a component map independently to pair-major monomial blocks."""

    return sp.SparseMatrix(
        sp.kronecker_product(component_matrix, sp.eye(monomial_count))
    )


def _vector_divergence_matrix(energy: int) -> sp.SparseMatrix:
    """Divergence from a full symmetric equation tensor to a vector."""

    equation_level = energy - 4
    equation_monomials = homogeneous_monomials(equation_level)
    vector_monomials = homogeneous_monomials(equation_level - 1)
    input_columns = {
        (pair, exponent): column
        for column, (pair, exponent) in enumerate(
            (item for pair in SYMMETRIC_PAIRS for item in ((pair, exponent) for exponent in equation_monomials))
        )
    }
    # The comprehension above deliberately preserves pair-major order.
    vector_rows = {
        (component, exponent): row
        for row, (component, exponent) in enumerate(
            (item for component in range(DIMENSION) for item in ((component, exponent) for exponent in vector_monomials))
        )
    }
    entries: dict[tuple[int, int], sp.Expr] = {}

    def differentiated(exponent, axis):
        if exponent[axis] == 0:
            return None
        output = list(exponent)
        coefficient = output[axis]
        output[axis] -= 1
        return coefficient, tuple(output)

    for pair in SYMMETRIC_PAIRS:
        first, second = pair
        for exponent in equation_monomials:
            column = input_columns[(pair, exponent)]
            if first == second:
                result = differentiated(exponent, first)
                if result is not None:
                    coefficient, output = result
                    entries[vector_rows[(first, output)], column] = coefficient
            else:
                for derivative, target in ((first, second), (second, first)):
                    result = differentiated(exponent, derivative)
                    if result is not None:
                        coefficient, output = result
                        entries[vector_rows[(target, output)], column] = coefficient
    return sp.SparseMatrix(
        len(vector_rows),
        len(input_columns),
        entries,
    )


def _scalar_divergence(energy: int) -> sp.SparseMatrix:
    """Divergence ``partial.xi`` from the vector gauge module."""

    source_monomials = homogeneous_monomials(energy + 1)
    target_monomials = homogeneous_monomials(energy)
    target_index = {exponent: row for row, exponent in enumerate(target_monomials)}
    entries = {}
    for component in range(DIMENSION):
        for monomial_index, exponent in enumerate(source_monomials):
            if exponent[component] == 0:
                continue
            output = list(exponent)
            coefficient = output[component]
            output[component] -= 1
            entries[
                target_index[tuple(output)],
                component * len(source_monomials) + monomial_index,
            ] = coefficient
    return sp.SparseMatrix(
        len(target_monomials), 4 * len(source_monomials), entries
    )


def conformal_killing_matrix(energy: int) -> sp.SparseMatrix:
    """Trace-free ``K_0 xi`` in the nine-component harmonic basis."""

    raw = gauge_matrix(energy)
    vector_dimension = 4 * len(homogeneous_monomials(energy + 1))
    vector = raw[:, :vector_dimension]
    scalar = raw[:, vector_dimension:]
    tracefree_full = vector - scalar * _scalar_divergence(energy) / 4
    projection = _component_map(
        TRACEFREE_PROJECTION, len(homogeneous_monomials(energy))
    )
    return sp.SparseMatrix(projection * tracefree_full)


def tracefree_bach_matrix(energy: int) -> sp.SparseMatrix:
    input_monomials = len(homogeneous_monomials(energy))
    output_monomials = len(homogeneous_monomials(energy - 4))
    inclusion = _component_map(TRACEFREE_INCLUSION, input_monomials)
    projection = _component_map(TRACEFREE_PROJECTION, output_monomials)
    return sp.SparseMatrix(projection * bach_matrix(energy) * inclusion)


def tracefree_identity_matrix(energy: int) -> sp.SparseMatrix:
    equation_monomials = len(homogeneous_monomials(energy - 4))
    inclusion = _component_map(TRACEFREE_INCLUSION, equation_monomials)
    return sp.SparseMatrix(_vector_divergence_matrix(energy) * inclusion)


@dataclass(frozen=True)
class PolynomialBVBlock:
    energy: int
    slices: tuple[ChainSlice, ...]
    q: sp.SparseMatrix

    @classmethod
    def at_energy(cls, energy: int) -> "PolynomialBVBlock":
        if energy < 0:
            # Low modules are allowed for equivariance buffers, but the
            # current bridge begins at the metric primary energy zero.
            raise ValueError("use energy >= 0")
        specifications = (
            ("gauge", ((GAUGE_VECTOR, _level(GAUGE_VECTOR, energy)), (GAUGE_WEYL, _level(GAUGE_WEYL, energy)))),
            ("metric", ((METRIC, _level(METRIC, energy)), (METRIC_TRACE, _level(METRIC_TRACE, energy)))),
            ("equation", ((EQUATION, _level(EQUATION, energy)), (EQUATION_TRACE, _level(EQUATION_TRACE, energy)))),
            ("identity", ((IDENTITY_VECTOR, _level(IDENTITY_VECTOR, energy)), (IDENTITY_WEYL, _level(IDENTITY_WEYL, energy)))),
        )
        slices = []
        cursor = 0
        for name, modules in specifications:
            dimension = sum(module.dimension(level) for module, level in modules)
            slices.append(ChainSlice(name, cursor, cursor + dimension, modules))
            cursor += dimension
        by_name = {value.name: value for value in slices}
        entries: dict[tuple[int, int], sp.Expr] = {}

        def insert(target: str, source: str, matrix: sp.MatrixBase):
            target_slice, source_slice = by_name[target], by_name[source]
            if matrix.shape != (target_slice.dimension, source_slice.dimension):
                raise AssertionError(
                    f"{source}->{target} shape {matrix.shape} != {(target_slice.dimension, source_slice.dimension)}"
                )
            for (row, column), value in matrix.todok().items():
                entries[target_slice.start + row, source_slice.start + column] = value

        gauge_vector_dimension = _module_dimension(GAUGE_VECTOR, energy)
        metric_tf_dimension = _module_dimension(METRIC, energy)
        equation_tf_dimension = _module_dimension(EQUATION, energy)
        identity_vector_dimension = _module_dimension(IDENTITY_VECTOR, energy)

        gauge_to_metric = sp.MutableSparseMatrix(
            by_name["metric"].dimension, by_name["gauge"].dimension, {}
        )
        gauge_to_metric[:metric_tf_dimension, :gauge_vector_dimension] = conformal_killing_matrix(energy)
        scalar_dimension = _module_dimension(GAUGE_WEYL, energy)
        gauge_to_metric[
            metric_tf_dimension : metric_tf_dimension + scalar_dimension,
            gauge_vector_dimension : gauge_vector_dimension + scalar_dimension,
        ] = sp.eye(scalar_dimension)

        metric_to_equation = sp.MutableSparseMatrix(
            by_name["equation"].dimension, by_name["metric"].dimension, {}
        )
        metric_to_equation[:equation_tf_dimension, :metric_tf_dimension] = tracefree_bach_matrix(energy)

        equation_to_identity = sp.MutableSparseMatrix(
            by_name["identity"].dimension, by_name["equation"].dimension, {}
        )
        equation_to_identity[:identity_vector_dimension, :equation_tf_dimension] = tracefree_identity_matrix(energy)
        equation_trace_dimension = _module_dimension(EQUATION_TRACE, energy)
        equation_to_identity[
            identity_vector_dimension : identity_vector_dimension + equation_trace_dimension,
            equation_tf_dimension : equation_tf_dimension + equation_trace_dimension,
        ] = sp.eye(equation_trace_dimension)

        insert("metric", "gauge", sp.SparseMatrix(gauge_to_metric))
        insert("equation", "metric", sp.SparseMatrix(metric_to_equation))
        insert("identity", "equation", sp.SparseMatrix(equation_to_identity))
        result = cls(energy, tuple(slices), sp.SparseMatrix(cursor, cursor, entries))
        result.verify()
        return result

    @property
    def dimension(self) -> int:
        return self.q.rows

    def slice(self, name: str) -> ChainSlice:
        return next(value for value in self.slices if value.name == name)

    def _action_within(self, kind: str, *indices: int) -> sp.SparseMatrix:
        matrices = []
        for chain_slice in self.slices:
            for module, level in chain_slice.modules:
                if kind == "D":
                    matrices.append(module.dilation(level))
                elif kind == "M":
                    matrices.append(module.rotation(indices[0], indices[1], level))
                else:
                    raise ValueError(kind)
        return _direct_sum(tuple(matrices))

    @property
    def dilation(self) -> sp.SparseMatrix:
        return self._action_within("D")

    def rotation(self, first: int, second: int) -> sp.SparseMatrix:
        return self._action_within("M", first, second)

    def translation_to(self, target: "PolynomialBVBlock", axis: int) -> sp.SparseMatrix:
        if target.energy != self.energy - 1:
            raise ValueError("coordinate translation target must have energy n-1")
        matrices = []
        for source_slice, target_slice in zip(self.slices, target.slices):
            if source_slice.name != target_slice.name:
                raise AssertionError("chain slice order changed")
            for (source_module, source_level), (target_module, target_level) in zip(
                source_slice.modules, target_slice.modules
            ):
                if source_module != target_module or target_level != source_level - 1:
                    raise AssertionError("module level mismatch")
                matrices.append(source_module.coordinate_translation(axis, source_level))
        return _rectangular_direct_sum(tuple(matrices))

    def special_to(self, target: "PolynomialBVBlock", axis: int) -> sp.SparseMatrix:
        if target.energy != self.energy + 1:
            raise ValueError("coordinate special-conformal target must have energy n+1")
        matrices = []
        for source_slice, target_slice in zip(self.slices, target.slices):
            if source_slice.name != target_slice.name:
                raise AssertionError("chain slice order changed")
            for (source_module, source_level), (target_module, target_level) in zip(
                source_slice.modules, target_slice.modules
            ):
                if source_module != target_module or target_level != source_level + 1:
                    raise AssertionError("module level mismatch")
                matrices.append(source_module.coordinate_special(axis, source_level))
        return _rectangular_direct_sum(tuple(matrices))

    def verify(self) -> None:
        if self.q * self.q != sp.SparseMatrix(self.dimension, self.dimension, {}):
            raise AssertionError(f"q^2 != 0 at energy {self.energy}")
        if self.dilation != self.energy * sp.SparseMatrix.eye(self.dimension):
            raise AssertionError("total energy is not uniform across the BV chain")
        for pair in ROTATION_PAIRS:
            rotation = self.rotation(*pair)
            if self.q * rotation != rotation * self.q:
                raise AssertionError(f"q is not SO(4)-equivariant for {pair}")

    def verify_noncompact_with(self, lower: "PolynomialBVBlock", upper: "PolynomialBVBlock") -> None:
        if lower.energy != self.energy - 1 or upper.energy != self.energy + 1:
            raise ValueError("need adjacent energy blocks")
        for axis in range(DIMENSION):
            translation = self.translation_to(lower, axis)
            special = self.special_to(upper, axis)
            if lower.q * translation != translation * self.q:
                raise AssertionError(f"q P_{axis} != P_{axis} q at energy {self.energy}")
            if upper.q * special != special * self.q:
                raise AssertionError(f"q K_{axis} != K_{axis} q at energy {self.energy}")


def _rectangular_direct_sum(matrices: tuple[sp.MatrixBase, ...]) -> sp.SparseMatrix:
    rows = sum(matrix.rows for matrix in matrices)
    columns = sum(matrix.cols for matrix in matrices)
    entries = {}
    row_offset = column_offset = 0
    for matrix in matrices:
        for (row, column), value in matrix.todok().items():
            entries[row_offset + row, column_offset + column] = value
        row_offset += matrix.rows
        column_offset += matrix.cols
    return sp.SparseMatrix(rows, columns, entries)
