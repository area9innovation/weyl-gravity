"""Exact boundary for lifting the Weyl--Cotton witness to the metric graph.

The hybrid algebraic projector retains the thirty-row metric complex as a
local graph inside the curvature mapping cylinder.  It is tempting to
restrict the already certified Weyl--Cotton backward map

``p_F : F[26] + C[14] -> U[26]``

to that graph.  On the middle row this would require a metric operator
``S:E_met[10]->M_met[10]`` satisfying, at the leading Douglis page,

``T S = p_F A_core = A_F``.

This module proves that equation impossible in the current incidence.  The
curvature-state symbol factors as ``T=J W``, where ``W`` is the electric /
magnetic Weyl symbol and the projection ``pi_EB`` obeys ``pi_EB J=1``.
The source attachment ``A_F`` has rank five and is supported only in the
``A_STF`` source rows, hence ``pi_EB A_F=0``.  Therefore

``T S=A_F => W S=0 => T S=J W S=0``,

contradicting ``rank(A_F)=5``.  This is an exact polynomial-symbol argument,
not a sampled-rank inference.

The upper graph lift is different and succeeds: an explicit pointwise map
``R:I_met[5]->E_met[10]`` satisfies ``A_core R=i_C B_core``.  Thus the first
open incidence is precisely the middle graph lift.  A complete causal
construction must either use a different curvature backward map or let its
witness leave the retained graph into the algebraically contractible
relative cone and prove that the resulting saddle system has compatible
advanced/retarded inverses.

No statement here rules out such a relative Green witness.  In particular,
the result is not a no-go theorem for the metric BV complex or for Green
hyperbolicity.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping

import sympy as sp

from covariant_completion.curved_operator.expanded_relative_witness_rank14_curvature_presentation import (
    _weyl_eb_symbol,
)
from covariant_completion.curved_operator.rank14_weyl_cotton_symbol_audit import (
    Rank14WeylCottonSymbolAudit,
)
from covariant_completion.curved_operator.weyl_3plus1 import (
    WeylCottonThreePlusOne,
)
from covariant_completion.curved_operator.weyl_cotton_row_audit import (
    _old_from_natural_state,
)
from covariant_completion.curved_retract.curved_core_curvature_chain_map import (
    CurvedCoreCurvatureChainMap,
)


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _certificate_digest(certificate: Mapping[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(certificate, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _nonzero_count(matrix: sp.MatrixBase) -> int:
    return sum(int(value != 0) for value in matrix)


def _nested(mapping: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = mapping.get(key)
    if not isinstance(value, Mapping):
        raise AssertionError(f"missing mapping {key}")
    return value


SAMPLE_COVECTORS = {
    "generic_(2,1,3,5)": (2, 1, 3, 5),
    "timelike_(2,1,0,0)": (2, 1, 0, 0),
    "spacelike_(0,1,0,0)": (0, 1, 0, 0),
    "null_(1,1,0,0)": (1, 1, 0, 0),
    "temporal_(1,0,0,0)": (1, 0, 0, 0),
}


@dataclass(frozen=True)
class EndpointCurvatureGraphLiftBoundary:
    """The exact upper lift and canonical-middle-lift obstruction."""

    covector: tuple[sp.Symbol, ...]
    state_symbol: sp.Matrix
    weyl_symbol: sp.Matrix
    state_from_weyl: sp.Matrix
    electric_magnetic_projection: sp.Matrix
    equation_attachment: sp.Matrix
    evolution_attachment: sp.Matrix
    constraint_attachment: sp.Matrix
    identity_attachment: sp.Matrix
    upper_metric_lift: sp.Matrix
    upper_target: sp.Matrix

    @staticmethod
    def build() -> "EndpointCurvatureGraphLiftBoundary":
        symbol = Rank14WeylCottonSymbolAudit.build()
        core = CurvedCoreCurvatureChainMap.build()
        decomposition = WeylCottonThreePlusOne.build()
        tau = symbol.tau
        spatial = symbol.spatial_covector

        divergence = sp.zeros(16, 10)
        for coefficient, table in zip(
            (tau, *spatial),
            decomposition.cotton_divergence_coefficients,
            strict=True,
        ):
            divergence += coefficient * table
        state_from_weyl = (
            _old_from_natural_state().inv()
            * sp.eye(10).col_join(divergence)
        ).applyfunc(sp.expand)
        weyl = _weyl_eb_symbol((tau, *spatial)).applyfunc(sp.expand)
        projection = sp.eye(26)[:10, :]

        attachment = core.core_equation_attachment
        evolution_attachment = attachment[:26, :]
        constraint_attachment = attachment[26:, :]
        identity_attachment = core.core_identity_attachment

        # In paired symmetric equation coordinates the first four rows are
        # the temporal and mixed components.  The fifth identity (Weyl
        # scalar) has zero B_core image and therefore has zero lift.
        upper_lift = sp.zeros(10, 5)
        upper_lift[0, 0] = sp.Rational(4, 3)
        upper_lift[1, 1] = 1
        upper_lift[2, 2] = 1
        upper_lift[3, 3] = 1
        upper_target = sp.zeros(40, 5)
        upper_target[26:, :] = identity_attachment

        result = EndpointCurvatureGraphLiftBoundary(
            covector=(tau, *spatial),
            state_symbol=symbol.state_symbol_metric,
            weyl_symbol=weyl,
            state_from_weyl=state_from_weyl,
            electric_magnetic_projection=projection,
            equation_attachment=attachment,
            evolution_attachment=evolution_attachment,
            constraint_attachment=constraint_attachment,
            identity_attachment=identity_attachment,
            upper_metric_lift=upper_lift,
            upper_target=upper_target,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.state_symbol.shape != (26, 10):
            raise AssertionError("metric curvature-state symbol shape drifted")
        if self.equation_attachment.shape != (40, 10):
            raise AssertionError("core equation attachment shape drifted")
        if self.evolution_attachment.rank() != 5:
            raise AssertionError("A_F rank drifted")
        if self.constraint_attachment.rank() != 4:
            raise AssertionError("A_C rank drifted")
        if self.equation_attachment.rank() != 9:
            raise AssertionError("A_core rank drifted")

        # Exact factorization and retraction of the Weyl state coordinates.
        if (
            self.state_from_weyl * self.weyl_symbol
            - self.state_symbol
        ).applyfunc(sp.expand) != sp.zeros(26, 10):
            raise AssertionError("T=J W factorization drifted")
        if (
            self.electric_magnetic_projection * self.state_from_weyl
            != sp.eye(10)
        ):
            raise AssertionError("pi_EB J is not the identity")

        # A_F occupies only the A_STF source rows.  This proves, over the
        # full polynomial symbol ring, im(T) intersect im(A_F)=0: equality
        # J W x=A_F y implies W x=0 after pi_EB, and hence both sides vanish.
        if (
            self.electric_magnetic_projection * self.evolution_attachment
            != sp.zeros(10, 10)
        ):
            raise AssertionError("A_F leaked into electric/magnetic rows")
        support = tuple(
            row
            for row in range(26)
            if any(self.evolution_attachment[row, column] != 0 for column in range(10))
        )
        if support != (10, 11, 12, 13, 14):
            raise AssertionError("A_F support is no longer exactly A_STF[5]")

        # The canonical upper WC backward map i_C *does* lift to the graph.
        if (
            self.equation_attachment * self.upper_metric_lift
            != self.upper_target
        ):
            raise AssertionError("A_core R=i_C B_core failed")
        if self.upper_metric_lift.rank() != 4:
            raise AssertionError("upper metric lift rank drifted")

        # Independent exact rank regressions on all characteristic strata.
        for covector in SAMPLE_COVECTORS.values():
            substitution = dict(zip(self.covector, covector, strict=True))
            state = self.state_symbol.subs(substitution)
            joined = state.row_join(self.evolution_attachment)
            if (state.rank(), self.evolution_attachment.rank(), joined.rank()) != (
                5,
                5,
                10,
            ):
                raise AssertionError(
                    f"canonical middle-lift rank boundary drifted at {covector}"
                )

    def sample_ranks(self) -> dict[str, dict[str, int]]:
        result: dict[str, dict[str, int]] = {}
        for name, covector in SAMPLE_COVECTORS.items():
            substitution = dict(zip(self.covector, covector, strict=True))
            state = self.state_symbol.subs(substitution)
            joined = state.row_join(self.evolution_attachment)
            result[name] = {
                "rank_T": state.rank(),
                "rank_A_F": self.evolution_attachment.rank(),
                "rank_T_join_A_F": joined.rank(),
                "intersection_dimension": (
                    state.rank()
                    + self.evolution_attachment.rank()
                    - joined.rank()
                ),
            }
        return result

    def certificate(
        self,
        *,
        hybrid_certificate: Mapping[str, object],
        core_chain_certificate: Mapping[str, object],
        curvature_witness_certificate: Mapping[str, object],
        ghost_factor_certificate: Mapping[str, object],
        tt_factor_certificate: Mapping[str, object],
        reverify: bool = True,
    ) -> dict[str, object]:
        if reverify:
            self.verify()
        if hybrid_certificate.get("schema") != (
            "pure-weyl-prolonged-hybrid-algebraic-projector-v1"
        ):
            raise AssertionError("wrong hybrid projector input")
        composite = _nested(hybrid_certificate, "composite_SDR")
        endpoint = _nested(hybrid_certificate, "retained_endpoint")
        if not all(
            (
                composite.get("P_end_idempotent") is True,
                composite.get("D_P_end_equals_P_end_D") is True,
                composite.get("support_local") is True,
                endpoint.get("dimension") == 30,
                endpoint.get("curvature_to_metric_inverse_used") is False,
            )
        ):
            raise AssertionError("the 30-row endpoint graph is unavailable")
        if core_chain_certificate.get("schema") != (
            "pure-weyl-curved-core-curvature-chain-map-v1"
        ):
            raise AssertionError("wrong curved core chain-map input")
        if not _nested(core_chain_certificate, "lifted_chain_squares").get(
            "exact"
        ):
            raise AssertionError("curved core attachment squares are open")
        if curvature_witness_certificate.get("schema") != (
            "pure-weyl-cotton-block-green-witness-v1"
        ):
            raise AssertionError("wrong Weyl--Cotton witness input")
        if not _nested(
            curvature_witness_certificate, "exact_block_identities"
        ).get("P_equals_QW_plus_WQ"):
            raise AssertionError("Weyl--Cotton witness identity regressed")
        if ghost_factor_certificate.get("schema") != (
            "pure-weyl-cylinder-ghost-curvature-completion-v1"
        ) or not _nested(ghost_factor_certificate, "factorization").get(
            "normally_hyperbolic_factors"
        ):
            raise AssertionError("metric ghost biwave factors are unavailable")
        if tt_factor_certificate.get("schema") != (
            "pure-weyl-tt-local-factorization-v1"
        ) or not tt_factor_certificate.get("reduced_green_hyperbolic"):
            raise AssertionError("physical triangular biwave input unavailable")

        samples = self.sample_ranks()
        return {
            "schema": "pure-weyl-endpoint-curvature-graph-lift-boundary-v1",
            "dependency_tag": "LORENTZIAN-CAUSAL",
            "input_certificate_sha256": {
                "hybrid_projector": _certificate_digest(hybrid_certificate),
                "curved_core_chain_map": _certificate_digest(
                    core_chain_certificate
                ),
                "weyl_cotton_witness": _certificate_digest(
                    curvature_witness_certificate
                ),
                "ghost_biwave": _certificate_digest(ghost_factor_certificate),
                "TT_biwave": _certificate_digest(tt_factor_certificate),
            },
            "retained_endpoint": {
                "complex": "G_met[5] -> M_met[10] -> E_met[10] -> I_met[5]",
                "dimension": 30,
                "embedding": "local metric-curvature graph",
                "curvature_inverse_used": False,
                "projector_support_local": True,
            },
            "certified_endpoint_blocks": {
                "gauge_ghost": {
                    "operator": "T_gauge K_met=Box(Box+2)",
                    "normally_hyperbolic_factors": True,
                    "advanced_retarded_support": True,
                },
                "physical_restriction": {
                    "operator": "B_TT=P_minus P_plus",
                    "triangular_biwave_green_formula_exact": True,
                    "arbitrary_source_TT_projector_used": False,
                    "extends_to_all_metric_sources": False,
                },
                "weyl_cotton": {
                    "diagonal_blocks": ["L_26", "S_14"],
                    "symmetric_hyperbolic": True,
                    "sourced_identity": "S K=R L",
                },
            },
            "upper_graph_lift": {
                "target_equation": "A_core R=i_C B_core",
                "exact": True,
                "R_shape": list(self.upper_metric_lift.shape),
                "R_rank": self.upper_metric_lift.rank(),
                "R_nonzero_entries": _nonzero_count(self.upper_metric_lift),
                "R_sha256": _digest(self.upper_metric_lift),
                "finite_order": 0,
                "support_local": True,
            },
            "canonical_middle_graph_lift_obstruction": {
                "required_equation": "T_core S=p_F A_core=A_F",
                "T_factorization": "T_core=J_WC W_EB",
                "pi_EB_J_WC": "identity",
                "pi_EB_A_F": "zero",
                "rank_A_F": self.evolution_attachment.rank(),
                "A_F_support": "A_STF[5] source rows",
                "proof": (
                    "T S=A_F implies W_EB S=pi_EB A_F=0; then "
                    "T S=J_WC W_EB S=0, contradicting rank(A_F)=5"
                ),
                "polynomial_symbol_identity": True,
                "sample_rank_regression": samples,
                "canonical_p_F_graph_lift_exists": False,
                "scope": (
                    "the leading Douglis incidence of the canonical zeroth-order "
                    "Weyl--Cotton backward map p_F"
                ),
                "does_not_rule_out": [
                    "a different curvature backward map",
                    "a witness with off-graph relative-cone components",
                    "a two-way Green-hyperbolic saddle extension",
                    "Green hyperbolicity of the metric BV complex",
                ],
            },
            "minimum_remaining_operator_identity": {
                "preferred_relative_form": (
                    "construct W_rel with (1-P_end) W_rel P_end nonzero and "
                    "L_rel=Q W_rel+W_rel Q a finite filtered extension of "
                    "L_26, S_14, the ghost waves and the physical biwave"
                ),
                "required_source_statement": (
                    "for every compact endpoint source, the same-sided Green "
                    "solution returns to the curvature graph and its sourced "
                    "subsidiary defect vanishes"
                ),
                "required_adjoint_statement": (
                    "W_rel is graded cyclic (or has a certified adjoint witness) "
                    "and G_rel,+^sharp equals the graded G_rel,-"
                ),
                "forbidden_shortcuts": [
                    "TT or helicity projector",
                    "inverse curl",
                    "inverse Laplacian",
                    "curvature-only metric reconstruction",
                ],
            },
            "decision": {
                "canonical_WC_witness_restricts_to_30_graph": False,
                "actual_W_end_constructed": False,
                "actual_L_end_two_sided_Green": False,
                "arbitrary_compact_endpoint_sources_solved": False,
                "graded_adjoint_Green_identity_proved": False,
                "prolonged_green_witness": False,
                "curvature_causal_green_operators": False,
                "causal_green_homotopy": False,
            },
            "warranted_atomic_flags": [
                "endpoint_upper_curvature_graph_lift_exact",
                "canonical_middle_curvature_graph_lift_no_go",
            ],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
