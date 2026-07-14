"""Differential-ideal audit for the Weyl--Cotton hyperbolic reduction.

The covariant first-order system has 34 rows on the 26 natural variables
``(E,B,A,C,x,y)``.  The symmetric-hyperbolic reduction has 26 evolution
rows and uses the fourteen constraint components

``q,r,a,c,s,t``.

These presentations are not equal as pointwise first-jet row modules: the
hyperbolic presentation has six additional ``a,c`` rows.  They are equal as
differential ideals.  Indeed, if ``U_x,U_y`` denote the exact vector Bach
rows and ``R_x,R_y`` the adjusted evolution rows, then

``R_x=U_x-2a`` and ``R_y=U_y-2c``.

Conversely the exact sourced subsidiary identities give

``2a=U_x-div f_E-(q_t+(1/2)curl r)`` and its dual.  Thus the six apparent
extra rows are first differential consequences of the exact system.

The module also audits the proposed 32-state graph prolongation.  Its
fourteen advertised constraints ``q,r,s,t,d_a,d_c`` are not an invariant
Cauchy constraint surface: their time derivatives contain the independent
promoted variables ``a,c``.  Six secondary algebraic constraints
``a=c=0`` are required.  No status flag is promoted here.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from .weyl_3plus1 import WeylCottonBachFirstOrder
from .weyl_cotton_hyperbolic import ConstraintAdjustedWeylCottonEvolution
from .weyl_cotton_promoted_constraints import (
    PromotedCottonConstraintEvolution,
)
from .weyl_cotton_row_audit import (
    _adjusted_tables,
    _constraint_tables,
    _exact_tables,
    _flatten_tables,
    _old_from_natural_state,
)


def _nonzero_count(matrix: sp.Matrix) -> int:
    return sum(int(value != 0) for value in matrix)


def _extend_columns(matrix: sp.Matrix, count: int) -> sp.Matrix:
    return matrix.row_join(sp.zeros(matrix.rows, count))


@dataclass(frozen=True)
class WeylCottonDifferentialIdealAudit:
    """Exact ranks and formal-integrability defects of both presentations."""

    exact_row_rank: int
    adjusted_plus_constraints_rank: int
    exact_union_adjusted_rank: int
    exact_containment_defect: int
    pointwise_reverse_defect_rank: int
    vector_relation_defect: int
    sourced_subsidiary_commuting_defect: int
    sourced_subsidiary_corrected_defect: int
    graph_prolongation_rank: int
    promoted_equations_rank: int
    graph_union_promoted_rank: int
    promoted_extra_rank: int
    advertised_constraint_rank: int
    advertised_propagation_defect_rank: int
    augmented_constraint_rank: int

    @staticmethod
    def build(*, verify: bool = True) -> "WeylCottonDifferentialIdealAudit":
        first_order = WeylCottonBachFirstOrder.build()
        adjusted = ConstraintAdjustedWeylCottonEvolution.build()
        transform = _old_from_natural_state()

        exact_tables = _exact_tables(first_order, transform)
        adjusted_tables = _adjusted_tables(adjusted)
        constraint_tables = _constraint_tables(adjusted)
        exact = _flatten_tables(exact_tables)
        adjusted_rows = _flatten_tables(adjusted_tables)
        constraints = _flatten_tables(constraint_tables)
        adjusted_with_constraints = adjusted_rows.col_join(constraints)

        # The 40-row hyperbolic presentation contains every covariant row.
        # Its full row rank gives a canonical rational right inverse.
        right_inverse = (
            adjusted_with_constraints.T
            * (adjusted_with_constraints * adjusted_with_constraints.T).inv()
        )
        exact_map = exact * right_inverse
        exact_containment = exact_map * adjusted_with_constraints - exact

        # The exact square reduction uses the temporal pivot rows.  Its last
        # six rows are U_x,U_y; compare them with R_x,R_y and a,c.
        pivots = tuple(first_order.temporal_matrix.T.rref()[1])
        temporal = exact_tables[0][list(pivots), :]
        unadjusted_tables = tuple(
            temporal.inv() * table[list(pivots), :] for table in exact_tables
        )
        ac_multiplier = sp.zeros(6, 14)
        ac_multiplier[:3, 6:9] = -2 * sp.eye(3)
        ac_multiplier[3:, 9:12] = -2 * sp.eye(3)
        vector_relation_defect = 0
        for candidate, unadjusted, constraint in zip(
            adjusted_tables, unadjusted_tables, constraint_tables, strict=True
        ):
            vector_relation_defect += _nonzero_count(
                candidate[20:26, :]
                - unadjusted[20:26, :]
                - ac_multiplier * constraint
            )

        # This is the exact natural-operator sourced identity.  Commuting
        # symbols miss the unit-S3 curvature contribution, which is stored
        # independently and must cancel it exactly.
        commuting_defect = adjusted.commuting_symbol_defect
        corrected_defect = (
            commuting_defect + adjusted.sphere_curvature_correction
        )

        # Audit the 32-state graph prolongation.  The graph system consists
        # of the exact 34 rows, extended trivially in a,c, and the six local
        # definitions d_a=d_c=0.  The promoted system consists of 32
        # evolution rows plus its advertised fourteen constraints.
        promoted = PromotedCottonConstraintEvolution.build()
        promoted_constraint_tables = (
            sp.zeros(14, 32),
            *promoted.constraint_spatial_coefficients,
            promoted.constraint_zeroth_coefficient,
        )
        graph_tables = tuple(
            _extend_columns(exact_table, 6).col_join(
                promoted_constraint_table[8:14, :]
            )
            for exact_table, promoted_constraint_table in zip(
                exact_tables, promoted_constraint_tables, strict=True
            )
        )
        promoted_tables = tuple(
            evolution.col_join(constraint)
            for evolution, constraint in zip(
                (
                    sp.eye(32),
                    *promoted.spatial_coefficients,
                    promoted.zeroth_coefficient,
                ),
                promoted_constraint_tables,
                strict=True,
            )
        )
        graph_rows = _flatten_tables(graph_tables)
        promoted_rows = _flatten_tables(promoted_tables)

        # A representative spatial covector exposes the Cauchy propagation
        # defect.  The first six differentiated constraints are q_t,r_t.
        # Their rank-six failure is exactly removed by adjoining a=c=0.
        evolution_symbol = (
            promoted.zeroth_coefficient + promoted.spatial_coefficients[0]
        )
        constraint_symbol = (
            promoted.constraint_zeroth_coefficient
            + promoted.constraint_spatial_coefficients[0]
        )
        differentiated_qr = (constraint_symbol * evolution_symbol)[:6, :]
        algebraic_ac = sp.zeros(6, 32)
        algebraic_ac[:, 26:32] = sp.eye(6)

        result = WeylCottonDifferentialIdealAudit(
            exact_row_rank=exact.rank(),
            adjusted_plus_constraints_rank=adjusted_with_constraints.rank(),
            exact_union_adjusted_rank=exact.col_join(
                adjusted_with_constraints
            ).rank(),
            exact_containment_defect=_nonzero_count(exact_containment),
            pointwise_reverse_defect_rank=(
                adjusted_with_constraints.rank() - exact.rank()
            ),
            vector_relation_defect=vector_relation_defect,
            sourced_subsidiary_commuting_defect=_nonzero_count(
                commuting_defect
            ),
            sourced_subsidiary_corrected_defect=_nonzero_count(
                corrected_defect
            ),
            graph_prolongation_rank=graph_rows.rank(),
            promoted_equations_rank=promoted_rows.rank(),
            graph_union_promoted_rank=graph_rows.col_join(promoted_rows).rank(),
            promoted_extra_rank=(promoted_rows.rank() - graph_rows.rank()),
            advertised_constraint_rank=constraint_symbol.rank(),
            advertised_propagation_defect_rank=(
                constraint_symbol.col_join(differentiated_qr).rank()
                - constraint_symbol.rank()
            ),
            augmented_constraint_rank=constraint_symbol.col_join(
                algebraic_ac
            ).rank(),
        )
        if verify:
            result.verify()
        return result

    def verify(self) -> None:
        if self.exact_row_rank != 34:
            raise AssertionError("exact covariant row rank drifted")
        if self.adjusted_plus_constraints_rank != 40:
            raise AssertionError("adjusted evolution plus constraints lost rank")
        if self.exact_union_adjusted_rank != 40:
            raise AssertionError("covariant rows are not contained in the reduction")
        if self.exact_containment_defect:
            raise AssertionError("exact row containment has a coefficient defect")
        if self.pointwise_reverse_defect_rank != 6:
            raise AssertionError("pointwise a,c row defect is not rank six")
        if self.vector_relation_defect:
            raise AssertionError("R=U-2(a,c) relation failed")
        if self.sourced_subsidiary_commuting_defect == 0:
            raise AssertionError("unit-S3 curvature correction was silently omitted")
        if self.sourced_subsidiary_corrected_defect:
            raise AssertionError("curved sourced subsidiary identity failed")
        if self.graph_prolongation_rank != 40:
            raise AssertionError("exact graph prolongation rank drifted")
        if self.promoted_equations_rank != 46:
            raise AssertionError("promoted equation rank drifted")
        if self.graph_union_promoted_rank != 46 or self.promoted_extra_rank != 6:
            raise AssertionError("promoted a,c evolution defect is not rank six")
        if self.advertised_constraint_rank != 14:
            raise AssertionError("advertised promoted constraint rank drifted")
        if self.advertised_propagation_defect_rank != 6:
            raise AssertionError("missing secondary a,c propagation defect drifted")
        if self.augmented_constraint_rank != 20:
            raise AssertionError("secondary a=c=0 constraints are not independent")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-cotton-differential-ideal-audit-v1",
            "exact_covariant_row_rank": self.exact_row_rank,
            "adjusted_evolution_plus_14_constraints_rank": (
                self.adjusted_plus_constraints_rank
            ),
            "exact_union_adjusted_rank": self.exact_union_adjusted_rank,
            "exact_rows_contained_pointwise": self.exact_containment_defect == 0,
            "pointwise_reverse_containment": False,
            "pointwise_reverse_defect_rank": self.pointwise_reverse_defect_rank,
            "exact_vector_relations": [
                "R_x=U_x-2a",
                "R_y=U_y-2c",
            ],
            "vector_relation_defect": self.vector_relation_defect,
            "differential_generation_of_missing_rows": [
                "2a=U_x-div(f_E)-q_t-(1/2)curl r",
                "2c=U_y-div(f_B)-r_t+(1/2)curl q",
            ],
            "sourced_subsidiary_identity_curvature_corrected": (
                self.sourced_subsidiary_corrected_defect == 0
            ),
            "unit_S3_curvature_correction_required": (
                self.sourced_subsidiary_commuting_defect != 0
            ),
            "covariant_and_adjusted_differential_ideals_equal": True,
            "covariant_and_adjusted_smooth_solution_spaces_equal": True,
            "source_compatibility_map_available": True,
            "source_compatibility_rows": [
                "f_x-div f_E",
                "f_y-div f_B",
                "div f_A+(1/2)curl f_y",
                "div f_C-(1/2)curl f_x",
                "div f_x",
                "div f_y",
            ],
            "promoted_32_state_audit": {
                "exact_graph_first_jet_rank": self.graph_prolongation_rank,
                "promoted_equation_first_jet_rank": self.promoted_equations_rank,
                "union_rank": self.graph_union_promoted_rank,
                "additional_formal_integrability_rows": self.promoted_extra_rank,
                "advertised_constraint_rank": self.advertised_constraint_rank,
                "advertised_constraints_propagate": False,
                "propagation_defect_rank": (
                    self.advertised_propagation_defect_rank
                ),
                "missing_secondary_constraints": "a[3]=0,c[3]=0",
                "constraint_rank_after_secondary_completion": (
                    self.augmented_constraint_rank
                ),
                "exact_constraint_derivatives": [
                    "q_t+(1/2)curl r+2a=f_x-div f_E",
                    "r_t-(1/2)curl q+2c=f_y-div f_B",
                ],
                "global_spacetime_solution_equivalence_with_all_rows": True,
                "rank_14_Cauchy_constraint_equivalence": False,
            },
            "interpretation": (
                "The 26-state adjusted system closes the covariant differential "
                "ideal when all q,r,a,c,s,t rows are retained.  The 32-state "
                "graph promotion is not a closed rank-14 Cauchy formulation; "
                "its secondary a=c=0 constraints must also be imposed."
            ),
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
