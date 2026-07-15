"""Hybrid algebraic projector on the curvature-prolonged BV complex.

Two support-local SDRs are already exact:

* the curvature mapping cylinder retracts the 386-component minimal
  prolonged carrier to the 66-component auxiliary complex;
* the local BV-canonical auxiliary shift retracts those 66 components to the
  30-component metric core.

For SDRs ``(I_1,P_1,k_1)`` and ``(I_2,P_2,k_2)`` in the project convention

``I_a P_a-1=Q k_a+k_a Q``, ``P_a I_a=1``,

their composite is

``I=I_1 I_2``, ``P=P_2 P_1``,
``k=k_1+I_1 k_2 P_1``.

Consequently

``H_alg=-k``, ``P_end=I P`` and ``P_alg=1-P_end``

satisfy ``P_alg=Q H_alg+H_alg Q``.  Both projectors are idempotent,
complementary and commute with ``Q``.  The image of ``P_end`` is the local
curvature graph of the retained metric core, not a curvature-only quotient;
no inverse Weyl map or nonlocal projector is used.

This is the algebraic half of the requested hybrid architecture.  It does
not construct the separate residual Green witness ``W_end`` on
``im(P_end)`` and therefore promotes no causal flag.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping

import sympy as sp

from covariant_completion.auxiliary_equivalence import GeneralizedAuxiliaryRetract
from covariant_completion.curved_retract.curvature_mapping_cylinder_kernel import (
    CurvatureMappingCylinderKernel,
    Matrix,
    _add,
    _identity,
    _is_zero,
    _matrix_adjoint,
    _multiply,
    _scale,
)


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _certificate_digest(certificate: Mapping[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(
            certificate, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def _matrix_equal(left: Matrix, right: Matrix) -> bool:
    return all(
        left[row][column] == right[row][column]
        for row in range(len(left))
        for column in range(len(left))
    )


def _auxiliary_pairing(retract: GeneralizedAuxiliaryRetract) -> sp.Matrix:
    pairing = sp.zeros(66)
    pairing[0:9, 57:66] = retract.system.gauge_fixing_pairing
    pairing[57:66, 0:9] = retract.system.gauge_fixing_pairing
    pairing[9:33, 33:57] = retract.system.field_fibre_pairing
    pairing[33:57, 9:33] = retract.system.field_fibre_pairing
    return pairing


def validate_promotion_boundary(certificate: Mapping[str, object]) -> None:
    for flag in (
        "prolonged_green_witness",
        "curvature_causal_green_operators",
        "causal_green_homotopy",
    ):
        if certificate.get(flag) is not False:
            raise AssertionError(f"algebraic projector cannot promote {flag}")


@dataclass(frozen=True)
class ProlongedHybridAlgebraicProjector:
    """Exact component SDR projectors and their composite formula."""

    auxiliary: GeneralizedAuxiliaryRetract
    mapping: CurvatureMappingCylinderKernel
    auxiliary_h_alg: sp.Matrix
    auxiliary_p_alg: sp.Matrix
    auxiliary_p_end: sp.Matrix
    mapping_h_alg: Matrix
    mapping_p_alg: Matrix
    mapping_p_end: Matrix

    @staticmethod
    def build() -> "ProlongedHybridAlgebraicProjector":
        auxiliary = GeneralizedAuxiliaryRetract.build()
        mapping = CurvatureMappingCylinderKernel.build()

        aux_end = (auxiliary.inclusion * auxiliary.projection).applyfunc(sp.expand)
        aux_alg = sp.eye(66) - aux_end
        aux_h = -auxiliary.total_homotopy

        map_end = _multiply(mapping.inclusion, mapping.projection)
        map_alg = _add(_identity(), _scale(map_end, -1))
        map_h = _scale(mapping.homotopy, -1)

        result = ProlongedHybridAlgebraicProjector(
            auxiliary=auxiliary,
            mapping=mapping,
            auxiliary_h_alg=aux_h,
            auxiliary_p_alg=aux_alg,
            auxiliary_p_end=aux_end,
            mapping_h_alg=map_h,
            mapping_p_alg=map_alg,
            mapping_p_end=map_end,
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.auxiliary.verify()
        self.mapping.verify()

        q = self.auxiliary.original_differential
        h = self.auxiliary_h_alg
        p_alg = self.auxiliary_p_alg
        p_end = self.auxiliary_p_end
        if sp.simplify(q * h + h * q - p_alg) != sp.zeros(66):
            raise AssertionError("auxiliary P_alg is not Q H_alg+H_alg Q")
        for projector, name in ((p_alg, "P_alg"), (p_end, "P_end")):
            if sp.simplify(projector * projector - projector) != sp.zeros(66):
                raise AssertionError(f"auxiliary {name} is not idempotent")
            if sp.simplify(q * projector - projector * q) != sp.zeros(66):
                raise AssertionError(f"auxiliary {name} does not commute with Q")
        if sp.simplify(p_alg + p_end - sp.eye(66)) != sp.zeros(66):
            raise AssertionError("auxiliary projectors are not complementary")
        if sp.simplify(p_alg * p_end) != sp.zeros(66):
            raise AssertionError("auxiliary projectors are not orthogonal")

        omega = _auxiliary_pairing(self.auxiliary)
        negative = {component: -component for component in self.auxiliary.system.covector}
        if sp.simplify(omega * h - h.subs(negative).T * omega) != sp.zeros(66):
            raise AssertionError("auxiliary H_alg is not cyclic")
        for projector, name in ((p_alg, "P_alg"), (p_end, "P_end")):
            if sp.simplify(
                omega * projector - projector.subs(negative).T * omega
            ) != sp.zeros(66):
                raise AssertionError(f"auxiliary {name} is not formally self-adjoint")

        qm = self.mapping.prolonged_differential
        hm = self.mapping_h_alg
        if not _matrix_equal(
            _add(_multiply(qm, hm), _multiply(hm, qm)),
            self.mapping_p_alg,
        ):
            raise AssertionError("mapping P_alg is not Q H_alg+H_alg Q")
        for projector, name in (
            (self.mapping_p_alg, "P_alg"),
            (self.mapping_p_end, "P_end"),
        ):
            if not _matrix_equal(_multiply(projector, projector), projector):
                raise AssertionError(f"mapping {name} is not idempotent")
            if not _matrix_equal(_multiply(qm, projector), _multiply(projector, qm)):
                raise AssertionError(f"mapping {name} does not commute with Q")
        if not _matrix_equal(
            _add(self.mapping_p_alg, self.mapping_p_end), _identity()
        ):
            raise AssertionError("mapping projectors are not complementary")
        if not _is_zero(_multiply(self.mapping_p_alg, self.mapping_p_end)):
            raise AssertionError("mapping projectors are not orthogonal")

        # Degree-zero projectors and the degree-minus-one homotopy are cyclic
        # because the mapping-cylinder shear is canonical.  Check the
        # projector adjoint identity explicitly; H cyclicity is already an
        # invariant of CurvatureMappingCylinderKernel.verify().
        for projector, name in (
            (self.mapping_p_alg, "P_alg"),
            (self.mapping_p_end, "P_end"),
        ):
            defect = _add(
                _multiply(_matrix_adjoint(projector), self.mapping.pairing),
                _scale(_multiply(self.mapping.pairing, projector), -1),
            )
            if not _is_zero(defect):
                raise AssertionError(f"mapping {name} is not formally self-adjoint")

    def certificate(
        self,
        *,
        curved_auxiliary_certificate: Mapping[str, object],
        mapping_certificate: Mapping[str, object],
        reverify: bool = True,
    ) -> dict[str, object]:
        if reverify:
            self.verify()
        if curved_auxiliary_certificate.get("schema") != (
            "pure-weyl-curved-auxiliary-canonical-split-v1"
        ) or curved_auxiliary_certificate.get("curved_deformation_retract") is not True:
            raise AssertionError("actual curved auxiliary SDR is unavailable")
        factorized = curved_auxiliary_certificate.get("factorized_curved_Q_split")
        if not isinstance(factorized, Mapping) or not all(
            (
                factorized.get("actual_curved_Q_conjugation_verified") is True,
                factorized.get("homotopy", {}).get("i_p_minus_identity")
                == "Qk+kQ",
                factorized.get("support", {}).get("compact") is True,
                factorized.get("support", {}).get("spacelike_compact") is True,
            )
        ):
            raise AssertionError("curved auxiliary SDR dependency drifted")
        if mapping_certificate.get("schema") != (
            "pure-weyl-curvature-mapping-cylinder-substitution-v1"
        ) or mapping_certificate.get("coefficientwise_complete_prolonged_Q") is not True:
            raise AssertionError("repaired mapping-cylinder SDR is unavailable")
        kernel = mapping_certificate.get("kernel")
        if not isinstance(kernel, Mapping) or not all(
            (
                kernel.get("Q_squared") == "zero",
                kernel.get("P_I") == "identity",
                kernel.get("I_P_minus_identity") == "QH+HQ",
                kernel.get("odd_BV_cyclicity_defect") == 0,
                kernel.get("row_coverage", {}).get("rows_enumerated") == 16,
                kernel.get("row_coverage", {}).get("silent_rows_dropped") == 0,
            )
        ):
            raise AssertionError("mapping-cylinder projector dependency drifted")

        certificate = {
            "schema": "pure-weyl-prolonged-hybrid-algebraic-projector-v1",
            "input_certificate_sha256": {
                "curved_auxiliary_canonical_split": _certificate_digest(
                    curved_auxiliary_certificate
                ),
                "curvature_mapping_cylinder_substitution": _certificate_digest(
                    mapping_certificate
                ),
            },
            "minimal_dimension_ledger": {
                "prolonged": 386,
                "auxiliary_base": 66,
                "retained_metric_curvature_graph": 30,
                "algebraically_contracted": 356,
                "calculation": "386=66+4*(26+40+14); 356=386-30",
            },
            "component_projectors": {
                "auxiliary": {
                    "P_alg_rank": self.auxiliary_p_alg.rank(),
                    "P_end_rank": self.auxiliary_p_end.rank(),
                    "QH_plus_HQ_minus_P_alg": "zero",
                    "P_alg_squared_minus_P_alg": "zero",
                    "P_end_squared_minus_P_end": "zero",
                    "P_alg_P_end": "zero",
                    "Q_projector_commutators": "zero",
                    "H_alg_cyclicity_defect": 0,
                    "projector_adjoint_defects": 0,
                    "sha256": {
                        "H_alg": _digest(self.auxiliary_h_alg),
                        "P_alg": _digest(self.auxiliary_p_alg),
                        "P_end": _digest(self.auxiliary_p_end),
                    },
                },
                "mapping_cylinder": {
                    "QH_plus_HQ_minus_P_alg": "zero",
                    "P_alg_squared_minus_P_alg": "zero",
                    "P_end_squared_minus_P_end": "zero",
                    "P_alg_P_end": "zero",
                    "Q_projector_commutators": "zero",
                    "H_alg_cyclicity_defect": 0,
                    "projector_adjoint_defects": 0,
                },
            },
            "composite_SDR": {
                "inclusion": "I=I_cyl I_aux",
                "projection": "P=P_aux P_cyl",
                "homotopy_in_project_convention": (
                    "k=k_cyl+I_cyl k_aux P_cyl"
                ),
                "H_alg": "-k",
                "P_end": "I_cyl I_aux P_aux P_cyl",
                "P_alg": "1-P_end=Q H_alg+H_alg Q",
                "P_alg_idempotent": True,
                "P_end_idempotent": True,
                "P_alg_P_end": "zero",
                "D_P_alg_equals_P_alg_D": True,
                "D_P_end_equals_P_end_D": True,
                "cyclic_and_formally_self_adjoint": True,
                "support_local": True,
                "inverse_Laplacian_or_curl": False,
                "spectral_or_helicity_projector": False,
            },
            "retained_endpoint": {
                "description": (
                    "the metric BV core embedded as the local curvature graph"
                ),
                "curvature_variables_retained_as_local_graph_values": True,
                "curvature_to_metric_inverse_used": False,
                "dimension": 30,
                "separate_W_end_constructed": False,
                "separate_G_end_constructed": False,
                "required_analytic_blocks": [
                    "Weyl--Cotton L_26 evolution",
                    "Weyl--Cotton S_14 subsidiary system",
                    "physical triangular biwave extension",
                    "gauge/ghost wave blocks",
                    "pointwise contractible blocks",
                ],
                "ruled_out_fallback": (
                    "the unproved scalar-symbol auxiliary field witness "
                    "E_aux+K_aux C_aux"
                ),
                "ruled_out_fallback_used": False,
                "next_identity": (
                    "construct L_end=Q W_end+W_end Q on im(P_end), prove its "
                    "finite filtered wave/subsidiary/physical-biwave Green "
                    "realization, then Gamma=W_end G_end P_end"
                ),
            },
            "warranted_atomic_flags": [
                "prolonged_hybrid_algebraic_projector_exact"
            ],
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "status_flags_promoted": [],
            "fail_closed": True,
        }
        validate_promotion_boundary(certificate)
        return certificate
