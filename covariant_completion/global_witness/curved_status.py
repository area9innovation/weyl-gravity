"""Audit the exact boundary between the symbol witness and its globalization.

The nonlinear ordinary-derivative action is a genuine covariant definition
of all lower-order coefficients.  What is not yet emitted by the repository
is the complete 24-by-24 first/zeroth-order cylinder coefficient table after
the background auxiliary tensor and the trace/Weyl triangular variables are
inserted.  This module records that distinction and prevents the exact symbol
identity from being mislabeled as the final curved operator certificate.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from covariant_completion.auxiliary_witness import OrdinaryDerivativeWeylSystem
from covariant_completion.curved_operator import CurvedOperatorIdentityStatus


@dataclass(frozen=True)
class CurvedAuxiliaryWitnessStatus:
    metric: sp.Matrix
    ricci: sp.Matrix
    scalar_curvature: sp.Integer
    background_auxiliary: sp.Matrix
    symbol_verified: bool
    action_definition_emitted: bool = True
    curved_gauge_map_emitted: bool = True
    derivative_normal_form_emitted: bool = True
    globalization_ledger_emitted: bool = True
    curved_lower_coefficient_table_emitted: bool = False
    curved_retract_chain_maps_emitted: bool = False

    @staticmethod
    def build() -> "CurvedAuxiliaryWitnessStatus":
        operator_status = CurvedOperatorIdentityStatus.build()
        background = operator_status.action.background
        metric = background.metric
        ricci = background.ricci
        scalar_curvature = sp.Integer(background.scalar_curvature)
        background_auxiliary = background.auxiliary_background
        OrdinaryDerivativeWeylSystem.build().verify()
        result = CurvedAuxiliaryWitnessStatus(
            metric=metric,
            ricci=ricci,
            scalar_curvature=scalar_curvature,
            background_auxiliary=background_auxiliary,
            symbol_verified=True,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if sp.trace(self.metric * self.ricci) != self.scalar_curvature:
            raise AssertionError("wrong cylinder scalar curvature")
        expected = -2 * self.ricci + sp.Rational(1, 3) * self.metric * self.scalar_curvature
        if self.background_auxiliary != expected:
            raise AssertionError("wrong auxiliary cylinder background")
        if self.background_auxiliary != sp.diag(-2, -2, -2, -2):
            raise AssertionError("unexpected cylinder auxiliary components")
        if not self.symbol_verified:
            raise AssertionError("the exact auxiliary symbol witness regressed")

    @property
    def complete(self) -> bool:
        return (
            self.symbol_verified
            and self.curved_lower_coefficient_table_emitted
            and self.curved_retract_chain_maps_emitted
        )

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-curved-auxiliary-witness-status-v1",
            "covariant_action": {
                "density": (
                    "-phi^{mu nu}G^b_(mu nu)-F(b)^2/4-phi^{mu nu}phi_mu nu/4"
                    "+(tr phi)^2/4"
                ),
                "G_b": (
                    "Ric+sym(nabla b)/2+b tensor b/2-"
                    "g(R+2 div b-b^2/2)/2"
                ),
                "defines_all_curved_coefficients": True,
            },
            "cylinder_background": {
                "metric_signature": "(-,+,+,+)",
                "Ricci_covariant_components": [0, 2, 2, 2],
                "scalar_curvature": int(self.scalar_curvature),
                "b_background": [0, 0, 0, 0],
                "phi_background": [-2, -2, -2, -2],
                "phi_formula": "-2 Ric+(R/3)g",
                "parallel_curvature_and_auxiliary": True,
            },
            "proved": [
                "exact covariant action and gauge symmetry define the global natural operator",
                "exact linearized cylinder gauge map includes Lie_xi(phi_background)",
                "exact curved gauge map reduces to the certified K_aux in the flat limit",
                "parallel-curvature derivative normal form is executable and idempotent",
                "the globalization ledger counts every required one-point jet vector",
                "exact flat/normal-frame Q^2 and QW+WQ symbol matrices",
                "scalar metric principal symbols in all four minimal degrees",
                "formal companion adjoint at symbol level",
            ],
            "remaining_for_certificate_A": [
                "emit the full first-order 24-by-24 cylinder coefficient matrices",
                "emit the full zeroth-order 24-by-24 cylinder coefficient matrices",
                "verify the curved trace/Weyl triangular variables against phi_background",
                "verify the curved 66-to-30 auxiliary inclusion, projection, and homotopy identities",
                "verify W^sharp=W by covariant integration by parts, including lower terms",
            ],
            "curved_lower_coefficient_table_emitted": self.curved_lower_coefficient_table_emitted,
            "curved_retract_chain_maps_emitted": self.curved_retract_chain_maps_emitted,
            "action_definition_emitted": self.action_definition_emitted,
            "curved_gauge_map_emitted": self.curved_gauge_map_emitted,
            "derivative_normal_form_emitted": self.derivative_normal_form_emitted,
            "globalization_ledger_emitted": self.globalization_ledger_emitted,
            "curved_operator_identity_status": (
                "covariant_completion/certificates/curved_operator_identity_status.json"
            ),
            "complete_curved_witness_certificate": self.complete,
            "guard": (
                "normal-frame wave symbols prove normal hyperbolicity only after the "
                "global curved operator and its lower coefficients have been instantiated; "
                "this status file does not promote that remaining implementation to a theorem"
            ),
        }
