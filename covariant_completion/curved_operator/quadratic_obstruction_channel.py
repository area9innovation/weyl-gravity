"""Exact repair of the bare-Box quadratic obstruction channel.

The four bare-Box branches fail in the same symmetrized order-two row,

``nabla_(0 nabla_1) : f_01 -> f_00``.

In the general factor product

``(Box+A_-^mu nabla_mu+B_-)(Box+A_+^mu nabla_mu+B_+)``

the missing order-two term is the bilinear product of the first-order
coefficients.  This module evaluates that product on the *complete* 93
parameter SO(3)-invariant first-order family.  The cubic equations determine
only ``S=A_-+A_+``; writing ``A_-=T`` and ``A_+=S-T`` retains an arbitrary
93-parameter split ``T``.

The common ``-8`` correction is attainable already on the zero cubic
solution ``X_1=S_L=S_R=0``.  A two-basis-direction rational split repairs the
entire SO(3) orbit of three rows and has no other bilinear support.  This is
only a scoped positive result: hundreds of other quadratic/lower equations
remain, so no factorization or Green theorem is inferred.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from .auxiliary_lower_order_factor_ansatz import (
    _coefficient_tuple,
    _field_first_order_invariance_matrix,
)
from .auxiliary_triangular_box_factor import (
    _add_tables,
    _field_operator_tables,
)
from .symmetrized_pbw_composition import SymmetrizedPBWComposer


def _complete_first_order_basis() -> sp.Matrix:
    equations = DomainMatrix.from_Matrix(_field_first_order_invariance_matrix())
    basis = equations.nullspace().to_Matrix().T
    if basis.shape != (2304, 93):
        raise AssertionError("complete invariant first-order basis drifted")
    return basis


def _channel_matrix(
    coefficient_tuples: tuple[tuple[sp.Matrix, ...], ...],
) -> sp.SparseMatrix:
    """Return ``(A_-^0 A_+^1+A_-^1 A_+^0)_{f00,f01}``.

    Rows label the outer-factor invariant basis and columns the inner-factor
    invariant basis.  This is the exhaustive bilinear coefficient on the
    complete family, before imposing the cubic sum.
    """

    entries: dict[tuple[int, int], sp.Expr] = {}
    for outer, left in enumerate(coefficient_tuples):
        for inner, right in enumerate(coefficient_tuples):
            value = sp.expand(
                (left[0] * right[1] + left[1] * right[0])[10, 11]
            )
            if value != 0:
                entries[(outer, inner)] = value
    return sp.SparseMatrix(93, 93, entries)


@dataclass(frozen=True)
class QuadraticObstructionChannel:
    invariant_first_order_dimension: int
    channel_matrix_shape: tuple[int, int]
    channel_matrix_rank: int
    channel_matrix_support: tuple[tuple[int, int, sp.Expr], ...]
    split_outer_coordinates: tuple[tuple[int, sp.Expr], ...]
    split_inner_coordinates: tuple[tuple[int, sp.Expr], ...]
    factor_channel_value: sp.Expr
    defect_correction_value: sp.Expr
    baseline_orbit: tuple[sp.Expr, ...]
    bilinear_orbit: tuple[sp.Expr, ...]
    corrected_orbit: tuple[sp.Expr, ...]
    bilinear_order_two_support: tuple[
        tuple[tuple[int, ...], int, int, sp.Expr], ...
    ]
    remaining_quadratic_defect_entries: int

    @staticmethod
    def build() -> "QuadraticObstructionChannel":
        basis = _complete_first_order_basis()
        coefficients = tuple(
            _coefficient_tuple(basis[:, column]) for column in range(basis.cols)
        )
        channel = _channel_matrix(coefficients)

        # The zero simultaneous cubic solution has X1=S_L=S_R=0.  Hence the
        # two factor coefficients may be opposite.  T=e_11-e_66 is the
        # sparsest rational choice in this canonical invariant basis which
        # reaches the obstruction channel.
        outer_vector = sp.zeros(93, 1)
        outer_vector[11] = 1
        outer_vector[66] = -1
        inner_vector = -outer_vector
        outer_coefficients = _coefficient_tuple(basis * outer_vector)
        inner_coefficients = _coefficient_tuple(basis * inner_vector)
        outer_table = {
            (axis,): matrix
            for axis, matrix in enumerate(outer_coefficients)
            if matrix != sp.zeros(24)
        }
        inner_table = {
            (axis,): matrix
            for axis, matrix in enumerate(inner_coefficients)
            if matrix != sp.zeros(24)
        }

        pbw = SymmetrizedPBWComposer.build()
        bilinear = pbw.compose(outer_table, inner_table)
        field, complement, box = _field_operator_tables(pbw)
        box_square = pbw.compose(box, box)
        baseline = _add_tables(
            (1, pbw.compose(complement, field)), (-1, box_square)
        )
        corrected = _add_tables((1, baseline), (-1, bilinear))

        orbit = ((1, 11), (2, 12), (3, 13))
        baseline_values = tuple(
            baseline[(0, spatial)][10, input_component]
            for spatial, input_component in orbit
        )
        bilinear_values = tuple(
            bilinear[(0, spatial)][10, input_component]
            for spatial, input_component in orbit
        )
        corrected_values = tuple(
            corrected.get((0, spatial), sp.zeros(24))[10, input_component]
            for spatial, input_component in orbit
        )
        order_two_support = tuple(
            (word, row, column, value)
            for word, matrix in sorted(bilinear.items())
            if len(word) == 2
            for (row, column), value in sorted(matrix.todok().items())
            if value != 0
        )
        result = QuadraticObstructionChannel(
            invariant_first_order_dimension=basis.cols,
            channel_matrix_shape=channel.shape,
            channel_matrix_rank=DomainMatrix.from_Matrix(channel).rank(),
            channel_matrix_support=tuple(
                (row, column, value)
                for (row, column), value in sorted(channel.todok().items())
            ),
            split_outer_coordinates=((11, sp.Integer(1)), (66, sp.Integer(-1))),
            split_inner_coordinates=((11, sp.Integer(-1)), (66, sp.Integer(1))),
            factor_channel_value=sp.expand(
                (outer_vector.T * channel * inner_vector)[0]
            ),
            defect_correction_value=sp.expand(
                -(outer_vector.T * channel * inner_vector)[0]
            ),
            baseline_orbit=baseline_values,
            bilinear_orbit=bilinear_values,
            corrected_orbit=corrected_values,
            bilinear_order_two_support=order_two_support,
            remaining_quadratic_defect_entries=sum(
                value != 0
                for word, matrix in corrected.items()
                if len(word) == 2
                for value in matrix
            ),
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.invariant_first_order_dimension != 93:
            raise AssertionError("complete first-order dimension drifted")
        if self.channel_matrix_shape != (93, 93):
            raise AssertionError("channel bilinear shape drifted")
        expected_support = (
            (2, 65, sp.Integer(4)),
            (11, 66, sp.Integer(8)),
            (11, 67, sp.Integer(4)),
            (17, 68, sp.Integer(4)),
            (26, 69, sp.Integer(8)),
            (26, 70, sp.Integer(4)),
            (32, 71, sp.Integer(4)),
            (47, 20, sp.Integer(4)),
            (68, 21, sp.Integer(4)),
            (89, 22, sp.Integer(4)),
        )
        if self.channel_matrix_support != expected_support:
            raise AssertionError("complete channel polynomial drifted")
        if self.channel_matrix_rank != 8:
            raise AssertionError("channel bilinear rank drifted")
        if self.factor_channel_value != 8 or self.defect_correction_value != -8:
            raise AssertionError("common -8 correction was not attained")
        if self.baseline_orbit != (8, 8, 8):
            raise AssertionError("bare-Box obstruction orbit drifted")
        if self.bilinear_orbit != (8, 8, 8):
            raise AssertionError("bilinear SO(3) orbit drifted")
        if self.corrected_orbit != (0, 0, 0):
            raise AssertionError("obstruction orbit was not repaired")
        expected_product_support = (
            ((0, 1), 10, 11, sp.Integer(8)),
            ((0, 2), 10, 12, sp.Integer(8)),
            ((0, 3), 10, 13, sp.Integer(8)),
        )
        if self.bilinear_order_two_support != expected_product_support:
            raise AssertionError("minimal bilinear support drifted")
        if self.remaining_quadratic_defect_entries != 315:
            raise AssertionError("scoped remaining-defect ledger drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-quadratic-obstruction-channel-v1",
            "scope": {
                "factorization_side": "DP only",
                "derivative_order": 2,
                "common_bare_Box_row": {
                    "symmetric_derivative_word": [0, 1],
                    "output": "f_00",
                    "input": "f_01",
                    "baseline_defect": "8",
                    "required_correction": "-8",
                },
                "complete_invariant_first_order_dimension": (
                    self.invariant_first_order_dimension
                ),
                "cubic_parameterization": (
                    "A_-=T, A_+=S_L-T; the simultaneous cubic equations "
                    "restrict S_L but leave T in the complete 93-dimensional "
                    "invariant family"
                ),
            },
            "exact_channel_polynomial": {
                "factor_coefficient": (
                    "C(T,S_L-T)=sum_ij T_i (S_L_j-T_j) M_ij"
                ),
                "defect_correction": "-C(T,S_L-T)",
                "matrix_shape": list(self.channel_matrix_shape),
                "matrix_rank": self.channel_matrix_rank,
                "nonzero_monomials": [
                    {"outer_basis": i, "inner_basis": j, "coefficient": str(v)}
                    for i, j, v in self.channel_matrix_support
                ],
                "nonzero_monomial_count": len(self.channel_matrix_support),
            },
            "minimal_rational_assignment": {
                "simultaneous_cubic_solution": "X_1=S_L=S_R=0",
                "A_minus": [
                    {"basis": i, "coefficient": str(value)}
                    for i, value in self.split_outer_coordinates
                ],
                "A_plus": [
                    {"basis": i, "coefficient": str(value)}
                    for i, value in self.split_inner_coordinates
                ],
                "A_minus_plus_A_plus": 0,
                "independent_invariant_basis_directions": 2,
                "minimality_within_zero_sum_branch": (
                    "all 93 diagonal entries M_ii vanish, so one invariant "
                    "basis direction gives zero; the displayed two-direction "
                    "assignment is therefore support-minimal in the canonical basis"
                ),
                "factor_bilinear_channel_value": str(self.factor_channel_value),
                "defect_correction_value": str(self.defect_correction_value),
                "required_minus_eight_attained": True,
            },
            "smallest_SO3_coupled_orbit": {
                "rows": [
                    {
                        "symmetric_derivative_word": [0, spatial],
                        "output": "f_00",
                        "input": f"f_0{spatial}",
                        "baseline": str(baseline),
                        "factor_bilinear": str(bilinear),
                        "corrected_defect": str(corrected),
                    }
                    for spatial, (baseline, bilinear, corrected) in enumerate(
                        zip(
                            self.baseline_orbit,
                            self.bilinear_orbit,
                            self.corrected_orbit,
                            strict=True,
                        ),
                        start=1,
                    )
                ],
                "bilinear_order_two_support_exhausted": True,
                "additional_bilinear_rows": 0,
            },
            "outcome": {
                "bare_Box_common_obstruction_survives_general_branch": False,
                "minus_eight_attainable": True,
                "common_SO3_orbit_repaired": True,
                "remaining_baseline_minus_bilinear_order_two_entries_before_other_corrections": (
                    self.remaining_quadratic_defect_entries
                ),
                "full_quadratic_system_solved": False,
                "mixed_order_factorization_proved": False,
                "green_realization_proved": False,
                "flag_promoted": False,
            },
            "theorem_boundary": (
                "The bilinear A_- A_+ term exactly repairs the one-row "
                "left-null obstruction of every bare-Box branch, together "
                "with its two SO(3)-related rows.  Therefore that obstruction "
                "does not extend to the full two-nontrivial-factor family.  "
                "The other quadratic and all lower-order equations are not "
                "solved here, so no factorization, Green operator, homotopy, "
                "or top-level flag follows."
            ),
        }
