"""All-level symplectic residues derived from the reduced Weyl action."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp


N = sp.symbols("N", integer=True, positive=True)
J = sp.symbols("J", integer=True, positive=True)


@dataclass(frozen=True)
class BranchResidues:
    """Derive positive residue magnitudes and Krein signs.

    The action convention is ``S=-alpha_g integral C^2`` with
    ``alpha_g>0``.  The repository's displayed Hamada--Horata oscillator
    normalization corresponds to ``alpha_g=1``.
    """

    def verify(self) -> None:
        omega_e = 2 * J
        omega_l = 2 * J + 2
        absolute_tensor_curl = 2 * J + 1
        gamma = -sp.Integer(1)
        gap = sp.expand(omega_l**2 - omega_e**2)
        if gap != 4 * absolute_tensor_curl:
            raise AssertionError("TT action residue is not 4|C_2|")

        effective_e = sp.expand(gamma * (omega_e**2 - omega_l**2))
        effective_l = sp.expand(gamma * (omega_l**2 - omega_e**2))
        if effective_e != gap or effective_l != -gap:
            raise AssertionError("TT residue signs do not give +E,-L")

        omega_a = 2 * J + 1
        vector_factor = (2 * J - 1) * (2 * J + 3)
        effective_a = -2 * vector_factor
        if sp.expand(vector_factor - (omega_a**2 - 4)) != 0:
            raise AssertionError("vector kinetic factor is not A_A^2-4")
        if sp.expand(effective_a + 2 * (omega_a**2 - 4)) != 0:
            raise AssertionError("vector residue does not give the A sign")

        normalizations = {
            "E": 1 / (4 * sp.sqrt(J * (2 * J + 1))),
            "A": 1 / (2 * sp.sqrt(vector_factor * omega_a)),
            "L": 1 / (4 * sp.sqrt((J + 1) * (2 * J + 1))),
        }
        signed_residues = {"E": gap, "A": effective_a, "L": -gap}
        frequencies = {"E": omega_e, "A": omega_a, "L": omega_l}
        expected_sign = {"E": 1, "A": -1, "L": -1}
        for family in ("E", "A", "L"):
            norm = sp.simplify(
                2
                * signed_residues[family]
                * frequencies[family]
                * normalizations[family] ** 2
            )
            if norm != expected_sign[family]:
                raise AssertionError(f"{family} oscillator norm is {norm}")

        # Energy-labelled positive residue magnitudes.
        residues = {
            "E": 4 * (N + 1),
            "A": 2 * (N**2 - 4),
            "L": 4 * (N - 1),
        }
        mode_normalizations = {
            family: sp.simplify(1 / sp.sqrt(2 * residue * N))
            for family, residue in residues.items()
        }
        if sp.simplify(mode_normalizations["E"].subs(N, 2 * J) - normalizations["E"]) != 0:
            raise AssertionError("energy-labelled E normalization failed")
        if sp.simplify(mode_normalizations["A"].subs(N, 2 * J + 1) - normalizations["A"]) != 0:
            raise AssertionError("energy-labelled A normalization failed")
        if sp.simplify(mode_normalizations["L"].subs(N, 2 * J + 2) - normalizations["L"]) != 0:
            raise AssertionError("energy-labelled L normalization failed")

    @staticmethod
    def residue(family: str, energy: sp.Expr = N) -> sp.Expr:
        energy = sp.sympify(energy)
        values = {
            "E": 4 * (energy + 1),
            "A": 2 * (energy**2 - 4),
            "L": 4 * (energy - 1),
        }
        return sp.expand(values[family])

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-branch-residues-v1",
            "action_convention": "S=-alpha_g integral C^2, alpha_g>0; certificate sets alpha_g=1",
            "source": "reduced metric-field PU and transverse-vector quadratic actions",
            "branches": {
                "E": {
                    "positive_residue": "R_E=4|C_2|",
                    "krein_sign": 1,
                    "energy_form": "R_E(N)=4(N+1)",
                    "elliptic_order": 1,
                },
                "A": {
                    "positive_residue": "R_A=2(A_A^2-4)",
                    "krein_sign": -1,
                    "energy_form": "R_A(N)=2(N^2-4)",
                    "elliptic_order": 2,
                },
                "L": {
                    "positive_residue": "R_L=4|C_2|",
                    "krein_sign": -1,
                    "energy_form": "R_L(N)=4(N-1)",
                    "elliptic_order": 1,
                },
            },
            "important_correction": (
                "the transverse-vector residue has elliptic order two, not zero"
            ),
            "oscillator_norms": {"E": 1, "A": -1, "L": -1},
            "normalization_fixed_all_levels": True,
        }
