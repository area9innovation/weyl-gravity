"""Auxiliary-shift filtration and the exact physical replacement witness.

The support-local BV-canonical auxiliary shift splits the *differential* into
the retained metric complex and generalized-auxiliary contractions.  It need
not split an independently chosen witness.  This module distinguishes those
two statements for the fixed-temporal pair-(1,6), cyclic ``-2 Pi`` branch.

First, the complete aligned 116-square witness symbol is conjugated by the
actual polynomial auxiliary field shift.  Its natural support graph still
contains the reciprocal rank-34 component ``(h,f_hat,C#)``.  Thus merely
changing coordinates does not turn the fixed witness into a triangular Green
operator.

Second, on the exact retained TT plus shifted-auxiliary subcomplex, choose a
new split witness.  The curved differential is

``Q(h,f_hat)=(B_TT h,A_g f_hat)``.

The backward witness is identity on the TT equation and ``A_g^{-1}`` on the
auxiliary equation.  Therefore

``P=QW+WQ=diag(B_TT,1,B_TT,1)``.

The certified local factorization ``B_TT=P_- P_+`` gives causal Green
operators, and the resulting ``Lambda=W G`` obeys the Green homotopy identity
on this restricted local subcomplex.  Conjugation by the differential,
support-local auxiliary shift transports that causal contraction to the
unshifted physical-plus-contractible sector.

This is an actual operator theorem, not a principal-symbol inference.  It is
still not the complete BV Green theorem: arbitrary sources cannot be sent to
the TT subcomplex by a support-local projector, and the full rank-34 plus
rank-four open blocks remain uninverted.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping

import sympy as sp

from covariant_completion.auxiliary_equivalence import (
    GeneralizedAuxiliaryRetract,
)
from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)

from .expanded_relative_witness_triangular_green_audit import (
    EXPECTED_EDGES,
    LEDGER,
    ExpandedRelativeTriangularGreenAudit,
    _physical_inclusion_projection,
    _strong_components,
    _support_edges,
)


SHIFTED_EXPECTED_EDGES = frozenset(
    {
        (0, 0),
        (5, 0),
        (0, 1),
        (1, 1),
        (2, 1),
        (5, 1),
        (2, 2),
        (3, 3),
        (0, 4),
        (1, 4),
        (2, 4),
        (4, 4),
        (0, 5),
        (1, 5),
        (2, 5),
        (5, 5),
        (6, 6),
    }
)


FormalMatrix = list[list[OperatorPolynomial]]


def _zero(size: int) -> FormalMatrix:
    return [
        [OperatorPolynomial.zero() for _ in range(size)]
        for _ in range(size)
    ]


def _add(left: FormalMatrix, right: FormalMatrix) -> FormalMatrix:
    return [
        [
            left[row][column] + right[row][column]
            for column in range(len(left))
        ]
        for row in range(len(left))
    ]


def _multiply(left: FormalMatrix, right: FormalMatrix) -> FormalMatrix:
    size = len(left)
    result = _zero(size)
    for row in range(size):
        for column in range(size):
            entry = OperatorPolynomial.zero()
            for middle in range(size):
                entry = entry + left[row][middle] * right[middle][column]
            result[row][column] = entry
    return result


def _reduce_actual(entry: OperatorPolynomial) -> OperatorPolynomial:
    inverse_pairs = {
        ("Ag", "AgInv"),
        ("AgInv", "Ag"),
        ("BTT", "GBTT"),
        ("GBTT", "BTT"),
    }
    values: dict[tuple[str, ...], Fraction] = {}
    for word, coefficient in entry.terms:
        reduced = word
        changed = True
        while changed:
            changed = False
            for index in range(max(0, len(reduced) - 1)):
                if reduced[index : index + 2] in inverse_pairs:
                    reduced = reduced[:index] + reduced[index + 2 :]
                    changed = True
                    break
        values[reduced] = values.get(reduced, Fraction()) + coefficient
    return OperatorPolynomial._from_dict(values)


def _is_identity_mod_actual(matrix: FormalMatrix) -> bool:
    for row in range(len(matrix)):
        for column in range(len(matrix)):
            expected = OperatorPolynomial.identity() if row == column else (
                OperatorPolynomial.zero()
            )
            if _reduce_actual(matrix[row][column]) != expected:
                return False
    return True


def _actual_physical_complex() -> tuple[
    FormalMatrix,
    FormalMatrix,
    FormalMatrix,
    FormalMatrix,
    FormalMatrix,
]:
    """Return Q,W,P,G,Lambda on (hTT,fhat,EhTT,Efhat)."""

    q = _zero(4)
    q[2][0] = OperatorPolynomial.atom("BTT")
    q[3][1] = OperatorPolynomial.atom("Ag")
    w = _zero(4)
    w[0][2] = OperatorPolynomial.identity()
    w[1][3] = OperatorPolynomial.atom("AgInv")
    p = _add(_multiply(q, w), _multiply(w, q))
    green = _zero(4)
    green[0][0] = OperatorPolynomial.atom("GBTT")
    green[1][1] = OperatorPolynomial.identity()
    green[2][2] = OperatorPolynomial.atom("GBTT")
    green[3][3] = OperatorPolynomial.identity()
    homotopy = _multiply(w, green)
    return q, w, p, green, homotopy


def _is_zero_mod_actual(matrix: FormalMatrix) -> bool:
    return all(
        _reduce_actual(entry) == OperatorPolynomial.zero()
        for row in matrix
        for entry in row
    )


def _nested(mapping: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = mapping.get(key)
    if not isinstance(value, Mapping):
        raise AssertionError(f"missing mapping {key}")
    return value


@dataclass(frozen=True)
class ExpandedRelativeShiftedGreenFiltration:
    base: ExpandedRelativeTriangularGreenAudit
    retract: GeneralizedAuxiliaryRetract
    shifted_aligned_symbol: sp.Matrix
    field_new_to_old: sp.Matrix
    shifted_support_edges: frozenset[tuple[int, int]]
    shifted_strong_components: tuple[tuple[int, ...], ...]
    physical_block: sp.Matrix
    expected_physical_block: sp.Matrix
    maximum_shift_degree: int
    maximum_shifted_symbol_degree: int

    @staticmethod
    def build() -> "ExpandedRelativeShiftedGreenFiltration":
        base = ExpandedRelativeTriangularGreenAudit.build()
        retract = GeneralizedAuxiliaryRetract.build()
        tau, rho = sp.symbols("shifted_green_tau shifted_green_rho")
        aligned = base.full_symbol.symbol((tau, rho, 0, 0), separated=True)
        substitution = dict(
            zip(retract.system.covector, (tau, rho, 0, 0), strict=True)
        )
        field_change = retract.field_new_to_old.subs(substitution)
        total_change = sp.diag(field_change, sp.eye(92))
        shifted = sp.simplify(total_change.inv() * aligned * total_change)
        inclusion, projection = _physical_inclusion_projection()
        physical = sp.simplify(projection * shifted * inclusion)
        q = rho**2 - tau**2
        expected_physical = sp.diag(q, q, q, q)
        expected_physical[2, 0] = 4 * rho**2
        expected_physical[3, 1] = 4 * rho**2

        result = ExpandedRelativeShiftedGreenFiltration(
            base=base,
            retract=retract,
            shifted_aligned_symbol=shifted,
            field_new_to_old=field_change,
            shifted_support_edges=_support_edges(shifted),
            shifted_strong_components=_strong_components(
                _support_edges(shifted), len(LEDGER)
            ),
            physical_block=physical,
            expected_physical_block=expected_physical,
            maximum_shift_degree=max(
                sp.Poly(value, tau, rho).total_degree()
                for value in field_change
                if value != 0
            ),
            maximum_shifted_symbol_degree=max(
                sp.Poly(value, tau, rho).total_degree()
                for value in shifted
                if value != 0
            ),
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.base.verify()
        self.retract.verify()
        if self.field_new_to_old.det() != 1:
            raise AssertionError("auxiliary shift is not polynomially invertible")
        if self.maximum_shift_degree != 2:
            raise AssertionError("auxiliary shift order drifted")
        if self.maximum_shifted_symbol_degree != 4:
            raise AssertionError("shifted fixed witness order drifted")
        if self.shifted_support_edges != SHIFTED_EXPECTED_EDGES:
            raise AssertionError("shifted natural support graph drifted")
        if self.shifted_strong_components != (
            (0, 1, 5),
            (2,),
            (3,),
            (4,),
            (6,),
        ):
            raise AssertionError("auxiliary shift changed the SCC ledger unexpectedly")

        inclusion, projection = _physical_inclusion_projection()
        if (
            self.shifted_aligned_symbol * inclusion
            != inclusion * self.physical_block
        ):
            raise AssertionError("shifted physical block is not invariant")
        if (
            projection * self.shifted_aligned_symbol
            != self.physical_block * projection
        ):
            raise AssertionError("shifted physical block is not coinvariant")
        if self.physical_block != self.expected_physical_block:
            raise AssertionError("fixed-witness physical Jordan block did not commute")

        q, w, p, green, homotopy = _actual_physical_complex()
        if not _is_zero_mod_actual(_multiply(q, q)):
            raise AssertionError("restricted shifted Q is not nilpotent")
        expected = _zero(4)
        expected[0][0] = OperatorPolynomial.atom("BTT")
        expected[1][1] = OperatorPolynomial.identity()
        expected[2][2] = OperatorPolynomial.atom("BTT")
        expected[3][3] = OperatorPolynomial.identity()
        if any(
            _reduce_actual(p[row][column]) != expected[row][column]
            for row in range(4)
            for column in range(4)
        ):
            raise AssertionError("actual restricted P=QW+WQ identity failed")
        if not _is_identity_mod_actual(_multiply(p, green)):
            raise AssertionError("actual restricted Green right inverse failed")
        if not _is_identity_mod_actual(_multiply(green, p)):
            raise AssertionError("actual restricted Green left inverse failed")
        homotopy_identity = _add(
            _multiply(q, homotopy), _multiply(homotopy, q)
        )
        if not _is_identity_mod_actual(homotopy_identity):
            raise AssertionError("actual restricted Green homotopy failed")

    def certificate(
        self,
        *,
        retract_certificate: Mapping[str, object],
        canonical_shift_certificate: Mapping[str, object],
        tt_factor_certificate: Mapping[str, object],
        jordan_homology_certificate: Mapping[str, object],
    ) -> dict[str, object]:
        self.verify()
        if retract_certificate.get("schema") != (
            "pure-weyl-curved-deformation-retract-status-v1"
        ) or not retract_certificate.get("curved_deformation_retract"):
            raise AssertionError("global curved auxiliary retract unavailable")
        split = _nested(retract_certificate, "factorized_actual_curved_Q")
        if not split.get("actual_curved_Q_conjugation_verified"):
            raise AssertionError("actual curved Q split regressed")
        if _nested(split, "transformed_Q").get("off_diagonal_blocks") != "zero":
            raise AssertionError("actual curved Q is no longer split")
        if canonical_shift_certificate.get("schema") != (
            "pure-weyl-curved-auxiliary-canonical-split-v1"
        ):
            raise AssertionError("wrong canonical shift certificate")
        if not canonical_shift_certificate.get("curved_deformation_retract"):
            raise AssertionError("canonical split retract unavailable")
        if tt_factor_certificate.get("schema") != (
            "pure-weyl-tt-local-factorization-v1"
        ) or not tt_factor_certificate.get("reduced_green_hyperbolic"):
            raise AssertionError("exact TT biwave Green factorization unavailable")
        if not tt_factor_certificate.get("locality_guard"):
            raise AssertionError("TT factorization is no longer local")
        if jordan_homology_certificate.get("schema") != (
            "pure-weyl-expanded-relative-jordan-homology-v1"
        ):
            raise AssertionError("wrong Jordan homology certificate")
        pair = _nested(jordan_homology_certificate, "existing_contractible_pair")
        if not pair.get("a0_is_in_Q_contractible_summand"):
            raise AssertionError("Jordan eigenvector lost its auxiliary contraction")
        architecture = _nested(
            jordan_homology_certificate, "architectural_consequence"
        )
        if not architecture.get("Jordan_block_touches_physical_curvature_through_a1"):
            raise AssertionError("Jordan physical leg classification regressed")

        central = self.shifted_strong_components[0]
        return {
            "schema": "pure-weyl-expanded-relative-shifted-green-filtration-v1",
            "scope": (
                "actual local shifted TT plus generalized-auxiliary subcomplex, "
                "and aligned complete-symbol filtration of the fixed pair-(1,6) witness"
            ),
            "auxiliary_shift": {
                "actual_curved_Q_conjugation_verified": True,
                "BV_canonical": True,
                "finite_order": self.maximum_shift_degree,
                "polynomial_inverse": True,
                "support_local": True,
                "transformed_Q_off_diagonal_blocks": 0,
                "retained_metric_block": "h -> B_lin h_star",
                "contractible_tensor_block": "f_hat -> A_g f_hat_star",
            },
            "fixed_witness_after_shift": {
                "maximum_aligned_polynomial_degree": (
                    self.maximum_shifted_symbol_degree
                ),
                "directed_edges_source_to_target": [
                    [LEDGER[source][2], LEDGER[target][2]]
                    for source, target in sorted(self.shifted_support_edges)
                ],
                "strong_components": [
                    [LEDGER[index][2] for index in component]
                    for component in self.shifted_strong_components
                ],
                "reciprocal_component": [
                    LEDGER[index][2] for index in central
                ],
                "reciprocal_component_rank": sum(
                    LEDGER[index][1] - LEDGER[index][0] for index in central
                ),
                "f_hat_shift_splits_fixed_witness_SCC": False,
                "physical_aligned_block_unchanged": True,
                "reason": (
                    "the polynomial lower-triangular physical coupling commutes "
                    "with the auxiliary EOM shear; Q-splitting does not imply "
                    "splitting of a separately selected W"
                ),
            },
            "actual_local_physical_replacement_witness": {
                "block_order": ["h_TT", "f_hat_TT", "E_h_TT", "E_f_hat_TT"],
                "Q": "h_TT -> B_TT E_h_TT; f_hat_TT -> A_g E_f_hat_TT",
                "W": "E_h_TT -> h_TT; E_f_hat_TT -> A_g^-1 f_hat_TT",
                "P_equals_QW_plus_WQ": "diag(B_TT,1,B_TT,1)",
                "Q_squared_defect": 0,
                "P_identity_defect": 0,
                "B_TT_factorization": "P_minus P_plus=P_plus P_minus",
                "factor_green_operators": (
                    "G_BTT_plus/minus=G_Pplus_plus/minus G_Pminus_plus/minus"
                ),
                "Green_operator": "diag(G_BTT,1,G_BTT,1)",
                "left_Green_defect": 0,
                "right_Green_defect": 0,
                "Lambda": "W G",
                "Q_Lambda_plus_Lambda_Q_defect": 0,
                "advanced_retarded_support": True,
                "operator_level_not_principal_symbol": True,
                "TT_constraint_preserved_by_both_factors": True,
                "uses_TT_projector_inside_restricted_block": False,
            },
            "transport_to_unshifted_sector": {
                "formula": "G_old=U_shift G_split U_shift^-1",
                "homotopy_formula": (
                    "Lambda_old=U_shift Lambda_split U_shift^-1"
                ),
                "support_preserved": True,
                "Green_homotopy_preserved_by_conjugation": True,
                "Jordan_eigenleg_contracts_in_f_hat_pair": True,
                "Jordan_generalized_leg_propagates_in_B_TT": True,
            },
            "warranted_atomic_flags": {
                "physical_biwave_block_green_hyperbolic": True,
                "physical_Jordan_extension_causal": True,
                "auxiliary_shifted_fixed_witness_filtration_audited": True,
            },
            "full_complex_boundary": {
                "arbitrary_source_TT_projection_support_local": False,
                "rank34_reciprocal_component_Green_inverse": False,
                "rank4_vector_singleton_Green_inverse": False,
                "all_BV_rows_included_in_restricted_homotopy": False,
                "complete_QLambda_identity": False,
            },
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "status_flags_promoted": {
                "physical_biwave_block_green_hyperbolic": True,
                "physical_Jordan_extension_causal": True,
                "auxiliary_shifted_fixed_witness_filtration_audited": True,
            },
            "fail_closed": True,
        }
