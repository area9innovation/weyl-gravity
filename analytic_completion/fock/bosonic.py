"""Second quantization of the one-particle fundamental symmetry."""

from __future__ import annotations

from dataclasses import dataclass
from math import comb

import sympy as sp

from analytic_completion.one_particle.krein import OneParticleKreinCompletion


def _normalized_symmetric_two_particle_check() -> None:
    """Check that symmetrization and second quantization commute exactly.

    A two-mode fixture with signs ``(+,-)`` catches the common mistake of
    checking an unsymmetrized tensor power but never its bosonic restriction.
    """

    exchange = sp.Matrix(
        [
            [1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
        ]
    )
    symmetrizer = (sp.eye(4) + exchange) / 2
    j_one = sp.diag(1, -1)
    j_two = sp.kronecker_product(j_one, j_one)
    if symmetrizer * j_two != j_two * symmetrizer:
        raise AssertionError("Gamma(J) does not preserve the bosonic subspace")
    # Columns are the normalized occupation basis |2,0>, |1,1>, |0,2>.
    inclusion = sp.Matrix(
        [
            [1, 0, 0],
            [0, sp.sqrt(2) / 2, 0],
            [0, sp.sqrt(2) / 2, 0],
            [0, 0, 1],
        ]
    )
    if inclusion.T * inclusion != sp.eye(3):
        raise AssertionError("bosonic occupation basis is not normalized")
    if inclusion.T * j_two * inclusion != sp.diag(1, -1, 1):
        raise AssertionError("second-quantized signature is wrong after symmetrization")


@dataclass(frozen=True)
class BosonicKreinFock:
    """Certificate for ``Gamma_s(H_1)`` with ``Gamma_s(J_1)``."""

    one_particle: OneParticleKreinCompletion = OneParticleKreinCompletion()

    @staticmethod
    def occupation_sign(positive_occupancy: int, negative_occupancy: int) -> int:
        if positive_occupancy < 0 or negative_occupancy < 0:
            raise ValueError("occupancies must be nonnegative")
        return (-1) ** negative_occupancy

    @staticmethod
    def finite_sector_dimension(number_of_modes: int, particles: int) -> int:
        """Dimension of the normalized bosonic N-particle sector."""

        if number_of_modes < 0 or particles < 0:
            raise ValueError("dimensions and particle numbers must be nonnegative")
        if number_of_modes == 0:
            return int(particles == 0)
        return comb(number_of_modes + particles - 1, particles)

    def verify(self) -> None:
        self.one_particle.verify()
        _normalized_symmetric_two_particle_check()
        for negative in range(6):
            sign = self.occupation_sign(3, negative)
            if sign not in (-1, 1) or sign * sign != 1:
                raise AssertionError("Gamma(J) is not a self-adjoint involution")
        if self.finite_sector_dimension(10, 2) != 55:
            raise AssertionError("Sym^2 of the energy-two block has wrong dimension")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-bosonic-krein-fock-v1",
            "hilbert_space": "completed Hilbert direct sum of symmetric tensor powers",
            "fundamental_symmetry": "Gamma_s(J_1)",
            "fundamental_symmetry_self_adjoint": True,
            "fundamental_symmetry_square": 1,
            "fundamental_symmetry_norm": 1,
            "bosonic_symmetrization_checked": True,
            "normalized_occupation_basis_checked": True,
            "algebraic_symmetric_fock_dense": True,
            "restriction": "multiplicative lift of the certified E/A/L form",
            "classification": "infinite-index Krein space",
            "sample": {
                "dimension_Sym2_H2": self.finite_sector_dimension(10, 2),
                "two_mode_Sym2_signature": [1, -1, 1],
            },
            "scope_guards": [
                "not a positive graviton Fock space",
                "not a particle-unitarity theorem",
                "not a completed interacting Fock construction",
            ],
        }
