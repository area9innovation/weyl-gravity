"""Exact identity-row map for the auxiliary-to-curvature chain square.

The equation component of the mapping-cylinder chain map is certified in
``curvature_auxiliary_chain_map``.  This module constructs the remaining
identity component without repeating its expensive 700-jet calculation.

In the SO(3)-adapted action-Bach basis

``(scalar[1], mixed[3], spatial-STF[5], trace[1])``

the constant metric equation map has nonzero blocks

``A[10:15,4:9]=-I_5/2``,
``A[32:35,1:4]=-I_3/2`` and ``A[38,0]=-3/2``.

Let ``N=(-R,S)`` be the rank-14 curvature identity operator and let
``C_met=K^sharp=-2 div`` (plus the Weyl trace identity).  Exact comparison
of the temporal, three spatial, and zeroth coefficient tables gives

``N A=B_met C_met``

with only

``B_met[6:9,1:4]=-I_3/4`` and ``B_met[12,0]=-1/4``.

The curved auxiliary SDR projects its nine identity rows onto the retained
metric block.  Only the old ``xi_0^*[4]`` block contributes to ``B_met``;
the derivative correction in the Weyl-scalar row is killed.  Hence
``B_aux=B_met p_id`` is the displayed order-zero 14-by-9 matrix.  The full
relation follows by composing the two certified chain squares:

``N A_aux=B_met C_met p_eq=B_met p_id C_aux=B_aux C_aux``.

No status flag is changed here.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Mapping

import sympy as sp

from covariant_completion.auxiliary_equivalence import GeneralizedAuxiliaryRetract
from covariant_completion.curved_operator.weyl_3plus1 import (
    tracefree_symmetric_spacetime_basis,
)
from covariant_completion.curved_operator.weyl_cotton_hyperbolic import (
    ConstraintAdjustedWeylCottonEvolution,
)


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class CurvatureAuxiliaryIdentityChainMap:
    """The exact ``B_identity`` coefficient matrix and chain defects."""

    bach_to_curvature: sp.Matrix
    metric_identity_coefficients: tuple[sp.Matrix, ...]
    curvature_identity_coefficients: tuple[sp.Matrix, ...]
    metric_identity_map: sp.Matrix
    auxiliary_identity_projection: sp.Matrix
    auxiliary_identity_map: sp.Matrix
    auxiliary_retract_projection_sha256: str
    metric_chain_defects: tuple[sp.Matrix, ...]

    @staticmethod
    def build() -> "CurvatureAuxiliaryIdentityChainMap":
        evolution = ConstraintAdjustedWeylCottonEvolution.build()

        # Action normalization is B_action=-2 B_standard.  The exact
        # SO(3)-component map found by the equation-square producer is
        # therefore -1/2 times the standard Bach component inclusion.
        bach_to_curvature = sp.zeros(40, 10)
        bach_to_curvature[10:15, 4:9] = -sp.eye(5) / 2
        bach_to_curvature[32:35, 1:4] = -sp.eye(3) / 2
        bach_to_curvature[38, 0] = -sp.Rational(3, 2)

        # N=(-R,S).  Table order is temporal, spatial 1/2/3, zeroth.
        curvature_identity = [sp.zeros(14, 26).row_join(sp.eye(14))]
        curvature_identity.extend(
            (-evolution.source_compatibility_spatial_coefficients[axis]).row_join(
                evolution.constraint_spatial_coefficients[axis]
            )
            for axis in range(3)
        )
        curvature_identity.append(
            (-evolution.source_compatibility_zeroth_coefficient).row_join(
                evolution.constraint_zeroth_coefficient
            )
        )

        # C_met=K^sharp=-2 div on the trace-free equation block.  The fifth
        # output is the Weyl trace identity and vanishes on Bach.  The tenth
        # equation input is the separately retained trace coordinate.
        signature = (-1, 1, 1, 1)
        tensor_basis = tracefree_symmetric_spacetime_basis()
        metric_identity: list[sp.Matrix] = []
        for derivative in range(4):
            coefficient = sp.zeros(5, 10)
            for column, tensor in enumerate(tensor_basis):
                for output in range(4):
                    coefficient[output, column] = (
                        -2 * signature[derivative] * tensor[derivative, output]
                    )
            metric_identity.append(coefficient)
        metric_identity.append(sp.zeros(5, 10))

        b_metric = sp.zeros(14, 5)
        b_metric[6:9, 1:4] = -sp.eye(3) / 4
        b_metric[12, 0] = -sp.Rational(1, 4)

        # Auxiliary identity order is
        # (xi_-2^*[4],xi_0^*[4],sigma^*[1]).  The retained metric vector
        # identity is xi_0^*.  Its scalar companion may contain a derivative
        # correction, but the scalar column of B_metric is zero.
        retract = GeneralizedAuxiliaryRetract.build()
        p_identity = retract.projection[25:30, 57:66]
        b_auxiliary = b_metric * p_identity

        defects = tuple(
            curvature * bach_to_curvature - b_metric * metric
            for curvature, metric in zip(
                curvature_identity, metric_identity, strict=True
            )
        )
        result = CurvatureAuxiliaryIdentityChainMap(
            bach_to_curvature=bach_to_curvature,
            metric_identity_coefficients=tuple(metric_identity),
            curvature_identity_coefficients=tuple(curvature_identity),
            metric_identity_map=b_metric,
            auxiliary_identity_projection=p_identity,
            auxiliary_identity_map=b_auxiliary,
            auxiliary_retract_projection_sha256=_digest(retract.projection),
            metric_chain_defects=defects,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.bach_to_curvature.shape != (40, 10):
            raise AssertionError("wrong action-Bach equation map shape")
        if self.bach_to_curvature.rank() != 9:
            raise AssertionError("action-Bach equation map lost a component")
        if len(self.metric_identity_coefficients) != 5 or any(
            matrix.shape != (5, 10)
            for matrix in self.metric_identity_coefficients
        ):
            raise AssertionError("C_met coefficient coverage drifted")
        if len(self.curvature_identity_coefficients) != 5 or any(
            matrix.shape != (14, 40)
            for matrix in self.curvature_identity_coefficients
        ):
            raise AssertionError("N_curv coefficient coverage drifted")
        if any(defect != sp.zeros(14, 10) for defect in self.metric_chain_defects):
            raise AssertionError("N_curv A_metric-B_metric C_metric is nonzero")
        if self.metric_identity_map.shape != (14, 5):
            raise AssertionError("wrong metric identity map shape")
        if self.metric_identity_map.rank() != 4:
            raise AssertionError("metric identity map rank drifted")
        if self.auxiliary_identity_projection.shape != (5, 9):
            raise AssertionError("wrong auxiliary identity projection shape")
        if self.auxiliary_identity_map.shape != (14, 9):
            raise AssertionError("wrong auxiliary identity map shape")
        if self.auxiliary_identity_map.rank() != 4:
            raise AssertionError("auxiliary identity map rank drifted")
        if (
            self.metric_identity_map * self.auxiliary_identity_projection
            != self.auxiliary_identity_map
        ):
            raise AssertionError("B_identity is not B_metric p_identity")
        if sum(int(value != 0) for value in self.auxiliary_identity_map) != 4:
            raise AssertionError("B_identity is not the four-coefficient map")

    def certificate(
        self,
        *,
        equation_certificate: Mapping[str, object],
        retract_certificate: Mapping[str, object],
        reverify: bool = True,
    ) -> dict[str, object]:
        if reverify:
            self.verify()
        if equation_certificate.get("schema") != (
            "pure-weyl-curvature-auxiliary-equation-chain-map-v1"
        ):
            raise AssertionError("wrong curvature equation-chain certificate")
        if not equation_certificate.get("first_chain_relation_exact"):
            raise AssertionError("the equation chain square is not exact")
        if retract_certificate.get("schema") != (
            "pure-weyl-curved-chain-map-status-v1"
        ):
            raise AssertionError("wrong auxiliary retract chain-map certificate")
        if not (
            retract_certificate.get("curved_p_is_chain_map")
            and retract_certificate.get("all_BV_rows_in_curved_comparison")
        ):
            raise AssertionError("the auxiliary identity projection is uncertified")
        regression = retract_certificate.get("Q_conjugation_engine_regression", {})
        hashes = (
            regression.get("matrix_sha256", {})
            if isinstance(regression, Mapping)
            else {}
        )
        if hashes.get("projection") != self.auxiliary_retract_projection_sha256:
            raise AssertionError(
                "the identity block is not bound to the certified retract projection"
            )

        return {
            "schema": "pure-weyl-curvature-auxiliary-identity-chain-map-v1",
            "basis_conventions": {
                "metric_equations": (
                    "action Bach scalar[1],mixed[3],spatial-STF[5],trace[1]"
                ),
                "metric_identities": "diffeomorphism[4],Weyl-trace[1]",
                "auxiliary_identities": (
                    "xi_minus_2_star[4],xi_0_star[4],sigma_star[1]"
                ),
                "curvature_identities": "q[3],r[3],a[3],c[3],s[1],t[1]",
                "adjoint_convention": "K^sharp=-2 div",
            },
            "B_metric": {
                "shape": [14, 5],
                "rank": self.metric_identity_map.rank(),
                "nonzero_blocks": [
                    "B_metric[a[3],spatial_divergence[3]]=-I_3/4",
                    "B_metric[s,temporal_divergence]=-1/4",
                ],
                "sha256": _digest(self.metric_identity_map),
            },
            "A_metric": {
                "tracefree_Bach_to_curvature_sha256": _digest(
                    self.bach_to_curvature[:, :9]
                ),
            },
            "identity_projection": {
                "shape": [5, 9],
                "vector_block": "xi_0_star[4] -> metric diffeomorphism identity[4]",
                "Weyl_scalar_block": "sigma_star -> metric Weyl identity",
                "derivative_scalar_correction_relevant": False,
                "reason": "B_metric annihilates the Weyl-scalar column",
                "sha256": _digest(self.auxiliary_identity_projection),
                "full_retract_projection_sha256": (
                    self.auxiliary_retract_projection_sha256
                ),
            },
            "B_identity": {
                "formula": "B_aux=B_metric p_identity",
                "shape": [14, 9],
                "maximum_order": 0,
                "coefficient_multiindices": 1,
                "rank": self.auxiliary_identity_map.rank(),
                "nonzero_coefficients": sum(
                    int(value != 0) for value in self.auxiliary_identity_map
                ),
                "nonzero_blocks": [
                    "B_aux[a[3],xi_0_star spatial[3]]=-I_3/4",
                    "B_aux[s,xi_0_star temporal]=-1/4",
                ],
                "sha256": _digest(self.auxiliary_identity_map),
            },
            "coefficientwise_identity_square": {
                "table_order": ["time", "space_1", "space_2", "space_3", "zeroth"],
                "N_curv_shapes": [[14, 40]] * 5,
                "C_metric_shapes": [[5, 10]] * 5,
                "defect_counts": [
                    sum(int(value != 0) for value in defect)
                    for defect in self.metric_chain_defects
                ],
                "N_curv_A_metric_minus_B_metric_C_metric": "zero",
                "curved_globalization": (
                    "natural SO(3) component identity with exact unit-S3 lower terms"
                ),
            },
            "full_auxiliary_chain_relation": {
                "derivation": [
                    "N A_aux=N A_metric p_equation",
                    "N A_metric=B_metric C_metric",
                    "C_metric p_equation=p_identity C_aux",
                    "therefore N A_aux=B_identity C_aux",
                ],
                "N_curv_A_equation_minus_B_identity_C_aux": "zero",
                "exact": True,
            },
            "cotangent_lift": {
                "map": "B_identity^sharp",
                "shape": [9, 14],
                "maximum_order": 0,
                "generated_from_same_BV_pairings": True,
            },
            "support": {
                "finite_order": True,
                "maximum_order": 0,
                "inverse_Laplacian_or_curl": False,
                "spectral_projector": False,
                "Green_operator": False,
                "compact": True,
                "spacelike_compact": True,
                "smooth_global": True,
            },
            "second_chain_relation": "N_curv A_equation=B_identity C_aux",
            "second_chain_relation_exact": True,
            "B_identity_emitted": True,
            "mapping_cylinder_cotangent_kernel_assembled": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "proof_boundary": (
                "both mapping-cylinder chain squares are now exact; assembly "
                "of the enlarged differential, cotangent cone, and SDR is separate"
            ),
            "fail_closed": True,
        }
