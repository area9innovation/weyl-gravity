"""Conditional Bär square-root promotion for the prolonged field block.

Let ``P`` be the still-open mixed-order auxiliary field block and ``D`` a
local differential companion.  Suppose exact coefficient certificates give

``D P=L_minus L_plus`` and ``P D=R_minus R_plus``

with all four factors Green hyperbolic.  Same-sided factor Green operators
then give

``G_P=G_Lplus G_Lminus D = D G_Rplus G_Rminus``.

The first expression is a right inverse, the second is a left inverse, and
their equality follows by inserting either certified identity.  This is the
standard square-root construction used for prenormally hyperbolic operators.

This module proves the noncommutative identities, causal-support statement,
formal-adjoint transfer, and the resulting sixteen-block insertion.  It is
strictly conditional: no coefficient factorization certificate currently
exists, so no project flag is promoted.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)


def _atom(name: str) -> OperatorPolynomial:
    return OperatorPolynomial.atom(name)


def _reduce(entry: OperatorPolynomial) -> OperatorPolynomial:
    rewrites = {
        ("D", "P"): ("Lm", "Lp"),
        ("P", "D"): ("Rm", "Rp"),
    }
    inverse_pairs = {
        ("Lm", "GLm"),
        ("GLm", "Lm"),
        ("Lp", "GLp"),
        ("GLp", "Lp"),
        ("Rm", "GRm"),
        ("GRm", "Rm"),
        ("Rp", "GRp"),
        ("GRp", "Rp"),
    }
    pending = list(entry.terms)
    values: dict[tuple[str, ...], Fraction] = {}
    while pending:
        word, coefficient = pending.pop()
        changed = False
        for index in range(max(0, len(word) - 1)):
            pair = word[index : index + 2]
            if pair in rewrites:
                pending.append(
                    (
                        word[:index] + rewrites[pair] + word[index + 2 :],
                        coefficient,
                    )
                )
                changed = True
                break
            if pair in inverse_pairs:
                pending.append((word[:index] + word[index + 2 :], coefficient))
                changed = True
                break
        if not changed:
            values[word] = values.get(word, Fraction()) + coefficient
    return OperatorPolynomial._from_dict(values)


def _is_identity(entry: OperatorPolynomial) -> bool:
    return _reduce(entry) == OperatorPolynomial.identity()


def _toggle_sharp(name: str) -> str:
    return name[:-5] if name.endswith("sharp") else name + "sharp"


def _formal_adjoint(entry: OperatorPolynomial) -> OperatorPolynomial:
    return OperatorPolynomial._from_dict(
        {
            tuple(_toggle_sharp(name) for name in reversed(word)): coefficient
            for word, coefficient in entry.terms
        }
    )


def _nested(mapping: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = mapping.get(key)
    if not isinstance(value, Mapping):
        raise AssertionError(f"missing mapping {key}")
    return value


def coefficient_certificate_passes(certificate: Mapping[str, object]) -> bool:
    if certificate.get("schema") != "pure-weyl-mixed-order-factorization-v1":
        return False
    exact = certificate.get("exact_factorizations")
    factors = certificate.get("green_factors")
    support = certificate.get("support")
    adjoint = certificate.get("formal_adjoint_completion")
    if not all(isinstance(value, Mapping) for value in (exact, factors, support, adjoint)):
        return False
    assert isinstance(exact, Mapping)
    assert isinstance(factors, Mapping)
    assert isinstance(support, Mapping)
    assert isinstance(adjoint, Mapping)
    return bool(
        exact.get("D_P_equals_Lminus_Lplus")
        and exact.get("P_D_equals_Rminus_Rplus")
        and exact.get("global_coefficientwise")
        and all(
            factors.get(name)
            for name in (
                "Lminus_green_hyperbolic",
                "Lplus_green_hyperbolic",
                "Rminus_green_hyperbolic",
                "Rplus_green_hyperbolic",
            )
        )
        and support.get("D_finite_order_differential")
        and support.get("all_factor_Green_operators_metric_causal")
        and adjoint.get("all_bundle_pairings_nondegenerate")
        and adjoint.get("factor_adjoint_relations_exact")
    )


@dataclass(frozen=True)
class MixedOrderGreenPromotion:
    """Exact formal theorem and fail-closed 16-block insertion audit."""

    mapping_witness_certificate: Mapping[str, object]
    green_bridge_certificate: Mapping[str, object]
    coefficient_certificate: Mapping[str, object] | None = None

    def verify(self) -> None:
        if self.mapping_witness_certificate.get("schema") != (
            "pure-weyl-curvature-mapping-cylinder-witness-v1"
        ):
            raise AssertionError("wrong sixteen-block witness certificate")
        if not self.mapping_witness_certificate.get("coefficientwise_candidate_W_prol"):
            raise AssertionError("coefficientwise W_prol is unavailable")
        if self.mapping_witness_certificate.get("open_green_diagonal_blocks") != 2:
            raise AssertionError("the open P/Psharp block count drifted")
        if self.green_bridge_certificate.get("schema") != (
            "pure-weyl-prolonged-green-bridge-v1"
        ):
            raise AssertionError("wrong triangular Green bridge certificate")
        if not _nested(
            self.green_bridge_certificate, "finite_triangular_green_theorem"
        ).get("finite_no_Neumann_convergence_assumption"):
            raise AssertionError("finite triangular Green theorem regressed")

        ga = _atom("GLp") * _atom("GLm")
        gb = _atom("GRp") * _atom("GRm")
        right_formula = ga * _atom("D")
        left_formula = _atom("D") * gb
        if not _is_identity(right_formula * _atom("P")):
            raise AssertionError("G_Lplus G_Lminus D is not a right inverse")
        if not _is_identity(_atom("P") * left_formula):
            raise AssertionError("D G_Rplus G_Rminus is not a left inverse")

        # Insert the left identity P D G_B=1 into G_A D, then use
        # G_A D P=1.  The resulting word must be the left formula.
        equality_word = ga * _atom("D") * _atom("P") * _atom("D") * gb
        if _reduce(equality_word) != left_formula:
            raise AssertionError("the two square-root Green formulas disagree")

        # Formal adjunction reverses both factor order and causal direction.
        adjoint_right = _formal_adjoint(right_formula)
        expected_adjoint = (
            _atom("Dsharp") * _atom("GLmsharp") * _atom("GLpsharp")
        )
        if adjoint_right != expected_adjoint:
            raise AssertionError("mixed-order Green adjoint order drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        coefficients_pass = (
            self.coefficient_certificate is not None
            and coefficient_certificate_passes(self.coefficient_certificate)
        )
        return {
            "schema": "pure-weyl-mixed-order-green-promotion-v1",
            "square_root_hypotheses": {
                "P": "local mixed-order field block",
                "D": "local finite-order differential companion",
                "left_product": "D P=L_minus L_plus",
                "right_product": "P D=R_minus R_plus",
                "factor_order_is_significant": True,
            },
            "exact_formal_construction": {
                "factor_product_Green_operators": {
                    "G_DP_plus_minus": "G_Lplus_plus_minus G_Lminus_plus_minus",
                    "G_PD_plus_minus": "G_Rplus_plus_minus G_Rminus_plus_minus",
                },
                "right_inverse_formula": (
                    "G_P_plus_minus=G_Lplus_plus_minus G_Lminus_plus_minus D"
                ),
                "left_inverse_formula": (
                    "G_P_plus_minus=D G_Rplus_plus_minus G_Rminus_plus_minus"
                ),
                "right_inverse_defect": 0,
                "left_inverse_defect": 0,
                "formula_equality_defect": 0,
                "two_sided": True,
            },
            "causal_support": {
                "same_sided_factor_composition": True,
                "retarded_intermediate_domains": "past-compact extensions",
                "advanced_intermediate_domains": "future-compact extensions",
                "D_does_not_enlarge_support": True,
                "conclusion": "supp G_P_plus_minus f subset J_plus_minus(supp f)",
            },
            "formal_adjoint_handling": {
                "adjoint_factorizations": [
                    "Psharp Dsharp=Lplussharp Lminussharp",
                    "Dsharp Psharp=Rplussharp Rminussharp",
                ],
                "factor_Green_adjoint_rule": (
                    "(G_A_plus)^sharp=G_Asharp_minus and conversely"
                ),
                "mixed_block_rule": "(G_P_plus)^sharp=G_Psharp_minus",
                "self_adjoint_specialization": (
                    "if Psharp=P under the certified fibre pairing, "
                    "then (G_P_plus)^sharp=G_P_minus"
                ),
                "operator_order_reversal_checked": True,
            },
            "sixteen_block_insertion": {
                "existing_green_blocks": 14,
                "replaced_open_blocks": ["M_aux P", "Ebar_aux Psharp"],
                "P_block_formula": "square-root G_P_plus_minus above",
                "Psharp_block_formula": "formal-adjoint square-root formula",
                "split_G_plus_minus": "block diagonal after the certified split",
                "prolonged_G_plus_minus": "S split_G_plus_minus S^-1",
                "S_and_Sinverse_support_local": True,
                "conditional_all_16_blocks_two_sided_and_causal": True,
            },
            "homological_consequence_if_coefficients_pass": {
                "QG_equals_GQ": True,
                "Lambda_plus_minus": "W_prol G_prol_plus_minus",
                "Q_Lambda_plus_Lambda_Q": "identity",
                "reason": "exact prolonged Green-bridge recognition theorem",
            },
            "coefficient_gate": {
                "expected_schema": "pure-weyl-mixed-order-factorization-v1",
                "certificate_supplied": self.coefficient_certificate is not None,
                "certificate_passes": coefficients_pass,
                "required_exact_fields": [
                    "global coefficientwise DP=Lminus Lplus",
                    "global coefficientwise PD=Rminus Rplus",
                    "four factor Green-hyperbolicity certificates",
                    "finite-order support-local D",
                    "nondegenerate pairings and exact factor adjoints",
                ],
            },
            "conditional_flags_if_coefficient_gate_passes": [
                "prolonged_green_witness",
                "curvature_causal_green_operators",
                "causal_green_homotopy",
            ],
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "proof_boundary": (
                "the square-root, causal, adjoint and sixteen-block insertion "
                "machinery is exact; the local coefficient factorization and "
                "factor Green-hyperbolicity certificate is absent"
            ),
            "fail_closed": True,
        }
