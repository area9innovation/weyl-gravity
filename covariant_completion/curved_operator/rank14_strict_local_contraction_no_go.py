"""Endpoint obstruction to a strict local contraction of the rank-14 cone.

The corrected relative equation cone has dimensions

``9 -> 24 -> 50 -> 49 -> 14``.

Write its first and last arrows as ``K:G->M`` and ``N:Q+I->J``.  A
finite-order differential contraction ``H`` with

``D H + H D = 1``

would force the endpoint identities

``H_1 K = 1_G`` and ``N H_4 = 1_J``.

These identities are polynomial identities in the covector.  Evaluation at
the zero covector is therefore legitimate.  In the corrected curved-core
coordinates, ``rank K(0)=5<9`` and ``rank N(0)=12<14``.  Exact kernel and
left-null vectors give basis-independent contradiction witnesses.

This is deliberately a narrow no-go theorem.  It does not obstruct a Green
witness ``D H+H D=P`` whose endpoint blocks are the known wave and
subsidiary operators.  Indeed those blocks are allowed to be characteristic;
the result only rules out replacing them by algebraic identities.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from .rank14_corrected_rees_weights import Rank14CorrectedReesWeights


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _columns(vectors: list[sp.Matrix], rows: int) -> sp.Matrix:
    return sp.Matrix.hstack(*vectors) if vectors else sp.zeros(rows, 0)


@dataclass(frozen=True)
class Rank14StrictLocalContractionNoGo:
    """Exact zero-covector obstruction and its null-vector witnesses."""

    gauge_endpoint: sp.Matrix
    identity_endpoint: sp.Matrix
    gauge_kernel: sp.Matrix
    identity_left_null: sp.Matrix

    @staticmethod
    def build() -> "Rank14StrictLocalContractionNoGo":
        rees = Rank14CorrectedReesWeights.build()

        def full_map(name: str) -> sp.Matrix:
            pieces = rees.map_components[name]
            sample = next(iter(pieces.values()))
            return sum(pieces.values(), sp.zeros(sample.rows, sample.cols))

        zero = {component: 0 for component in rees.covector}
        gauge = full_map("K").subs(zero)
        identity = full_map("N").subs(zero)
        result = Rank14StrictLocalContractionNoGo(
            gauge_endpoint=gauge,
            identity_endpoint=identity,
            gauge_kernel=_columns(gauge.nullspace(), gauge.cols),
            identity_left_null=_columns(identity.T.nullspace(), identity.rows),
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.gauge_endpoint.shape != (24, 9):
            raise AssertionError("rank-14 cone gauge endpoint shape drifted")
        if self.identity_endpoint.shape != (14, 40):
            raise AssertionError("rank-14 cone identity endpoint shape drifted")
        if self.gauge_endpoint.rank() != 5:
            raise AssertionError("zero-covector gauge endpoint rank drifted")
        if self.identity_endpoint.rank() != 12:
            raise AssertionError("zero-covector identity endpoint rank drifted")
        if self.gauge_kernel.shape != (9, 4):
            raise AssertionError("gauge endpoint kernel dimension drifted")
        if self.identity_left_null.shape != (14, 2):
            raise AssertionError("identity endpoint cokernel dimension drifted")
        if self.gauge_endpoint * self.gauge_kernel != sp.zeros(24, 4):
            raise AssertionError("gauge endpoint kernel witness is not exact")
        if self.identity_left_null.T * self.identity_endpoint != sp.zeros(2, 40):
            raise AssertionError("identity endpoint left-null witness is not exact")
        if self.gauge_kernel.rank() != 4:
            raise AssertionError("gauge kernel witnesses are dependent")
        if self.identity_left_null.rank() != 2:
            raise AssertionError("identity left-null witnesses are dependent")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-rank14-strict-local-contraction-no-go-v1",
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
                "N_shape": list(self.identity_endpoint.shape),
                "N_rank": self.identity_endpoint.rank(),
                "N_left_null_dimension": self.identity_left_null.cols,
                "exact_witnesses": {
                    "K_times_kernel": "zero",
                    "left_null_transpose_times_N": "zero",
                    "K_kernel_sha256": _digest(self.gauge_kernel),
                    "N_left_null_sha256": _digest(self.identity_left_null),
                },
            },
            "strict_contraction_obstruction": {
                "endpoint_equations_for_DH_plus_HD_equals_identity": [
                    "H1 K=I_9",
                    "N H4=I_14",
                ],
                "H1_K_identity_possible": False,
                "N_H4_identity_possible": False,
                "proof": (
                    "evaluation at zeta=0 gives ranks at most 5 and 12, "
                    "strictly below the identity ranks 9 and 14"
                ),
                "polynomial_support_local_DH_plus_HD_equals_identity_possible": False,
            },
            "surviving_green_witness_route": {
                "DH_plus_HD_equals_P_cone_ruled_out": False,
                "endpoint_targets": [
                    "P_G=C_aux K_aux (gauge wave block)",
                    "P_J=N_curv i_C (subsidiary block)",
                ],
                "reason": (
                    "Green-hyperbolic endpoint operators may be characteristic "
                    "and need not have full rank at the zero covector"
                ),
                "next_exact_system": (
                    "solve the four adjacent PBW identities in D H+H D=P_cone, "
                    "fixing the endpoint blocks to the certified gauge-wave and "
                    "Weyl--Cotton subsidiary operators"
                ),
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
