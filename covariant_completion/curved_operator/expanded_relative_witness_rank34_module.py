"""Differential-module audit of the reciprocal rank-34 component.

The natural principal support graph of the fixed-temporal pair-(1,6),
cyclic ``-2 Pi`` witness contains the component

``F_34=(h[10],f[10],Csharp[14])``.

A component graph cannot see the differential relations inside this block.
This module exposes one exact local filtration.  The six ``q,r``
constraint-dual coordinates and the six vector-gauge columns form a
presented rank-twelve submodule.  If ``B`` is the vector-gauge incidence,
``C`` its reciprocal row and ``D_6`` the ``q,r`` subsidiary block, the exact
polynomial relations are

``A B=0,  C B=tau^2 D_6,  D i_6=i_6 D_6``.

Consequently the local differential embedding

``J=diag(B,i_6)``

intertwines the rank-34 symbol with

``L_12=[[0,I],[tau^2 D_6,D_6]]``.

The latter has an explicit recursive inverse after choosing same-sided
inverses of ``tau^2`` and of the symmetric-hyperbolic ``q,r`` system.  This
does not invert the rank-34 block: the quotient still contains a rank-fourteen
field cokernel whose aligned determinant is ``4 tau^8 q^10``.  The exact
curvature map ``(C1,div C1)`` annihilates the gauge presentation and hence
descends to that cokernel, but its intertwiner with a projector-free physical
biwave quotient has not been constructed.

The raw off-diagonal ideal is not nilpotent: its square has nonzero trace.
Thus a finite Neumann series around the naive diagonal is unavailable.  The
filtration, rather than componentwise triangularization, is the useful
positive result.  No Green or causal flag is promoted here.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
from typing import Mapping

import sympy as sp

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)

from .expanded_relative_witness_full_symbol import ExpandedRelativeFullSymbol
from .weyl_cotton_hyperbolic import ConstraintAdjustedWeylCottonEvolution


FIELD_INDICES = tuple(range(20))
CONSTRAINT_INDICES = tuple(range(76, 90))
RANK34_INDICES = FIELD_INDICES + CONSTRAINT_INDICES
VECTOR_CONSTRAINT_INDICES = tuple(range(6))


FormalMatrix = list[list[OperatorPolynomial]]


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _nonzero_count(matrix: sp.MatrixBase) -> int:
    return sum(int(value != 0) for value in matrix)


def _zero(size: int) -> FormalMatrix:
    return [
        [OperatorPolynomial.zero() for _ in range(size)]
        for _ in range(size)
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


def _reduce_submodule_green(entry: OperatorPolynomial) -> OperatorPolynomial:
    """Reduce T/GT and D/GD two-sided inverse words and TD=DT."""

    values: dict[tuple[str, ...], Fraction] = {}
    for word, coefficient in entry.terms:
        reduced = tuple(word)
        changed = True
        while changed:
            changed = False
            # Put T before D (and GT before GD) to make commutation explicit.
            substitutions = {
                ("D", "T"): ("T", "D"),
                ("GD", "GT"): ("GT", "GD"),
                ("D", "GT"): ("GT", "D"),
                ("GD", "T"): ("T", "GD"),
            }
            for index in range(max(0, len(reduced) - 1)):
                pair = reduced[index : index + 2]
                if pair in substitutions:
                    reduced = (
                        reduced[:index]
                        + substitutions[pair]
                        + reduced[index + 2 :]
                    )
                    changed = True
                    break
                if pair in (
                    ("T", "GT"),
                    ("GT", "T"),
                    ("D", "GD"),
                    ("GD", "D"),
                ):
                    reduced = reduced[:index] + reduced[index + 2 :]
                    changed = True
                    break
        values[reduced] = values.get(reduced, Fraction()) + coefficient
    return OperatorPolynomial._from_dict(values)


def _formal_submodule_pair() -> tuple[FormalMatrix, FormalMatrix]:
    """Return L and its same-sided inverse on the two presented blocks."""

    operator = _zero(2)
    operator[0][1] = OperatorPolynomial.identity()
    operator[1][0] = (
        OperatorPolynomial.atom("T") * OperatorPolynomial.atom("D")
    )
    operator[1][1] = OperatorPolynomial.atom("D")

    green = _zero(2)
    green[0][0] = OperatorPolynomial.atom("GT").scale(-1)
    green[0][1] = (
        OperatorPolynomial.atom("GT") * OperatorPolynomial.atom("GD")
    )
    green[1][0] = OperatorPolynomial.identity()
    return operator, green


def _formal_identity(matrix: FormalMatrix) -> bool:
    for row in range(len(matrix)):
        for column in range(len(matrix)):
            expected = (
                OperatorPolynomial.identity()
                if row == column
                else OperatorPolynomial.zero()
            )
            if _reduce_submodule_green(matrix[row][column]) != expected:
                return False
    return True


def _nested(mapping: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = mapping.get(key)
    if not isinstance(value, Mapping):
        raise AssertionError(f"missing mapping {key}")
    return value


@dataclass(frozen=True)
class ExpandedRelativeRank34Module:
    tau: sp.Symbol
    rho: sp.Symbol
    spatial_covector: tuple[sp.Symbol, sp.Symbol, sp.Symbol]
    rank34_symbol: sp.Matrix
    field_diagonal: sp.Matrix
    constraint_diagonal: sp.Matrix
    gauge_incidence: sp.Matrix
    reciprocal_incidence: sp.Matrix
    vector_subsidiary: sp.Matrix
    vector_constraint_inclusion: sp.Matrix
    submodule_embedding: sp.Matrix
    submodule_operator: sp.Matrix
    intertwining_defect: sp.Matrix
    raw_off_diagonal: sp.Matrix
    quotient_determinant: sp.Expr
    quotient_constraint_determinant: sp.Expr
    quotient_field_determinant: sp.Expr
    quotient_constraint_symmetrizer: sp.Matrix

    @staticmethod
    def build() -> "ExpandedRelativeRank34Module":
        full = ExpandedRelativeFullSymbol.build()
        tau, rho = sp.symbols("rank34_tau rank34_rho", real=True)
        xi1, xi2, xi3 = sp.symbols("rank34_xi1 rank34_xi2 rank34_xi3", real=True)
        complete = full.symbol((tau, xi1, xi2, xi3), separated=True)
        rank34 = complete.extract(RANK34_INDICES, RANK34_INDICES)
        a = rank34[:20, :20]
        d = rank34[20:, 20:]
        b = rank34[:20, 20:26]
        c = rank34[20:26, :20]
        d6 = d[:6, :6]
        i6 = sp.zeros(14, 6)
        i6[:6, :] = sp.eye(6)

        embedding = sp.zeros(34, 12)
        embedding[:20, :6] = b
        embedding[20:, 6:] = i6
        submodule = sp.zeros(12)
        submodule[:6, 6:] = sp.eye(6)
        submodule[6:, :6] = tau**2 * d6
        submodule[6:, 6:] = d6
        defect = (rank34 * embedding - embedding * submodule).applyfunc(
            sp.expand
        )

        diagonal = sp.diag(a, d)
        off_diagonal = rank34 - diagonal
        aligned = rank34.subs({xi1: rho, xi2: 0, xi3: 0})
        aligned_submodule = submodule.subs({xi1: rho, xi2: 0, xi3: 0})
        rank34_determinant = sp.factor(aligned.det(method="domain-ge"))
        submodule_determinant = sp.factor(
            aligned_submodule.det(method="domain-ge")
        )
        quotient_determinant = sp.factor(
            rank34_determinant / submodule_determinant
        )
        quotient_constraint = sp.factor(
            d[6:, 6:].subs({xi1: rho, xi2: 0, xi3: 0}).det(method="domain-ge")
        )
        quotient_field = sp.factor(quotient_determinant / quotient_constraint)
        subsidiary = ConstraintAdjustedWeylCottonEvolution.build()
        quotient_symmetrizer = subsidiary.constraint_symmetrizer.inv()[6:, 6:]

        result = ExpandedRelativeRank34Module(
            tau=tau,
            rho=rho,
            spatial_covector=(xi1, xi2, xi3),
            rank34_symbol=rank34,
            field_diagonal=a,
            constraint_diagonal=d,
            gauge_incidence=b,
            reciprocal_incidence=c,
            vector_subsidiary=d6,
            vector_constraint_inclusion=i6,
            submodule_embedding=embedding,
            submodule_operator=submodule,
            intertwining_defect=defect,
            raw_off_diagonal=off_diagonal,
            quotient_determinant=quotient_determinant,
            quotient_constraint_determinant=quotient_constraint,
            quotient_field_determinant=quotient_field,
            quotient_constraint_symmetrizer=quotient_symmetrizer,
        )
        result.verify()
        return result

    def verify(self) -> None:
        tau, rho = self.tau, self.rho
        b, c, d6 = (
            self.gauge_incidence,
            self.reciprocal_incidence,
            self.vector_subsidiary,
        )
        i6 = self.vector_constraint_inclusion
        if self.rank34_symbol.shape != (34, 34):
            raise AssertionError("reciprocal component rank drifted")
        if b.shape != (20, 6) or c.shape != (6, 20):
            raise AssertionError("six-direction reciprocal incidence drifted")
        if b.rank() != 6:
            raise AssertionError("vector-gauge polynomial incidence lost rank")
        if (self.field_diagonal * b).applyfunc(sp.expand) != sp.zeros(20, 6):
            raise AssertionError("A B=0 gauge-Noether relation failed")
        if (c * b - tau**2 * d6).applyfunc(sp.expand) != sp.zeros(6):
            raise AssertionError("reciprocal cycle no longer equals tau^2 D6")
        if (
            self.constraint_diagonal * i6 - i6 * d6
        ).applyfunc(sp.expand) != sp.zeros(14, 6):
            raise AssertionError("q/r subsidiary subspace is not invariant")
        if self.intertwining_defect != sp.zeros(34, 12):
            raise AssertionError("rank-twelve differential submodule failed")

        spatial_norm = sum(value**2 for value in self.spatial_covector)
        expected_d6 = sp.factor(tau**2 * (spatial_norm - 4 * tau**2) ** 2 / 16)
        if sp.factor(d6.det()) != expected_d6:
            raise AssertionError("q/r subsidiary characteristic drifted")
        expected_q_constraint = sp.factor(
            tau**4 * (rho**2 - 3 * tau**2) ** 2 / 9
        )
        if self.quotient_constraint_determinant != expected_q_constraint:
            raise AssertionError("eight-rank constraint quotient drifted")
        expected_q_field = sp.factor(4 * tau**8 * (rho**2 - tau**2) ** 10)
        if self.quotient_field_determinant != expected_q_field:
            raise AssertionError("field cokernel characteristic drifted")
        if self.quotient_determinant != sp.factor(
            expected_q_constraint * expected_q_field
        ):
            raise AssertionError("quotient determinant is not multiplicative")

        # The q/r block is symmetric hyperbolic with the identity multiplier.
        # The remaining dual subsidiary quotient uses the inverse action of
        # the certified positive constraint symmetrizer.
        for variable in self.spatial_covector:
            d6_coefficient = self.vector_subsidiary.applyfunc(
                lambda value, variable=variable: sp.expand(value).coeff(variable)
            )
            if d6_coefficient != d6_coefficient.T:
                raise AssertionError("q/r dual subsidiary symbol is not symmetric")
            quotient_coefficient = self.constraint_diagonal[6:, 6:].applyfunc(
                lambda value, variable=variable: sp.expand(value).coeff(variable)
            )
            weighted = self.quotient_constraint_symmetrizer * quotient_coefficient
            if weighted != weighted.T:
                raise AssertionError("constraint quotient symmetrizer failed")
        if self.quotient_constraint_symmetrizer != sp.diag(
            *([sp.Rational(1, 3)] * 6 + [1, 1])
        ):
            raise AssertionError("constraint quotient positive form drifted")

        # R is not nilpotent.  Its square has trace 2 tr(CB)=-12 tau^3.
        square = (self.raw_off_diagonal**2).applyfunc(sp.expand)
        if sp.expand(sp.trace(square)) != -12 * tau**3:
            raise AssertionError("off-diagonal nonnilpotence witness drifted")

        operator, green = _formal_submodule_pair()
        if not _formal_identity(_multiply(operator, green)):
            raise AssertionError("presented submodule Green right inverse failed")
        if not _formal_identity(_multiply(green, operator)):
            raise AssertionError("presented submodule Green left inverse failed")

    def certificate(
        self,
        *,
        state_gauge_certificate: Mapping[str, object],
        identity_chain_certificate: Mapping[str, object],
        subsidiary_certificate: Mapping[str, object],
    ) -> dict[str, object]:
        self.verify()
        if state_gauge_certificate.get("schema") != (
            "pure-weyl-curvature-state-gauge-chain-map-v1"
        ) or not state_gauge_certificate.get("T_state_K_aux_exact"):
            raise AssertionError("C1 gauge-annihilation theorem unavailable")
        if state_gauge_certificate.get("T_state") != "(C1,div C1)":
            raise AssertionError("wrong local curvature quotient map")
        if identity_chain_certificate.get("schema") != (
            "pure-weyl-curvature-auxiliary-identity-chain-map-v1"
        ) or not identity_chain_certificate.get("second_chain_relation_exact"):
            raise AssertionError("Bianchi/Bach identity square unavailable")
        if not _nested(identity_chain_certificate, "full_auxiliary_chain_relation").get(
            "exact"
        ):
            raise AssertionError("full auxiliary identity relation regressed")
        if subsidiary_certificate.get("schema") != (
            "pure-weyl-cotton-constraint-adjusted-hyperbolic-v1"
        ):
            raise AssertionError("wrong sourced subsidiary certificate")
        if not subsidiary_certificate.get(
            "exact_sourced_subsidiary_operator_identity"
        ):
            raise AssertionError("sourced subsidiary identity unavailable")

        tau, rho = self.tau, self.rho
        square = (self.raw_off_diagonal**2).applyfunc(sp.expand)
        operator, green = _formal_submodule_pair()
        return {
            "schema": "pure-weyl-expanded-relative-rank34-module-v1",
            "scope": (
                "arbitrary-covector principal differential module, with aligned "
                "characteristic determinants, of the fixed-temporal pair-(1,6), "
                "cyclic -2Pi rank-34 (h,f,Csharp) component"
            ),
            "cross_certificates": {
                "C1_gauge_annihilation": (
                    "curved_curvature_state_gauge_chain_map.json"
                ),
                "Bianchi_Bach_identity_square": (
                    "curved_curvature_identity_chain_map.json"
                ),
                "sourced_subsidiary_system": (
                    "curved_weyl_cotton_hyperbolic.json"
                ),
            },
            "rank34_component": {
                "bundle_order": ["h[10]", "f[10]", "Csharp[14]"],
                "rank": 34,
                "matrix_sha256": _digest(self.rank34_symbol),
                "nonzero_coefficients": _nonzero_count(self.rank34_symbol),
                "reciprocal_vector_rank": self.gauge_incidence.rank(),
                "arbitrary_spatial_covector": [
                    str(value) for value in self.spatial_covector
                ],
            },
            "local_differential_submodule": {
                "presentation_rank": 12,
                "coordinates": ["vector_gauge_parameter[6]", "qsharp,rsharp[6]"],
                "embedding": "J=diag(B_vector,i_(qsharp,rsharp))",
                "embedding_differential_order": 1,
                "embedding_sha256": _digest(self.submodule_embedding),
                "operator": "[[0,I6],[partial_t^2 D_qr,D_qr]]",
                "intertwining_identity": "L_34 J=J L_12",
                "intertwining_defect": _nonzero_count(self.intertwining_defect),
                "defining_relations": {
                    "A_B": "zero",
                    "C_B": "partial_t^2 D_qr",
                    "D_i_qr": "i_qr D_qr",
                },
                "Noether_origin": "B_vector factors through local K",
                "Bianchi_origin": (
                    "C factors through the formal adjoint of the local "
                    "curvature identity N=(-R,S)"
                ),
                "support_local": True,
                "pointwise_or_helicity_projector_used": False,
            },
            "presented_submodule_recursive_inverse": {
                "D_qr_characteristic": str(sp.factor(self.vector_subsidiary.det())),
                "D_qr_system": (
                    "q_t+(1/2)curl r=0; r_t-(1/2)curl q=0"
                ),
                "D_qr_symmetric_hyperbolic": True,
                "T": "partial_t^2",
                "inverse_formula": "[[-G_T,G_T G_D],[I,0]]",
                "left_inverse_defect": 0,
                "right_inverse_defect": 0,
                "same_sided_compositions_only": True,
                "causal_support_candidate": True,
                "boundary": (
                    "this is an inverse of the presented rank-twelve module, "
                    "not an inverse or splitting of the rank-34 bundle operator"
                ),
            },
            "quotient_presentation": {
                "abstract_sequence": "0 -> presented F12 -> F34 -> coker(J) -> 0",
                "bundle_split_or_local_retraction_constructed": False,
                "quotient_rank": 22,
                "constraint_quotient_rank": 8,
                "constraint_quotient_characteristic": str(
                    self.quotient_constraint_determinant
                ),
                "constraint_quotient_symmetric_hyperbolic": True,
                "constraint_quotient_positive_symmetrizer": [
                    "1/3"
                ] * 6 + ["1", "1"],
                "field_cokernel_rank": 14,
                "field_cokernel_characteristic": str(
                    self.quotient_field_determinant
                ),
                "full_quotient_characteristic": str(self.quotient_determinant),
                "multiplicative_characteristic_identity_exact": True,
                "C1_descends_to_field_cokernel": True,
                "reason": "the exact local identity (C1,div C1) K_aux=0",
                "C1_induced_biwave_intertwiner_constructed": False,
                "projector_free_physical_quotient_inverse_constructed": False,
            },
            "off_diagonal_algebra": {
                "raw_generator": "R=[[0,B],[C,0]]",
                "R_squared_trace": str(sp.expand(sp.trace(square))),
                "raw_ideal_nilpotent": False,
                "finite_naive_Neumann_series_available": False,
                "cycle_relation": "C B=partial_t^2 D_qr",
                "interpretation": (
                    "the reciprocal cycle is controlled by the subsidiary "
                    "operator but does not vanish in the raw operator algebra"
                ),
            },
            "differential_identity_ledger": {
                "curvature_state_map": "T_state=(C1,div C1)",
                "T_state_K_aux": "zero",
                "identity_square": "N_curv A_equation=B_identity C_aux",
                "sourced_subsidiary_identity": True,
                "all_maps_local_differential": True,
            },
            "precise_remaining_obstruction": {
                "statement": (
                    "construct a local induced intertwiner and Green inverse "
                    "for the rank-fourteen field cokernel (or a further exact "
                    "filtration), then lift it through the nonsplit extension"
                ),
                "rank34_Green_inverse_constructed": False,
                "coefficientwise_lower_order_extension_verified": False,
                "all_BV_rows_included": False,
            },
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "status_flags_promoted": [],
            "warranted_atomic_flags": [],
            "fail_closed": True,
        }
