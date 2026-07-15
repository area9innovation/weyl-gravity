"""Exact bootstrap for the local BV algebra of pure Weyl gravity.

This package deliberately covers only the minimal coordinate-jet sector.
Antifield rows and covariant quotient relations must be imported from the
frozen classical certificate before the package can make cohomology claims.
"""

from .algebra import Expression, JetVariable, LocalJetAlgebra
from .brst import MinimalBRSTDifferential
from .metadata import FieldSpec, IndexVariance, SpacetimeParity, minimal_registry

__all__ = [
    "Expression",
    "FieldSpec",
    "IndexVariance",
    "JetVariable",
    "LocalJetAlgebra",
    "MinimalBRSTDifferential",
    "SpacetimeParity",
    "minimal_registry",
]
