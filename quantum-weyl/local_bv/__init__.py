"""Exact bootstrap for the local BV algebra of pure Weyl gravity.

This package covers the minimal coordinate-jet sector and finite exact
abstract-index curvature, differential-Bianchi, commutator, and Hodge
quotients.  Antifield rows and the remaining covariant identities must be
imported or implemented before the package can make local-cohomology claims.
"""

from .algebra import Expression, JetVariable, LocalJetAlgebra
from .brst import MinimalBRSTDifferential
from .covariant_derivatives import (
    covariant_commutator_relation,
    covariant_commutator_relation_in_monomial,
)
from .hodge import Signature, TwoFormHodge
from .metadata import FieldSpec, IndexVariance, SpacetimeParity, minimal_registry
from .pairing_orbits import PairingOrbit, signed_pairing_orbits
from .six_derivative import six_derivative_curvature_analysis
from .tensors import TensorExpression, TensorFactor, TensorMonomial, TensorSpec

__all__ = [
    "Expression",
    "FieldSpec",
    "IndexVariance",
    "JetVariable",
    "LocalJetAlgebra",
    "MinimalBRSTDifferential",
    "PairingOrbit",
    "SpacetimeParity",
    "Signature",
    "TensorExpression",
    "TensorFactor",
    "TensorMonomial",
    "TensorSpec",
    "TwoFormHodge",
    "covariant_commutator_relation",
    "covariant_commutator_relation_in_monomial",
    "minimal_registry",
    "signed_pairing_orbits",
    "six_derivative_curvature_analysis",
]
