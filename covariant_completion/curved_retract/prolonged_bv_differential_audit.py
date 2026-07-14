"""Exact autonomous curvature equation complex and BV-attachment audit.

The certified rank-26 curvature evolution ``L``, rank-14 constraint operator
``K``, subsidiary evolution ``S`` and source-compatibility operator ``R``
satisfy the natural-operator identity

``S K-R L=0``.

Hence they define the three-term equation complex

``U[26] --(L,K)--> Eq[26+14] --(-R,S)--> Id[14]``.

This module adds its formal cotangent-adjoint complex and checks nilpotency
in exact noncommutative block algebra.  It then audits whether that complex
can already be attached to the support-local Weyl/Cotton graph SDR.

It cannot yet: the autonomous curvature complex carries the nonzero E/A/L
solution module, so adjoining it as a direct summand duplicates physical
cohomology.  A mapping-cylinder attachment needs explicit chain-map
components on equation and identity rows.  Existing certificates provide
the state map ``T=(C1,div C1)`` and differential-ideal equivalence, but not
the coefficient operators ``A`` and ``B`` in

``(L,K) T=A E_aux`` and ``(-R,S) A=B C_aux``.

Moreover the adjusted forty-row presentation exceeds the pointwise
covariant row module by the six ``a,c`` rows; those rows are generated only
differentially.  Thus ``A`` cannot be manufactured by a pointwise row
selection.  No project flag is promoted here.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
from typing import Mapping

from covariant_completion.curved_operator.weyl_cotton_differential_ideal import (
    WeylCottonDifferentialIdealAudit,
)
from covariant_completion.curved_operator.weyl_cotton_hyperbolic import (
    CONSTRAINT_DIMENSION,
    EVOLUTION_DIMENSION,
    ConstraintAdjustedWeylCottonEvolution,
)
from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)


Matrix = list[list[OperatorPolynomial]]


def _zero(size: int) -> Matrix:
    return [
        [OperatorPolynomial.zero() for _ in range(size)] for _ in range(size)
    ]


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    size = len(left)
    output = _zero(size)
    for row in range(size):
        for column in range(size):
            value = OperatorPolynomial.zero()
            for middle in range(size):
                value = value + left[row][middle] * right[middle][column]
            output[row][column] = value
    return output


def _reduce(entry: OperatorPolynomial) -> OperatorPolynomial:
    relations = {("N", "E"), ("Esharp", "Nsharp")}
    values: dict[tuple[str, ...], Fraction] = {}
    for word, coefficient in entry.terms:
        if any(
            word[index : index + 2] in relations
            for index in range(max(0, len(word) - 1))
        ):
            continue
        values[word] = values.get(word, Fraction()) + coefficient
    return OperatorPolynomial._from_dict(values)


def _is_zero_mod_relations(matrix: Matrix) -> bool:
    zero = OperatorPolynomial.zero()
    return all(_reduce(entry) == zero for row in matrix for entry in row)


def _adjoint(entry: OperatorPolynomial) -> OperatorPolynomial:
    involution = {
        "E": "Esharp",
        "Esharp": "E",
        "N": "Nsharp",
        "Nsharp": "N",
    }
    return OperatorPolynomial._from_dict(
        {
            tuple(involution[atom] for atom in reversed(word)): coefficient
            for word, coefficient in entry.terms
        }
    )


def _matrix_adjoint(matrix: Matrix) -> Matrix:
    return [
        [_adjoint(matrix[column][row]) for column in range(len(matrix))]
        for row in range(len(matrix))
    ]


def _digest(matrix: Matrix) -> str:
    payload = "\n".join(
        ",".join(entry.display() for entry in row) for row in matrix
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class ProlongedBVDifferentialAudit:
    """Cotangent equation complex plus the exact graph-attachment blocker."""

    evolution: ConstraintAdjustedWeylCottonEvolution
    differential_ideal: WeylCottonDifferentialIdealAudit
    cotangent_differential: Matrix

    @staticmethod
    def build() -> "ProlongedBVDifferentialAudit":
        # Cotangent block order:
        #   Id^*[14], Eq^*[40], U^*[26], U[26], Eq[40], Id[14].
        # E=(L,K), N=(-R,S), and N E=0 is precisely SK-RL=0.
        q = _zero(6)
        q[1][0] = OperatorPolynomial.atom("Nsharp")
        q[2][1] = OperatorPolynomial.atom("Esharp")
        q[4][3] = OperatorPolynomial.atom("E")
        q[5][4] = OperatorPolynomial.atom("N")
        result = ProlongedBVDifferentialAudit(
            evolution=ConstraintAdjustedWeylCottonEvolution.build(),
            differential_ideal=WeylCottonDifferentialIdealAudit.build(),
            cotangent_differential=q,
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.evolution.verify()
        self.differential_ideal.verify()
        if EVOLUTION_DIMENSION != 26 or CONSTRAINT_DIMENSION != 14:
            raise AssertionError("curvature evolution/constraint ranks drifted")
        if (
            self.evolution.commuting_symbol_defect
            + self.evolution.sphere_curvature_correction
        ).applyfunc(lambda value: value.expand()) != self.evolution.commuting_symbol_defect.zeros(
            CONSTRAINT_DIMENSION, EVOLUTION_DIMENSION
        ):
            raise AssertionError("the curved sourced subsidiary identity failed")
        if not _is_zero_mod_relations(
            _multiply(self.cotangent_differential, self.cotangent_differential)
        ):
            raise AssertionError("the cotangent curvature equation complex is not nilpotent")

        # The two halves must be literal formal adjoints, not independently
        # normalized copies.
        if self.cotangent_differential[1][0] != _adjoint(
            self.cotangent_differential[5][4]
        ):
            raise AssertionError("the identity/equation arrow is not cotangent lifted")
        if self.cotangent_differential[2][1] != _adjoint(
            self.cotangent_differential[4][3]
        ):
            raise AssertionError("the equation/state arrow is not cotangent lifted")
        if _matrix_adjoint(_matrix_adjoint(self.cotangent_differential)) != (
            self.cotangent_differential
        ):
            raise AssertionError("formal adjunction is not involutive")
        pairing = _zero(6)
        for left, right in ((0, 5), (1, 4), (2, 3)):
            pairing[left][right] = OperatorPolynomial.identity()
            pairing[right][left] = OperatorPolynomial.identity()
        if _multiply(_matrix_adjoint(self.cotangent_differential), pairing) != (
            _multiply(pairing, self.cotangent_differential)
        ):
            raise AssertionError("the cotangent incidence pairing is inconsistent")

    def certificate(
        self,
        *,
        eal_certificate: Mapping[str, object],
        graph_certificate: Mapping[str, object],
        reverify: bool = True,
    ) -> dict[str, object]:
        if reverify:
            self.verify()
        if eal_certificate.get("schema") != (
            "pure-weyl-curvature-eal-spectrum-all-level-v1"
        ):
            raise AssertionError("wrong all-level curvature spectrum certificate")
        if not eal_certificate.get("EAL_curvature_spectrum_match"):
            raise AssertionError("nontrivial curvature solution module is uncertified")
        if graph_certificate.get("schema") != (
            "pure-weyl-support-local-curvature-graph-SDR-v1"
        ):
            raise AssertionError("wrong support-local curvature graph certificate")
        if not graph_certificate.get("support_local_curvature_graph_retract"):
            raise AssertionError("the state-level graph SDR is not certified")

        differential = self.differential_ideal
        return {
            "schema": "pure-weyl-prolonged-BV-differential-attachment-audit-v1",
            "autonomous_curvature_equation_complex": {
                "state": {"rank": 26, "order": "E,B,A,C,x,y"},
                "equations": {
                    "rank": 40,
                    "decomposition": "26 evolution plus 14 constraints",
                    "operator": "E_curv=(L,K)",
                },
                "identities": {
                    "rank": 14,
                    "operator": "N_curv=(-R,S)",
                    "identity": "N_curv E_curv=SK-RL=0",
                    "unit_S3_curvature_correction_included": True,
                },
                "Q_squared": "zero",
                "support_local": True,
            },
            "cotangent_completion": {
                "block_order": [
                    "identity_dual[14]",
                    "equation_dual[40]",
                    "state_dual[26]",
                    "state[26]",
                    "equation[40]",
                    "identity[14]",
                ],
                "total_rank": 160,
                "arrows": [
                    "N_curv^sharp",
                    "E_curv^sharp",
                    "zero central arrow",
                    "E_curv",
                    "N_curv",
                ],
                "all_arrows_are_formal_cotangent_adjoints": True,
                "formal_cotangent_incidence_pairing_preserved": True,
                "Q_squared": "zero",
                "matrix_sha256": _digest(self.cotangent_differential),
            },
            "unchanged_auxiliary_rows": {
                "minimal_auxiliary_BV_rank": 66,
                "ghost_rows": 9,
                "field_rows": 24,
                "equation_antifield_rows": 24,
                "identity_antifield_rows": 9,
                "trace_Weyl_and_nonminimal_rows": "unchanged direct summands",
                "direct_sum_total_before_reattached_summands": 226,
                "direct_sum_Q_squared": "zero",
                "direct_sum_P_I": "identity on the 66-row auxiliary summand",
            },
            "attachment_obstruction": {
                "direct_sum_is_support_local_prolongation_SDR": False,
                "reason": (
                    "the autonomous curvature complex has the nonzero all-level "
                    "E/A/L solution module, so forgetting it cannot satisfy "
                    "IP-1=QH+HQ"
                ),
                "nonzero_curvature_module_certified": True,
                "covariant_first_jet_row_rank": differential.exact_row_rank,
                "adjusted_first_jet_evolution_plus_constraint_rank": (
                    differential.adjusted_plus_constraints_rank
                ),
                "differential_only_row_excess": (
                    differential.pointwise_reverse_defect_rank
                ),
                "missing_rows": "a[3],c[3]",
                "pointwise_row_selection_suffices": False,
                "promoted_32_state_rank14_constraints_propagate": False,
                "promoted_constraint_propagation_defect_rank": (
                    differential.advertised_propagation_defect_rank
                ),
            },
            "required_mapping_cylinder_data": {
                "T_state": "(C1,div C1): auxiliary fields[24] -> U[26]",
                "gauge_relation": "T_state K_aux=0",
                "A_equation": (
                    "auxiliary equations[24] -> curvature equations[40]"
                ),
                "first_missing_chain_relation": (
                    "E_curv T_state=A_equation E_aux"
                ),
                "B_identity": (
                    "auxiliary identity-antifields[9] -> curvature identities[14]"
                ),
                "second_missing_chain_relation": (
                    "N_curv A_equation=B_identity C_aux"
                ),
                "cotangent_rows": "A_equation^sharp and B_identity^sharp",
                "coefficientwise_A_equation_emitted": False,
                "coefficientwise_B_identity_emitted": False,
                "all_row_mapping_cylinder_constructible_now": False,
            },
            "exact_results": {
                "autonomous_curvature_Q_squared": True,
                "cotangent_adjoint_Q_squared": True,
                "all_autonomous_curvature_rows_enumerated": True,
                "support_local_operator_complex": True,
                "base_direct_sum_P_I": True,
            },
            "support_orders": {
                "L_evolution": 1,
                "K_constraint": 1,
                "R_source_compatibility": 1,
                "S_subsidiary": 1,
                "formal_adjoints": 1,
                "nonlocal_inverse_or_projector": False,
            },
            "unproved_results": {
                "complete_attachment_chain_map": False,
                "complete_IP_minus_identity_equals_QH_plus_HQ": False,
                "support_local_prolongation_retract": False,
                "prolonged_BV_operator_identity": False,
            },
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "precise_next_step": (
                "emit A_equation and B_identity as exact local differential "
                "operators, including the six differential a/c generators, then "
                "apply the mapping-cylinder cotangent kernel"
            ),
            "fail_closed": True,
        }
