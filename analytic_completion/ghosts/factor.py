"""Separate ghost topology from the centered complementary-degree pairing."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
from math import comb

from bridge.residual_bfv.conformal_ce import ConformalCE, Monomial


@lru_cache(maxsize=1)
def _certified_ce() -> ConformalCE:
    """Build the immutable residual algebra once per verification process."""

    return ConformalCE.build()


@dataclass(frozen=True)
class ResidualGhostFactor:
    ce: ConformalCE

    @classmethod
    def build(cls) -> "ResidualGhostFactor":
        return cls(_certified_ce())

    def degree_dimensions(self) -> dict[int, int]:
        """Dimensions of all compact-degree eigenspaces in Lambda(g*)."""

        counts: Counter[int] = Counter()
        for degree in range(self.ce.dimension + 1):
            for monomial in combinations(range(self.ce.dimension), degree):
                counts[self.ce.compact_degree(monomial)] += 1
        return dict(sorted(counts.items()))

    def degree_and_ghost_number_dimensions(self) -> dict[tuple[int, int], int]:
        counts: Counter[tuple[int, int]] = Counter()
        for ghost_number in range(self.ce.dimension + 1):
            for monomial in combinations(range(self.ce.dimension), ghost_number):
                counts[(self.ce.compact_degree(monomial), ghost_number)] += 1
        return dict(sorted(counts.items()))

    def verify(self) -> None:
        self.ce.verify_ce(maximum_degree=5)
        expected = {
            compact_degree: 2**7 * comb(8, 4 + compact_degree)
            for compact_degree in range(-4, 5)
        }
        if self.degree_dimensions() != expected:
            raise AssertionError("ghost compact-degree generating function is wrong")
        if self.ce.polarized_pair(
            self.ce.lowering_ghosts, self.ce.lowering_ghosts
        ) != 1:
            raise AssertionError("centered four-ghost representative is not normalized")

        # With the positive exterior basis the wedge and contraction
        # operators are Hilbert adjoints and each has operator norm one.
        for ghost in range(15):
            for degree in range(3):
                for monomial in combinations(range(15), degree):
                    contracted = self.ce.contract(ghost, {monomial: 1})
                    if any(abs(value) != 1 for value in contracted.values()):
                        raise AssertionError("ghost contraction is not a partial isometry")

        # The centered insertion deliberately is not a global ghost metric:
        # a monomial containing a zero-degree ghost duplicates that ghost in
        # Theta_0 and hence has zero pairing with every ket.
        zero_ghost_example: Monomial = (self.ce.zero_ghosts[0],)
        for second in ((), self.ce.lowering_ghosts, self.ce.raising_ghosts):
            if self.ce.polarized_pair(zero_ghost_example, second) != 0:
                raise AssertionError("centered insertion unexpectedly became global")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-residual-ghost-topology-v1",
            "hilbert_topology": "ordered exterior monomials are orthonormal",
            "dimension": 2**15,
            "compact_spectrum": list(range(-4, 5)),
            "compact_degree_dimensions": {
                str(key): value for key, value in self.degree_dimensions().items()
            },
            "ghost_wedge_contraction_norm": 1,
            "centered_pairing_bounded": True,
            "centered_four_ghost_overlap": 1,
            "centered_pairing_role": "complementary-degree cohomological insertion",
            "centered_pairing_global_nondegenerate": False,
            "state_krein_topology": "J_Fock tensor identity_on_ghost_Hilbert_space",
            "scope_guard": (
                "the centered insertion is not called a nondegenerate Krein metric "
                "on the full ghost exterior algebra"
            ),
        }
