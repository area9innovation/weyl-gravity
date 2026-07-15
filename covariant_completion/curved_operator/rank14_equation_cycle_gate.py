"""Green-witness companion-cycle diagnostic for the rank-fourteen bridge.

The typed curvature equation complex is

``U --(L,K_state)--> F+C --(-R_src,S)--> I``

and the auxiliary attachment has equation component

``A=(A_F,A_C):Ebar_aux -> F+C``.

The exact chain relation is ``(-R_src,S)A=B C_aux``.  Therefore, if
``J_id`` presents the principal kernel of the Green-witness companion,
the meaningful source-cycle test is

``(R_src A_F-S A_C) J_id=0``.

The occasionally suggested shorthand ``K_state A_F=A_C`` is not literal:
the two sides have different target types and differential orders.  Even
after the canonical coordinate identification ``K_state=R_src``, the
right-hand term required by the chain complex is ``S A_C``.

This module predates the full BV-cone audit.  Its ``C`` is the witness
companion, not the BV identity row ``K(-zeta)^T J``.  It therefore certifies
only the displayed witness-cycle diagnostic.  It does not certify BV cone
cohomology, a Green inverse, or any curved lower-order PBW lift.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from covariant_completion.curved_retract.curvature_auxiliary_chain_map import (
    _symmetric_coordinate_inclusion,
    _target_extraction,
)
from .conventions import CurvedBVConventions, _ordinary_system
from .rank14_weyl_cotton_incoming_map_ledger import _bach_to_curvature
from .weyl_cotton_hyperbolic import ConstraintAdjustedWeylCottonEvolution


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _polynomial_kernel_from_fixed_minor(
    matrix: sp.Matrix,
    pivot_columns: tuple[int, ...],
) -> tuple[sp.Matrix, sp.Expr]:
    """Return a denominator-cleared fraction-field kernel presentation.

    The temporal coefficient has a constant nonzero 9-by-9 minor.  Hence the
    same columns give a generically invertible polynomial minor of the full
    symbol.  ``inv_den`` computes its fraction-free inverse ``N/d`` and the
    standard graph presentation ``(-N C_free, d I)`` avoids SymPy's expensive
    symbolic nullspace routine entirely.
    """

    free_columns = tuple(
        column for column in range(matrix.cols) if column not in pivot_columns
    )
    pivot = matrix[:, list(pivot_columns)]
    free = matrix[:, list(free_columns)]
    numerator_domain, denominator_domain = DomainMatrix.from_Matrix(pivot).inv_den()
    numerator = numerator_domain.to_Matrix()
    denominator = numerator_domain.domain.to_sympy(denominator_domain)
    pivot_rows = (-numerator * free).applyfunc(sp.expand)
    free_rows = denominator * sp.eye(len(free_columns))
    kernel = sp.zeros(matrix.cols, len(free_columns))
    for row, column in enumerate(pivot_columns):
        kernel[column, :] = pivot_rows[row, :]
    for row, column in enumerate(free_columns):
        kernel[column, :] = free_rows[row, :]
    return kernel, sp.expand(denominator)


@dataclass(frozen=True)
class Rank14EquationCycleGate:
    covector: tuple[sp.Symbol, ...]
    auxiliary_identity_principal: sp.Matrix
    identity_kernel_generators: sp.Matrix
    identity_pivot_columns: tuple[int, ...]
    identity_pivot_denominator: sp.Expr
    equation_map_principal: sp.Matrix
    equation_source_principal: sp.Matrix
    equation_constraint_principal: sp.Matrix
    source_compatibility_principal: sp.Matrix
    subsidiary_principal: sp.Matrix
    typed_cycle_defect: sp.Matrix
    cone_cycle_generators: sp.Matrix
    literal_degree_three_term: sp.Matrix

    @staticmethod
    def build(*, workers: int = 1) -> "Rank14EquationCycleGate":
        # ``workers`` is retained for a stable verifier CLI.  The principal
        # map is reconstructed directly from the authoritative tangent-shift
        # and Bach row maps, so no sampled or exhaustive jet rebuild occurs.
        if workers < 1:
            raise ValueError("workers must be positive")
        covector = tuple(sp.symbols("rank14_cycle_z0:4", real=True))
        conventions = CurvedBVConventions.build()
        evolution = ConstraintAdjustedWeylCottonEvolution.build()

        c_principal = sum(
            (
                covector[axis]
                * conventions.gauge_companion.derivative_coefficients[axis]
                for axis in range(4)
            ),
            sp.zeros(9, 24),
        ).applyfunc(sp.expand)
        temporal = conventions.gauge_companion.derivative_coefficients[0]
        pivot_columns = tuple(int(column) for column in temporal.rref()[1])
        kernel, pivot_denominator = _polynomial_kernel_from_fixed_minor(
            c_principal, pivot_columns
        )

        # This is exactly the order-two part of A_equation=A_raw J_aux in
        # curvature_auxiliary_chain_map.py.  A_raw has only the E_f input at
        # this order, namely H_Bach p_TF J_tensor^-1 S_h^sharp.
        source = _ordinary_system()
        source_to_cycle = dict(zip(source.covector, covector, strict=True))
        mass = source.gauge_invariant_flat_hessian[10:20, 10:20]
        shift_symbol = (
            -mass.inv() * source.gauge_invariant_flat_hessian[10:20, :10]
        ).subs(source_to_cycle)
        raw = sp.zeros(40, 24)
        raw[:, 10:20] = (
            _bach_to_curvature()
            * _target_extraction()
            * _symmetric_coordinate_inclusion()
            * _ordinary_system().tensor_pairing.inv()
            * shift_symbol.T
        )
        a_principal = (raw * conventions.field_pairing).applyfunc(sp.expand)
        a_f = a_principal[:26, :]
        a_c = a_principal[26:, :]
        r_principal = sum(
            (
                covector[axis + 1]
                * evolution.source_compatibility_spatial_coefficients[axis]
                for axis in range(3)
            ),
            sp.zeros(14, 26),
        ).applyfunc(sp.expand)
        s_principal = (
            covector[0] * sp.eye(14)
            + sum(
                (
                    covector[axis + 1]
                    * evolution.constraint_spatial_coefficients[axis]
                    for axis in range(3)
                ),
                sp.zeros(14),
            )
        ).applyfunc(sp.expand)
        defect = (r_principal * a_f - s_principal * a_c) * kernel
        cone = sp.Matrix.vstack(a_f * kernel, a_c * kernel).applyfunc(sp.cancel)
        literal_degree_three = (r_principal * a_f * kernel).applyfunc(sp.cancel)

        result = Rank14EquationCycleGate(
            covector=covector,
            auxiliary_identity_principal=c_principal,
            identity_kernel_generators=kernel,
            identity_pivot_columns=pivot_columns,
            identity_pivot_denominator=pivot_denominator,
            equation_map_principal=a_principal,
            equation_source_principal=a_f,
            equation_constraint_principal=a_c,
            source_compatibility_principal=r_principal,
            subsidiary_principal=s_principal,
            typed_cycle_defect=defect.applyfunc(sp.cancel),
            cone_cycle_generators=cone,
            literal_degree_three_term=literal_degree_three,
        )
        result.verify()
        return result

    def _sample(self, covector: tuple[int, int, int, int]) -> dict[str, int]:
        substitution = dict(zip(self.covector, covector, strict=True))
        c = self.auxiliary_identity_principal.subs(substitution)
        kernel = sp.Matrix.hstack(*c.nullspace())
        a_f = self.equation_source_principal.subs(substitution)
        a_c = self.equation_constraint_principal.subs(substitution)
        r = self.source_compatibility_principal.subs(substitution)
        s = self.subsidiary_principal.subs(substitution)
        cone = sp.Matrix.vstack(a_f * kernel, a_c * kernel)
        return {
            "C_aux_rank": c.rank(),
            "J_id_columns": kernel.cols,
            "A_F_on_cycles_rank": (a_f * kernel).rank(),
            "A_C_on_cycles_rank": (a_c * kernel).rank(),
            "cone_cycle_rank": cone.rank(),
            "typed_cycle_defect_rank": ((r * a_f - s * a_c) * kernel).rank(),
            "literal_degree_three_rank": (r * a_f * kernel).rank(),
        }

    def verify(self) -> None:
        c = self.auxiliary_identity_principal
        kernel = self.identity_kernel_generators
        temporal_substitution = {
            self.covector[0]: 1,
            self.covector[1]: 0,
            self.covector[2]: 0,
            self.covector[3]: 0,
        }
        if c.shape != (9, 24) or c.subs(temporal_substitution).rank() != 9:
            raise AssertionError("auxiliary identity principal rank drifted")
        if kernel.shape != (24, 15):
            raise AssertionError("J_id presentation rank drifted")
        if self.identity_pivot_denominator == 0:
            raise AssertionError("J_id pivot minor vanished identically")
        generic_substitution = dict(
            zip(self.covector, (2, 1, 3, 5), strict=True)
        )
        if kernel.subs(generic_substitution).rank() != 15:
            raise AssertionError("J_id generic rank drifted")
        if any(sp.denom(value) != 1 for value in kernel if value != 0):
            raise AssertionError("J_id denominator clearing failed")
        if (c * kernel).applyfunc(sp.expand) != sp.zeros(9, 15):
            raise AssertionError("C_aux J_id is nonzero")
        if self.equation_map_principal.shape != (40, 24):
            raise AssertionError("wrong A principal shape")
        if self.equation_source_principal.shape != (26, 24):
            raise AssertionError("wrong A_F principal shape")
        if self.equation_constraint_principal.shape != (14, 24):
            raise AssertionError("wrong A_C principal shape")
        if self.source_compatibility_principal.shape != (14, 26):
            raise AssertionError("wrong R_src principal shape")
        if self.subsidiary_principal.shape != (14, 14):
            raise AssertionError("wrong S principal shape")
        if self.typed_cycle_defect != sp.zeros(14, 15):
            raise AssertionError("typed equation-cycle identity failed")
        if self.cone_cycle_generators.shape != (40, 15):
            raise AssertionError("wrong equation-cone generator shape")
        n_principal = (-self.source_compatibility_principal).row_join(
            self.subsidiary_principal
        )
        if (n_principal * self.cone_cycle_generators).applyfunc(sp.cancel) != sp.zeros(
            14, 15
        ):
            raise AssertionError("canonical equation cone is not N-closed")
        if self.literal_degree_three_term == sp.zeros(14, 15):
            raise AssertionError("literal K_state A_F shorthand lost its obstruction")

        # The four standard causal strata make the fraction-field statement
        # auditable without promoting a finite sample to the proof.
        for covector in (
            (2, 1, 0, 0),
            (0, 1, 0, 0),
            (1, 1, 0, 0),
            (1, 0, 0, 0),
        ):
            if self._sample(covector)["typed_cycle_defect_rank"] != 0:
                raise AssertionError(f"typed cycle defect at {covector}")

    def certificate(self) -> dict[str, object]:
        self.verify()
        generic_substitution = dict(
            zip(self.covector, (2, 1, 3, 5), strict=True)
        )
        samples = {
            str(covector): self._sample(covector)
            for covector in (
                (2, 1, 0, 0),
                (0, 1, 0, 0),
                (1, 1, 0, 0),
                (1, 0, 0, 0),
            )
        }
        return {
            "schema": "pure-weyl-rank14-equation-cycle-gate-v1",
            "scope": (
                "exact arbitrary-covector Green-witness companion-cycle "
                "diagnostic; full BV cone, curved PBW and Green work excluded"
            ),
            "auxiliary_identity_kernel": {
                "operator": "C_witness,1(zeta):Ebar_aux[24] -> G[9]",
                "generic_rank": self.auxiliary_identity_principal.subs(
                    generic_substitution
                ).rank(),
                "kernel_generic_rank": self.identity_kernel_generators.subs(
                    generic_substitution
                ).rank(),
                "J_id_shape": list(self.identity_kernel_generators.shape),
                "J_id_polynomial": True,
                "pivot_columns": list(self.identity_pivot_columns),
                "pivot_denominator": str(self.identity_pivot_denominator),
                "C_aux_J_id_defect": 0,
                "J_id_sha256": _digest(self.identity_kernel_generators),
            },
            "typed_translation": {
                "curvature_complex": (
                    "U --(L,K_state)--> F+C --(-R_src,S)--> I"
                ),
                "attachment": "A=(A_F,A_C):Ebar_aux -> F+C",
                "exact_chain_relation": "(-R_src,S)A=B C_aux",
                "cycle_relation": "(R_src A_F-S A_C)J_id=0",
                "cycle_relation_defect": 0,
                "K_state_and_R_src_tables_identified_only_after_typing": True,
            },
            "canonical_equation_cone": {
                "map": "J_id e |-> (A_F J_id e,A_C J_id e)",
                "shape": list(self.cone_cycle_generators.shape),
                "generic_rank": self.cone_cycle_generators.subs(
                    generic_substitution
                ).rank(),
                "Ncurv_cycle_defect": 0,
                "sha256": _digest(self.cone_cycle_generators),
            },
            "literal_shorthand_audit": {
                "proposal": "K_state A_F=A_C",
                "literally_well_typed": False,
                "left_target": "C_state[14] after identifying F coordinates with U",
                "right_target": "C_source[14]",
                "left_order": 3,
                "right_order": 2,
                "degree_three_term_on_J_id_is_zero": False,
                "degree_three_term_generic_rank": self.literal_degree_three_term.subs(
                    generic_substitution
                ).rank(),
                "correct_replacement": "R_src A_F=S A_C on ker C_aux",
                "becomes_shorthand_only_if_A_C_is_redefined": "A_C_tilde=S A_C",
            },
            "principal_ranks": {
                "sample_covector": [2, 1, 3, 5],
                "A_total": self.equation_map_principal.subs(generic_substitution).rank(),
                "A_F": self.equation_source_principal.subs(generic_substitution).rank(),
                "A_C": self.equation_constraint_principal.subs(generic_substitution).rank(),
                "R_src": self.source_compatibility_principal.subs(
                    generic_substitution
                ).rank(),
                "S": self.subsidiary_principal.subs(generic_substitution).rank(),
            },
            "causal_strata": samples,
            "decision": {
                "canonical_equation_cone_certified": True,
                "strict_F_only_lift_certified": False,
                "principal_H7_contraction_certified": False,
                "resume_curved_lower_order_PBW": False,
            },
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": {
                "rank14_witness_companion_cycle_gate_exact": True,
            },
            "status_flags_promoted": [],
            "fail_closed": True,
        }
