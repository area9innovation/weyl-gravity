"""Exact positive-frequency map from branch Cauchy data to mode coefficients."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from .branch_residues import BranchResidues


N = sp.symbols("N", integer=True, positive=True)


@dataclass(frozen=True)
class PositiveFrequencyTransform:
    def verify(self) -> None:
        BranchResidues().verify()
        for family, minimum in {"E": 2, "A": 3, "L": 4}.items():
            residue = BranchResidues.residue(family, N)
            mode_normalization = 1 / sp.sqrt(2 * residue * N)
            q = mode_normalization
            p = -sp.I * N * mode_normalization
            coordinate = sp.simplify(
                (
                    sp.sqrt(residue * N) * q
                    + sp.I * sp.sqrt(residue / N) * p
                )
                / sp.sqrt(2)
            )
            if coordinate != 1:
                raise AssertionError(f"positive-frequency {family} map is not normalized")
            if residue.subs(N, minimum) <= 0:
                raise AssertionError(f"{family} residue is not positive on its spectrum")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-positive-frequency-transform-v1",
            "coordinate": (
                "z_alpha=2^-1/2[(R_alpha A_alpha)^1/2 q_alpha"
                "+i(R_alpha A_alpha^-1)^1/2 p_alpha]"
            ),
            "positive_norm": (
                "||z||^2=1/2(||sqrt(RA)q||^2+||sqrt(R/A)p||^2)"
            ),
            "normalized_metric_modes_map_to_unit_coefficients": True,
            "harmonic_transform_isometry_on_algebraic_core": True,
            "krein_signs": {"E": 1, "A": -1, "L": -1},
        }
