"""Keep bulk endpoint, BFV momenta, and obstruction values distinct.

The bulk endpoint and the BFV momentum transform in the same dual module,
but they live in different complexes and degrees.  A time-slice BV--BFV
transgression is expected to identify them up to one scalar.  This module
certifies the roles and dimensions; it deliberately does not manufacture
that still-uncomputed scalar.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from bridge.residual_bfv import ConformalCE
from field_bv_identification.gauge_fixed_equivalence.contraction import (
    ZeroModePreservation,
)
from field_bv_identification.zero_modes.dual_cokernel import (
    DualEndpointCokernel,
)


@dataclass(frozen=True)
class ResidualRole:
    symbol: str
    space: str
    ghost_degree: str
    origin: str
    role: str
    is_bfv_coordinate: bool
    transgression_relation: str


@dataclass(frozen=True)
class ResidualBFVRoles:
    """Exact role ledger before the one-scalar BV--BFV transgression check."""

    endpoint: DualEndpointCokernel
    ce_to_ckv: sp.Matrix
    ghost_symplectic_form: sp.Matrix
    ghost_replacement_basis: sp.Matrix
    endpoint_decomposition_basis: sp.Matrix
    roles: tuple[ResidualRole, ...]

    @classmethod
    def build(cls) -> "ResidualBFVRoles":
        endpoint = DualEndpointCokernel.build()
        compact = ZeroModePreservation.build()
        ce = ConformalCE.build()
        ckv_index = {label: index for index, label in enumerate(endpoint.labels)}

        def ckv_label(name: str) -> str:
            if name == "D":
                return "D"
            if name.startswith("R"):
                return "M" + name[1:]
            if name.startswith("K+_"):
                return "K" + name[-1]
            if name.startswith("K-_"):
                return "P" + name[-1]
            raise ValueError(f"unknown residual generator {name}")

        ce_to_ckv = sp.zeros(15)
        for ce_column, name in enumerate(ce.names):
            ce_to_ckv[ckv_index[ckv_label(name)], ce_column] = 1

        # Ordering (c^a,b_a).  This is the even cotangent form associated
        # with Omega_gh = delta b_a wedge delta c^a.
        ghost_symplectic = sp.zeros(30)
        ghost_symplectic[:15, 15:] = -sp.eye(15)
        ghost_symplectic[15:, :15] = sp.eye(15)

        ghost_replacement = sp.Matrix.hstack(
            compact.complement_basis,
            endpoint.zero_basis,
        )
        endpoint_decomposition = sp.Matrix.hstack(
            endpoint.adjoint_map,
            endpoint.quotient_section,
        )
        roles = (
            ResidualRole(
                "c^a",
                "Z[1]",
                "+1",
                "the fifteen local gauge reducibilities, moved to residual BFV",
                "residual ghost",
                True,
                "identity on Z after zero-mode extraction",
            ),
            ResidualRole(
                "b_a",
                "Z^*[-1]",
                "-1",
                "cotangent coordinates on T^*[0](Z[1])",
                "BFV ghost momentum",
                True,
                "target of tau:H_endpoint^bulk -> Z^*[-1]; scalar lambda open",
            ),
            ResidualRole(
                "mu_a",
                "Z^*-valued functions on the physical phase space",
                "0",
                "quadratic Taub/Kuranishi obstruction map",
                "residual constraint",
                False,
                "takes values in the same Z^* module but is not a coordinate",
            ),
            ResidualRole(
                "[u]",
                "coker K^sharp ~= Z^*",
                "local tangent degree +2",
                "dual endpoint cohomology of the minimal BV detour chain",
                "obstruction codomain",
                False,
                "source of tau=lambda Theta into the BFV momentum module",
            ),
        )
        result = cls(
            endpoint=endpoint,
            ce_to_ckv=sp.Matrix(ce_to_ckv),
            ghost_symplectic_form=sp.Matrix(ghost_symplectic),
            ghost_replacement_basis=ghost_replacement,
            endpoint_decomposition_basis=endpoint_decomposition,
            roles=roles,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.ce_to_ckv.T * self.ce_to_ckv != sp.eye(15):
            raise AssertionError("CE and CKV bases are not related by a permutation")
        if self.ghost_symplectic_form.rank() != 30:
            raise AssertionError("the adjoined BFV cotangent form is degenerate")
        if self.ghost_symplectic_form.T != -self.ghost_symplectic_form:
            raise AssertionError("the BFV cotangent matrix is not antisymmetric")
        if self.ghost_replacement_basis.rank() != 65:
            raise AssertionError("local complement plus one residual ghost copy is incomplete")
        if self.endpoint_decomposition_basis.rank() != 65:
            raise AssertionError("exact endpoint plus obstruction quotient is incomplete")

        by_symbol = {role.symbol: role for role in self.roles}
        if by_symbol["b_a"].origin == by_symbol["[u]"].origin:
            raise AssertionError("bulk endpoint and BFV momentum lost their degree distinction")
        if not by_symbol["b_a"].is_bfv_coordinate:
            raise AssertionError("b_a is not an adjoined BFV coordinate")
        if by_symbol["[u]"].is_bfv_coordinate:
            raise AssertionError("dual endpoint was incorrectly retained as BFV momentum")
        if by_symbol["mu_a"].is_bfv_coordinate:
            raise AssertionError("the constraint value was incorrectly made a coordinate")
        if "scalar lambda open" not in by_symbol["b_a"].transgression_relation:
            raise AssertionError("the uncomputed transgression scalar was hidden")

        if self.endpoint.zero_dimension != 15:
            raise AssertionError("there is not exactly one residual ghost copy")
        if self.endpoint.obstruction_dimension != 15:
            raise AssertionError("there is not exactly one obstruction codomain")
