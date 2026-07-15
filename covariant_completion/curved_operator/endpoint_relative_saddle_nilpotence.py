"""Exact Schur nilpotence of the minimal endpoint/relative saddle.

The rank-five ``A_F`` incidence can be inserted as a finite-order odd-cyclic
off-diagonal witness between the retained metric graph and the algebraic
mapping-cylinder complement.  The generic saddle feasibility certificate
left open whether its Schur correction changed the endpoint diagonal.

This module answers that question in the complete formal mapping-cylinder
algebra.  If

``L_AF = Q W_AF + W_AF Q``, then its two off-diagonal blocks are

``B=P_alg L_AF P_end`` and ``C=P_end L_AF P_alg``.

Direct multiplication gives ``C B=0`` before applying any chain relation.
Thus the minimal ``A_F`` saddle is triangular/nilpotent at Schur level and
the endpoint Schur operator is exactly the original endpoint diagonal
``D``.  In particular no hidden ``T^sharp L T`` normal correction survives.

This is deliberately narrow: it neither proves nor obstructs Green
hyperbolicity of ``D``, and a larger relative witness could have a nonzero
Schur correction.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping

from covariant_completion.curved_operator.endpoint_relative_saddle_feasibility import (
    EndpointRelativeSaddleFeasibility,
    _nonzero_entries,
)
from covariant_completion.curved_operator.prolonged_metric_endpoint_complex import (
    ProlongedMetricEndpointComplex,
)
from covariant_completion.curved_retract import curvature_mapping_cylinder_kernel as cmc


Matrix = cmc.Matrix


def _certificate_digest(certificate: Mapping[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(certificate, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


@dataclass(frozen=True)
class EndpointRelativeSaddleNilpotence:
    """The exact off-diagonal anticommutator and its zero Schur square."""

    feasibility: EndpointRelativeSaddleFeasibility
    relative_operator: Matrix
    endpoint_to_algebraic: Matrix
    algebraic_to_endpoint: Matrix
    schur_correction: Matrix

    @staticmethod
    def build(
        endpoint: ProlongedMetricEndpointComplex,
    ) -> "EndpointRelativeSaddleNilpotence":
        feasibility = EndpointRelativeSaddleFeasibility.build(endpoint)
        differential = feasibility.mapping.prolonged_differential
        witness = feasibility.relative_witness
        relative_operator = cmc._add(
            cmc._multiply(differential, witness),
            cmc._multiply(witness, differential),
        )
        endpoint_to_algebraic = cmc._multiply(
            cmc._multiply(feasibility.p_alg, relative_operator),
            feasibility.p_end,
        )
        algebraic_to_endpoint = cmc._multiply(
            cmc._multiply(feasibility.p_end, relative_operator),
            feasibility.p_alg,
        )
        schur_correction = cmc._multiply(
            algebraic_to_endpoint, endpoint_to_algebraic
        )
        result = EndpointRelativeSaddleNilpotence(
            feasibility=feasibility,
            relative_operator=relative_operator,
            endpoint_to_algebraic=endpoint_to_algebraic,
            algebraic_to_endpoint=algebraic_to_endpoint,
            schur_correction=schur_correction,
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.feasibility.verify()
        if not _nonzero_entries(self.relative_operator):
            raise AssertionError("the relative anticommutator vanished")
        if not _nonzero_entries(self.endpoint_to_algebraic):
            raise AssertionError("the endpoint-to-algebraic block vanished")
        if not _nonzero_entries(self.algebraic_to_endpoint):
            raise AssertionError("the algebraic-to-endpoint block vanished")
        if not cmc._is_zero(self.schur_correction):
            raise AssertionError("the minimal A_F saddle changed the endpoint Schur block")
        if not cmc._is_zero(
            cmc._multiply(
                cmc._multiply(
                    cmc._multiply(
                        cmc._multiply(
                            self.feasibility.p_end, self.relative_operator
                        ),
                        self.feasibility.p_alg,
                    ),
                    self.relative_operator,
                ),
                self.feasibility.p_end,
            )
        ):
            raise AssertionError("the expanded Schur product is nonzero")

    def certificate(
        self,
        *,
        feasibility_certificate: Mapping[str, object],
        endpoint_certificate: Mapping[str, object],
        mapping_certificate: Mapping[str, object],
    ) -> dict[str, object]:
        self.verify()
        if feasibility_certificate.get("schema") != (
            "pure-weyl-endpoint-relative-saddle-feasibility-v1"
        ):
            raise AssertionError("wrong saddle feasibility input")
        if endpoint_certificate.get("schema") != (
            "pure-weyl-prolonged-metric-endpoint-complex-v1"
        ):
            raise AssertionError("wrong metric endpoint input")
        if mapping_certificate.get("schema") != (
            "pure-weyl-curvature-mapping-cylinder-substitution-v1"
        ):
            raise AssertionError("wrong mapping-cylinder input")
        if mapping_certificate.get("coefficientwise_complete_prolonged_Q") is not True:
            raise AssertionError("the complete prolonged differential is unavailable")
        if endpoint_certificate.get("dimension") != 30:
            raise AssertionError("the retained endpoint dimension drifted")

        relative_entries = _nonzero_entries(self.relative_operator)
        forward_entries = _nonzero_entries(self.endpoint_to_algebraic)
        backward_entries = _nonzero_entries(self.algebraic_to_endpoint)
        return {
            "schema": "pure-weyl-endpoint-relative-saddle-nilpotence-v1",
            "dependency_sha256": {
                "saddle_feasibility": _certificate_digest(
                    feasibility_certificate
                ),
                "metric_endpoint": _certificate_digest(endpoint_certificate),
                "mapping_cylinder": _certificate_digest(mapping_certificate),
            },
            "minimal_AF_relative_operator": {
                "formula": "L_AF=Q_prol W_AF+W_AF Q_prol",
                "nonzero_entries": len(relative_entries),
                "endpoint_to_algebraic_nonzero_entries": len(forward_entries),
                "algebraic_to_endpoint_nonzero_entries": len(backward_entries),
                "purely_off_diagonal": True,
                "finite_order_support_local": True,
                "identity_attachment_occurs_in_L_AF": False,
            },
            "schur_calculation": {
                "B": "P_alg L_AF P_end",
                "C": "P_end L_AF P_alg",
                "correction": "C B",
                "expanded_formula": (
                    "P_end L_AF P_alg L_AF P_end"
                ),
                "correction_nonzero_entries": len(
                    _nonzero_entries(self.schur_correction)
                ),
                "correction_is_zero_before_chain_reduction": True,
                "endpoint_schur_operator": "S_end=D-CB=D",
                "Tsharp_L_T_correction_survives": False,
            },
            "interpretation": {
                "positive": (
                    "the rank-five A_F incidence is triangular/nilpotent at "
                    "Schur level and introduces no new endpoint obstruction"
                ),
                "negative": (
                    "the minimal saddle cannot improve Green invertibility of "
                    "the endpoint diagonal D"
                ),
                "remaining_theorem": (
                    "construct and prove a Green realization for the exact "
                    "thirty-row endpoint diagonal"
                ),
            },
            "scope_guard": (
                "this is a no-effect theorem for the minimal projected A_F "
                "relative witness only; it is neither a no-go theorem for "
                "larger relative witnesses nor a Green theorem for D"
            ),
            "status_flags_promoted": [],
            "causal_green_homotopy": False,
            "prolonged_green_witness": False,
            "fail_closed": True,
        }
