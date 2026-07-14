"""Support-local Stueckelberg and generalized-auxiliary reduction."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from .ordinary_derivative import OrdinaryDerivativeWeylSystem


def _digest(matrix: sp.MatrixBase) -> str:
    payload = sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class CausalAuxiliaryReduction:
    """The exact local change isolating the conformal-boost doublet.

    Put

    ``eta=xi_0-d sigma`` and ``f_hat=f+2 d_(a v_b)``.

    Then ``Qv=-eta`` and no other transformed field depends on ``eta``.
    Both the change and its inverse are finite differential operators, so
    they preserve supports.  The remaining ``f_hat`` equation is the
    pointwise-invertible auxiliary equation certified by
    :mod:`ordinary_derivative`.
    """

    system: OrdinaryDerivativeWeylSystem
    ghost_new_to_old: sp.Matrix
    field_new_to_old: sp.Matrix
    transformed_gauge_map: sp.Matrix

    @staticmethod
    def build() -> "CausalAuxiliaryReduction":
        system = OrdinaryDerivativeWeylSystem.build()
        zeta = system.covector

        # New ghost order remains (xi_-2[4], eta[4], sigma), while old xi_0
        # equals eta+d sigma.
        ghost_new_to_old = sp.eye(9)
        ghost_new_to_old[4:8, 8] = zeta

        # New field order is (h,f_hat,v), with
        # f_old=f_hat-2 d_(a v_b).  The repository symmetrization writes the
        # latter as z_a v_b+z_b v_a.
        field_new_to_old = sp.eye(24)
        for vector_column in range(4):
            vector = sp.zeros(4, 1)
            vector[vector_column] = 1
            symmetric_gradient = zeta * vector.T + vector * zeta.T
            field_new_to_old[10:20, 20 + vector_column] = -system.tensor_coordinates(
                symmetric_gradient
            )

        transformed = sp.simplify(
            field_new_to_old.inv()
            * system.gauge_map
            * ghost_new_to_old
        )
        result = CausalAuxiliaryReduction(
            system=system,
            ghost_new_to_old=ghost_new_to_old,
            field_new_to_old=field_new_to_old,
            transformed_gauge_map=transformed,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.ghost_new_to_old.det() != 1:
            raise AssertionError("ghost Stueckelberg change is not unipotent")
        if self.field_new_to_old.det() != 1:
            raise AssertionError("field Stueckelberg change is not unipotent")

        zeta = self.system.covector
        expected = sp.zeros(24, 9)
        # h transforms under xi_-2 and sigma exactly as before.
        expected[:10, :4] = self.system.gauge_map[:10, :4]
        expected[:10, 8] = self.system.gauge_map[:10, 8]
        # f_hat transforms only by the Hessian of sigma.
        expected_f_sigma = 2 * zeta * zeta.T
        expected[10:20, 8] = self.system.tensor_coordinates(expected_f_sigma)
        # v and eta are a unit algebraic doublet.
        expected[20:24, 4:8] = -sp.eye(4)
        if sp.simplify(self.transformed_gauge_map - expected) != sp.zeros(24, 9):
            raise AssertionError("the conformal-boost Stueckelberg pair did not split")

        # The algebraic contraction is s(eta)=-v for Qv=-eta.
        q_pair = sp.Matrix([[0, 0], [-1, 0]])
        s_pair = sp.Matrix([[0, -1], [0, 0]])
        if q_pair * s_pair + s_pair * q_pair != sp.eye(2):
            raise AssertionError("the Stueckelberg doublet homotopy failed")

        # Exact Schur complement of the algebraic auxiliary tensor.  This is
        # computed on the gauge-fixed principal tensor block; on trace-free
        # tensors it is a scalar biwave symbol.
        de_witt = (
            self.system.tensor_pairing
            - sp.Rational(1, 2) * self.system.trace.T * self.system.trace
        )
        schur = sp.simplify(
            -de_witt
            * self.system.auxiliary_mass_hessian.inv()
            * de_witt
        )
        # Include the nine trace-free basis vectors explicitly.
        from covariant_completion.minimal_witness.principal_symbols import (
            MinimalWitnessPrincipalSymbols,
        )

        tracefree = MinimalWitnessPrincipalSymbols.build()
        inclusion = sp.zeros(10, 9)
        for column, tensor in enumerate(tracefree.tensor_basis):
            inclusion[:, column] = self.system.tensor_coordinates(tensor)
        tracefree_pairing = sp.simplify(
            inclusion.T * self.system.tensor_pairing * inclusion
        )
        normalized_schur = sp.simplify(
            tracefree_pairing.inv() * inclusion.T * schur * inclusion
        )
        if normalized_schur != 2 * sp.eye(9):
            raise AssertionError("auxiliary Schur complement is not scalar on S^2_0")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-causal-auxiliary-reduction-v1",
            "local_changes": {
                "ghost": "eta=xi_0-d sigma",
                "field": "f_hat=f+2 d_(a v_b)",
                "changes_unipotent": True,
                "inverses_are_finite_differential_operators": True,
            },
            "contractible_stueckelberg_pair": {
                "differential": "Q v=-eta, Q eta=0",
                "homotopy": "s eta=-v, s v=0",
                "field_and_antifield_duals": True,
            },
            "remaining_gauge_transformations": {
                "Q h": "2 d_(a xi_minus_2_b)+g_ab sigma",
                "Q f_hat": "2 d_a d_b sigma plus cylinder lower-curvature terms",
                "eta_occurs_elsewhere": False,
            },
            "auxiliary_schur_complement": {
                "algebraic_mass_inverse": True,
                "tracefree_normalized_principal_symbol": "2 (zeta^2)^2 I_9",
                "h_h_green_block_after_curved_certificate": (
                    "after curved Green operators are constructed, the physical "
                    "fourth-order Green operator is their h-h Schur block"
                ),
            },
            "causal_support": {
                "field_redefinition_support_preserving": True,
                "inverse_redefinition_support_preserving": True,
                "auxiliary_elimination_support_preserving": True,
                "reason": (
                    "finite differential maps do not enlarge support, and the "
                    "only inverse used in elimination is pointwise algebraic"
                ),
            },
            "matrix_sha256": {
                "ghost_new_to_old": _digest(self.ghost_new_to_old),
                "field_new_to_old": _digest(self.field_new_to_old),
                "transformed_gauge_map": _digest(self.transformed_gauge_map),
            },
            "scope_guard": (
                "support-local reduction and principal Schur recovery are "
                "certified; the global retarded/advanced homotopy identities "
                "are emitted only after the degreewise Green operators are assembled"
            ),
        }
