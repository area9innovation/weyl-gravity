"""Exact Sobolev exponents and Krein-unitary cylinder harmonic transform."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from covariant_completion.spectral_dictionary.eal import EALFieldDictionary
from covariant_completion.symplectic.branch_residues import BranchResidues
from covariant_completion.symplectic.positive_frequency import PositiveFrequencyTransform


N = sp.symbols("N", integer=True, positive=True)


@dataclass(frozen=True)
class BranchSobolevRealization:
    def verify(self) -> None:
        EALFieldDictionary().verify()
        BranchResidues().verify()
        PositiveFrequencyTransform().verify()

        # Exact spectral weights in the Cauchy norm.
        weights = {
            "E": (4 * N * (N + 1), 4 * (N + 1) / N, 2),
            "A": (2 * N * (N**2 - 4), 2 * (N**2 - 4) / N, 3),
            "L": (4 * N * (N - 1), 4 * (N - 1) / N, 4),
        }
        for family, (q_weight, p_weight, minimum) in weights.items():
            for energy in range(minimum, 16):
                q_value = sp.Rational(q_weight.subs(N, energy), energy ** ({"E": 2, "A": 3, "L": 2}[family]))
                p_value = sp.Rational(p_weight.subs(N, energy), energy ** ({"E": 0, "A": 1, "L": 0}[family]))
                if q_value <= 0 or p_value <= 0:
                    raise AssertionError(f"{family} Sobolev weights are not positive")

        # Symbolic uniform comparison constants on the full allowed tails.
        inequalities = {
            "E": {
                "q_lower": sp.expand(4 * N * (N + 1) - 4 * N**2),
                "q_upper": sp.expand(6 * N**2 - 4 * N * (N + 1)),
                "p_lower": sp.expand(4 * (N + 1) / N - 4),
                "p_upper": sp.expand(6 - 4 * (N + 1) / N),
            },
            "A": {
                "q_lower": sp.expand(2 * N * (N**2 - 4) - sp.Rational(10, 9) * N**3),
                "q_upper": sp.expand(2 * N**3 - 2 * N * (N**2 - 4)),
                "p_lower": sp.expand(2 * (N**2 - 4) / N - sp.Rational(10, 9) * N),
                "p_upper": sp.expand(2 * N - 2 * (N**2 - 4) / N),
            },
            "L": {
                "q_lower": sp.expand(4 * N * (N - 1) - 3 * N**2),
                "q_upper": sp.expand(4 * N**2 - 4 * N * (N - 1)),
                "p_lower": sp.expand(4 * (N - 1) / N - 3),
                "p_upper": sp.expand(4 - 4 * (N - 1) / N),
            },
        }
        minima = {"E": 2, "A": 3, "L": 4}
        for family, relations in inequalities.items():
            for relation in relations.values():
                numerator, denominator = sp.fraction(sp.cancel(relation))
                shifted = sp.Poly(sp.expand(numerator.subs(N, sp.Symbol("m", nonnegative=True) + minima[family])), sp.Symbol("m", nonnegative=True))
                if any(value < 0 for value in shifted.all_coeffs()):
                    raise AssertionError(f"{family} Sobolev comparison failed: {relation}")
                if denominator.subs(N, minima[family]) <= 0:
                    raise AssertionError("Sobolev comparison denominator is not positive")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-cauchy-sobolev-v1",
            "branch_spaces": {
                "E": "H^1_TT direct_sum L^2_TT",
                "A": "H^(3/2)_T direct_sum H^(1/2)_T",
                "L": "H^1_TT direct_sum L^2_TT",
            },
            "orders": {
                "A_E,A_A,A_L": 1,
                "R_E": 1,
                "R_A": 2,
                "R_L": 1,
            },
            "positive_frequency_harmonic_transform": (
                "extends by density to a Hilbert-unitary map onto the E/A/L l2 majorant"
            ),
            "krein_transform": (
                "intertwines field signs +E,-A,-L with J_conf"
            ),
            "krein_unitary": True,
            "target": "certified energy-mode one-particle Krein completion",
            "vector_prediction_corrected": "H^(3/2) direct_sum H^(1/2)",
        }
