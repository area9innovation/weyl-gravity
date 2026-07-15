"""Order-two no-go for the minimal rational obstruction-channel split.

The companion module :mod:`quadratic_obstruction_channel` proves that

``A_-=e_11-e_66,  A_+=-e_11+e_66``

repairs the common bare-Box ``f_0i -> f_00`` obstruction orbit.  Here that
split is frozen and the *complete* simultaneous order-two equations for
``DP`` and ``PD`` are assembled.  The remaining variables are the shared
parallel invariant correction ``X_0`` and four independent parallel
invariant factor coefficients ``B_{L-},B_{L+},B_{R-},B_{R+}``, 38 parameters
each.

The resulting exact rational system is inconsistent.  Its one-row left-null
witness is a different DP channel, so the attractive two-direction repair
does not extend to a factorization branch.  The obstruction lies wholly on
the DP side and is therefore independent of how the right first-order split
is chosen.
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
    _endomorphism,
    _field_operator_tables,
    _left_null_witness,
    _matrix_system,
    _sparse_entries,
    _zeroth_invariant_basis,
)
from .symmetrized_pbw_composition import SymmetrizedPBWComposer


def _order_two(table: dict[tuple[int, ...], sp.Matrix]) -> dict:
    return {word: matrix for word, matrix in table.items() if len(word) == 2}


@dataclass(frozen=True)
class QuadraticObstructionChannelFixedBranch:
    invariant_algebraic_dimension: int
    unknown_count: int
    equation_shape: tuple[int, int]
    coefficient_rank: int
    augmented_rank: int
    left_null_witness: dict[str, object]

    @staticmethod
    def build() -> "QuadraticObstructionChannelFixedBranch":
        pbw = SymmetrizedPBWComposer.build()
        first_equations = DomainMatrix.from_Matrix(
            _field_first_order_invariance_matrix()
        )
        first_basis = first_equations.nullspace().to_Matrix().T
        if first_basis.shape != (2304, 93):
            raise AssertionError("complete first-order invariant basis drifted")
        basis_11 = _coefficient_tuple(first_basis[:, 11])
        basis_66 = _coefficient_tuple(first_basis[:, 66])
        split = tuple(basis_11[axis] - basis_66[axis] for axis in range(4))
        a_minus = {
            (axis,): matrix
            for axis, matrix in enumerate(split)
            if matrix != sp.zeros(24)
        }
        a_plus = {
            (axis,): -matrix
            for axis, matrix in enumerate(split)
            if matrix != sp.zeros(24)
        }

        field, complement, box = _field_operator_tables(pbw)
        left_minus = _add_tables((1, box), (1, a_minus))
        left_plus = _add_tables((1, box), (1, a_plus))
        # The same split is used to instantiate PD.  The final obstruction is
        # supported only on DP, so changing this right split cannot alter it.
        right_minus = left_minus
        right_plus = left_plus
        baseline_left = _add_tables(
            (1, pbw.compose(complement, field)),
            (-1, pbw.compose(left_minus, left_plus)),
        )
        baseline_right = _add_tables(
            (1, pbw.compose(field, complement)),
            (-1, pbw.compose(right_minus, right_plus)),
        )

        zeroth_basis = _zeroth_invariant_basis()
        zeroth_tables = tuple(
            {(): _endomorphism(zeroth_basis[:, column])}
            for column in range(zeroth_basis.cols)
        )
        columns: list[dict] = []
        # Shared X0 in D.
        for table in zeroth_tables:
            columns.append(
                {
                    **_sparse_entries("DP", _order_two(pbw.compose(table, field))),
                    **_sparse_entries("PD", _order_two(pbw.compose(field, table))),
                }
            )
        # Four independent B0 coefficients.  Their products with each other
        # start at order zero, so the order-two gate is exactly linear.
        for side, minus, plus in (
            ("DP", left_minus, left_plus),
            ("PD", right_minus, right_plus),
        ):
            for table in zeroth_tables:  # outer B_-
                columns.append(
                    _sparse_entries(
                        side,
                        {
                            word: -matrix
                            for word, matrix in _order_two(
                                pbw.compose(table, plus)
                            ).items()
                        },
                    )
                )
            for table in zeroth_tables:  # inner B_+
                columns.append(
                    _sparse_entries(
                        side,
                        {
                            word: -matrix
                            for word, matrix in _order_two(
                                pbw.compose(minus, table)
                            ).items()
                        },
                    )
                )

        baseline = {
            **_sparse_entries("DP", _order_two(baseline_left)),
            **_sparse_entries("PD", _order_two(baseline_right)),
        }
        keys, matrix, rhs = _matrix_system(baseline, tuple(columns))
        rank = DomainMatrix.from_Matrix(matrix).rank()
        augmented_rank = DomainMatrix.from_Matrix(matrix.row_join(rhs)).rank()
        witness = _left_null_witness(keys, matrix, rhs)
        if witness is None:
            raise AssertionError("fixed minimal split unexpectedly became consistent")
        result = QuadraticObstructionChannelFixedBranch(
            invariant_algebraic_dimension=zeroth_basis.cols,
            unknown_count=len(columns),
            equation_shape=matrix.shape,
            coefficient_rank=rank,
            augmented_rank=augmented_rank,
            left_null_witness=witness,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.invariant_algebraic_dimension != 38:
            raise AssertionError("invariant algebraic dimension drifted")
        if self.unknown_count != 190:
            raise AssertionError("fixed-branch variable ledger drifted")
        if self.equation_shape != (1377, 190):
            raise AssertionError("fixed-branch order-two equation shape drifted")
        if (self.coefficient_rank, self.augmented_rank) != (100, 101):
            raise AssertionError("fixed-branch rank obstruction drifted")
        if self.left_null_witness["support_size"] != 1:
            raise AssertionError("fixed-branch witness support drifted")
        support = self.left_null_witness["support"][0]
        if (
            self.left_null_witness["lT_b"],
            support["side"],
            support["symmetric_derivative_word"],
            support["output_component"],
            support["input_component"],
            support["coefficient"],
        ) != ("16", "DP", [0, 1], 11, 7, "1"):
            raise AssertionError("fixed-branch one-row obstruction drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-quadratic-obstruction-channel-fixed-branch-v1",
            "fixed_first_order_split": {
                "left_A_minus": "e_11-e_66",
                "left_A_plus": "-e_11+e_66",
                "left_sum": 0,
                "right_instantiation": "same split",
                "right_split_independence_of_obstruction": (
                    "the exact left-null witness is supported only on DP"
                ),
                "source_certificate": "quadratic_obstruction_channel.json",
            },
            "complete_order_two_system": {
                "sides": ["DP", "PD"],
                "symmetrized_PBW_curvature_exact": True,
                "variables": {
                    "shared_X0": self.invariant_algebraic_dimension,
                    "B_L_minus": self.invariant_algebraic_dimension,
                    "B_L_plus": self.invariant_algebraic_dimension,
                    "B_R_minus": self.invariant_algebraic_dimension,
                    "B_R_plus": self.invariant_algebraic_dimension,
                    "total": self.unknown_count,
                },
                "equation_shape": list(self.equation_shape),
                "coefficient_rank": self.coefficient_rank,
                "augmented_rank": self.augmented_rank,
                "consistent": False,
                "kernel_dimension_of_coefficient_matrix": (
                    self.unknown_count - self.coefficient_rank
                ),
                "left_null_obstruction": self.left_null_witness,
                "invariant_channel": {
                    "side": "DP",
                    "symmetric_derivative": "nabla_(0 nabla_1)",
                    "map": "h_22 -> f_01",
                    "required_right_hand_side": "16",
                    "all_190_variable_coefficients": 0,
                },
            },
            "outcome": {
                "minimal_rational_channel_split_extends_to_order_two": False,
                "obstructed_before_order_one_and_zero": True,
                "order_one_system_assembled": False,
                "order_zero_system_assembled": False,
                "other_first_order_splits_decided": False,
                "general_two_nontrivial_factor_branch_decided": False,
                "mixed_order_factorization_proved": False,
                "green_realization_proved": False,
                "flag_promoted": False,
            },
            "theorem_boundary": (
                "The support-minimal rational split which repairs the old "
                "f_0i-to-f_00 orbit fails the complete simultaneous DP/PD "
                "order-two equations after exhausting all 190 invariant "
                "algebraic variables.  This is a no-go only for that fixed "
                "left split; it neither obstructs other nonzero cubic sums "
                "nor the complete 421-parameter nonlinear family."
            ),
        }
