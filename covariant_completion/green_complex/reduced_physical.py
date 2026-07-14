"""Green-hyperbolic realization of the reduced E/A/L physical system."""

from __future__ import annotations

from dataclasses import dataclass

from covariant_completion.physical_operator.tt_bach_factorization import (
    TTBachFactorization,
)
from covariant_completion.physical_operator.vector_wave_operator import VectorWaveFactor
from covariant_completion.sobolev.branch_spaces import BranchSobolevRealization


@dataclass(frozen=True)
class ReducedPhysicalGreenRealization:
    def verify(self) -> None:
        TTBachFactorization().verify()
        VectorWaveFactor().verify()
        BranchSobolevRealization().verify()

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-reduced-physical-green-v1",
            "spacetime": "Lorentzian R x S^3, unit radius",
            "operators": {
                "TT": "B_TT=P_minus P_plus",
                "vector": "P_A=d_t^2+C_1^2",
            },
            "normally_hyperbolic_factors": ["P_minus", "P_plus", "P_A"],
            "green_hyperbolic_blocks": ["B_TT", "P_A"],
            "composition_theorem_used": True,
            "direct_sum_theorem_used": True,
            "advanced_retarded_support": True,
            "cauchy_sobolev_realization": True,
            "energy_mode_krein_equivalence": True,
            "scope": "reduced physical E/A/L system",
            "full_bv_green_witness": False,
        }
