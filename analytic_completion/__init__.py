"""Energy-mode Krein completion of the classical residual complex.

This package deliberately works with the completed cylinder-energy mode
spaces.  It does not construct a covariant Sobolev completion of metric
fields and it does not integrate the unbounded conformal Lie-algebra action
to a group representation.
"""

from analytic_completion.fock.bosonic import BosonicKreinFock
from analytic_completion.fock.energy_blocks import TotalDegreeBlocks
from analytic_completion.ghosts.factor import ResidualGhostFactor
from analytic_completion.one_particle.generators import ClosedGeneratorCertificate
from analytic_completion.one_particle.krein import OneParticleKreinCompletion
from analytic_completion.residual.completed_complex import CompletedResidualComplex

__all__ = [
    "BosonicKreinFock",
    "ClosedGeneratorCertificate",
    "CompletedResidualComplex",
    "OneParticleKreinCompletion",
    "ResidualGhostFactor",
    "TotalDegreeBlocks",
]
