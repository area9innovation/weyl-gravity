"""Principal-symbol obstruction for the smallest local relative saddle.

Let ``A_F=p_F A_equation`` be the evolution-row part of the exact equation
chain map.  It has order two and obeys

``A_F Eaux = L T_state``.

The smallest pairing-cyclic pair-4+5 ansatz can therefore be instantiated
without a new coefficient fit by

``S=A_F^sharp`` and ``R=A_F^sharp J_U``,

where ``J_U`` is the positive pointwise Weyl--Cotton symmetrizer used only as
a fibre identification.  Both maps have order two; their adjoints followed
by ``Eaux`` factor through the same rank-fifteen gauge-invariant Hessian.

The balanced Douglis weights which retain both reciprocal couplings and the
first-order curvature evolution are

``s_M=2, t_M=3, s_U=1, t_U=0``.

They make the old auxiliary diagonal lower order and give a temporal saddle
whose curvature Schur complement has rank at most fifteen on a 24-component
field row.  Hence the complete degree-zero principal matrix (including the
triangular forty-component equation-dual block) has rank at most 107 of 116.
The temporal leading coefficient of its characteristic determinant is zero,
and no positive symmetric-hyperbolic temporal form exists for this ansatz.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import sympy as sp

from .expanded_hessian import load_coefficient_cache
from .null_symbol_rank_obstruction import DEFAULT_CACHE


def _nested(mapping: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = mapping.get(key)
    if not isinstance(value, Mapping):
        raise AssertionError(f"missing mapping {key}")
    return value


@dataclass(frozen=True)
class RelativeSaddlePrincipalDiagnostic:
    """Exact orders, weights and temporal rank obstruction."""

    hessian_timelike_rank: int
    field_rank: int = 24
    curvature_rank: int = 26
    equation_dual_rank: int = 40

    @staticmethod
    def build() -> "RelativeSaddlePrincipalDiagnostic":
        covector, hessian, _ = load_coefficient_cache(DEFAULT_CACHE)
        scale = sp.Symbol("relative_saddle_timelike_scale")
        timelike = {
            covector[0]: scale,
            covector[1]: 0,
            covector[2]: 0,
            covector[3]: 0,
        }
        principal = hessian.applyfunc(
            lambda value: sp.expand(value.subs(timelike)).coeff(scale, 2)
        )
        result = RelativeSaddlePrincipalDiagnostic(
            hessian_timelike_rank=principal.rank()
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.hessian_timelike_rank != 15:
            raise AssertionError("timelike auxiliary Hessian rank drifted")
        if self.field_rank != 24 or self.curvature_rank != 26:
            raise AssertionError("relative saddle bundle ranks drifted")
        # The reduced 76 block has the 52 curvature temporal rows plus at
        # most rank(Eaux)=15 field Schur rows.  The equation-dual block is an
        # independently invertible triangular 40 block.
        if 2 * self.curvature_rank + self.hessian_timelike_rank != 67:
            raise AssertionError("reduced temporal rank bound drifted")
        if self.equation_dual_rank + 67 != 107:
            raise AssertionError("complete temporal rank bound drifted")
        if self.field_rank + 2 * self.curvature_rank + self.equation_dual_rank != 116:
            raise AssertionError("complete degree-zero rank drifted")

        # Solve the three equality conditions which retain B(order 2),
        # C(order 4), and D(order 1) in the Douglis principal matrix.
        s_m, t_m, s_u, t_u = sp.symbols("s_m t_m s_u t_u")
        solution = sp.linsolve(
            (
                s_m + t_u - 2,
                s_u + t_m - 4,
                s_u + t_u - 1,
            ),
            (s_m, t_m, s_u),
        )
        expected = {(2 - t_u, 3 + t_u, 1 - t_u)}
        if solution != expected:
            raise AssertionError("balanced Douglis weight family drifted")
        # For every member, the auxiliary diagonal has weighted order five,
        # while its actual differential order is only two.
        expression = sp.simplify((2 - t_u) + (3 + t_u))
        if expression != 5:
            raise AssertionError("auxiliary diagonal weighted order drifted")

    def certificate(
        self,
        *,
        equation_chain_certificate: Mapping[str, object],
        hyperbolic_certificate: Mapping[str, object],
        saddle_certificate: Mapping[str, object],
    ) -> dict[str, object]:
        self.verify()
        if equation_chain_certificate.get("schema") != (
            "pure-weyl-curvature-auxiliary-equation-chain-map-v1"
        ) or not equation_chain_certificate.get("first_chain_relation_exact"):
            raise AssertionError("equation chain map is unavailable")
        t_state = _nested(equation_chain_certificate, "T_state")
        a_equation = _nested(equation_chain_certificate, "A_equation")
        if not (
            t_state.get("maximum_order") == 3
            and a_equation.get("maximum_order") == 2
            and a_equation.get("shape") == [40, 24]
        ):
            raise AssertionError("T/A local-map order ledger drifted")
        if hyperbolic_certificate.get("schema") != (
            "pure-weyl-cotton-constraint-adjusted-hyperbolic-v1"
        ):
            raise AssertionError("wrong curvature hyperbolic certificate")
        if not hyperbolic_certificate.get("evolution_symmetrizer_positive"):
            raise AssertionError("positive curvature fibre form is unavailable")
        if saddle_certificate.get("schema") != (
            "pure-weyl-relative-saddle-witness-diagnostic-v1"
        ):
            raise AssertionError("wrong relative saddle certificate")
        if saddle_certificate.get("smallest_physical_saddle_candidate", {}).get(
            "relative_pairs"
        ) != [4, 5]:
            raise AssertionError("smallest saddle incidence drifted")

        reduced_rank_bound = 2 * self.curvature_rank + self.hessian_timelike_rank
        total_rank = self.field_rank + 2 * self.curvature_rank + self.equation_dual_rank
        complete_rank_bound = self.equation_dual_rank + reduced_rank_bound
        return {
            "schema": "pure-weyl-relative-saddle-principal-obstruction-v1",
            "instantiated_local_maps": {
                "A_F": "p_F A_equation: Ebar_aux[24] -> F_curv[26]",
                "A_F_order": 2,
                "T_state_order": 3,
                "J_U": "positive pointwise rank-26 Weyl-Cotton symmetrizer",
                "S": "A_F^sharp: U^sharp -> M_aux",
                "R": "A_F^sharp J_U: U -> M_aux",
                "R_order": 2,
                "S_order": 2,
                "formal_adjoints_from_same_oriented_pairings": True,
                "source_compatibility_relation": "A_F Eaux=L_26 T_state",
                "all_constraint_and_identity_rows_retained": True,
            },
            "differential_order_matrix": {
                "block_order": ["M_aux[24]", "U[26]+Usharp[26]"],
                "orders": [[2, 2], [4, 1]],
                "explanation": {
                    "A": "Eaux+K C, order 2",
                    "B": "[R,S], order 2",
                    "C": "[Ssharp Eaux,Rsharp Eaux]^T, order 4",
                    "D": "diag(L_26,L_26sharp), order 1",
                },
            },
            "balanced_Douglis_weights": {
                "row_weights": {"M": 2, "U": 1},
                "column_weights": {"M": 3, "U": 0},
                "shift_freedom": "t_U may be shifted with the displayed affine family",
                "principal_blocks": ["B_order2", "C_order4", "D_order1"],
                "auxiliary_A_weighted_order": 5,
                "auxiliary_A_actual_order": 2,
                "A_absent_from_balanced_principal_symbol": True,
                "no_weights_make_A_B_C_D_all_principal": True,
            },
            "timelike_principal_test": {
                "covector": "dt",
                "Eaux_principal_rank": self.hessian_timelike_rank,
                "curvature_temporal_blocks_invertible_rank": 52,
                "field_Schur_rank_upper_bound": self.hessian_timelike_rank,
                "reduced_76_rank_upper_bound": reduced_rank_bound,
                "equation_dual_triangular_rank": self.equation_dual_rank,
                "complete_degree_zero_dimension": total_rank,
                "complete_degree_zero_rank_upper_bound": complete_rank_bound,
                "timelike_rank_defect_lower_bound": total_rank - complete_rank_bound,
                "invertible": False,
            },
            "characteristic_and_symmetrizer": {
                "Douglis_characteristic_temporal_leading_coefficient": "zero",
                "reason": (
                    "at zeta=dt the curvature blocks are invertible, while "
                    "the field Schur block factors through rank(Eaux)=15<24"
                ),
                "causal_characteristic_polynomial_exists": False,
                "positive_temporal_symmetrizer_exists": False,
                "symmetric_hyperbolicity_obstruction": (
                    "the balanced temporal principal matrix has rank defect at least nine"
                ),
            },
            "scope": (
                "exact no-go for the smallest pair-4+5 ansatz with R,S induced "
                "by p_F A_equation and J_U; not a no-go for larger relative "
                "witnesses or an additional local first-order prolongation"
            ),
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
