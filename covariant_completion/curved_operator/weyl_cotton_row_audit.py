"""Audit the adjusted Weyl--Cotton evolution against the covariant 34 rows.

The exact curvature/Cotton system has 34 first-order rows on 26 variables:
sixteen Cotton definitions, nine Bach equations and nine dual equations.
The symmetric-hyperbolic reduction replaces the six vector Bach evolution
rows by propagation equations for the two primary divergence constraints.

This module checks that replacement as an equality of differential-operator
row modules.  It deliberately distinguishes:

* the first twenty adjusted rows, which are exact covariant row combinations;
* the final six propagation rows, which differ from the covariant vector
  Bach rows by the six additional ``a,c`` constraint components; and
* the original eight constraints ``q,r,s,t`` from the enlarged fourteen
  component subsidiary state ``q,r,a,c,s,t``.

No status flag is promoted here.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from .weyl_3plus1 import WeylCottonBachFirstOrder
from .weyl_cotton_hyperbolic import ConstraintAdjustedWeylCottonEvolution


def _matrix_digest(matrix: sp.Matrix) -> str:
    return hashlib.sha256(sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode()).hexdigest()


def _old_from_natural_state() -> sp.Matrix:
    """Map ``(E,B,A,C,x,y)`` to ``(E,B,X_STF,X_vec,Y_STF,Y_vec)``.

    Exact Weyl divergence gives ``A=X_STF``, ``C=Y_STF``,
    ``x=-2 Y_vec`` and ``y=2 X_vec``.
    """

    transform = sp.zeros(26)
    transform[:10, :10] = sp.eye(10)
    transform[10:15, 10:15] = sp.eye(5)
    transform[15:18, 23:26] = sp.eye(3) / 2
    transform[18:23, 15:20] = sp.eye(5)
    transform[23:26, 20:23] = -sp.eye(3) / 2
    return transform


def _exact_tables(
    first_order: WeylCottonBachFirstOrder,
    transform: sp.Matrix,
) -> tuple[sp.Matrix, ...]:
    zero_16 = sp.zeros(16, 16)
    zero_9_10 = sp.zeros(9, 10)
    derivative_tables: list[sp.Matrix] = []
    for axis in range(4):
        table = (
            (-first_order.decomposition.cotton_divergence_coefficients[axis])
            .row_join(zero_16)
            .col_join(
                zero_9_10.row_join(
                    first_order.bach_derivative_coefficients[axis]
                )
            )
            .col_join(
                zero_9_10.row_join(
                    first_order.compatibility_derivative_coefficients[axis]
                )
            )
        )
        derivative_tables.append(table * transform)
    zeroth = (
        sp.zeros(16, 10)
        .row_join(sp.eye(16))
        .col_join(
            first_order.bach_zeroth_coefficient.row_join(sp.zeros(9, 16))
        )
        .col_join(
            first_order.compatibility_zeroth_coefficient.row_join(
                sp.zeros(9, 16)
            )
        )
    )
    return tuple(derivative_tables) + (zeroth * transform,)


def _adjusted_tables(
    adjusted: ConstraintAdjustedWeylCottonEvolution,
) -> tuple[sp.Matrix, ...]:
    return (
        sp.eye(26),
        *adjusted.evolution_spatial_coefficients,
        adjusted.evolution_zeroth_coefficient,
    )


def _constraint_tables(
    adjusted: ConstraintAdjustedWeylCottonEvolution,
) -> tuple[sp.Matrix, ...]:
    # These are the natural constraint definitions K(U), not their
    # subsidiary evolution operator.
    return (
        sp.zeros(14, 26),
        *adjusted.source_compatibility_spatial_coefficients,
        adjusted.source_compatibility_zeroth_coefficient,
    )


def _flatten_tables(tables: tuple[sp.Matrix, ...]) -> sp.Matrix:
    return sp.Matrix.hstack(*tables)


@dataclass(frozen=True)
class WeylCottonRowReductionAudit:
    exact_row_rank: int
    adjusted_row_rank: int
    exact_plus_adjusted_rank: int
    exact_first_twenty_defects: int
    adjusted_vector_defects: int
    original_constraint_rank: int
    original_constraint_defects: int
    enlarged_constraint_rank: int
    additional_ac_rank: int
    adjusted_plus_eight_rank: int
    exact_plus_adjusted_plus_eight_rank: int
    vector_difference_defect: int
    zeroth_order_difference_defect: int
    first_twenty_row_map_sha256: str

    @staticmethod
    def build(*, verify: bool = True) -> "WeylCottonRowReductionAudit":
        first_order = WeylCottonBachFirstOrder.build()
        adjusted = ConstraintAdjustedWeylCottonEvolution.build()
        transform = _old_from_natural_state()
        exact_tables = _exact_tables(first_order, transform)
        adjusted_tables = _adjusted_tables(adjusted)
        constraint_tables = _constraint_tables(adjusted)

        exact = _flatten_tables(exact_tables)
        adjusted_rows = _flatten_tables(adjusted_tables)
        constraints = _flatten_tables(constraint_tables)

        # The temporal pivot rows give the canonical unadjusted square
        # reduction.  Normalize them so their time coefficient is I_26.
        pivots = tuple(first_order.temporal_matrix.T.rref()[1])
        selected_temporal = exact_tables[0][list(pivots), :]
        unadjusted_tables = tuple(
            selected_temporal.inv() * table[list(pivots), :]
            for table in exact_tables
        )

        # Row-containment defects.  The exact row table has full row rank,
        # so the displayed right inverse gives the unique coefficient map.
        exact_right_inverse = exact.T * (exact * exact.T).inv()
        first_twenty_map = adjusted_rows[:20, :] * exact_right_inverse
        first_twenty_defect_matrix = first_twenty_map * exact - adjusted_rows[:20, :]
        vector_map = adjusted_rows[20:26, :] * exact_right_inverse
        vector_defect_matrix = vector_map * exact - adjusted_rows[20:26, :]

        # Original constraints are q[3],r[3],s[1],t[1].  The adjusted
        # subsidiary state additionally contains a[3],c[3].
        original_indices = (0, 1, 2, 3, 4, 5, 12, 13)
        ac_indices = tuple(range(6, 12))
        original_constraints = constraints[list(original_indices), :]
        ac_constraints = constraints[list(ac_indices), :]
        original_constraint_map = original_constraints * exact_right_inverse
        original_constraint_defect_matrix = (
            original_constraint_map * exact - original_constraints
        )

        # The exact relation is R_x=U_x-2a and R_y=U_y-2c for every
        # derivative and zeroth table.
        ac_multiplier = sp.zeros(6, 14)
        ac_multiplier[:3, 6:9] = -2 * sp.eye(3)
        ac_multiplier[3:, 9:12] = -2 * sp.eye(3)
        vector_difference_defect = 0
        zeroth_difference_defect = 0
        for table_index, (candidate, unadjusted, constraint) in enumerate(
            zip(adjusted_tables, unadjusted_tables, constraint_tables, strict=True)
        ):
            defect = (
                candidate[20:26, :]
                - unadjusted[20:26, :]
                - ac_multiplier * constraint
            )
            count = sum(int(value != 0) for value in defect)
            if table_index == 4:
                zeroth_difference_defect += count
            else:
                vector_difference_defect += count

        result = WeylCottonRowReductionAudit(
            exact_row_rank=exact.rank(),
            adjusted_row_rank=adjusted_rows.rank(),
            exact_plus_adjusted_rank=exact.col_join(adjusted_rows).rank(),
            exact_first_twenty_defects=sum(
                int(value != 0) for value in first_twenty_defect_matrix
            ),
            adjusted_vector_defects=sum(
                int(value != 0) for value in vector_defect_matrix
            ),
            original_constraint_rank=original_constraints.rank(),
            original_constraint_defects=sum(
                int(value != 0) for value in original_constraint_defect_matrix
            ),
            enlarged_constraint_rank=constraints.rank(),
            additional_ac_rank=original_constraints.col_join(ac_constraints).rank()
            - original_constraints.rank(),
            adjusted_plus_eight_rank=adjusted_rows.col_join(
                original_constraints
            ).rank(),
            exact_plus_adjusted_plus_eight_rank=exact.col_join(
                adjusted_rows
            ).col_join(original_constraints).rank(),
            vector_difference_defect=vector_difference_defect,
            zeroth_order_difference_defect=zeroth_difference_defect,
            first_twenty_row_map_sha256=_matrix_digest(first_twenty_map),
        )
        if verify:
            result.verify()
        return result

    def verify(self) -> None:
        if self.exact_row_rank != 34 or self.adjusted_row_rank != 26:
            raise AssertionError("unexpected covariant/adjusted row ranks")
        if self.exact_first_twenty_defects != 0:
            raise AssertionError("the first twenty adjusted rows are not covariant rows")
        if self.adjusted_vector_defects == 0:
            raise AssertionError("the six adjusted propagation rows were mistaken for Bach rows")
        if self.exact_plus_adjusted_rank != 40:
            raise AssertionError("the exact adjusted-row defect lost rank six")
        if self.original_constraint_rank != 8:
            raise AssertionError("the original q,r,s,t constraint rank drifted")
        if self.original_constraint_defects != 0:
            raise AssertionError("q,r,s,t are not exact covariant constraint rows")
        if self.enlarged_constraint_rank != 14 or self.additional_ac_rank != 6:
            raise AssertionError("the a,c constraints are not six independent additions")
        if self.adjusted_plus_eight_rank != 34:
            raise AssertionError("adjusted evolution plus eight constraints lost rank")
        if self.exact_plus_adjusted_plus_eight_rank != 40:
            raise AssertionError("eight constraints unexpectedly repaired row equivalence")
        if self.vector_difference_defect or self.zeroth_order_difference_defect:
            raise AssertionError("R_vector=U_vector-2(a,c) identity failed")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-cotton-adjusted-row-audit-v1",
            "state_order": "E[5],B[5],A[5],C[5],x[3],y[3]",
            "exact_covariant_rows": 34,
            "adjusted_evolution_rows": 26,
            "exact_row_rank": self.exact_row_rank,
            "adjusted_row_rank": self.adjusted_row_rank,
            "first_twenty_adjusted_rows_are_exact_covariant_combinations": True,
            "first_twenty_row_map_sha256": self.first_twenty_row_map_sha256,
            "exact_curvature_lower_terms_in_first_twenty": [
                "+E in the A row",
                "+B in the C row",
            ],
            "exact_first_order_couplings_in_first_twenty": [
                "-(1/2)Lx",
                "-(1/2)Ly",
            ],
            "first_twenty_lower_order_covariant": True,
            "adjusted_vector_rows_are_covariant_Bach_row_combinations": False,
            "exact_vector_relation": [
                "R_x=U_x-2a",
                "R_y=U_y-2c",
            ],
            "vector_relation_defect": self.vector_difference_defect,
            "zeroth_order_relation_defect": self.zeroth_order_difference_defect,
            "original_eight_constraints": "q[3],r[3],s[1],t[1]",
            "original_constraint_rank": self.original_constraint_rank,
            "original_constraints_are_exact_covariant_rows": True,
            "additional_constraints": "a[3],c[3]",
            "additional_constraint_rank": self.additional_ac_rank,
            "enlarged_constraint_rank": self.enlarged_constraint_rank,
            "adjusted_plus_eight_rank": self.adjusted_plus_eight_rank,
            "exact_plus_adjusted_plus_eight_rank": (
                self.exact_plus_adjusted_plus_eight_rank
            ),
            "row_equivalent_modulo_original_eight_constraints": False,
            "exact_defect_rank": (
                self.exact_plus_adjusted_plus_eight_rank
                - self.adjusted_plus_eight_rank
            ),
            "interpretation": (
                "the hyperbolic R_x,R_y rows propagate q,r; they replace, rather "
                "than pointwise recombine, the vector Bach rows. Recovering the "
                "covariant rows additionally requires a=c=0 or a separate proof "
                "that these six conditions follow in the formally integrable "
                "prolonged system"
            ),
            "subsidiary_identity_is_row_equivalence": False,
            "symmetric_hyperbolicity_disputed_here": False,
            "sourced_subsidiary_identity_disputed_here": False,
            "status_flags_promoted": [],
            "fail_closed": True,
        }
