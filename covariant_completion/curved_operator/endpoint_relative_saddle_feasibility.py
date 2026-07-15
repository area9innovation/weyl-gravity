"""Exact feasibility boundary for the endpoint/relative-cone saddle witness.

The canonical Weyl--Cotton backward map does not preserve the retained
thirty-row metric graph.  Its first obstruction is the rank-five map

``A_F : E_met[10] -> X_U[26]``.

This module checks that the obstruction *does* have the correct incidence
to be used by a two-way relative witness.  In the curvature mapping
cylinder, a raw degree-minus-one seed and its forced cyclic adjoint are

``Ebar_aux -> X_U       : A_F p_E``
``X_U_sharp -> M_aux    : A_F_sharp``.

Here ``p_E`` is the auxiliary-to-metric equation projection; it is absorbed
in the typed formal atom ``AF`` below.  Since ``p_E i_E=1``, the composite
still has rank five.  Projecting the two directions with the complementary
chain projectors gives

``W_AF = P_alg w P_end + P_end w P_alg``.

The result is finite-order, support local, odd cyclic, purely off diagonal,
and its ``X_U <- Ebar_aux`` component is still exactly ``A_F``.  Thus the
rank-five graph-lift obstruction can be coupled without an inverse Weyl map
or a helicity projector.

This is only a feasibility theorem.  For

``W_total = H_alg + W_AF + W_0``

the anticommutator has saddle form ``[[1,B],[C,D]]`` on
``im(P_alg) + im(P_end)``.  It is Green invertible exactly when the Schur
operator ``S_end=D-CB`` has advanced and retarded two-sided inverses.  The
finite block inverse is certified here, conditional on those inverses.  No
existing certificate identifies ``S_end`` with the known Weyl--Cotton /
biwave blocks for arbitrary compact sources, so no causal flag is promoted.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from typing import Mapping

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)
from covariant_completion.curved_retract import curvature_mapping_cylinder_kernel as cmc
from covariant_completion.curved_operator.endpoint_curvature_graph_lift_boundary import (
    EndpointCurvatureGraphLiftBoundary,
)


Matrix = cmc.Matrix


def _certificate_digest(certificate: Mapping[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(certificate, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _relative_adjoint(entry: OperatorPolynomial) -> OperatorPolynomial:
    involution = {
        "K": "C",
        "C": "K",
        "Eaux": "Eaux",
        "Ecurv": "EcurvSharp",
        "EcurvSharp": "Ecurv",
        "Ncurv": "NcurvSharp",
        "NcurvSharp": "Ncurv",
        "T": "Tsharp",
        "Tsharp": "T",
        "A": "Asharp",
        "Asharp": "A",
        "B": "Bsharp",
        "Bsharp": "B",
        "AF": "AFsharp",
        "AFsharp": "AF",
    }
    return OperatorPolynomial._from_dict(
        {
            tuple(involution[name] for name in reversed(word)): coefficient
            for word, coefficient in entry.terms
        }
    )


def _relative_matrix_adjoint(matrix: Matrix) -> Matrix:
    return [
        [_relative_adjoint(matrix[column][row]) for column in range(cmc.SIZE)]
        for row in range(cmc.SIZE)
    ]


def _nonzero_entries(matrix: Matrix) -> tuple[tuple[int, int, str], ...]:
    zero = OperatorPolynomial.zero()
    return tuple(
        (row, column, entry.display())
        for row, values in enumerate(matrix)
        for column, entry in enumerate(values)
        if entry != zero
    )


def _cyclic_defect(matrix: Matrix, pairing: Matrix) -> Matrix:
    return cmc._add(
        cmc._multiply(_relative_matrix_adjoint(matrix), pairing),
        cmc._scale(
            cmc._multiply(cmc._multiply(cmc._degree_sign(), pairing), matrix),
            -1,
        ),
    )


SmallMatrix = list[list[OperatorPolynomial]]


def _small_multiply(left: SmallMatrix, right: SmallMatrix) -> SmallMatrix:
    result = [
        [OperatorPolynomial.zero() for _ in range(2)] for _ in range(2)
    ]
    for row in range(2):
        for column in range(2):
            for middle in range(2):
                result[row][column] = (
                    result[row][column] + left[row][middle] * right[middle][column]
                )
    return result


def _reduce_schur(entry: OperatorPolynomial) -> OperatorPolynomial:
    """Reduce only the assumed two-sided endpoint Green relations."""

    pending = list(entry.terms)
    values: dict[tuple[str, ...], Fraction] = {}
    while pending:
        word, coefficient = pending.pop()
        replaced = False
        for index in range(max(0, len(word) - 1)):
            if word[index : index + 2] in {("G", "S"), ("S", "G")}:
                pending.append((word[:index] + word[index + 2 :], coefficient))
                replaced = True
                break
        if not replaced:
            values[word] = values.get(word, Fraction()) + coefficient
    return OperatorPolynomial._from_dict(values)


def _small_identity_after_reduction(matrix: SmallMatrix) -> bool:
    for row in range(2):
        for column in range(2):
            expected = OperatorPolynomial.identity() if row == column else (
                OperatorPolynomial.zero()
            )
            if _reduce_schur(matrix[row][column]) != expected:
                return False
    return True


@dataclass(frozen=True)
class EndpointRelativeSaddleFeasibility:
    """The exact off-graph coupling and conditional Schur inverse."""

    mapping: cmc.CurvatureMappingCylinderKernel
    boundary: EndpointCurvatureGraphLiftBoundary
    p_alg: Matrix
    p_end: Matrix
    raw_cyclic_seed: Matrix
    endpoint_to_algebraic: Matrix
    algebraic_to_endpoint: Matrix
    relative_witness: Matrix
    saddle_operator: SmallMatrix
    saddle_green: SmallMatrix

    @staticmethod
    def build() -> "EndpointRelativeSaddleFeasibility":
        mapping = cmc.CurvatureMappingCylinderKernel.build()
        boundary = EndpointCurvatureGraphLiftBoundary.build()
        p_end = cmc._multiply(mapping.inclusion, mapping.projection)
        p_alg = cmc._add(cmc._identity(), cmc._scale(p_end, -1))

        seed = cmc._zero()
        # The second entry is the unique sign compatible with the odd
        # incidence pairing used by the mapping cylinder.
        seed[4][2] = OperatorPolynomial.atom("AF")
        seed[1][12] = OperatorPolynomial.atom("AFsharp")

        endpoint_to_algebraic = cmc._multiply(
            cmc._multiply(p_alg, seed), p_end
        )
        algebraic_to_endpoint = cmc._multiply(
            cmc._multiply(p_end, seed), p_alg
        )
        witness = cmc._add(endpoint_to_algebraic, algebraic_to_endpoint)

        one = OperatorPolynomial.identity()
        b = OperatorPolynomial.atom("Brel")
        c = OperatorPolynomial.atom("Crel")
        s = OperatorPolynomial.atom("S")
        g = OperatorPolynomial.atom("G")
        d = s + c * b
        saddle = [[one, b], [c, d]]
        green = [
            [one + b * g * c, (b * g).scale(-1)],
            [(g * c).scale(-1), g],
        ]

        result = EndpointRelativeSaddleFeasibility(
            mapping=mapping,
            boundary=boundary,
            p_alg=p_alg,
            p_end=p_end,
            raw_cyclic_seed=seed,
            endpoint_to_algebraic=endpoint_to_algebraic,
            algebraic_to_endpoint=algebraic_to_endpoint,
            relative_witness=witness,
            saddle_operator=saddle,
            saddle_green=green,
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.mapping.verify()
        # EndpointCurvatureGraphLiftBoundary.build() already performs its
        # comparatively expensive all-stratum exact rank audit.  Do not
        # repeat that audit in each downstream certificate pass.
        if self.boundary.evolution_attachment.rank() != 5:
            raise AssertionError("A_F rank drifted")
        if not cmc._is_zero(cmc._multiply(self.p_alg, self.p_end)):
            raise AssertionError("hybrid projectors overlap")

        zero = OperatorPolynomial.zero()
        if self.endpoint_to_algebraic[4][2] != OperatorPolynomial.atom("AF"):
            raise AssertionError("the rank-five Ebar-to-X_U incidence was lost")
        if any(
            self.endpoint_to_algebraic[row][column] != zero
            and row not in (4,)
            for row in range(cmc.SIZE)
            for column in range(cmc.SIZE)
        ):
            raise AssertionError("endpoint-to-algebraic lift left X_U")
        if not cmc._is_zero(
            cmc._add(
                cmc._multiply(
                    cmc._multiply(self.p_alg, self.relative_witness), self.p_alg
                ),
                cmc._zero(),
            )
        ):
            raise AssertionError("relative witness acquired an algebraic diagonal")
        if not cmc._is_zero(
            cmc._multiply(cmc._multiply(self.p_end, self.relative_witness), self.p_end)
        ):
            raise AssertionError("relative witness acquired an endpoint diagonal")
        if not cmc._is_zero(
            _cyclic_defect(self.relative_witness, self.mapping.pairing)
        ):
            raise AssertionError("the two-way relative witness is not odd cyclic")

        if not _small_identity_after_reduction(
            _small_multiply(self.saddle_operator, self.saddle_green)
        ):
            raise AssertionError("conditional Schur formula has no right inverse")
        if not _small_identity_after_reduction(
            _small_multiply(self.saddle_green, self.saddle_operator)
        ):
            raise AssertionError("conditional Schur formula has no left inverse")

    def certificate(
        self,
        *,
        hybrid_certificate: Mapping[str, object],
        boundary_certificate: Mapping[str, object],
        mapping_certificate: Mapping[str, object],
        curvature_witness_certificate: Mapping[str, object],
        green_bridge_certificate: Mapping[str, object],
    ) -> dict[str, object]:
        self.verify()
        if hybrid_certificate.get("schema") != (
            "pure-weyl-prolonged-hybrid-algebraic-projector-v1"
        ):
            raise AssertionError("wrong hybrid projector input")
        composite = hybrid_certificate.get("composite_SDR")
        if not isinstance(composite, Mapping) or not all(
            (
                composite.get("P_alg_idempotent") is True,
                composite.get("P_end_idempotent") is True,
                composite.get("D_P_end_equals_P_end_D") is True,
                composite.get("cyclic_and_formally_self_adjoint") is True,
            )
        ):
            raise AssertionError("hybrid projectors are unavailable")
        if boundary_certificate.get("schema") != (
            "pure-weyl-endpoint-curvature-graph-lift-boundary-v1"
        ):
            raise AssertionError("wrong endpoint lift boundary input")
        obstruction = boundary_certificate.get(
            "canonical_middle_graph_lift_obstruction"
        )
        if not isinstance(obstruction, Mapping) or not all(
            (
                obstruction.get("rank_A_F") == 5,
                obstruction.get("canonical_p_F_graph_lift_exists") is False,
                obstruction.get("polynomial_symbol_identity") is True,
            )
        ):
            raise AssertionError("canonical middle graph-lift boundary drifted")
        if mapping_certificate.get("schema") != (
            "pure-weyl-curvature-mapping-cylinder-substitution-v1"
        ) or mapping_certificate.get("coefficientwise_complete_prolonged_Q") is not True:
            raise AssertionError("expanded mapping cylinder is unavailable")
        if curvature_witness_certificate.get("schema") != (
            "pure-weyl-cotton-block-green-witness-v1"
        ) or curvature_witness_certificate.get("prolonged_green_witness") is not False:
            raise AssertionError("wrong curvature witness boundary")
        if green_bridge_certificate.get("schema") != (
            "pure-weyl-prolonged-green-bridge-v1"
        ) or green_bridge_certificate.get("prolonged_green_witness") is not False:
            raise AssertionError("wrong Green bridge boundary")

        return {
            "schema": "pure-weyl-endpoint-relative-saddle-feasibility-v1",
            "dependency_tag": "LORENTZIAN-CAUSAL",
            "input_certificate_sha256": {
                "hybrid_projector": _certificate_digest(hybrid_certificate),
                "endpoint_graph_lift_boundary": _certificate_digest(
                    boundary_certificate
                ),
                "mapping_cylinder": _certificate_digest(mapping_certificate),
                "weyl_cotton_witness": _certificate_digest(
                    curvature_witness_certificate
                ),
                "green_bridge": _certificate_digest(green_bridge_certificate),
            },
            "rank_five_relative_incidence": {
                "map": "A_F p_E:Ebar_aux[24]->X_U,relative[26]",
                "rank": self.boundary.evolution_attachment.rank(),
                "typed_atom_convention": "AF denotes A_F p_E",
                "rank_reason": "p_E i_E=1 and rank(A_F)=5",
                "A_F_support": "A_STF[5] state rows",
                "projected_component": (
                    "the X_U<-Ebar component of P_alg w P_end is A_F p_E; "
                    "the full map also contains the forced graph-cotangent term"
                ),
                "finite_order_after_projection": 3,
                "support_local": True,
                "inverse_Weyl_or_spatial_projector_used": False,
            },
            "cyclic_two_way_witness": {
                "formula": (
                    "W_AF=P_alg w P_end+P_end w P_alg, "
                    "w=(A_F,A_F^sharp)"
                ),
                "odd_cyclicity_defect": 0,
                "algebraic_diagonal": "zero",
                "endpoint_diagonal": "zero",
                "endpoint_to_algebraic_entries": [
                    list(entry) for entry in _nonzero_entries(
                        self.endpoint_to_algebraic
                    )
                ],
                "algebraic_to_endpoint_entries": [
                    list(entry) for entry in _nonzero_entries(
                        self.algebraic_to_endpoint
                    )
                ],
                "consequence": (
                    "the canonical graph-internal lift no-go does not extend "
                    "to the two-way relative incidence"
                ),
            },
            "conditional_saddle_green_formula": {
                "W_total": "H_alg+W_AF+W_0",
                "L_total": "[[1,B],[C,D]]",
                "B": "Q_alg U+U Q_end",
                "C": "Q_end V+V Q_alg",
                "Schur_endpoint": "S_end=D-CB",
                "inverse": (
                    "[[1+B G_S C,-B G_S],[-G_S C,G_S]]"
                ),
                "left_inverse_mod_G_S_S_end_equals_1": True,
                "right_inverse_mod_S_end_G_S_equals_1": True,
                "causal_support_if_G_S_is_causal": True,
            },
            "minimum_missing_operator": {
                "object": "an endpoint-diagonal W_0",
                "required_identity": (
                    "S_end=(Q_end W_0+W_0 Q_end)-CB is a finite filtered "
                    "extension of L_26, S_14, ghost waves and the physical biwave"
                ),
                "required_source_theorem": (
                    "for every compact endpoint source, both same-sided Schur "
                    "solutions satisfy the curvature-graph and sourced-subsidiary rows"
                ),
                "required_adjoint_theorem": (
                    "G_S,+^sharp equals the graded G_S,- and the block Schur "
                    "inverse obeys the prolonged BV adjoint convention"
                ),
                "currently_certified": False,
            },
            "decision": {
                "A_F_obstruction_couples_through_relative_cone": True,
                "two_way_saddle_incidence_feasible": True,
                "Schur_endpoint_green_hyperbolic": False,
                "arbitrary_compact_sources_solved": False,
                "two_sided_Green_operators_constructed": False,
                "graded_adjoint_Green_identity": False,
                "prolonged_green_witness": False,
                "curvature_causal_green_operators": False,
                "causal_green_homotopy": False,
            },
            "warranted_atomic_flags": [
                "endpoint_relative_rank5_incidence_exact",
                "endpoint_relative_cyclic_saddle_feasible",
            ],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
