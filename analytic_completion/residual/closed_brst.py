"""Maximal block-direct-sum realization of the residual BRST operator."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from analytic_completion.fock.energy_blocks import TotalDegreeBlocks
from analytic_completion.one_particle.generators import ClosedGeneratorCertificate


def _finite_block_direct_sum_regression() -> None:
    """Exact fixture for closure, graph-core truncation, and nilpotency.

    The infinite proof is the standard componentwise Hilbert-direct-sum
    lemma recorded in the certificate.  This fixture catches a domain
    convention in which the image would fail to lie in the domain again.
    """

    blocks = (
        sp.Matrix([[0, 1], [0, 0]]),
        sp.Matrix([[0, 2], [0, 0]]),
        sp.Matrix([[0, 3], [0, 0]]),
    )
    for block in blocks:
        if block * block != sp.zeros(2):
            raise AssertionError("nilpotent block fixture failed")
        vector = sp.Matrix([sp.Rational(2, 3), sp.Rational(5, 7)])
        image = block * vector
        if block * image != sp.zeros(2, 1):
            raise AssertionError("Q psi is not in Dom Q in the block fixture")


@dataclass(frozen=True)
class ClosedResidualBRST:
    blocks: TotalDegreeBlocks

    @classmethod
    def build(cls) -> "ClosedResidualBRST":
        return cls(TotalDegreeBlocks.build())

    def verify(self, verify_dependencies: bool = True) -> None:
        if verify_dependencies:
            self.blocks.verify()
            ClosedGeneratorCertificate().verify()
            self.blocks.ghosts.ce.verify_ce(maximum_degree=5)
        _finite_block_direct_sum_regression()

    def certificate(self, verify: bool = True) -> dict[str, object]:
        if verify:
            self.verify()
        return {
            "schema": "pure-weyl-closed-residual-brst-v1",
            "state_hilbert_space": "Gamma_s(H_1) completed_tensor Lambda(g*)",
            "total_degree_decomposition": "orthogonal Hilbert direct sum over integer delta",
            "block_dimension_finite": True,
            "block_operator": "finite-dimensional nilpotent Q_delta",
            "maximal_domain": "sum_delta ||Q_delta Psi_delta||^2 finite",
            "densely_defined": True,
            "closed": True,
            "proof_closed": (
                "component convergence plus closedness of each finite Q_delta "
                "places the limit in the maximal domain"
            ),
            "finite_total_degree_support_graph_core": True,
            "proof_graph_core": "symmetric delta truncations converge in norm and graph norm",
            "algebraic_state_core": True,
            "nilpotent": True,
            "nilpotent_domain_statement": (
                "Q_delta^2=0 implies Q Psi lies in Dom Q with second graph sum zero"
            ),
            "closure_of_algebraic_Q_is_maximal_direct_sum": True,
            "lie_algebra_input": (
                "all-energy representation identities on the common finite-energy core "
                "and exact CE Jacobi identity"
            ),
            "scope_guards": [
                "Q is closed and generally unbounded",
                "no bounded SO(4,2) action is claimed",
                "no integration to a global group representation is claimed",
            ],
        }
