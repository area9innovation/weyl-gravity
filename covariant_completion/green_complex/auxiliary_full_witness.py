"""Exact symbol witness for the ordinary-derivative auxiliary realization.

This is the causal fallback allowed by the project brief.  It does not turn
the unresolved same-bundle product ``H_- H_+`` into a claim.  Instead it
uses a locally and support-preservingly equivalent second-order field
system.  The complete curved lower-coefficient table is deliberately kept
as a separate certification obligation.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from covariant_completion.auxiliary_witness import (
    CausalAuxiliaryReduction,
    OrdinaryDerivativeWeylSystem,
)
from covariant_completion.auxiliary_equivalence import GeneralizedAuxiliaryRetract


def _digest(matrix: sp.MatrixBase) -> str:
    payload = sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class AuxiliaryFullGreenWitness:
    system: OrdinaryDerivativeWeylSystem
    reduction: CausalAuxiliaryReduction
    generalized_retract: GeneralizedAuxiliaryRetract

    @staticmethod
    def build() -> "AuxiliaryFullGreenWitness":
        generalized_retract = GeneralizedAuxiliaryRetract.build()
        result = AuxiliaryFullGreenWitness(
            system=OrdinaryDerivativeWeylSystem.build(),
            reduction=CausalAuxiliaryReduction.build(),
            generalized_retract=generalized_retract,
        )
        result.verify(reverify_retract=False)
        return result

    def verify(self, *, reverify_retract: bool = True) -> None:
        if self.system.ghost_operator.shape != (9, 9):
            raise AssertionError("wrong auxiliary ghost block")
        if self.system.field_fibre_pairing.rank() != 24:
            raise AssertionError("wrong auxiliary field block")
        if self.reduction.ghost_new_to_old.det() != 1:
            raise AssertionError("the causal ghost reduction is not invertible")
        if self.reduction.field_new_to_old.det() != 1:
            raise AssertionError("the causal field reduction is not invertible")
        if reverify_retract:
            self.generalized_retract.verify()

        q_symbol, witness_symbol, pairing, witness_operator = self.symbol_matrices()
        if sp.simplify(q_symbol * q_symbol) != sp.zeros(66):
            raise AssertionError("the auxiliary minimal symbol is not a complex")

        assembled = sp.simplify(
            q_symbol * witness_symbol + witness_symbol * q_symbol
        )
        if assembled != witness_operator:
            raise AssertionError("the exact auxiliary QW+WQ identity failed")

        negative_covector = {
            component: -component for component in self.system.covector
        }
        if sp.simplify(
            pairing * witness_symbol
            - witness_symbol.subs(negative_covector).T * pairing
        ) != sp.zeros(66):
            raise AssertionError("the auxiliary witness is not formally self-adjoint")
        if sp.simplify(
            pairing * witness_operator
            - witness_operator.subs(negative_covector).T * pairing
        ) != sp.zeros(66):
            raise AssertionError(
                "the degreewise auxiliary witness operator is not formally self-adjoint"
            )

    def symbol_matrices(
        self,
    ) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix]:
        """Return the exact four-row flat-symbol witness matrices.

        The dual rows are identified with the primal rows using the perfect
        fibre pairings ``J_aux`` and ``Y_ghost``.  Curvature completion changes
        only lower-order coefficients, while this matrix identity fixes the
        full principal and Stueckelberg couplings relevant to hyperbolicity.
        """

        system = self.system
        gauge = system.gauge_map
        companion = system.gauge_condition
        field_equation = sp.simplify(
            system.field_fibre_pairing.inv()
            * system.gauge_invariant_flat_hessian
        )

        # Degrees have dimensions 9,24,24,9.
        q_symbol = sp.zeros(66)
        q_symbol[9:33, 0:9] = gauge
        q_symbol[33:57, 9:33] = field_equation
        q_symbol[57:66, 33:57] = companion

        witness_symbol = sp.zeros(66)
        witness_symbol[0:9, 9:33] = companion
        witness_symbol[9:33, 33:57] = sp.eye(24)
        witness_symbol[33:57, 57:66] = gauge

        pairing = sp.zeros(66)
        pairing[0:9, 57:66] = system.gauge_fixing_pairing
        pairing[57:66, 0:9] = system.gauge_fixing_pairing
        pairing[9:33, 33:57] = system.field_fibre_pairing
        pairing[33:57, 9:33] = system.field_fibre_pairing

        ghost_operator = companion * gauge
        field_operator = system.field_witness_operator
        witness_operator = sp.zeros(66)
        witness_operator[0:9, 0:9] = ghost_operator
        witness_operator[9:33, 9:33] = field_operator
        witness_operator[33:57, 33:57] = field_operator
        witness_operator[57:66, 57:66] = ghost_operator
        return q_symbol, witness_symbol, pairing, witness_operator

    def certificate(self, *, reverify: bool = True) -> dict[str, object]:
        if reverify:
            self.verify()
        q_symbol, witness_symbol, pairing, witness_operator = self.symbol_matrices()
        return {
            "schema": "pure-weyl-auxiliary-symbol-green-witness-v3",
            "category": (
                "exact cylinder Fourier-symbol algebra; the retract formulas "
                "are finite differential or pointwise support-local maps"
            ),
            "realization": (
                "ordinary-derivative h--f--v BV Fourier complex with an exact "
                "66-to-30 SDR; its formulas are support local"
            ),
            "witness_blocks": {
                "M_to_G": "C_aux (modified de Donder companion)",
                "E_to_M": "J_aux^{-1}",
                "I_to_E": "C_aux^sharp",
            },
            "identity": "P_aux=Q_aux W_aux+W_aux Q_aux",
            "exact_symbol_checks": {
                "Q_squared": "zero",
                "QW_plus_WQ": "P_aux",
                "field_block": "J_aux^{-1}E_aux+K_aux C_aux",
                "companion_adjoint": "Y C(zeta)=K(-zeta)^T J_aux",
            },
            "degreewise_operators": {
                "ghost": {
                    "operator": "C_aux K_aux",
                    "normalized_principal_symbol": "zeta^2 I_9",
                    "wave_principal_symbol_verified": True,
                    "curved_global_operator_verified": False,
                },
                "field": {
                    "operator": "J_aux^{-1}E_aux+K_aux C_aux",
                    "normalized_principal_symbol": "zeta^2 I_24",
                    "wave_principal_symbol_verified": True,
                    "curved_global_operator_verified": False,
                },
                "antifield": {
                    "operator": "field block sharp",
                    "wave_principal_symbol_verified": True,
                    "curved_global_operator_verified": False,
                },
                "identity_antifield": {
                    "operator": "ghost block sharp",
                    "wave_principal_symbol_verified": True,
                    "curved_global_operator_verified": False,
                },
            },
            "formal_self_adjointness": {
                "W_aux_sharp_equals_W_aux_at_symbol_level": True,
                "symbol_convention": "A^sharp(zeta)=Pairing^{-1}A(-zeta)^T Pairing",
                "field_hessian_symbol_formally_self_adjoint": True,
                "antifield_symbol_blocks_are_formal_adjoints": True,
                "curved_integration_by_parts_check": False,
            },
            "green_operators": {
                "status": "formal consequence after curved globalization certificate A",
                "existence_if_A_passes": (
                    "unique G_plus and G_minus for every degreewise normally "
                    "hyperbolic curved operator on the globally hyperbolic cylinder"
                ),
                "commutation": "Q_aux G_plus/minus=G_plus/minus Q_aux",
                "reason": "[Q_aux,P_aux]=0 and uniqueness of causal Green operators",
            },
            "green_homotopies": {
                "definition": "Lambda_plus/minus=W_aux G_plus/minus",
                "identity": "Q Lambda_plus/minus+Lambda_plus/minus Q=1 on Gamma_c",
                "support": "supp Lambda_plus/minus f subset J_plus/minus(supp f)",
                "derivation": [
                    "Q^2=0 implies [Q,P]=0 for P=QW+WQ",
                    "uniqueness gives [Q,G_plus/minus]=0",
                    "(QW+WQ)G_plus/minus=P G_plus/minus=1",
                    "W is differential and therefore does not enlarge support",
                ],
                "status": "exact recognition identity, conditional on curved G_plus/minus",
            },
            "fourier_complex_deformation_retract": {
                "stueckelberg_pair": "Qv=-eta with support-preserving homotopy",
                "auxiliary_tensor": (
                    "exact equation-of-motion shift followed by the pointwise-invertible mass block"
                ),
                "all_row_sdr": (
                    "66-to-30 chain maps and i p-1=Q k+k Q on the "
                    "36-dimensional added cotangent sector"
                ),
                "compact_support": True,
                "spacelike_compact_support": True,
                "physical_green_recovery_after_A": (
                    "once curved Green operators exist, their h-h Schur block is "
                    "the fourth-order pure-Weyl Green operator in the selected gauge"
                ),
            },
            "trace_and_nonminimal_reattachment": {
                "trace_weyl_doublet": "pointwise contractible P=I block",
                "diff_antighost_multiplier_and_dual": "pointwise contractible P=I blocks",
                "weyl_antighost_multiplier_and_dual": "pointwise contractible P=I blocks",
                "retarded_equals_advanced_on_algebraic_blocks": True,
                "support_unchanged": True,
            },
            "global_ckv_guard": (
                "no conformal-Killing projector enters a local operator; the fifteen "
                "non-compactly-supported smooth modes remain global cohomology and "
                "are reattached once through the certified residual BFV sector"
            ),
            "theorem_boundary": (
                "this establishes the exact four-row auxiliary symbol witness and "
                "66-to-30 Fourier SDR with support-local formulas.  It does not "
                "assert the still-missing curved lower-coefficient/retract/adjoint "
                "certificate, a direct same-bundle "
                "factorization of B+KT/2, or covariant/Cauchy pairing normalization"
            ),
            "matrix_sha256": {
                "Q_aux": _digest(q_symbol),
                "W_aux": _digest(witness_symbol),
                "BV_pairing": _digest(pairing),
                "P_aux": _digest(witness_operator),
            },
        }
