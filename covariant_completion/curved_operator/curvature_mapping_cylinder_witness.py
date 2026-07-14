"""Coefficientwise witness audit for the canonical curvature cylinder.

The corrected sixteen-block mapping cylinder has an exact odd BV
differential ``Q_prol=S Q_split S^{-1}``.  There is a canonical first witness
to test: put the existing four-row auxiliary witness on the retained rows and
the Weyl--Cotton compatibility witness on both copies of the curvature cone,
with the Koszul-forced cotangent signs, then conjugate it by the same local
canonical shear ``S``.

This module constructs that degree-minus-one operator exactly and proves

``P_prol=Q_prol W_prol+W_prol Q_prol
        =S P_split S^{-1}``.

In split coordinates ``P_split`` is literally diagonal in all sixteen
blocks.  Twelve curvature/cotangent blocks are the certified ``L_26``,
``S_14`` and middle ``L_26+S_14`` blocks; the two ghost endpoints are the
certified gauge wave block.  The remaining two diagonal entries are both the
old action-normalized auxiliary field completion ``Eaux+K C``.  Its scalar
wave realization is ruled out by the exact null-rank theorem and no separate
Green-hyperbolicity theorem exists for it.  Thus the canonical conjugated
witness is a rigorous coefficientwise candidate, but not the final Green
witness.  Since ``Q_split`` is block diagonal, relative off-diagonal entries
of ``W`` cannot change either diagonal anticommutator block.  A successful
construction must therefore either replace the auxiliary diagonal witness
itself, or produce a genuinely non-triangular two-way saddle system and prove
that coupled system Green hyperbolic by a separate argument.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Mapping

from covariant_completion.curved_retract.curvature_mapping_cylinder_kernel import (
    BLOCK_DEGREES,
    BLOCK_NAMES,
    CurvatureMappingCylinderKernel,
    Matrix,
    SIZE,
    _add,
    _identity,
    _multiply,
    _scale,
    _zero,
)
from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)


def _digest(matrix: Matrix) -> str:
    payload = "\n".join(
        ",".join(entry.display() for entry in row) for row in matrix
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _matrix_equal(left: Matrix, right: Matrix) -> bool:
    return all(
        left[row][column] == right[row][column]
        for row in range(SIZE)
        for column in range(SIZE)
    )


def _nested(mapping: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = mapping.get(key)
    if not isinstance(value, Mapping):
        raise AssertionError(f"missing mapping {key}")
    return value


def _split_witness() -> Matrix:
    """Return the degree-minus-one auxiliary plus doubled-curvature witness."""

    w = _zero()

    # Existing action-normalized auxiliary witness.
    w[0][1] = OperatorPolynomial.atom("C")
    w[1][2] = OperatorPolynomial.identity()
    w[2][3] = OperatorPolynomial.atom("K")

    # Primal X curvature complex and the shifted Y copy.  Since Q_Y=-Q_X,
    # the Y witness also changes sign; this cancels the cone identity blocks.
    w[4][5] = OperatorPolynomial.atom("pF")
    w[5][6] = OperatorPolynomial.atom("iC")
    w[7][8] = OperatorPolynomial.atom("pF", -1)
    w[8][9] = OperatorPolynomial.atom("iC", -1)

    # Corrected odd-cotangent signs.  X# carries +D# and Y# carries -D#.
    w[11][12] = OperatorPolynomial.atom("pFsharp")
    w[10][11] = OperatorPolynomial.atom("iCsharp")
    w[14][15] = OperatorPolynomial.atom("pFsharp", -1)
    w[13][14] = OperatorPolynomial.atom("iCsharp", -1)
    return w


def _expected_diagonal() -> tuple[OperatorPolynomial, ...]:
    atom = OperatorPolynomial.atom
    return (
        atom("C") * atom("K"),
        atom("Eaux") + atom("K") * atom("C"),
        atom("Eaux") + atom("K") * atom("C"),
        atom("C") * atom("K"),
        atom("pF") * atom("Ecurv"),
        atom("Ecurv") * atom("pF") + atom("iC") * atom("Ncurv"),
        atom("Ncurv") * atom("iC"),
        atom("pF") * atom("Ecurv"),
        atom("Ecurv") * atom("pF") + atom("iC") * atom("Ncurv"),
        atom("Ncurv") * atom("iC"),
        atom("iCsharp") * atom("NcurvSharp"),
        atom("NcurvSharp") * atom("iCsharp")
        + atom("pFsharp") * atom("EcurvSharp"),
        atom("EcurvSharp") * atom("pFsharp"),
        atom("iCsharp") * atom("NcurvSharp"),
        atom("NcurvSharp") * atom("iCsharp")
        + atom("pFsharp") * atom("EcurvSharp"),
        atom("EcurvSharp") * atom("pFsharp"),
    )


@dataclass(frozen=True)
class CurvatureMappingCylinderWitness:
    """Exact candidate witness and its unavoidable residual analytic block."""

    kernel: CurvatureMappingCylinderKernel
    split_witness: Matrix
    prolonged_witness: Matrix
    split_witness_operator: Matrix
    prolonged_witness_operator: Matrix

    @staticmethod
    def build() -> "CurvatureMappingCylinderWitness":
        kernel = CurvatureMappingCylinderKernel.build()
        split_witness = _split_witness()
        prolonged_witness = _multiply(
            _multiply(kernel.new_to_old, split_witness), kernel.old_to_new
        )
        split_p = _add(
            _multiply(kernel.split_differential, split_witness),
            _multiply(split_witness, kernel.split_differential),
        )
        prolonged_p = _add(
            _multiply(kernel.prolonged_differential, prolonged_witness),
            _multiply(prolonged_witness, kernel.prolonged_differential),
        )
        result = CurvatureMappingCylinderWitness(
            kernel=kernel,
            split_witness=split_witness,
            prolonged_witness=prolonged_witness,
            split_witness_operator=split_p,
            prolonged_witness_operator=prolonged_p,
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.kernel.verify()
        for row in range(SIZE):
            for column in range(SIZE):
                if self.split_witness[row][column] != OperatorPolynomial.zero():
                    if BLOCK_DEGREES[row] != BLOCK_DEGREES[column] - 1:
                        raise AssertionError("split W does not have degree minus one")
                if self.prolonged_witness[row][column] != OperatorPolynomial.zero():
                    if BLOCK_DEGREES[row] != BLOCK_DEGREES[column] - 1:
                        raise AssertionError("prolonged W does not have degree minus one")

        # The split cone must have no residual X--Y mixing.
        diagonal = _zero()
        for index, entry in enumerate(_expected_diagonal()):
            diagonal[index][index] = entry
        if not _matrix_equal(self.split_witness_operator, diagonal):
            raise AssertionError("split witness operator is not the expected diagonal")

        conjugated_p = _multiply(
            _multiply(self.kernel.new_to_old, self.split_witness_operator),
            self.kernel.old_to_new,
        )
        if not _matrix_equal(self.prolonged_witness_operator, conjugated_p):
            raise AssertionError("P_prol does not conjugate from P_split")

        direct_identity = _add(
            _add(
                self.prolonged_witness_operator,
                _scale(
                    _multiply(
                        self.kernel.prolonged_differential,
                        self.prolonged_witness,
                    ),
                    -1,
                ),
            ),
            _scale(
                _multiply(
                    self.prolonged_witness,
                    self.kernel.prolonged_differential,
                ),
                -1,
            ),
        )
        if not _matrix_equal(direct_identity, _zero()):
            raise AssertionError("P_prol=QW+WQ failed")

        identity = _identity()
        if not _matrix_equal(
            _multiply(self.kernel.new_to_old, self.kernel.old_to_new), identity
        ):
            raise AssertionError("support-local diagonalization has no inverse")

    def certificate(
        self,
        *,
        substitution_certificate: Mapping[str, object],
        curvature_witness_certificate: Mapping[str, object],
        auxiliary_witness_certificate: Mapping[str, object],
        scalar_no_go_certificate: Mapping[str, object],
    ) -> dict[str, object]:
        self.verify()
        if substitution_certificate.get("schema") != (
            "pure-weyl-curvature-mapping-cylinder-substitution-v1"
        ) or not substitution_certificate.get("coefficientwise_complete_prolonged_Q"):
            raise AssertionError("coefficientwise Q substitution is unavailable")
        if curvature_witness_certificate.get("schema") != (
            "pure-weyl-cotton-block-green-witness-v1"
        ):
            raise AssertionError("wrong curvature witness input")
        if not _nested(curvature_witness_certificate, "exact_block_identities").get(
            "P_equals_QW_plus_WQ"
        ):
            raise AssertionError("curvature compatibility witness regressed")
        if auxiliary_witness_certificate.get("schema") != (
            "pure-weyl-curved-four-row-operator-kernel-v1"
        ) or auxiliary_witness_certificate.get("QW_plus_WQ_minus_P") != "zero":
            raise AssertionError("auxiliary four-row witness regressed")
        if scalar_no_go_certificate.get("schema") != (
            "pure-weyl-curved-null-symbol-rank-obstruction-v1"
        ):
            raise AssertionError("wrong scalar-wave no-go input")
        if not scalar_no_go_certificate.get("curved_scalar_wave_no_go"):
            raise AssertionError("the field-block no-go theorem is unavailable")

        nonzero_w = sum(
            entry != OperatorPolynomial.zero()
            for row in self.prolonged_witness
            for entry in row
        )
        return {
            "schema": "pure-weyl-curvature-mapping-cylinder-witness-v1",
            "construction": {
                "formula": "W_prol=S (W_aux direct_sum W_cone) S^-1",
                "degree": -1,
                "coefficientwise_16_block_Q_input": True,
                "coefficientwise_W_nonzero_blocks": nonzero_w,
                "finite_differential_operators_only": True,
                "support_local": True,
                "curvature_backward_maps": {
                    "Eq_to_U": "pF, projection onto the 26 evolution rows",
                    "Id_to_Eq": "iC, inclusion into the 14 constraint rows",
                    "orders": 0,
                },
                "cotangent_signs_from_corrected_odd_pairing": True,
            },
            "exact_identities": {
                "W_has_degree_minus_one": True,
                "P_prol_equals_QW_plus_WQ": True,
                "P_prol_equals_S_Psplit_Sinverse": True,
                "support_local_diagonalization_inverse_exact": True,
                "split_off_diagonal_blocks": 0,
            },
            "split_diagonal_ledger": [
                {
                    "block": BLOCK_NAMES[index],
                    "operator": entry.display(),
                    "green_status": (
                        "open auxiliary field block"
                        if index in (1, 2)
                        else "certified curvature/gauge block"
                    ),
                }
                for index, entry in enumerate(_expected_diagonal())
            ],
            "certified_green_diagonal_blocks": 14,
            "open_green_diagonal_blocks": 2,
            "open_block": {
                "indices": [1, 2],
                "operator": "Eaux+K C and its cotangent copy",
                "scalar_normally_hyperbolic_realization": False,
                "basis_independent_null_rank_no_go": True,
                "general_mixed_order_green_hyperbolicity_proved": False,
                "consequence": (
                    "the canonical conjugate of the direct-sum witnesses does "
                    "not close the prolonged Green theorem"
                ),
            },
            "design_constraint_for_next_witness": {
                "block_diagonal_Q_implies_offdiagonal_W_cannot_change_diagonal_P": True,
                "successful_options": [
                    "replace the auxiliary diagonal witness so its field block is independently Green hyperbolic",
                    "add two-way relative blocks producing a non-triangular saddle operator and prove that coupled operator Green hyperbolic",
                ],
                "lower_triangular_relative_terms_alone_suffice": False,
                "mere_conjugation_of_direct_sum_witnesses_suffices": False,
                "curvature_must_carry_physical_helicity_two": True,
            },
            "matrix_sha256": {
                "W_split": _digest(self.split_witness),
                "W_prol": _digest(self.prolonged_witness),
                "P_split": _digest(self.split_witness_operator),
                "P_prol": _digest(self.prolonged_witness_operator),
            },
            "coefficientwise_candidate_W_prol": True,
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
