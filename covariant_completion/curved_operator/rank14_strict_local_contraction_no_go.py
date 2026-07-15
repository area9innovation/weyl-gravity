"""Endpoint obstruction to a strict local contraction of the rank-14 cone.

The corrected relative equation cone has dimensions

``9 -> 24 -> 50 -> 49 -> 14``.

Write its first arrow as ``K:G->M``.  A finite-order differential
contraction ``H`` with

``D H + H D = 1``

would force the lower endpoint identity

``H_1 K = 1_G``.

These identities are polynomial identities in the covector.  Evaluation at
the zero covector is therefore legitimate.  In the corrected curved-core
coordinates, ``rank K(0)=5<9``.  Four exact kernel vectors give a
basis-independent contradiction witness.

The last arrow is the *combined* map ``[N,B]:Q+I->J``.  It has rank thirteen
at the zero covector, so it supplies one further obstruction direction.  The
restricted rank-twelve map ``N`` alone must not be used: the certificate
computes the correctly typed combined arrow and its one-dimensional left
nullspace.

This is deliberately a narrow no-go theorem.  It does not obstruct an
idempotent algebraic contraction ``P_alg=D H_alg+H_alg D`` with complementary
projector ``P_end=1-P_alg``.  The Green witness must then be constructed
separately on ``im(P_end)``; wave operators are not themselves projectors.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping

import sympy as sp

from .rank14_corrected_rees_weights import Rank14CorrectedReesWeights


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _columns(vectors: list[sp.Matrix], rows: int) -> sp.Matrix:
    return sp.Matrix.hstack(*vectors) if vectors else sp.zeros(rows, 0)


def _certificate_digest(certificate: Mapping[str, object]) -> str:
    payload = json.dumps(
        certificate, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_promotion_boundary(certificate: Mapping[str, object]) -> None:
    """Reject any use of the endpoint no-go as a positive Green theorem."""

    for flag in (
        "prolonged_green_witness",
        "curvature_causal_green_operators",
        "causal_green_homotopy",
    ):
        if certificate.get(flag) is not False:
            raise AssertionError(f"endpoint no-go cannot promote {flag}")


@dataclass(frozen=True)
class Rank14StrictLocalContractionNoGo:
    """Exact zero-covector obstruction and its null-vector witnesses."""

    gauge_endpoint: sp.Matrix
    upper_endpoint: sp.Matrix
    gauge_kernel: sp.Matrix
    upper_left_null: sp.Matrix

    @staticmethod
    def build() -> "Rank14StrictLocalContractionNoGo":
        rees = Rank14CorrectedReesWeights.build()

        def full_map(name: str) -> sp.Matrix:
            pieces = rees.map_components[name]
            sample = next(iter(pieces.values()))
            return sum(pieces.values(), sp.zeros(sample.rows, sample.cols))

        zero = {component: 0 for component in rees.covector}
        gauge = full_map("K").subs(zero)
        upper = full_map("N").row_join(full_map("B")).subs(zero)
        result = Rank14StrictLocalContractionNoGo(
            gauge_endpoint=gauge,
            upper_endpoint=upper,
            gauge_kernel=_columns(gauge.nullspace(), gauge.cols),
            upper_left_null=_columns(upper.T.nullspace(), upper.rows),
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.gauge_endpoint.shape != (24, 9):
            raise AssertionError("rank-14 cone gauge endpoint shape drifted")
        if self.upper_endpoint.shape != (14, 49):
            raise AssertionError("rank-14 cone upper endpoint shape drifted")
        if self.gauge_endpoint.rank() != 5:
            raise AssertionError("zero-covector gauge endpoint rank drifted")
        if self.upper_endpoint.rank() != 13:
            raise AssertionError("zero-covector combined upper endpoint rank drifted")
        if self.gauge_kernel.shape != (9, 4):
            raise AssertionError("gauge endpoint kernel dimension drifted")
        if self.gauge_endpoint * self.gauge_kernel != sp.zeros(24, 4):
            raise AssertionError("gauge endpoint kernel witness is not exact")
        if self.upper_left_null.shape != (14, 1):
            raise AssertionError("combined upper endpoint cokernel drifted")
        if self.upper_left_null.T * self.upper_endpoint != sp.zeros(1, 49):
            raise AssertionError("combined upper left-null witness is not exact")
        if self.gauge_kernel.rank() != 4:
            raise AssertionError("gauge kernel witnesses are dependent")
        if self.upper_left_null.rank() != 1:
            raise AssertionError("combined upper left-null witness vanished")

    def certificate(
        self, *, rees_certificate: Mapping[str, object]
    ) -> dict[str, object]:
        self.verify()
        if rees_certificate.get("schema") != (
            "pure-weyl-rank14-corrected-rees-weights-v2"
        ):
            raise AssertionError("wrong corrected rank-14 Rees certificate")
        decision = rees_certificate.get("decision")
        if not isinstance(decision, Mapping) or not all(
            (
                decision.get("degree_zero_associated_graded_is_a_complex")
                is True,
                decision.get("degree_minus_one_multicomplex_relation") is True,
                decision.get("null_PBW_E2_page_is_exact") is True,
                decision.get("support_local_contraction_constructed") is False,
                decision.get("prolonged_green_witness") is False,
            )
        ):
            raise AssertionError("corrected Rees dependency boundary drifted")
        certificate = {
            "schema": "pure-weyl-rank14-strict-local-contraction-no-go-v1",
            "input_certificate_sha256": {
                "curved_rank14_corrected_rees_weights": _certificate_digest(
                    rees_certificate
                )
            },
            "scope": (
                "finite-order polynomial contraction of the corrected five-term "
                "relative equation cone with algebraic identity anticommutator"
            ),
            "cone_dimensions": [9, 24, 50, 49, 14],
            "endpoint_audit": {
                "zero_covector": [0, 0, 0, 0],
                "K_shape": list(self.gauge_endpoint.shape),
                "K_rank": self.gauge_endpoint.rank(),
                "K_kernel_dimension": self.gauge_kernel.cols,
                "combined_N_B_shape": list(self.upper_endpoint.shape),
                "combined_N_B_rank": self.upper_endpoint.rank(),
                "combined_N_B_left_null_dimension": self.upper_left_null.cols,
                "upper_endpoint_has_rank_obstruction": True,
                "exact_witnesses": {
                    "K_times_kernel": "zero",
                    "K_kernel_sha256": _digest(self.gauge_kernel),
                    "left_null_transpose_times_combined_N_B": "zero",
                    "combined_N_B_left_null_sha256": _digest(
                        self.upper_left_null
                    ),
                },
            },
            "strict_contraction_obstruction": {
                "endpoint_equations_for_DH_plus_HD_equals_identity": [
                    "H1 K=I_9",
                    "[N,B] H4=I_14",
                ],
                "H1_K_identity_possible": False,
                "combined_N_B_H4_rank_obstructed_at_zero": True,
                "proof": (
                    "evaluation at zeta=0 gives rank(H1 K)<=5<9 and "
                    "rank([N,B] H4)<=13<14"
                ),
                "polynomial_support_local_DH_plus_HD_equals_identity_possible": False,
            },
            "surviving_hybrid_projector_route": {
                "idempotent_P_alg_ruled_out": False,
                "projector_identities_required": [
                    "P_alg=D H_alg+H_alg D",
                    "P_alg^2=P_alg",
                    "P_end=1-P_alg",
                    "P_end^2=P_end",
                    "D P_alg=P_alg D",
                ],
                "lower_endpoint_constraint": (
                    "P_alg,G=H1 K has rank at most five at zeta=0, so "
                    "P_end,G retains at least four directions"
                ),
                "upper_endpoint_constraint": (
                    "P_alg,J=[N,B] H4 has rank at most thirteen at zeta=0, "
                    "so P_end,J retains at least one direction"
                ),
                "reason": (
                    "the rank defect forbids contraction of the whole cone but "
                    "is compatible with an algebraic projector onto a proper "
                    "contractible summand"
                ),
                "next_exact_system": (
                    "first solve the four adjacent PBW projector identities for "
                    "H_alg; then solve L_end=D W_end+W_end D on im(P_end) and "
                    "prove L_end Green hyperbolic before defining Gamma"
                ),
                "wave_or_subsidiary_operator_used_as_projector": False,
            },
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [
                "rank14_strict_local_identity_contraction_no_go"
            ],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
        validate_promotion_boundary(certificate)
        return certificate
