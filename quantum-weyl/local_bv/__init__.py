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
from .four_dimensional import four_dimensional_schouten_analysis
from .metadata import FieldSpec, IndexVariance, SpacetimeParity, minimal_registry
from .pairing_orbits import PairingOrbit, signed_pairing_orbits
from .six_derivative import six_derivative_curvature_analysis
from .specialization import (
    RelationFamily,
    SpecializationStage,
    SpecializationTower,
    TensorOccurrence,
    WEYL,
    antisymmetrize_occurrences,
    epsilon_pair_expansion,
    reduce_epsilon_pair_in_monomial,
    replace_riemann_by_weyl,
    schouten_antisymmetrization,
    tracefree_weyl_reduce,
)
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
    "SpecializationStage",
    "SpecializationTower",
    "Signature",
    "TensorExpression",
    "TensorFactor",
    "TensorMonomial",
    "TensorOccurrence",
    "TensorSpec",
    "TwoFormHodge",
    "WEYL",
    "RelationFamily",
    "antisymmetrize_occurrences",
    "covariant_commutator_relation",
    "covariant_commutator_relation_in_monomial",
    "epsilon_pair_expansion",
    "four_dimensional_schouten_analysis",
    "reduce_epsilon_pair_in_monomial",
    "minimal_registry",
    "replace_riemann_by_weyl",
    "schouten_antisymmetrization",
    "signed_pairing_orbits",
    "six_derivative_curvature_analysis",
    "tracefree_weyl_reduce",
]
