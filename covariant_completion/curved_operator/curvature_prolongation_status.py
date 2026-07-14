"""Fail-closed status for the curvature-prolonged Green realization.

The exact null-symbol calculation already identifies the physical
helicity-two quotient and proves that the linearized Weyl symbol is an
isomorphism on it.  This module keeps that positive symbol theorem separate
from the two still-missing operator theorems: construction of the prolonged
BV complex and construction of its causal Green operators.
"""

from __future__ import annotations

from dataclasses import dataclass

from .null_symbol_quotient import CurvedNullSymbolQuotient


@dataclass(frozen=True)
class CurvatureProlongationStatus:
    quotient: CurvedNullSymbolQuotient
    curved_EB_equations: bool = False
    curved_EB_symmetric_hyperbolicity: bool = False
    curved_constraint_propagation: bool = False
    support_local_prolongation_retract: bool = False
    curvature_causal_green_operators: bool = False

    @staticmethod
    def build(
        quotient: CurvedNullSymbolQuotient | None = None,
    ) -> "CurvatureProlongationStatus":
        result = CurvatureProlongationStatus(
            quotient if quotient is not None else CurvedNullSymbolQuotient.build()
        )
        result.verify()
        return result

    @property
    def weyl_symbol_helicity_isomorphism(self) -> bool:
        return (
            self.quotient.quotient_dimension == 2
            and self.quotient.weyl_target_quotient_dimension == 2
            and self.quotient.induced_weyl_matrix.det() != 0
        )

    @property
    def curvature_prolonged_complex_exact(self) -> bool:
        return (
            self.curved_EB_equations
            and self.curved_constraint_propagation
            and self.support_local_prolongation_retract
        )

    @property
    def curvature_green_realization(self) -> bool:
        return (
            self.curvature_prolonged_complex_exact
            and self.curved_EB_symmetric_hyperbolicity
            and self.curvature_causal_green_operators
        )

    def verify(self) -> None:
        self.quotient.verify()
        if self.curved_EB_symmetric_hyperbolicity and not self.curved_EB_equations:
            raise AssertionError(
                "curved E/B hyperbolicity promoted before deriving its equations"
            )
        if self.curved_constraint_propagation and not self.curved_EB_equations:
            raise AssertionError(
                "curved constraint propagation promoted before deriving E/B"
            )
        if self.curvature_causal_green_operators and not (
            self.curved_EB_symmetric_hyperbolicity
            and self.curved_constraint_propagation
            and self.support_local_prolongation_retract
        ):
            raise AssertionError(
                "curvature Green operators promoted before the exact constrained "
                "support-local system"
            )
        if (
            self.curvature_prolonged_complex_exact
            and not self.weyl_symbol_helicity_isomorphism
        ):
            raise AssertionError(
                "curvature prolongation promoted without the exact reduced "
                "Weyl-symbol isomorphism"
            )
        if self.curvature_green_realization and not (
            self.curvature_prolonged_complex_exact
            and self.weyl_symbol_helicity_isomorphism
        ):
            raise AssertionError(
                "curvature Green realization promoted without its prolonged complex"
            )

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-curvature-prolongation-status-v1",
            "exact_symbol_reduction": {
                "domain": (
                    "(F/ker N_2)/(N_2^{-1} im K_1/ker N_2)"
                ),
                "target": "im W_2/W_2(N_2^{-1} im K_1)",
                "domain_dimension": self.quotient.quotient_dimension,
                "target_dimension": self.quotient.weyl_target_quotient_dimension,
                "induced_matrix": [
                    [str(value) for value in row]
                    for row in self.quotient.induced_weyl_matrix.tolist()
                ],
                "isomorphism": self.weyl_symbol_helicity_isomorphism,
                "full_fibre_exact_sequence_guard": (
                    "ker(W_2) is larger than im(K_1) on the un-reduced 24-field "
                    "fibre; exactness is asserted only on the displayed Hessian "
                    "reduction"
                ),
                "full_fibre_ker_W_equals_im_K_claimed": False,
            },
            "weyl_symbol_helicity_isomorphism": (
                self.weyl_symbol_helicity_isomorphism
            ),
            "curved_EB_equations": self.curved_EB_equations,
            "curved_EB_symmetric_hyperbolicity": (
                self.curved_EB_symmetric_hyperbolicity
            ),
            "curved_constraint_propagation": self.curved_constraint_propagation,
            "support_local_prolongation_retract": (
                self.support_local_prolongation_retract
            ),
            "curvature_causal_green_operators": (
                self.curvature_causal_green_operators
            ),
            "curvature_prolonged_complex_exact": (
                self.curvature_prolonged_complex_exact
            ),
            "curvature_green_realization": self.curvature_green_realization,
            "next_exact_step": (
                "construct the local Psi-W(h) defining row, Bianchi/Bach rows, "
                "and support-local prolongation SDR before promoting a causal "
                "electric/magnetic Weyl evolution"
            ),
            "fail_closed": True,
        }
