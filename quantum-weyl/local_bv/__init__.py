"""Exact bootstrap for the local BV algebra of pure Weyl gravity.

This package covers the minimal coordinate-jet sector and a finite exact
abstract-index curvature/total-derivative quotient.  Antifield rows and the
remaining covariant identities must be imported or implemented before the
package can make local-cohomology claims.
"""

from .algebra import Expression, JetVariable, LocalJetAlgebra
from .brst import MinimalBRSTDifferential
from .metadata import FieldSpec, IndexVariance, SpacetimeParity, minimal_registry
from .tensors import TensorExpression, TensorFactor, TensorMonomial, TensorSpec

__all__ = [
    "Expression",
    "FieldSpec",
    "IndexVariance",
    "JetVariable",
    "LocalJetAlgebra",
    "MinimalBRSTDifferential",
    "SpacetimeParity",
    "TensorExpression",
    "TensorFactor",
    "TensorMonomial",
    "TensorSpec",
    "minimal_registry",
]
