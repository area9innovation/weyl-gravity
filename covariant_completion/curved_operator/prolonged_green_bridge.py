"""Fail-closed Green bridge for the curvature mapping cylinder.

This module isolates the part of the prolonged Green construction which is
pure block algebra.  A finite lower-triangular operator with Green-hyperbolic
diagonal blocks has exact retarded/advanced inverses obtained by finite
forward substitution.  If that operator is ``P=QW+WQ``, the usual identities
then give ``QG=GQ`` and ``Q(WG)+(WG)Q=1``.

The theorem is useful for the curvature prolongation because all proposed
diagonal analytic blocks are already certified: the rank-26 Weyl--Cotton
evolution, its rank-14 subsidiary system, wave gauge blocks, formal-adjoint
copies, and pointwise contractible blocks.  What is *not* supplied here is a
coefficientwise degree-minus-one ``W_prol`` whose anticommutator with the
sixteen-block mapping-cylinder differential triangularizes to those blocks.
The certificate therefore records the exact remaining input and promotes no
project flag.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
from typing import Mapping

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)


Matrix = list[list[OperatorPolynomial]]


def _zero(size: int) -> Matrix:
    return [
        [OperatorPolynomial.zero() for _ in range(size)]
        for _ in range(size)
    ]


def _identity(size: int) -> Matrix:
    result = _zero(size)
    for index in range(size):
        result[index][index] = OperatorPolynomial.identity()
    return result


def _add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            left[row][column] + right[row][column]
            for column in range(len(left))
        ]
        for row in range(len(left))
    ]


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    size = len(left)
    result = _zero(size)
    for row in range(size):
        for column in range(size):
            value = OperatorPolynomial.zero()
            for middle in range(size):
                value = value + left[row][middle] * right[middle][column]
            result[row][column] = value
    return result


def _reduce_green_word(
    word: tuple[str, ...], coefficient: Fraction
) -> tuple[tuple[str, ...], Fraction]:
    """Cancel the exact two-sided diagonal Green relations."""

    reduced = word
    changed = True
    while changed:
        changed = False
        for index in range(max(0, len(reduced) - 1)):
            left, right = reduced[index : index + 2]
            if (
                left.startswith("D")
                and right == "G" + left[1:]
            ) or (
                left.startswith("G")
                and right == "D" + left[1:]
            ):
                reduced = reduced[:index] + reduced[index + 2 :]
                changed = True
                break
    return reduced, coefficient


def _reduce_green(entry: OperatorPolynomial) -> OperatorPolynomial:
    values: dict[tuple[str, ...], Fraction] = {}
    for word, coefficient in entry.terms:
        reduced, coefficient = _reduce_green_word(word, coefficient)
        values[reduced] = values.get(reduced, Fraction()) + coefficient
    return OperatorPolynomial._from_dict(values)


def _is_identity_mod_green(matrix: Matrix) -> bool:
    identity = _identity(len(matrix))
    zero = OperatorPolynomial.zero()
    defect = _add(matrix, [[entry.scale(-1) for entry in row] for row in identity])
    return all(_reduce_green(entry) == zero for row in defect for entry in row)


def _digest(matrix: Matrix) -> str:
    payload = "\n".join(
        ",".join(entry.display() for entry in row) for row in matrix
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _lower_triangular_operator(size: int) -> Matrix:
    result = _zero(size)
    for row in range(size):
        result[row][row] = OperatorPolynomial.atom(f"D{row}")
        for column in range(row):
            result[row][column] = OperatorPolynomial.atom(f"A{row}_{column}")
    return result


def _forward_green(operator: Matrix) -> Matrix:
    """Finite retarded/advanced inverse, with the sign common to both."""

    size = len(operator)
    result = _zero(size)
    for row in range(size):
        result[row][row] = OperatorPolynomial.atom(f"G{row}")
        for column in range(row):
            correction = OperatorPolynomial.zero()
            for middle in range(column, row):
                correction = (
                    correction
                    + operator[row][middle] * result[middle][column]
                )
            result[row][column] = (
                OperatorPolynomial.atom(f"G{row}") * correction
            ).scale(-1)
    return result


def _nested(mapping: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = mapping.get(key)
    if not isinstance(value, Mapping):
        raise AssertionError(f"missing mapping {key}")
    return value


@dataclass(frozen=True)
class ProlongedGreenBridge:
    """Exact triangular inverse theorem plus repository dependency audit."""

    mapping_substitution: Mapping[str, object]
    curvature_witness: Mapping[str, object]
    causal_pde: Mapping[str, object]
    recognition: Mapping[str, object]
    triangular_size: int = 8

    def triangular_matrices(self) -> tuple[Matrix, Matrix]:
        operator = _lower_triangular_operator(self.triangular_size)
        return operator, _forward_green(operator)

    def verify(self) -> None:
        substitution = self.mapping_substitution
        if substitution.get("schema") != (
            "pure-weyl-curvature-mapping-cylinder-substitution-v1"
        ):
            raise AssertionError("wrong mapping-cylinder substitution certificate")
        if not substitution.get("coefficientwise_complete_prolonged_Q"):
            raise AssertionError("the prolonged Q substitution is incomplete")
        kernel = _nested(substitution, "kernel")
        if not (
            kernel.get("Q_squared") == "zero"
            and kernel.get("BV_pairing_defect") == 0
            and kernel.get("I_P_minus_identity") == "QH+HQ"
        ):
            raise AssertionError("mapping-cylinder BV identities regressed")

        witness = self.curvature_witness
        if witness.get("schema") != "pure-weyl-cotton-block-green-witness-v1":
            raise AssertionError("wrong curvature block-witness certificate")
        identities = _nested(witness, "exact_block_identities")
        if not (
            identities.get("P_equals_QW_plus_WQ") is True
            and identities.get("Q_P_equals_P_Q") is True
        ):
            raise AssertionError("curvature block witness identity regressed")
        if not _nested(witness, "canonical_source_identification").get(
            "K_and_R_coefficient_tables_equal"
        ):
            raise AssertionError("the L/S diagonalization has an open K-R block")

        causal = self.causal_pde
        if causal.get("schema") != "pure-weyl-cotton-causal-pde-v1":
            raise AssertionError("wrong causal curvature certificate")
        if not causal.get("curvature_block_causal_solution_operators"):
            raise AssertionError("curvature causal solution theorem regressed")
        if not _nested(causal, "unconstrained_green_operators").get(
            "exists_for_every_compact_source"
        ):
            raise AssertionError("rank-26 two-sided Green operators are unavailable")
        if not _nested(causal, "compatible_source_restriction").get("unique"):
            raise AssertionError("constraint-compatible uniqueness is unavailable")

        recognition = self.recognition
        if recognition.get("schema") != "pure-weyl-green-witness-recognition-v1":
            raise AssertionError("wrong Green recognition theorem")
        if _nested(recognition, "green_homotopies").get("identity") != (
            "Q Lambda_plus/minus+Lambda_plus/minus Q=1"
        ):
            raise AssertionError("Green homotopy recognition identity drifted")

        if self.triangular_size < 2:
            raise AssertionError("the triangular theorem was not tested nontrivially")
        operator, green = self.triangular_matrices()
        if not _is_identity_mod_green(_multiply(operator, green)):
            raise AssertionError("right triangular Green inverse failed")
        if not _is_identity_mod_green(_multiply(green, operator)):
            raise AssertionError("left triangular Green inverse failed")

    def certificate(self) -> dict[str, object]:
        self.verify()
        operator, green = self.triangular_matrices()
        return {
            "schema": "pure-weyl-prolonged-green-bridge-v1",
            "exact_inputs": {
                "coefficientwise_16_block_Q": True,
                "Q_prol_squared": "zero",
                "BV_canonical_mapping_cylinder": True,
                "support_local_mapping_cylinder_SDR": True,
                "curvature_kernel_QW_plus_WQ": True,
                "curvature_kernel_QP_equals_PQ": True,
                "rank26_symmetric_hyperbolic_green_operators": True,
                "rank14_subsidiary_symmetric_hyperbolicity": True,
                "compatible_sources_land_in_constraint_kernel": True,
            },
            "finite_triangular_green_theorem": {
                "tested_block_count": self.triangular_size,
                "operator": "P_ii=D_i, P_ij=A_ij for i>j",
                "diagonal_relations": "D_i G_i^+/-=G_i^+/- D_i=1",
                "recursion": (
                    "G_ii=G_i; G_ij=-G_i sum_{k=j}^{i-1} P_ik G_kj"
                ),
                "left_inverse_defect": 0,
                "right_inverse_defect": 0,
                "finite_no_Neumann_convergence_assumption": True,
                "retarded_support_preserved": True,
                "advanced_support_preserved": True,
                "same_sided_extension_domain": (
                    "retarded diagonal Green operators are used on past-compact "
                    "intermediate sources and advanced ones on future-compact "
                    "intermediate sources; the standard unique extensions of "
                    "Green-hyperbolic operators are understood"
                ),
                "support_reason": (
                    "finite compositions of differential blocks and same-sided "
                    "causal Green operators remain inside J^+ or J^-; global "
                    "hyperbolicity gives J^+(J^+(K))=J^+(K) and likewise in "
                    "the advanced direction"
                ),
                "matrix_sha256": {
                    "generic_P": _digest(operator),
                    "generic_G": _digest(green),
                },
            },
            "recognition_after_full_witness": {
                "chain_commutation": "QG^+/-=G^+/-Q",
                "derivation": "QG=GPQG=GQPG=GQ",
                "definition": "Lambda^+/-=W_prol G^+/-",
                "homotopy": "Q Lambda^+/-+Lambda^+/- Q=1",
                "causal_support": True,
                "purely_formal_step_complete": True,
            },
            "target_diagonal_ledger": [
                "gauge/ghost wave blocks and formal adjoints",
                "Weyl-Cotton L_26 and its formal adjoint",
                "subsidiary S_14 and its formal adjoint",
                "generalized-auxiliary pointwise blocks",
                "trace/Weyl and nonminimal pointwise doublets",
                "mapping-cylinder contractible identity blocks",
            ],
            "single_missing_constructive_certificate": {
                "name": "coefficientwise prolonged Green witness",
                "required_data": [
                    "a degree-minus-one finite differential W_prol on all 16 mapping-cylinder blocks and retained direct summands",
                    "the exact equality P_prol=Q_prol W_prol+W_prol Q_prol",
                    "a support-local triangular transformation of every degree of P_prol to the target diagonal ledger",
                    "the formal-adjoint/cotangent blocks with the project fibre pairings",
                ],
                "why_existing_kernel_witness_is_insufficient": (
                    "it acts on the autonomous curvature compatibility kernel, "
                    "not on every block of the canonically attached 16-block BV cylinder"
                ),
                "analytic_gap_after_triangularization": False,
                "koszul_or_pairing_gap_before_triangularization": True,
            },
            "dependency_closure": {
                "if_full_W_and_triangularization_pass": [
                    "prolonged_green_witness",
                    "curvature_causal_green_operators",
                    "causal_green_homotopy",
                ],
                "reason": (
                    "the triangular inverse and Green-homotopy recognition steps "
                    "are exact and introduce no further coefficient calculation"
                ),
            },
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
