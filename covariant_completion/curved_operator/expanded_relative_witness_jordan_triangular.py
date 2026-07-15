"""Exact triangular Green algebra of the certified Jordan helicity block.

This is a deliberately small follow-up to
``expanded_relative_witness_jordan_homology``.  At an aligned covector put

``L=1-z^2``.

The fixed pair-(1,6), cyclic ``-2 Pi`` weighted witness has the closed block

``P_TT = [[L,0],[4,L]]``

on ``(h_23,f_23)``.  The support-local auxiliary shift is
``f=f_hat+L h``.  Including its forced cotangent transformation splits the
BV differential into the physical biwave block ``L^2`` and the pointwise
contractible block ``-1``.  The same field shift does *not* diagonalize the
witness block: it commutes with its nilpotent extension and leaves ``P_TT``
unchanged.

Nevertheless a triangular Green recursion exists algebraically.  If
``G_+`` or ``G_-`` is a two-sided Green inverse of ``L`` on the appropriate
one-sided support spaces, then

``[[G,0],[-4 G^2,G]]``

is the corresponding inverse of ``P_TT``.  It uses only the local coupling
``4`` and same-sign compositions of the wave Green operator; no inverse
curl, TT projector, or helicity projector occurs in the formula.

What is *not* proved here is equally important: the two-dimensional aligned
helicity subspace is selected by the covector.  This certificate does not
construct a support-local filtration of the complete 116-row operator or
its full BV witness.  It therefore supplies an exact design lemma for a
block-triangular construction, not a Green flag.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from .conventions import _ordinary_system
from .expanded_relative_witness_full_symbol import (
    COMPLETE_RANK,
    ExpandedRelativeFullSymbol,
)


H23 = 8
F23 = 18


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class ExpandedRelativeJordanTriangular:
    spectral_parameter: sp.Symbol
    wave_polynomial: sp.Expr
    original_bv_block: sp.Matrix
    field_shift: sp.Matrix
    dual_shift: sp.Matrix
    shifted_bv_block: sp.Matrix
    reordered_shifted_bv_block: sp.Matrix
    witness_block: sp.Matrix
    shifted_witness_block: sp.Matrix
    witness_column_leakage: int
    witness_row_leakage: int
    formal_green_block: sp.Matrix
    formal_left_defect: sp.Matrix
    formal_right_defect: sp.Matrix

    @staticmethod
    def build() -> "ExpandedRelativeJordanTriangular":
        z = sp.Symbol("jordan_triangular_z", real=True)
        wave = 1 - z**2
        substitution_values = (-z, sp.Integer(1), sp.Integer(0), sp.Integer(0))

        system = _ordinary_system()
        substitution = dict(
            zip(system.covector, substitution_values, strict=True)
        )
        full_bv = (
            system.field_fibre_pairing.inv()
            * system.gauge_invariant_flat_hessian
        ).subs(substitution)
        original_bv = full_bv.extract((H23, F23), (H23, F23))

        # New-to-old field change f=f_hat+L h and its action-pairing
        # cotangent lift.  The restricted action fibre form is the exchange
        # matrix, so U#=J^-1 U(-zeta)^(-T) J.
        field_shift = sp.Matrix([[1, 0], [wave, 1]])
        pairing = system.field_fibre_pairing.extract(
            (H23, F23), (H23, F23)
        )
        dual_shift = pairing.inv() * field_shift.inv().T * pairing
        shifted_bv = sp.simplify(
            dual_shift.inv() * original_bv * field_shift
        )
        equation_reorder = sp.Matrix([[0, 1], [1, 0]])
        reordered_bv = sp.simplify(equation_reorder * shifted_bv)

        expanded = ExpandedRelativeFullSymbol.build()
        complete_witness = expanded.symbol(
            substitution_values, separated=True
        )
        witness = complete_witness.extract((H23, F23), (H23, F23))
        selected = {H23, F23}
        column_leakage = sum(
            int(complete_witness[row, column] != 0)
            for column in selected
            for row in range(COMPLETE_RANK)
            if row not in selected
        )
        row_leakage = sum(
            int(complete_witness[row, column] != 0)
            for row in selected
            for column in range(COMPLETE_RANK)
            if column not in selected
        )
        shifted_witness = sp.simplify(field_shift.inv() * witness * field_shift)

        # Formal triangular inverse.  The symbol g stands for either G_+
        # or G_- and is reduced only by the two-sided identity Lg=gL=1.
        g = sp.Symbol("same_sign_wave_Green", commutative=True)
        formal_green = sp.Matrix([[g, 0], [-4 * g**2, g]])
        left = (witness * formal_green).applyfunc(
            lambda value: sp.expand(value).subs(wave * g, 1)
        )
        right = (formal_green * witness).applyfunc(
            lambda value: sp.expand(value).subs(wave * g, 1)
        )
        # SymPy may expand 1-z^2 before the substitution.  Reduce through a
        # temporary scalar generator to make the algebraic relation exact.
        ell = sp.Symbol("wave_operator_L", commutative=True)
        abstract_witness = sp.Matrix([[ell, 0], [4, ell]])
        abstract_green = sp.Matrix([[g, 0], [-4 * g**2, g]])
        left_defect = (abstract_witness * abstract_green - sp.eye(2)).applyfunc(
            lambda value: sp.expand(value).subs(ell * g, 1)
        )
        right_defect = (abstract_green * abstract_witness - sp.eye(2)).applyfunc(
            lambda value: sp.expand(value).subs(ell * g, 1)
        )

        result = ExpandedRelativeJordanTriangular(
            spectral_parameter=z,
            wave_polynomial=wave,
            original_bv_block=original_bv,
            field_shift=field_shift,
            dual_shift=dual_shift,
            shifted_bv_block=shifted_bv,
            reordered_shifted_bv_block=reordered_bv,
            witness_block=witness,
            shifted_witness_block=shifted_witness,
            witness_column_leakage=column_leakage,
            witness_row_leakage=row_leakage,
            formal_green_block=formal_green,
            formal_left_defect=left_defect,
            formal_right_defect=right_defect,
        )
        result.verify()
        return result

    def verify(self) -> None:
        wave = self.wave_polynomial
        if self.original_bv_block != sp.Matrix([[wave, -1], [0, wave]]):
            raise AssertionError("unshifted h23/f23 BV block drifted")
        if self.field_shift != sp.Matrix([[1, 0], [wave, 1]]):
            raise AssertionError("restricted auxiliary shift drifted")
        if self.dual_shift != sp.Matrix([[1, 0], [-wave, 1]]):
            raise AssertionError("restricted cotangent lift drifted")
        if sp.simplify(
            self.shifted_bv_block - sp.Matrix([[0, -1], [wave**2, 0]])
        ) != sp.zeros(2):
            raise AssertionError("shifted BV block did not split")
        if sp.simplify(
            self.reordered_shifted_bv_block - sp.diag(wave**2, -1)
        ) != sp.zeros(2):
            raise AssertionError("physical biwave/auxiliary split drifted")
        expected_witness = sp.Matrix([[wave, 0], [4, wave]])
        if sp.simplify(self.witness_block - expected_witness) != sp.zeros(2):
            raise AssertionError("aligned witness Jordan block drifted")
        if sp.simplify(self.shifted_witness_block - expected_witness) != sp.zeros(2):
            raise AssertionError("the field shift unexpectedly split the witness")
        if self.witness_column_leakage or self.witness_row_leakage:
            raise AssertionError("the aligned helicity block is not closed")
        if self.formal_left_defect != sp.zeros(2):
            raise AssertionError("formal triangular Green left inverse failed")
        if self.formal_right_defect != sp.zeros(2):
            raise AssertionError("formal triangular Green right inverse failed")

    def certificate(self) -> dict[str, object]:
        self.verify()
        wave = str(self.wave_polynomial)
        return {
            "schema": "pure-weyl-expanded-relative-jordan-triangular-v1",
            "scope": {
                "relative_branch": "fixed-temporal pair-(1,6)",
                "scalar_branch": "BV-cyclic D_alt=-2 Pi_(h00,f00,v0)",
                "aligned_covector": [f"-{self.spectral_parameter}", "1", "0", "0"],
                "helicity_basis": ["h23", "f23"],
                "full_116_support_local_filtration_certified": False,
            },
            "auxiliary_BV_shift": {
                "wave_polynomial_L": wave,
                "unshifted_QBV_block": [
                    [str(value) for value in row]
                    for row in self.original_bv_block.tolist()
                ],
                "field_shift_new_to_old": [
                    [str(value) for value in row]
                    for row in self.field_shift.tolist()
                ],
                "cotangent_shift_new_to_old": [
                    [str(value) for value in row]
                    for row in self.dual_shift.tolist()
                ],
                "shifted_QBV_before_equation_reorder": [
                    [str(value) for value in row]
                    for row in self.shifted_bv_block.tolist()
                ],
                "shifted_QBV_after_equation_reorder": [
                    [str(value) for value in row]
                    for row in self.reordered_shifted_bv_block.tolist()
                ],
                "physical_metric_block": "L^2 (biwave)",
                "generalized_auxiliary_block": "-1 (pointwise invertible)",
                "off_diagonal_defect": 0,
                "field_shift_finite_order_local": True,
            },
            "fixed_witness_block": {
                "matrix": [
                    [str(value) for value in row]
                    for row in self.witness_block.tolist()
                ],
                "formula": "[[L,0],[4,L]]",
                "full_116_row_leakage": self.witness_row_leakage,
                "full_116_column_leakage": self.witness_column_leakage,
                "conjugated_by_auxiliary_field_shift": [
                    [str(value) for value in row]
                    for row in self.shifted_witness_block.tolist()
                ],
                "field_shift_removes_Jordan_extension": False,
                "reason": "U=I+L N commutes with P=L I+4 N",
                "contractible_filtration_invariant": True,
                "associated_graded_blocks": ["L on f_hat", "L on h quotient"],
                "matrix_sha256": _digest(self.witness_block),
            },
            "triangular_Green_recursion": {
                "assumption": "G_+ or G_- is a two-sided Green inverse of L on its standard one-sided support extension",
                "candidate": "[[G,0],[-4 G^2,G]]",
                "left_inverse_defect": 0,
                "right_inverse_defect": 0,
                "off_diagonal_formula": "-G (4) G",
                "same_sign_composition_only": True,
                "causal_support_identity": "J^+J^+(K)=J^+(K), J^-J^-(K)=J^-(K)",
                "inverse_curl_used": False,
                "inverse_Laplacian_used": False,
                "TT_projector_used_in_recursion": False,
                "helicity_projector_used_in_recursion": False,
                "projector_free_full_BV_embedding_certified": False,
            },
            "interpretation": {
                "strong_hyperbolicity_obstruction_and_Green_recursion_compatible": True,
                "reason": (
                    "a triangular extension of Green-hyperbolic wave blocks can "
                    "have a defective combined first-order symbol while retaining "
                    "finite recursive advanced/retarded inverses"
                ),
                "next_required_certificate": (
                    "a support-local filtration of all 116 rows (and their BV "
                    "partners) whose associated graded diagonal blocks are Green hyperbolic"
                ),
            },
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "status_flags_promoted": [],
            "warranted_atomic_flags": [],
            "fail_closed": True,
        }
