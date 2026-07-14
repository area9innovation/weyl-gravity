"""Exact contraction of the raw polynomial pure-Weyl BV detour complex.

The split normal form in :mod:`bridge.bv_complex.free_block` is useful for
dimension and pairing arguments, but it does not remember how the
noncompact conformal generators act on metric, ghost, and antifield
coordinates.  This module extracts a strong deformation retract directly
from :class:`~bridge.bv_complex.polynomial_bv.PolynomialBVBlock`.

At compact energy ``n >= 2`` the raw complex is the finite exact sequence

``G --A--> M --B--> E --C--> I``

with cohomology only at the metric slot.  Exact rational changes of basis
put the three nonzero arrows into partial-identity form.  The resulting
``p``, ``j``, and ``s`` therefore contain no fitted or floating-point data.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from bridge.bv_complex.polynomial_bv import PolynomialBVBlock


def _inverse(matrix: sp.MatrixBase) -> sp.Matrix:
    """Invert an exact rational matrix through the sparse domain engine."""

    if matrix.rows == 0:
        return sp.zeros(0, 0)
    domain_matrix = DomainMatrix.from_Matrix(matrix)
    if not domain_matrix.domain.is_Field:
        domain_matrix = domain_matrix.to_field()
    return domain_matrix.inv().to_Matrix()


def _block_diagonal(matrices: tuple[sp.MatrixBase, ...]) -> sp.Matrix:
    if not matrices:
        return sp.zeros(0, 0)
    return sp.diag(*matrices)


def _standard_columns(dimension: int, columns: tuple[int, ...]) -> sp.Matrix:
    if not columns:
        return sp.zeros(dimension, 0)
    return sp.eye(dimension)[:, list(columns)]


def _left_inverse_on_columns(matrix: sp.MatrixBase) -> sp.Matrix:
    """Return ``L`` with ``L*matrix=1`` for a full-column-rank matrix."""

    if matrix.cols == 0:
        return sp.zeros(0, matrix.rows)
    independent_rows = tuple(
        matrix.T.rref(simplify=False, normalize_last=True)[1]
    )
    if len(independent_rows) != matrix.cols:
        raise AssertionError("matrix is not full column rank")
    square = matrix.extract(list(independent_rows), range(matrix.cols))
    square_inverse = _inverse(square)
    result = sp.zeros(matrix.cols, matrix.rows)
    for local_column, ambient_column in enumerate(independent_rows):
        result[:, ambient_column] = square_inverse[:, local_column]
    if result * matrix != sp.eye(matrix.cols):
        raise AssertionError("failed to construct a left inverse")
    return result


@dataclass(frozen=True)
class RawPolynomialRetraction:
    """Strong deformation retract extracted from one raw energy block."""

    block: PolynomialBVBlock
    inclusion: sp.Matrix
    projection: sp.Matrix
    homotopy: sp.Matrix
    adapted_basis: sp.Matrix
    adapted_inverse: sp.Matrix
    cohomology_dimension: int

    @classmethod
    def build(cls, energy: int) -> "RawPolynomialRetraction":
        if energy < 2:
            raise ValueError(
                "energies below two contain the global reducibility band"
            )
        block = PolynomialBVBlock.at_energy(energy)
        slices = {value.name: value for value in block.slices}
        gauge = slices["gauge"]
        metric = slices["metric"]
        equation = slices["equation"]
        identity = slices["identity"]

        def arrow(target, source) -> sp.Matrix:
            return sp.Matrix(
                block.q[target.start : target.stop, source.start : source.stop]
            )

        a = arrow(metric, gauge)
        b = arrow(equation, metric)
        c = arrow(identity, equation)

        # The positive-energy band has no gauge-parameter cohomology.
        if a.rank() != a.cols:
            raise AssertionError("gauge arrow is not injective")

        # Choose a coordinate complement L_B on which B is injective.  Its
        # image is im(B), and P_ker projects arbitrary metric coordinates
        # into ker(B) without altering im(A).
        b_pivots = tuple(b.rref(simplify=False, normalize_last=True)[1])
        l_b = _standard_columns(metric.dimension, b_pivots)
        b_l = b * l_b
        b_left = _left_inverse_on_columns(b_l)
        p_kernel_b = sp.eye(metric.dimension) - l_b * b_left * b
        if b * p_kernel_b != sp.zeros(equation.dimension, metric.dimension):
            raise AssertionError("metric kernel projector failed")

        # Standard coordinate vectors complementary to im(A)+L_B are
        # projected into ker(B).  This avoids a large nullspace/RREF of the
        # whole BV complex and yields exact cohomology representatives H.
        occupied = sp.Matrix.hstack(a, l_b)
        pivot_rows = set(
            occupied.T.rref(simplify=False, normalize_last=True)[1]
        )
        free_rows = tuple(
            row for row in range(metric.dimension) if row not in pivot_rows
        )
        h = p_kernel_b * _standard_columns(metric.dimension, free_rows)
        t_metric = sp.Matrix.hstack(a, h, l_b)
        if t_metric.cols != metric.dimension:
            raise AssertionError("metric decomposition has the wrong size")
        t_metric_inverse = _inverse(t_metric)

        # Exactness at the equation and identity slots supplies the two
        # remaining contractible pairs.
        c_pivots = tuple(c.rref(simplify=False, normalize_last=True)[1])
        l_c = _standard_columns(equation.dimension, c_pivots)
        c_l = c * l_c
        t_equation = sp.Matrix.hstack(b_l, l_c)
        if t_equation.cols != equation.dimension:
            raise AssertionError("equation row contains additional cohomology")
        t_equation_inverse = _inverse(t_equation)
        if c_l.shape != (identity.dimension, identity.dimension):
            raise AssertionError("identity arrow is not surjective")
        t_identity = c_l
        t_identity_inverse = _inverse(t_identity)

        t_gauge = sp.eye(gauge.dimension)
        t = _block_diagonal((t_gauge, t_metric, t_equation, t_identity))
        t_inverse = _block_diagonal(
            (
                t_gauge,
                t_metric_inverse,
                t_equation_inverse,
                t_identity_inverse,
            )
        )

        h_dimension = h.cols
        q_adapted = sp.zeros(block.dimension)
        # G -> the first metric coordinates (im A).
        for index in range(gauge.dimension):
            q_adapted[metric.start + index, gauge.start + index] = 1
        # L_B -> the first equation coordinates (im B).
        metric_l_start = metric.start + gauge.dimension + h_dimension
        for index in range(len(b_pivots)):
            q_adapted[equation.start + index, metric_l_start + index] = 1
        # L_C -> identity.
        equation_l_start = equation.start + len(b_pivots)
        for index in range(len(c_pivots)):
            q_adapted[identity.start + index, equation_l_start + index] = 1

        if t_inverse * sp.Matrix(block.q) * t != q_adapted:
            raise AssertionError("adapted differential is not a partial identity")

        inclusion_adapted = sp.zeros(block.dimension, h_dimension)
        for index in range(h_dimension):
            inclusion_adapted[metric.start + gauge.dimension + index, index] = 1
        projection_adapted = inclusion_adapted.T

        homotopy_adapted = sp.zeros(block.dimension)
        for index in range(gauge.dimension):
            homotopy_adapted[
                gauge.start + index, metric.start + index
            ] = 1
        for index in range(len(b_pivots)):
            homotopy_adapted[
                metric_l_start + index, equation.start + index
            ] = 1
        for index in range(len(c_pivots)):
            homotopy_adapted[
                equation_l_start + index, identity.start + index
            ] = 1

        result = cls(
            block=block,
            inclusion=t * inclusion_adapted,
            projection=projection_adapted * t_inverse,
            homotopy=t * homotopy_adapted * t_inverse,
            adapted_basis=t,
            adapted_inverse=t_inverse,
            cohomology_dimension=h_dimension,
        )
        result.verify()
        return result

    def verify(self) -> None:
        identity = sp.eye(self.block.dimension)
        reduced_identity = sp.eye(self.cohomology_dimension)
        q = sp.Matrix(self.block.q)
        if self.projection * self.inclusion != reduced_identity:
            raise AssertionError("p j != 1")
        if (
            self.inclusion * self.projection
            != identity - q * self.homotopy - self.homotopy * q
        ):
            raise AssertionError("j p != 1-q s-s q")
        if q * self.inclusion != sp.zeros(
            self.block.dimension, self.cohomology_dimension
        ):
            raise AssertionError("q j != 0")
        if self.projection * q != sp.zeros(
            self.cohomology_dimension, self.block.dimension
        ):
            raise AssertionError("p q != 0")
        if self.projection * self.homotopy != sp.zeros(
            self.cohomology_dimension, self.block.dimension
        ):
            raise AssertionError("p s != 0")
        if self.homotopy * self.inclusion != sp.zeros(
            self.block.dimension, self.cohomology_dimension
        ):
            raise AssertionError("s j != 0")
        if self.homotopy * self.homotopy != sp.zeros(
            self.block.dimension, self.block.dimension
        ):
            raise AssertionError("s^2 != 0")

    def induced(self, operator: sp.MatrixBase, target: "RawPolynomialRetraction") -> sp.Matrix:
        """Induce a chain map from this block to ``target`` on cohomology."""

        return target.projection * sp.Matrix(operator) * self.inclusion

    def inclusion_defect(
        self, operator: sp.MatrixBase, target: "RawPolynomialRetraction"
    ) -> sp.Matrix:
        induced = self.induced(operator, target)
        return sp.Matrix(operator) * self.inclusion - target.inclusion * induced

    def projection_defect(
        self, operator: sp.MatrixBase, target: "RawPolynomialRetraction"
    ) -> sp.Matrix:
        induced = self.induced(operator, target)
        return target.projection * sp.Matrix(operator) - induced * self.projection

    def homotopy_defect(
        self, operator: sp.MatrixBase, target: "RawPolynomialRetraction"
    ) -> sp.Matrix:
        return (
            sp.Matrix(operator) * self.homotopy
            - target.homotopy * sp.Matrix(operator)
        )


def verify_homotopy_equivariance(
    source: RawPolynomialRetraction,
    target: RawPolynomialRetraction,
    operator: sp.MatrixBase,
    *,
    measure_ranks: bool = True,
) -> dict[str, int]:
    """Measure a conformal chain map and prove its defects are controlled."""

    rho = sp.Matrix(operator)
    q_source = sp.Matrix(source.block.q)
    q_target = sp.Matrix(target.block.q)
    if q_target * rho != rho * q_source:
        raise AssertionError("operator is not a chain map")

    inclusion_defect = source.inclusion_defect(rho, target)
    projection_defect = source.projection_defect(rho, target)
    homotopy_defect = source.homotopy_defect(rho, target)

    if q_target * inclusion_defect != sp.zeros(
        target.block.dimension, source.cohomology_dimension
    ):
        raise AssertionError("inclusion defect is not closed")
    if target.projection * inclusion_defect != sp.zeros(
        target.cohomology_dimension, source.cohomology_dimension
    ):
        raise AssertionError("inclusion defect survives on cohomology")
    if q_target * target.homotopy * inclusion_defect != inclusion_defect:
        raise AssertionError("inclusion defect is not explicitly q-exact")

    # p rho-rho_H p is a right q-homotopy.  This is the exact identity,
    # not merely a rank comparison.
    if projection_defect != (
        target.projection * rho * source.homotopy * q_source
    ):
        raise AssertionError("projection defect lacks its q-homotopy")

    # The commutator of rho with s is itself a homotopy between two
    # contractions.  Its graded commutator with q is minus the difference
    # between the two jp projectors.
    expected = -(
        rho * source.inclusion * source.projection
        - target.inclusion * target.projection * rho
    )
    if q_target * homotopy_defect + homotopy_defect * q_source != expected:
        raise AssertionError("homotopy-defect identity failed")

    if not measure_ranks:
        return {}
    return {
        "induced_rank": source.induced(rho, target).rank(),
        "inclusion_defect_rank": inclusion_defect.rank(),
        "projection_defect_rank": projection_defect.rank(),
        "homotopy_defect_rank": homotopy_defect.rank(),
    }
