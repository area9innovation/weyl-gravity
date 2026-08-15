"""Exact Green contraction of the shifted rank-four vector singleton.

The natural principal support graph of the fixed pair-(1,6) witness leaves
the vector field ``v[4]`` as an apparently open singleton.  The graph forgets
the BV differential.  After the certified local canonical auxiliary shift,
the vector row belongs to the pointwise generalized-auxiliary complex

``eta -> -v`` and ``v^sharp -> +eta^sharp``.

Consequently there is no need to invert the second-order diagonal selected
by the fixed witness.  On the sixteen-dimensional vector cotangent summand,
ordered as ``(eta,v,v^sharp,eta^sharp)``, choose the replacement witness

``W(v)=-eta`` and ``W(eta^sharp)=+v^sharp``.

Then, as an equality of complete local operators,

``P=QW+WQ=I_16``.

Thus both same-sided Green operators are the pointwise identity and
``Lambda_+=Lambda_-=W`` obey the Green-homotopy identity.  This statement
includes every lower-order coefficient: the replacement operator has order
zero, coefficient ``I_16``, and no derivative or curvature terms.

This is an isolated replacement on a certified direct summand.  It does not
insert the replacement witness into the remaining rank-34 component or prove
the complete all-row Green identity.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Mapping

import sympy as sp


VECTOR_RANK = 4
BLOCK_COUNT = 4
TOTAL_RANK = VECTOR_RANK * BLOCK_COUNT


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _nested(mapping: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = mapping.get(key)
    if not isinstance(value, Mapping):
        raise AssertionError(f"missing mapping {key}")
    return value


def _block_matrix() -> tuple[sp.Matrix, sp.Matrix]:
    """Return exact Q and its degree-minus-one replacement witness."""

    identity = sp.eye(VECTOR_RANK)
    q = sp.zeros(TOTAL_RANK)
    witness = sp.zeros(TOTAL_RANK)

    # Block order: eta, v, v^sharp, eta^sharp.
    q[VECTOR_RANK : 2 * VECTOR_RANK, 0:VECTOR_RANK] = -identity
    q[3 * VECTOR_RANK : 4 * VECTOR_RANK, 2 * VECTOR_RANK : 3 * VECTOR_RANK] = identity
    witness[0:VECTOR_RANK, VECTOR_RANK : 2 * VECTOR_RANK] = -identity
    witness[2 * VECTOR_RANK : 3 * VECTOR_RANK, 3 * VECTOR_RANK : 4 * VECTOR_RANK] = identity
    return q, witness


@dataclass(frozen=True)
class ExpandedRelativeVectorContraction:
    """Pointwise Green witness on the shifted vector cotangent summand."""

    differential: sp.Matrix
    witness: sp.Matrix
    operator: sp.Matrix
    green_plus: sp.Matrix
    green_minus: sp.Matrix
    homotopy_plus: sp.Matrix
    homotopy_minus: sp.Matrix

    @staticmethod
    def build() -> "ExpandedRelativeVectorContraction":
        differential, witness = _block_matrix()
        operator = differential * witness + witness * differential
        green_plus = sp.eye(TOTAL_RANK)
        green_minus = sp.eye(TOTAL_RANK)
        result = ExpandedRelativeVectorContraction(
            differential=differential,
            witness=witness,
            operator=operator,
            green_plus=green_plus,
            green_minus=green_minus,
            homotopy_plus=witness * green_plus,
            homotopy_minus=witness * green_minus,
        )
        result.verify()
        return result

    def verify(self) -> None:
        identity = sp.eye(TOTAL_RANK)
        zero = sp.zeros(TOTAL_RANK)
        if self.differential * self.differential != zero:
            raise AssertionError("shifted vector differential is not nilpotent")
        if self.witness * self.witness != zero:
            raise AssertionError("replacement vector witness is not nilpotent")
        if self.operator != identity:
            raise AssertionError("vector replacement P=QW+WQ is not identity")
        for name, green in (
            ("advanced", self.green_plus),
            ("retarded", self.green_minus),
        ):
            if self.operator * green != identity:
                raise AssertionError(f"{name} vector Green right inverse failed")
            if green * self.operator != identity:
                raise AssertionError(f"{name} vector Green left inverse failed")
        for name, homotopy in (
            ("advanced", self.homotopy_plus),
            ("retarded", self.homotopy_minus),
        ):
            if (
                self.differential * homotopy
                + homotopy * self.differential
                != identity
            ):
                raise AssertionError(f"{name} vector Green homotopy failed")
        if self.homotopy_plus != self.homotopy_minus:
            raise AssertionError("pointwise advanced/retarded homotopies differ")

    def certificate(
        self,
        *,
        retract_certificate: Mapping[str, object],
        canonical_shift_certificate: Mapping[str, object],
        shifted_filtration_certificate: Mapping[str, object],
    ) -> dict[str, object]:
        self.verify()
        if retract_certificate.get("schema") != (
            "pure-weyl-curved-deformation-retract-status-v1"
        ) or not retract_certificate.get("curved_deformation_retract"):
            raise AssertionError("exact curved deformation retract unavailable")
        split = _nested(retract_certificate, "factorized_actual_curved_Q")
        if not split.get("actual_curved_Q_conjugation_verified"):
            raise AssertionError("actual curved Q split regressed")
        transformed = _nested(split, "transformed_Q")
        if transformed.get("off_diagonal_blocks") != "zero":
            raise AssertionError("vector auxiliary summand is no longer direct")
        expected_arrows = {"eta -> -v", "v^* -> +eta^*"}
        actual_arrows = set(transformed.get("generalized_auxiliary", []))
        if not expected_arrows.issubset(actual_arrows):
            raise AssertionError("shifted vector cotangent arrows unavailable")
        support = _nested(split, "support")
        if not all(support.get(key) for key in ("compact", "spacelike_compact", "smooth_global")):
            raise AssertionError("shifted vector split is not support local")

        if canonical_shift_certificate.get("schema") != (
            "pure-weyl-curved-auxiliary-canonical-split-v1"
        ) or not canonical_shift_certificate.get(
            "actual_curved_Q_conjugation_verified"
        ):
            raise AssertionError("canonical shifted coordinates unavailable")
        universal = _nested(
            canonical_shift_certificate, "universal_generalized_auxiliary_split"
        )
        if not universal.get("pointwise_after_shift") or not universal.get(
            "contractible"
        ):
            raise AssertionError("universal vector summand lost pointwise contraction")
        rows = {
            (entry.get("arrow"), entry.get("rank"))
            for entry in universal.get("all_rows", [])
            if isinstance(entry, Mapping)
        }
        if ("eta -> -v", 4) not in rows or ("v^* -> +eta^*", 4) not in rows:
            raise AssertionError("universal split vector ranks drifted")

        if shifted_filtration_certificate.get("schema") != (
            "pure-weyl-expanded-relative-shifted-green-filtration-v1"
        ):
            raise AssertionError("wrong shifted-filtration certificate")
        boundary = _nested(shifted_filtration_certificate, "full_complex_boundary")
        if boundary.get("rank4_vector_singleton_Green_inverse"):
            raise AssertionError("input unexpectedly already claims vector inverse")

        return {
            "schema": "pure-weyl-expanded-relative-vector-contraction-v1",
            "scope": (
                "exact shifted generalized-auxiliary vector cotangent summand; "
                "replacement witness, not inversion of the fixed second-order "
                "principal singleton"
            ),
            "cross_certificates": {
                "actual_curved_Q_split": "curved_deformation_retract_status.json",
                "canonical_shift": "curved_auxiliary_canonical_split.json",
                "open_singleton_ledger": (
                    "curved_expanded_relative_witness_shifted_green_filtration.json"
                ),
            },
            "shifted_vector_complex": {
                "block_order": ["eta[4]", "v[4]", "v_sharp[4]", "eta_sharp[4]"],
                "field_singleton_rank": VECTOR_RANK,
                "dimension": TOTAL_RANK,
                "differential": "eta -> -v; v_sharp -> +eta_sharp",
                "differential_order": 0,
                "curvature_coefficients": 0,
                "Q_squared_defect": 0,
                "direct_summand_of_actual_curved_Q": True,
                "all_primal_and_cotangent_vector_rows_included": True,
                "matrix_sha256": _digest(self.differential),
            },
            "replacement_witness": {
                "formula": "W(v)=-eta; W(eta_sharp)=+v_sharp",
                "differential_order": 0,
                "W_squared_defect": 0,
                "cotangent_partner_included": True,
                "matrix_sha256": _digest(self.witness),
            },
            "exact_local_operator": {
                "identity": "P_vec=Q_vec W_vec+W_vec Q_vec=I_16",
                "order": 0,
                "principal_derivative_coefficients": 0,
                "complete_zeroth_order_coefficient": "I_16",
                "curvature_lower_order_terms": 0,
                "operator_identity_defect": 0,
                "formal_adjoint_defect": 0,
                "classification": "pointwise invertible contractible block",
                "normally_hyperbolic": False,
                "Green_hyperbolic": True,
                "reason_not_normally_hyperbolic": (
                    "the replacement is an invertible order-zero operator, not "
                    "a second-order wave operator"
                ),
                "matrix_sha256": _digest(self.operator),
            },
            "same_sided_green_operators": {
                "G_plus": "I_16",
                "G_minus": "I_16",
                "advanced_left_defect": 0,
                "advanced_right_defect": 0,
                "retarded_left_defect": 0,
                "retarded_right_defect": 0,
                "G_plus_sharp_equals_G_minus": True,
                "support": "supp(G_plus/minus f)=supp(f) subset J_plus/minus(supp f)",
                "finite_propagation": True,
            },
            "green_homotopy_contribution": {
                "Lambda_plus": "W_vec",
                "Lambda_minus": "W_vec",
                "Q_Lambda_plus_plus_Lambda_plus_Q_defect": 0,
                "Q_Lambda_minus_plus_Lambda_minus_Q_defect": 0,
                "causal_propagator_on_contractible_vector_summand": 0,
                "support_local": True,
            },
            "warranted_atomic_flags": {
                "shifted_rank4_vector_block_contractible": True,
                "shifted_rank4_vector_replacement_Green_inverse": True,
                "shifted_rank4_vector_Green_homotopy": True,
            },
            "status_flags_promoted": {
                "shifted_rank4_vector_block_contractible": True,
                "shifted_rank4_vector_replacement_Green_inverse": True,
                "shifted_rank4_vector_Green_homotopy": True,
            },
            "full_complex_boundary": {
                "fixed_witness_second_order_vector_block_inverted": False,
                "reason": (
                    "the Green witness is replaced on an exact Q-direct summand; "
                    "no claim is made about the fixed candidate's lower-order "
                    "second-order singleton"
                ),
                "replacement_inserted_into_complete_prolonged_W": False,
                "rank34_reciprocal_component_Green_inverse": False,
                "all_BV_rows_complete_QLambda_identity": False,
            },
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "fail_closed": True,
        }
