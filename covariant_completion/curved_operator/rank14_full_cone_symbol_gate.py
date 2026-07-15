"""Fail-closed gate for the full graded symbol cone of the curvature map.

The operator-level auxiliary-to-curvature map is exact, but a symbol cone
requires one *common* Douglis/Rees filtration for every component.  The
currently available principal tables were produced with different
filtrations.  In particular, ``gauge_companion`` is witness data and is not
the BV identity row

``C_aux(zeta)=K_aux(-zeta)^T J_aux``.

This module assembles the requested degree-by-degree cone using the true BV
``C_aux`` and the presently emitted principal tables.  The incoming gauge
row is retained:

``9 -> 24 -> (26+24) -> (40+9) -> 14``.

The two internal squares have nonzero ranks on every causal stratum.  Hence
these tables do not define a graded symbol complex and no cohomology rank may
honestly be assigned yet.  This is a filtration mismatch, not a failure of
the exact differential-operator cone, whose chain squares are separately
certified.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from .conventions import CurvedBVConventions, _ordinary_system
from .rank14_equation_cycle_gate import Rank14EquationCycleGate
from .rank14_weyl_cotton_incoming_map_ledger import _auxiliary_identity_map
from .rank14_weyl_cotton_symbol_audit import Rank14WeylCottonSymbolAudit
from .weyl_cotton_hyperbolic import ConstraintAdjustedWeylCottonEvolution


OBJECT_WEIGHTS = {
    "G": (-6, -6, -6, -6, -4, -4, -4, -4, -5),
    "M": (-5,) * 10 + (-3,) * 10 + (-4,) * 4,
    "E": (-3,) * 10 + (-1,) * 10 + (-2,) * 4,
    "I": (2, 2, 2, 2, 0, 0, 0, 0, 1),
    "U": (-3,) * 10 + (-2,) * 16,
    "Q": (-2,) * 10 + (-1,) * 16 + (-2,) * 6 + (-1,) * 8,
    "J": (-1,) * 6 + (0,) * 8,
}
MAP_DEGREES = {"K": 0, "E": 0, "C": -2, "T": 0, "A": 0, "B": 0,
               "Ewc": 0, "N": 0}


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class Rank14FullConeSymbolGate:
    covector: tuple[sp.Symbol, ...]
    gauge: sp.Matrix
    auxiliary_equation: sp.Matrix
    auxiliary_identity: sp.Matrix
    curved_auxiliary_identity: sp.Matrix
    curvature_state_map: sp.Matrix
    curvature_equation: sp.Matrix
    curvature_identity: sp.Matrix
    equation_attachment: sp.Matrix
    identity_attachment: sp.Matrix
    cone_differentials: tuple[sp.Matrix, ...]

    @staticmethod
    def build() -> "Rank14FullConeSymbolGate":
        source = _ordinary_system()
        conventions = CurvedBVConventions.build()
        curvature = ConstraintAdjustedWeylCottonEvolution.build()
        state_audit = Rank14WeylCottonSymbolAudit.build()
        equation_gate = Rank14EquationCycleGate.build()
        zeta = equation_gate.covector

        source_substitution = dict(zip(source.covector, zeta, strict=True))
        gauge = source.gauge_map.subs(source_substitution).applyfunc(sp.expand)
        hessian = source.gauge_invariant_flat_hessian.subs(source_substitution)
        e_aux = (conventions.field_pairing.inv() * hessian).applyfunc(sp.expand)
        negative = {source.covector[axis]: -zeta[axis] for axis in range(4)}
        c_aux = (
            source.gauge_map.subs(negative).T * conventions.field_pairing
        ).applyfunc(sp.expand)
        curved_k_at_negative = (
            conventions.gauge_generator.zeroth_coefficient
            - sum(
                (
                    zeta[axis]
                    * conventions.gauge_generator.derivative_coefficients[axis]
                    for axis in range(4)
                ),
                sp.zeros(24, 9),
            )
        )
        curved_c_aux = (
            curved_k_at_negative.T * conventions.field_pairing
        ).applyfunc(sp.expand)

        state_substitution = {
            state_audit.tau: zeta[0],
            **dict(zip(state_audit.spatial_covector, zeta[1:], strict=True)),
        }
        state_map = state_audit.state_symbol_fields.subs(
            state_substitution
        ).row_join(sp.zeros(26, 4))

        l_symbol = zeta[0] * sp.eye(26) + sum(
            (
                zeta[axis + 1]
                * curvature.evolution_spatial_coefficients[axis]
                for axis in range(3)
            ),
            sp.zeros(26),
        )
        k_symbol = sum(
            (
                zeta[axis + 1]
                * curvature.source_compatibility_spatial_coefficients[axis]
                for axis in range(3)
            ),
            sp.zeros(14, 26),
        )
        s_symbol = zeta[0] * sp.eye(14) + sum(
            (
                zeta[axis + 1]
                * curvature.constraint_spatial_coefficients[axis]
                for axis in range(3)
            ),
            sp.zeros(14),
        )
        e_curv = l_symbol.col_join(k_symbol)
        n_curv = (-k_symbol).row_join(s_symbol)
        attachment = equation_gate.equation_map_principal
        b_identity = _auxiliary_identity_map()

        # Cone(Phi), signs fixed by Ecurv T=A Eaux and N A=B Caux.
        d_minus_two = gauge
        d_minus_one = state_map.col_join(-e_aux)
        d_zero = e_curv.row_join(attachment).col_join(
            sp.zeros(9, 26).row_join(-c_aux)
        )
        d_one = n_curv.row_join(b_identity)

        result = Rank14FullConeSymbolGate(
            covector=zeta,
            gauge=gauge,
            auxiliary_equation=e_aux,
            auxiliary_identity=c_aux,
            curved_auxiliary_identity=curved_c_aux,
            curvature_state_map=state_map,
            curvature_equation=e_curv,
            curvature_identity=n_curv,
            equation_attachment=attachment,
            identity_attachment=b_identity,
            cone_differentials=(d_minus_two, d_minus_one, d_zero, d_one),
        )
        result.verify()
        return result

    def _sample(self, value: tuple[int, int, int, int]) -> dict[str, object]:
        substitution = dict(zip(self.covector, value, strict=True))
        matrices = tuple(matrix.subs(substitution) for matrix in self.cone_differentials)
        square_ranks = tuple(
            (matrices[index + 1] * matrices[index]).rank()
            for index in range(3)
        )
        return {
            "differential_ranks": [matrix.rank() for matrix in matrices],
            "square_ranks": list(square_ranks),
            "is_complex": square_ranks == (0, 0, 0),
            "cohomology_defined": square_ranks == (0, 0, 0),
        }

    def verify(self) -> None:
        d_m2, d_m1, d_0, d_1 = self.cone_differentials
        if [matrix.shape for matrix in self.cone_differentials] != [
            (24, 9),
            (50, 24),
            (49, 50),
            (14, 49),
        ]:
            raise AssertionError("full cone degree ledger drifted")
        if (self.auxiliary_identity * self.auxiliary_equation).applyfunc(
            sp.expand
        ) != sp.zeros(9, 24):
            raise AssertionError("ordinary-layer Caux Eaux identity failed")
        if (self.auxiliary_equation * self.gauge).applyfunc(
            sp.expand
        ) != sp.zeros(24, 9):
            raise AssertionError("Eaux K identity failed")
        if (self.curvature_state_map * self.gauge).applyfunc(
            sp.expand
        ) != sp.zeros(26, 9):
            raise AssertionError("T K identity failed")
        if (self.curvature_identity * self.curvature_equation).applyfunc(
            sp.expand
        ) != sp.zeros(14, 26):
            raise AssertionError("Ncurv Ecurv principal identity failed")
        if (d_m1 * d_m2).applyfunc(sp.expand) != sp.zeros(50, 9):
            raise AssertionError("incoming gauge square failed")

        # One common integer Douglis assignment exists for every monomial
        # currently retained.  The failure is therefore missing equal-weight
        # coefficient blocks, not infeasibility of the weight equations.
        weighted_maps = (
            ("K", "G", "M", self.gauge),
            ("E", "M", "E", self.auxiliary_equation),
            ("C", "E", "I", self.auxiliary_identity),
            ("T", "M", "U", self.curvature_state_map),
            ("A", "E", "Q", self.equation_attachment),
            ("B", "I", "J", self.identity_attachment),
            ("Ewc", "U", "Q", self.curvature_equation),
            ("N", "Q", "J", self.curvature_identity),
        )
        for name, source, target, matrix in weighted_maps:
            for row in range(matrix.rows):
                for column in range(matrix.cols):
                    value = matrix[row, column]
                    if value == 0:
                        continue
                    for monomial, coefficient in sp.Poly(
                        sp.expand(value), *self.covector
                    ).terms():
                        if coefficient == 0:
                            continue
                        weighted_degree = (
                            sum(monomial)
                            + OBJECT_WEIGHTS[source][column]
                            - OBJECT_WEIGHTS[target][row]
                        )
                        if weighted_degree != MAP_DEGREES[name]:
                            raise AssertionError(
                                f"Douglis weight defect in {name}[{row},{column}]"
                            )

        # The inconsistent principal extractions must not be silently treated
        # as a complex.  Exact ranks are guarded on every requested stratum.
        expected = {
            (2, 1, 3, 5): [0, 11, 4],
            (2, 1, 0, 0): [0, 11, 4],
            (0, 1, 0, 0): [0, 11, 4],
            (1, 0, 0, 0): [0, 11, 4],
            (1, 1, 0, 0): [0, 7, 4],
        }
        for covector, ranks in expected.items():
            if self._sample(covector)["square_ranks"] != ranks:
                raise AssertionError(f"cone square ranks drifted at {covector}")
            substitution = dict(zip(self.covector, covector, strict=True))
            if (
                self.curved_auxiliary_identity - self.auxiliary_identity
            ).subs(substitution).rank() != 4:
                raise AssertionError(f"curved/ordinary Caux rank drifted at {covector}")

    def certificate(self) -> dict[str, object]:
        self.verify()
        samples = {
            "generic_(2,1,3,5)": self._sample((2, 1, 3, 5)),
            "timelike_(2,1,0,0)": self._sample((2, 1, 0, 0)),
            "spacelike_(0,1,0,0)": self._sample((0, 1, 0, 0)),
            "temporal_(1,0,0,0)": self._sample((1, 0, 0, 0)),
            "null_(1,1,0,0)": self._sample((1, 1, 0, 0)),
        }
        return {
            "schema": "pure-weyl-rank14-full-cone-symbol-gate-v1",
            "scope": (
                "full degree ledger and exact failure of the currently mixed "
                "principal extractions; no symbol cohomology is claimed"
            ),
            "degree_ledger": {
                "degrees": [-2, -1, 0, 1, 2],
                "ranks": [9, 24, 50, 49, 14],
                "differential_shapes": [[24, 9], [50, 24], [49, 50], [14, 49]],
                "incoming_gauge_row_included": True,
            },
            "ordinary_auxiliary_BV_layer": {
                "Eaux": "J_aux^-1 H_aux",
                "Caux": "K_ordinary(-zeta)^T J_aux",
                "Caux_Eaux_defect": 0,
                "Eaux_K_defect": 0,
                "Caux_sha256": _digest(self.auxiliary_identity),
                "gauge_companion_is_Caux": False,
                "gauge_companion_role": "Green-witness companion",
                "exact_curved_K_used": False,
                "scope": "ordinary/Douglis representative before common Rees lift",
            },
            "curved_identity_comparison": {
                "Caux_curved": "K_curved(-zeta)^T J_aux",
                "Caux_curved_sha256": _digest(self.curved_auxiliary_identity),
                "curved_minus_ordinary_rank_on_all_tested_strata": 4,
                "interpretation": (
                    "the background-induced f<-xi derivative block occupies a "
                    "different layer until the common Rees filtration is fixed"
                ),
            },
            "valid_subcomplex_squares": {
                "T_K_defect": 0,
                "Ncurv_Ecurv_defect": 0,
                "incoming_cone_square_defect": 0,
            },
            "causal_strata": samples,
            "full_cone_symbol_is_a_complex": False,
            "full_cone_symbol_cohomology_computed": False,
            "reason": (
                "T, Eaux, A, B, Ecurv and Ncurv were extracted with incompatible "
                "ordinary/Douglis leading layers; the exact curved K also differs "
                "from the ordinary K layer, so the two internal cone "
                "squares are nonzero"
            ),
            "required_repair": {
                "object": "one componentwise Douglis/Rees filtration",
                "integer_weight_constraints_feasible": True,
                "representative_object_weights": {
                    key: list(value) for key, value in OBJECT_WEIGHTS.items()
                },
                "representative_map_degrees": MAP_DEGREES,
                "all_currently_retained_monomials_have_required_weight": True,
                "must_emit": [
                    "weights for every auxiliary and Weyl--Cotton component",
                    "associated-graded T,Eaux,Caux,A,B,Ecurv,Ncurv",
                    "three exact associated-graded chain squares",
                ],
                "only_then": "compute degree-by-degree cone cohomology",
                "refined_boundary": (
                    "weights exist; the missing object is the complete associated-"
                    "graded coefficient extraction, especially lower A and weighted "
                    "zeroth Weyl--Cotton blocks"
                ),
            },
            "certificate_corrections": {
                "rank14_equation_cycle_gate": (
                    "uses gauge_companion and is a witness-cycle diagnostic, "
                    "not the full BV ker(Caux) gate"
                ),
                "rank14_equation_sdr_boundary": (
                    "its canonical operator cone remains exact, but any validation "
                    "through the companion-based J_id must be demoted"
                ),
            },
            "decision": {
                "principal_full_cone_acyclic": False,
                "principal_full_cone_residual_rank": "undefined until d^2=0",
                "support_local_contraction_constructed": False,
                "prolonged_green_witness": False,
                "causal_green_homotopy": False,
            },
            "warranted_atomic_flags": {
                "rank14_ordinary_BV_Caux_layer_identified": True,
                "rank14_mixed_symbol_cone_rejected": True,
                "rank14_common_Douglis_filtration_required": True,
            },
            "status_flags_promoted": [],
            "fail_closed": True,
        }
