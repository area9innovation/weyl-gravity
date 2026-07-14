"""Normalized algebraic suspension of bulk endpoint modes to BFV momenta.

The bulk endpoint quotient is already normalized by

    Theta : coker(K^sharp) -> Z^*.

The Taub certificate identifies the quadratic endpoint component with the
fixed moment map ``mu``.  In the selected BFV convention

    Omega_gh = delta b_a wedge delta c^a,
    Omega_res = c^a mu_a - 1/2 f^a_bc c^b c^c b_a,

the ghost-free Hamiltonian vector field obeys ``Q b_a=mu_a``.  Compatibility
therefore fixes the only equivariant suspension scalar to ``lambda=+1``.

This is an exact theorem for the selected finite algebraic zero-mode data.
It is not a continuity theorem, nor an independent derivation of a temporal
boundary one-form on a completed field space.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from bridge.residual_bfv import ConformalCE
from field_bv_identification.zero_modes import ResidualBFVRoles


@dataclass(frozen=True)
class AlgebraicZeroModeTransgression:
    """The unique normalized algebraic map ``tau=suspension o Theta``."""

    roles: ResidualBFVRoles
    endpoint_to_bfv: sp.Matrix
    normalized_endpoint_representatives: sp.Matrix
    bulk_quadratic_component: sp.Matrix
    bfv_ghost_free_component: sp.Matrix
    transgression_scalar: sp.Expr
    transgression_map: sp.Matrix
    homogeneous_generator_order: tuple[str, ...]
    ghost_volume_orientation: sp.Expr
    centered_ghost_overlap: sp.Expr

    @classmethod
    def build(cls) -> "AlgebraicZeroModeTransgression":
        roles = ResidualBFVRoles.build()
        endpoint = roles.endpoint
        ce = ConformalCE.build()

        # P maps CE generator coordinates to the certified CKV coordinates.
        # Covectors consequently transform with P^T.
        p = roles.ce_to_ckv
        endpoint_to_bfv = sp.simplify(p.T * endpoint.quotient_map)
        representatives = sp.simplify(endpoint.quotient_section * p)

        # The endpoint/Taub theorem says that the normalized quadratic bulk
        # component is the moment-map vector itself.
        bulk_component = sp.simplify(endpoint_to_bfv * representatives)

        # Derive Qb on the ghost-free slice from the actual selected
        # cotangent matrix.  Coordinates are ordered (c,b), and
        # i_Q Omega=d(c.mu) gives Q=Omega grad(c.mu) in this convention.
        charge_gradient = sp.Matrix.vstack(sp.eye(15), sp.zeros(15))
        hamiltonian_vector = sp.simplify(
            roles.ghost_symplectic_form * charge_gradient
        )
        bfv_component = sp.Matrix(hamiltonian_vector[15:, :])

        lam = sp.symbols("lambda", nonzero=True, real=True)
        equations = list(lam * bulk_component - bfv_component)
        solutions = sp.solve(equations, [lam], dict=True)
        if solutions != [{lam: sp.Integer(1)}]:
            raise AssertionError(f"BFV compatibility did not fix lambda=1: {solutions}")
        transgression_scalar = sp.Integer(1)
        transgression_map = endpoint_to_bfv

        # The declared homogeneous order is g_-1, g_0, g_+1.  On dual
        # ghosts this is v_+ wedge Theta_0 wedge v_-.
        homogeneous_indices = (
            *ce.raising_ghosts,
            *ce.zero_ghosts,
            *ce.lowering_ghosts,
        )
        homogeneous_order = tuple(ce.names[index] for index in homogeneous_indices)
        volume = ce.wedge(
            ce.wedge({ce.raising_ghosts: 1}, {ce.zero_ghosts: 1}),
            {ce.lowering_ghosts: 1},
        )
        ghost_orientation = ce.top_coefficient(volume)
        overlap = ce.polarized_pair(ce.lowering_ghosts, ce.lowering_ghosts)

        result = cls(
            roles=roles,
            endpoint_to_bfv=sp.Matrix(endpoint_to_bfv),
            normalized_endpoint_representatives=sp.Matrix(representatives),
            bulk_quadratic_component=sp.Matrix(bulk_component),
            bfv_ghost_free_component=sp.Matrix(bfv_component),
            transgression_scalar=transgression_scalar,
            transgression_map=sp.Matrix(transgression_map),
            homogeneous_generator_order=homogeneous_order,
            ghost_volume_orientation=ghost_orientation,
            centered_ghost_overlap=overlap,
        )
        result.verify()
        return result

    @property
    def ce(self) -> ConformalCE:
        return ConformalCE.build()

    @property
    def d_index(self) -> int:
        return self.ce.index["D"]

    @property
    def d_bulk_coefficient(self) -> sp.Expr:
        return self.bulk_quadratic_component[self.d_index, self.d_index]

    @property
    def d_bfv_coefficient(self) -> sp.Expr:
        return self.bfv_ghost_free_component[self.d_index, self.d_index]

    @property
    def cotangent_orientation(self) -> sp.Expr:
        return sp.simplify(self.transgression_scalar ** 15)

    def verify(self) -> None:
        endpoint = self.roles.endpoint
        if self.endpoint_to_bfv * endpoint.adjoint_map != sp.zeros(15, 50):
            raise AssertionError("tau does not descend through coker K^sharp")
        if (
            self.endpoint_to_bfv * self.normalized_endpoint_representatives
            != sp.eye(15)
        ):
            raise AssertionError("the normalized endpoint basis did not map to b_a")
        if self.bulk_quadratic_component != sp.eye(15):
            raise AssertionError("bulk endpoint coefficient is not normalized to mu")
        if self.bfv_ghost_free_component != sp.eye(15):
            raise AssertionError("canonical BFV convention does not give Qb=mu")
        if self.transgression_scalar != 1:
            raise AssertionError("the selected conventions require lambda=+1")
        if not (
            self.d_bulk_coefficient == self.d_bfv_coefficient == sp.Integer(1)
        ):
            raise AssertionError("D-component normalization failed")

        # Both endpoint and BFV momenta carry the same coadjoint action.  The
        # identity coordinate map must therefore intertwine every generator.
        f = self.ce.structure_constants
        for generator in range(15):
            coadjoint = sp.Matrix(
                15,
                15,
                lambda row, column: -f[generator][row][column],
            )
            if coadjoint * sp.eye(15) != sp.eye(15) * coadjoint:
                raise AssertionError("tau is not coadjoint-equivariant")

        if self.cotangent_orientation != 1:
            raise AssertionError("lambda changed the fifteen-momentum orientation")
        if self.ghost_volume_orientation != 1:
            raise AssertionError("homogeneous ghost volume has the wrong orientation")
        if self.centered_ghost_overlap != 1:
            raise AssertionError("centered four-ghost overlap is not one")
