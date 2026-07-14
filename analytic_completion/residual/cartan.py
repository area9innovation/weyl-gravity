"""Bounded off-center Cartan contraction with explicit domain control."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from analytic_completion.residual.closed_brst import ClosedResidualBRST


@dataclass(frozen=True)
class BoundedCartanContraction:
    brst: ClosedResidualBRST

    @classmethod
    def build(cls) -> "BoundedCartanContraction":
        return cls(ClosedResidualBRST.build())

    def verify(self, verify_dependencies: bool = True) -> None:
        if verify_dependencies:
            self.brst.verify()
        ce = self.brst.blocks.ghosts.ce
        if max(abs(value) for value in ce.ghost_degrees) != 1:
            raise AssertionError("iota_D normalization is not the certified one")

        # The maximal exterior contraction is a signed deletion matrix in an
        # orthonormal monomial basis, hence has norm one.  Verify all 2^15
        # basis vectors, which is still a finite exact check.
        for mask in range(1 << ce.dimension):
            monomial = tuple(index for index in range(ce.dimension) if mask >> index & 1)
            image = ce.contract(ce.index["D"], {monomial: sp.Integer(1)})
            if len(image) > 1 or any(abs(value) != 1 for value in image.values()):
                raise AssertionError("iota_D is not a norm-one partial isometry")

    def certificate(self, verify: bool = True) -> dict[str, object]:
        if verify:
            self.verify()
        return {
            "schema": "pure-weyl-bounded-cartan-contraction-v1",
            "cartan_identity_on_core": "Q iota_D + iota_D Q = L",
            "iota_D_bounded": True,
            "iota_D_norm": 1,
            "off_center_inverse": "h_delta=iota_D/delta for integer delta!=0",
            "h_bounded": True,
            "h_norm_bound": 1,
            "domain_invariance": True,
            "domain_estimate": (
                "||Q_delta h_delta Psi_delta|| <= ||Psi_delta|| "
                "+ ||h_delta|| ||Q_delta Psi_delta||"
            ),
            "closed_identity": "Qbar h + h Qbar = 1-P_0 on Dom(Qbar)",
            "proof_method": (
                "apply the finite-block identity and the displayed square-summable "
                "domain estimate; no continuity assumption on unbounded Qbar"
            ),
            "requires_full_residual_gauging": True,
            "D_as_physical_hamiltonian_supported": False,
        }
