"""Principal-symbol audit of the rank-14 to Weyl--Cotton proposal.

The rank-fourteen field cokernel is the quotient of ``(h[10],f[10])`` by
the six spatial vector-gauge columns.  The natural curvature state map is

``T=(C1, div C1): (h,f) -> (E,B,A,C,x,y)``.

This module computes its induced map over the polynomial fraction field and
compares its image with the compatible-source kernel of the adjusted
twenty-six-state Weyl--Cotton system.  The comparison uses the correct
Douglis symbol: the algebraic ``x,y`` terms in the first six compatibility
rows have the same weighted order as the spatial divergences of ``E,B``.

The result is deliberately diagnostic.  The curvature map has rank five,
whereas the compatible-source kernel has generic rank twelve, but the raw
off-shell curvature image is not contained in that kernel: its generic
constraint defect has rank three.  Their generic common core has rank two.
This is the symbol shadow of ``K T=A_C E``: curvature states are constrained
only after imposing the field equation.  Moreover, in the existing
``P14`` coordinates the unprolonged factor is rational; multiplication by
``partial_t`` gives the certified local differential factor.  No curved
Green or BV flag follows from this principal-symbol calculation.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Mapping

import sympy as sp

from .expanded_relative_witness_rank14_curvature_presentation import (
    _coordinate_right_inverse,
    _quotient_map,
    _spatial_gauge,
    _weyl_eb_symbol,
)
from .weyl_3plus1 import WeylCottonThreePlusOne
from .weyl_cotton_hyperbolic import ConstraintAdjustedWeylCottonEvolution
from .weyl_cotton_row_audit import _old_from_natural_state


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _nonzero_count(matrix: sp.MatrixBase) -> int:
    return sum(int(value != 0) for value in matrix)


@dataclass(frozen=True)
class Rank14WeylCottonSymbolAudit:
    tau: sp.Symbol
    spatial_covector: tuple[sp.Symbol, sp.Symbol, sp.Symbol]
    quotient14: sp.Matrix
    gauge_incidence: sp.Matrix
    state_symbol_metric: sp.Matrix
    state_symbol_fields: sp.Matrix
    rational_descended_map: sp.Matrix
    local_prolonged_map: sp.Matrix
    source_principal_symbol: sp.Matrix
    compatibility_symbol: sp.Matrix

    @staticmethod
    def build() -> "Rank14WeylCottonSymbolAudit":
        tau = sp.Symbol("rank14_wc_tau", real=True)
        spatial = tuple(sp.symbols("rank14_wc_xi1:4", real=True))
        quotient7 = _quotient_map(tau, spatial)
        quotient = sp.diag(quotient7, quotient7)
        gauge = sp.diag(_spatial_gauge(tau, spatial), _spatial_gauge(tau, spatial))
        decomposition = WeylCottonThreePlusOne.build()
        evolution = ConstraintAdjustedWeylCottonEvolution.build()

        # Natural state order is (E,B,A,C,x,y).  The old curvature order is
        # (E,B,X_STF,X_vec,Y_STF,Y_vec).
        divergence = sp.zeros(16, 10)
        for covector, coefficient in zip(
            (tau, *spatial),
            decomposition.cotton_divergence_coefficients,
            strict=True,
        ):
            divergence += covector * coefficient
        natural_from_old = _old_from_natural_state().inv()
        state_metric = (
            natural_from_old
            * sp.eye(10).col_join(divergence)
            * _weyl_eb_symbol((tau, *spatial))
        ).applyfunc(sp.expand)
        state_fields = state_metric.row_join(sp.zeros(26, 10))

        quotient_right_inverse = sp.diag(
            _coordinate_right_inverse(quotient7),
            _coordinate_right_inverse(quotient7),
        )
        rational_descended = (state_fields * quotient_right_inverse).applyfunc(
            sp.cancel
        )
        local_prolonged = (tau * rational_descended).applyfunc(sp.cancel)

        # Weighted principal compatibility symbol.  The zeroth x/y block is
        # retained because x,y represent one more derivative than E,B.
        source_principal = sp.zeros(14, 26)
        for covector, coefficient in zip(
            spatial,
            evolution.source_compatibility_spatial_coefficients,
            strict=True,
        ):
            source_principal += covector * coefficient
        compatibility = (
            source_principal
            + evolution.source_compatibility_zeroth_coefficient
        )

        result = Rank14WeylCottonSymbolAudit(
            tau=tau,
            spatial_covector=spatial,
            quotient14=quotient,
            gauge_incidence=gauge,
            state_symbol_metric=state_metric,
            state_symbol_fields=state_fields,
            rational_descended_map=rational_descended,
            local_prolonged_map=local_prolonged,
            source_principal_symbol=source_principal,
            compatibility_symbol=compatibility,
        )
        result.verify()
        return result

    def _specialization(self, covector: tuple[int, int, int, int]) -> dict[str, int]:
        tau = self.tau
        spatial = self.spatial_covector
        substitution = {
            tau: covector[0],
            spatial[0]: covector[1],
            spatial[1]: covector[2],
            spatial[2]: covector[3],
        }
        curvature = self.state_symbol_fields.subs(substitution)
        compatibility = self.compatibility_symbol.subs(substitution)
        defect_rank = (compatibility * curvature).rank()
        intersection_rank = curvature.rank() - defect_rank
        return {
            "curvature_rank": curvature.rank(),
            "compatible_kernel_rank": 26 - compatibility.rank(),
            "compatibility_rank": compatibility.rank(),
            "curvature_compatible_intersection_rank": intersection_rank,
            "compatible_mod_common_core_rank": (
                26 - compatibility.rank() - intersection_rank
            ),
            "compatibility_curvature_defect_rank": defect_rank,
        }

    def verify(self) -> None:
        quotient = self.quotient14
        gauge = self.gauge_incidence
        tau = self.tau
        if self.state_symbol_fields.shape != (26, 20):
            raise AssertionError("wrong curvature state symbol shape")
        if (self.state_symbol_fields * gauge).applyfunc(sp.expand) != sp.zeros(26, 6):
            raise AssertionError("curvature state does not descend through gauge")
        generic = self._specialization((2, 1, 0, 0))
        if generic["curvature_rank"] != 5:
            raise AssertionError("generic curvature state rank drifted")
        if (
            self.rational_descended_map * quotient - self.state_symbol_fields
        ).applyfunc(sp.cancel) != sp.zeros(26, 20):
            raise AssertionError("fraction-field descended curvature factor failed")
        if any(
            sp.Poly(
                sp.denom(value),
                tau,
                *self.spatial_covector,
            ).total_degree()
            != 0
            for value in self.local_prolonged_map
            if value != 0
        ):
            raise AssertionError("temporally prolonged curvature factor is not local")
        if (
            self.local_prolonged_map * quotient - tau * self.state_symbol_fields
        ).applyfunc(sp.expand) != sp.zeros(26, 20):
            raise AssertionError("local prolonged curvature factor failed")
        if all(
            sp.Poly(
                sp.denom(value),
                tau,
                *self.spatial_covector,
            ).total_degree()
            == 0
            for value in self.rational_descended_map
            if value != 0
        ):
            raise AssertionError("unprolonged P14 factor unexpectedly became local")

        if self.compatibility_symbol.shape != (14, 26):
            raise AssertionError("wrong compatible-source symbol shape")
        if generic["compatibility_rank"] != 14:
            raise AssertionError("generic compatible-source row rank drifted")
        if generic["compatibility_curvature_defect_rank"] != 3:
            raise AssertionError("generic curvature/constraint defect rank drifted")
        source_generic = self.source_principal_symbol.subs(
            {
                self.spatial_covector[0]: 1,
                self.spatial_covector[1]: 0,
                self.spatial_covector[2]: 0,
            }
        ) * self.state_symbol_fields.subs(
            {
                self.tau: 2,
                self.spatial_covector[0]: 1,
                self.spatial_covector[1]: 0,
                self.spatial_covector[2]: 0,
            }
        )
        if source_generic.rank() != 3:
            raise AssertionError("derivative-only source defect rank drifted")
        if source_generic.rank() == 0 or generic[
            "compatibility_curvature_defect_rank"
        ] == 0:
            raise AssertionError("raw curvature map was falsely marked compatible")
        if generic["curvature_compatible_intersection_rank"] != 2:
            raise AssertionError("generic curvature-compatible intersection drifted")

        for covector in ((2, 1, 0, 0), (0, 1, 0, 0), (1, 1, 0, 0)):
            values = self._specialization(covector)
            expected_defect = 1 if covector == (1, 1, 0, 0) else 3
            expected_intersection = 5 - expected_defect
            if values != {
                "curvature_rank": 5,
                "compatible_kernel_rank": 12,
                "compatibility_rank": 14,
                "curvature_compatible_intersection_rank": expected_intersection,
                "compatible_mod_common_core_rank": 12 - expected_intersection,
                "compatibility_curvature_defect_rank": expected_defect,
            }:
                raise AssertionError(f"causal-stratum ranks drifted at {covector}: {values}")
        temporal = self._specialization((1, 0, 0, 0))
        if temporal != {
            "curvature_rank": 5,
            "compatible_kernel_rank": 20,
            "compatibility_rank": 6,
            "curvature_compatible_intersection_rank": 5,
            "compatible_mod_common_core_rank": 15,
            "compatibility_curvature_defect_rank": 0,
        }:
            raise AssertionError(f"temporal-axis ranks drifted: {temporal}")

    def certificate(
        self,
        *,
        helicity_certificate: Mapping[str, object],
        chain_certificate: Mapping[str, object],
        rank14_certificate: Mapping[str, object],
    ) -> dict[str, object]:
        self.verify()
        weyl = helicity_certificate.get("linearized_Weyl_symbol")
        if helicity_certificate.get("schema") != (
            "pure-weyl-curved-helicity-two-channel-v1"
        ) or not isinstance(weyl, Mapping):
            raise AssertionError("wrong null helicity certificate")
        if (
            weyl.get("full_symbol_rank"),
            weyl.get("rank_W_on_gauge_preimages"),
            weyl.get("target_quotient_dimension"),
            weyl.get("induced_quotient_matrix"),
        ) != (5, 3, 2, [["1/4", "0"], ["0", "1/4"]]):
            raise AssertionError("null B3 plus H2 split regressed")
        if chain_certificate.get("schema") != (
            "pure-weyl-curvature-auxiliary-equation-chain-map-v1"
        ) or not chain_certificate.get("first_chain_relation_exact"):
            raise AssertionError("exact curvature equation chain square unavailable")
        if rank14_certificate.get("schema") != (
            "pure-weyl-expanded-relative-rank14-curvature-presentation-v1"
        ):
            raise AssertionError("wrong authoritative rank14 presentation")
        quotient_input = rank14_certificate.get("projector_free_quotient")
        if not isinstance(quotient_input, Mapping) or (
            quotient_input.get("generic_rank"),
            quotient_input.get("P14_B_vector_defect"),
        ) != (14, 0):
            raise AssertionError("authoritative rank14 quotient regressed")
        samples = {
            "generic_timelike_(2,1,0,0)": self._specialization((2, 1, 0, 0)),
            "spacelike_(0,1,0,0)": self._specialization((0, 1, 0, 0)),
            "null_(1,1,0,0)": self._specialization((1, 1, 0, 0)),
            "temporal_axis_(1,0,0,0)": self._specialization((1, 0, 0, 0)),
        }
        generic = samples["generic_timelike_(2,1,0,0)"]
        return {
            "schema": "pure-weyl-rank14-weyl-cotton-symbol-audit-v1",
            "scope": (
                "arbitrary-covector Douglis principal symbol; no curved "
                "lower-order Green or BV identity is claimed"
            ),
            "rank14_domain": {
                "presentation": "coker(K_vector) on (h[10],f[10])",
                "generic_rank": 14,
                "curvature_operator": "(C1,div C1) on h; zero on f",
                "gauge_annihilation_defect": 0,
            },
            "descended_curvature_map": {
                "generic_rank": generic["curvature_rank"],
                "generic_kernel_rank_on_F14": 14 - generic["curvature_rank"],
                "fraction_field_factor": "T_state=R_rat P14",
                "fraction_field_factor_defect": 0,
                "unprolonged_factor_is_polynomial": False,
                "local_factor": "partial_t T_state=R_local P14",
                "local_factor_defect": 0,
                "local_factor_maximum_order": 3,
                "matrix_sha256": _digest(self.local_prolonged_map),
            },
            "compatible_source_symbol": {
                "operator": "K_src^(D)=K_src,0+xi_i K_src,i",
                "why_zeroth_block_is_principal": (
                    "x,y have one higher Douglis state weight than E,B"
                ),
                "generic_row_rank": generic["compatibility_rank"],
                "generic_kernel_rank": generic["compatible_kernel_rank"],
                "polynomial_syzygy_basis_emitted": False,
                "reason": (
                    "the strict containment required for the proposed V7 is "
                    "false; an expensive quotient-basis computation would not "
                    "define the requested deformation retract"
                ),
                "derivative_only_symbol_rank": 14,
                "derivative_only_Ksrc_R_generic_defect_rank": 3,
                "weighted_Ksrc_R_generic_defect_rank": generic[
                    "compatibility_curvature_defect_rank"
                ],
            },
            "image_kernel_comparison": {
                "K_weighted_R_generic_defect_rank": 3,
                "image_is_contained_in_compatible_kernel": False,
                "image_equals_compatible_kernel": False,
                "generic_image_rank": generic["curvature_rank"],
                "generic_compatible_rank": generic["compatible_kernel_rank"],
                "generic_common_core_rank": generic[
                    "curvature_compatible_intersection_rank"
                ],
                "generic_compatible_mod_common_core_rank": 10,
                "interpretation": (
                    "the natural curvature state has a rank-two generic common "
                    "core with the rank-twelve compatible module; its other "
                    "three directions source secondary a/c/s constraints"
                ),
                "explicit_polynomial_K12_basis": "not emitted after failed containment gate",
                "V10_basis_not_emitted": (
                    "the proposed V7 route is invalid off shell; no unnecessary "
                    "fraction-field projector is introduced"
                ),
            },
            "dimension_ledger": {
                "U14_domain": 14,
                "U9_kernel_of_raw_curvature_map": 9,
                "I5_raw_curvature_image": 5,
                "K12_compatible_kernel": 12,
                "H2_generic_common_core": 2,
                "V10_compatible_mod_common_core": 10,
                "proposed_V7_equals_K12_mod_I5_is_defined": False,
                "reason": "I5 is not a submodule of K12 off shell",
            },
            "null_common_core_audit": {
                "authoritative_Weyl_image_rank": 5,
                "B3_Weyl_gauge_preimage_rank": 3,
                "H2_Weyl_target_quotient_rank": 2,
                "induced_H2_map": "(1/4) I2",
                "raw_curvature_intersection_with_K_at_null": 4,
                "warning": (
                    "the certified B3+H2 quotient is modulo Weyl images of "
                    "gauge preimages; it is not the same quotient as ker K"
                ),
            },
            "causal_strata": samples,
            "decision": {
                "strict_differential_equivalence_SR_equals_1_possible_for_this_R": False,
                "reason": (
                    "raw R is not contained in the fourteen-row compatible "
                    "kernel and has rank 5 rather than 12"
                ),
                "SDR_requires_additional_rows_or_a_different_map": True,
                "full_rank14_green_problem_solved": False,
            },
            "exact_chain_square_replacement": {
                "state_map": "T=(C1,div C1)",
                "curvature_equation_operator": "E_curv=(L_WC,K_state)",
                "first_square": [
                    "L_WC T=A_F E_aux",
                    "K_state T=A_C E_aux",
                ],
                "identity_operator": "N=(-K_src,L_K)",
                "second_square": "N A_equation=B_identity C_aux",
                "equation_cone": {
                    "That": "(T,E_aux)",
                    "Khat": "(K_state,-A_C)",
                    "identity": "Khat That=K_state T-A_C E_aux=0",
                    "cross_certificate": (
                        "curved_curvature_auxiliary_chain_map.json"
                    ),
                    "exact": True,
                },
                "consequence": (
                    "T lands in the constraint kernel only on shell; the "
                    "full 40-row equation complex, not raw T, is the correct "
                    "object for a deformation retract"
                ),
            },
            "status_flags_promoted": [],
            "warranted_atomic_flags": [],
            "fail_closed": True,
        }
