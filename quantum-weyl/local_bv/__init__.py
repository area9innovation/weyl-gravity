"""Exact bootstrap for the local BV algebra of pure Weyl gravity.

This package covers the minimal coordinate-jet sector and finite exact
abstract-index curvature, differential-Bianchi, commutator, and Hodge
quotients.  Antifield rows and the remaining covariant identities must be
imported or implemented before the package can make local-cohomology claims.
"""

from .algebra import Expression, JetVariable, LocalJetAlgebra
from .brst import MinimalBRSTDifferential
from .covariant_derivatives import covariant_commutator_relation
from .hodge import Signature, TwoFormHodge
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
    "Signature",
    "TensorExpression",
    "TensorFactor",
    "TensorMonomial",
    "TensorSpec",
    "TwoFormHodge",
    "covariant_commutator_relation",
    "minimal_registry",
]
