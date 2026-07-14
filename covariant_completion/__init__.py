"""Lorentzian cylinder Cauchy--Sobolev realization of free pure Weyl gravity.

The package proves the reduced physical tensor/vector theorem, the exact
ghost biwave, an auxiliary four-row Fourier-symbol witness, and an exact
66-to-30 Fourier-complex retract with support-local formulas.  The curved
lower-order witness/retract and covariant-current comparison remain
fail-closed targets.
"""

from .geometry.tensor_curl import TensorCurlCertificate
from .geometry.vector_curl import VectorCurlCertificate
from .physical_operator.tt_bach_factorization import TTBachFactorization
from .physical_operator.vector_wave_operator import VectorWaveFactor
from .physical_operator.branch_projectors import TTBranchProjectors
from .spectral_dictionary.eal import EALFieldDictionary
from .symplectic.branch_residues import BranchResidues
from .sobolev.branch_spaces import BranchSobolevRealization
from .green_complex.reduced_physical import ReducedPhysicalGreenRealization
from .dependencies import FinalClaimDependencyReport
from .final_transport import FinalCovariantTransportStatus

__all__ = [
    "TensorCurlCertificate",
    "VectorCurlCertificate",
    "TTBachFactorization",
    "VectorWaveFactor",
    "TTBranchProjectors",
    "EALFieldDictionary",
    "BranchResidues",
    "BranchSobolevRealization",
    "ReducedPhysicalGreenRealization",
    "FinalClaimDependencyReport",
    "FinalCovariantTransportStatus",
]
