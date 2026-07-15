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
from .weyl_decomposition import (
    COTTON,
    METRIC,
    SCHOUTEN,
    cotton_cyclic_relation,
    cotton_definition_relation,
    differentiated_ricci_decomposition_relation,
    expand_cotton_definitions,
    hodge_dualize_weyl_factor,
    ricci_decomposition_relation,
    tracefree_cotton_reduce,
    weyl_differential_bianchi_relation,
    weyl_hodge_square_contraction,
)

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
    "COTTON",
    "METRIC",
    "SCHOUTEN",
    "RelationFamily",
    "antisymmetrize_occurrences",
    "covariant_commutator_relation",
    "covariant_commutator_relation_in_monomial",
    "cotton_cyclic_relation",
    "cotton_definition_relation",
    "differentiated_ricci_decomposition_relation",
    "epsilon_pair_expansion",
    "expand_cotton_definitions",
    "four_dimensional_schouten_analysis",
    "hodge_dualize_weyl_factor",
    "reduce_epsilon_pair_in_monomial",
    "minimal_registry",
    "replace_riemann_by_weyl",
    "ricci_decomposition_relation",
    "schouten_antisymmetrization",
    "signed_pairing_orbits",
    "six_derivative_curvature_analysis",
    "tracefree_weyl_reduce",
    "tracefree_cotton_reduce",
    "weyl_differential_bianchi_relation",
    "weyl_hodge_square_contraction",
]
