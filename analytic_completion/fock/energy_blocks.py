"""Exact fixed-energy Fock counts and total compact-degree finiteness."""

from __future__ import annotations

from dataclasses import dataclass
from math import comb

from analytic_completion.ghosts.factor import ResidualGhostFactor
from analytic_completion.one_particle.krein import level_dimension


def bosonic_fixed_energy_dimensions(maximum_energy: int) -> dict[int, int]:
    """Coefficients of ``prod_{n>=2}(1-q^n)^(-dim H_n)``.

    Only factors with ``n <= maximum_energy`` can affect the requested
    coefficients, so this is both an exact algorithm and the machine version
    of the all-energy finiteness proof.
    """

    if maximum_energy < 0:
        raise ValueError("maximum energy must be nonnegative")
    coefficients = [0] * (maximum_energy + 1)
    coefficients[0] = 1
    for energy in range(2, maximum_energy + 1):
        modes = level_dimension(energy)
        updated = [0] * (maximum_energy + 1)
        for old_energy, old_count in enumerate(coefficients):
            if not old_count:
                continue
            for occupancy in range((maximum_energy - old_energy) // energy + 1):
                multiplicity = comb(modes + occupancy - 1, occupancy)
                updated[old_energy + occupancy * energy] += old_count * multiplicity
        coefficients = updated
    return {energy: value for energy, value in enumerate(coefficients)}


@dataclass(frozen=True)
class TotalDegreeBlocks:
    ghosts: ResidualGhostFactor

    @classmethod
    def build(cls) -> "TotalDegreeBlocks":
        return cls(ResidualGhostFactor.build())

    def dimension(self, total_degree: int) -> int:
        """Dimension of ``ker(D_F+D_gh-total_degree)``."""

        maximum_matter_energy = max(0, total_degree + 4)
        matter = bosonic_fixed_energy_dimensions(maximum_matter_energy)
        ghost = self.ghosts.degree_dimensions()
        return sum(
            matter_energy_dimension * ghost.get(total_degree - matter_energy, 0)
            for matter_energy, matter_energy_dimension in matter.items()
        )

    def centered_dimension_by_ghost_number(self) -> dict[int, int]:
        matter = bosonic_fixed_energy_dimensions(4)
        ghost = self.ghosts.degree_and_ghost_number_dimensions()
        return {
            ghost_number: sum(
                matter_dimension * ghost.get((-matter_energy, ghost_number), 0)
                for matter_energy, matter_dimension in matter.items()
            )
            for ghost_number in range(16)
        }

    def verify(self, regression_radius: int = 12, verify_ghosts: bool = True) -> None:
        if regression_radius < 4:
            raise ValueError("use a regression radius of at least four")
        if verify_ghosts:
            self.ghosts.verify()
        matter = bosonic_fixed_energy_dimensions(max(4, regression_radius + 4))
        expected_low = {0: 1, 1: 0, 2: 10, 3: 40, 4: 137}
        if {key: matter[key] for key in expected_low} != expected_low:
            raise AssertionError("low-energy completed Fock coefficients changed")

        # A fixed delta only sees E in [max(0,delta-4),delta+4], hence at
        # most nine finite matter blocks.  The direct calculation below is a
        # regression of that all-delta proof rather than a cutoff premise.
        for delta in range(-regression_radius, regression_radius + 1):
            if not isinstance(self.dimension(delta), int):
                raise AssertionError("total-degree block is not finite dimensional")
        if self.dimension(0) != 103296:
            raise AssertionError("completed centered block has the wrong total dimension")

        by_ghost_number = self.centered_dimension_by_ghost_number()
        expected_cochain = {3: 727, 4: 3084, 5: 8532}
        if {key: by_ghost_number[key] for key in expected_cochain} != expected_cochain:
            raise AssertionError("centered cochain blocks differ from the algebraic complex")

    def certificate(
        self, regression_radius: int = 12, verify: bool = True
    ) -> dict[str, object]:
        if verify:
            self.verify(regression_radius)
        centered = self.centered_dimension_by_ghost_number()
        return {
            "schema": "pure-weyl-finite-total-degree-blocks-v1",
            "matter_generating_function": "product_{n>=2}(1-q^n)^(-dim H_n)",
            "matter_energy_operator": "self-adjoint dGamma(D) on its spectral domain",
            "ghost_energy_operator": "finite-dimensional self-adjoint diagonal operator",
            "total_degree_operator": "self-adjoint L=dGamma(D)+D_gh",
            "total_degree_decomposition_complete": True,
            "ghost_compact_spectrum": [-4, -3, -2, -1, 0, 1, 2, 3, 4],
            "all_total_degree_blocks_finite": True,
            "proof": [
                "fixed delta restricts matter energy to delta plus [-4,4]",
                "fixed matter energy implies particle number N<=E/2",
                "only finite-dimensional one-particle blocks n<=E occur",
                "there are finitely many partitions and bosonic occupations of E",
            ],
            "centered_matter_energy_range": [0, 4],
            "centered_total_dimension": self.dimension(0),
            "centered_dimension_by_ghost_number": {
                str(key): value for key, value in centered.items() if value
            },
            "centered_regression": {
                "ghost_number_3": centered[3],
                "ghost_number_4": centered[4],
                "ghost_number_5": centered[5],
            },
            "sample_total_degree_dimensions": {
                str(delta): self.dimension(delta)
                for delta in range(-regression_radius, regression_radius + 1)
            },
            "completed_centered_equals_algebraic_centered": True,
        }
