"""Exact mixed six-derivative curvature quotient infrastructure."""

from __future__ import annotations

from functools import lru_cache

from .curvature import (
    curvature_product_bianchi_analysis,
    one_derivative_contraction_from_pairing,
    one_derivative_curvature_analysis,
    pair_partitions,
    two_derivative_contraction_from_pairing,
    two_derivative_curvature_analysis,
)
from .pairing_orbits import SignedPositionPermutation, transform_pairing
from .quotient import RelationQuotient
from .tensors import (
    TensorExpression,
    TensorFactor,
    TensorMonomial,
    total_covariant_derivative,
)


def _deduplicate_relations(
    relations: list[TensorExpression],
) -> tuple[TensorExpression, ...]:
    unique = {
        relation.canonical_hash(): relation for relation in relations if relation
    }
    return tuple(unique[digest] for digest in sorted(unique))


def _ibp_relations() -> tuple[TensorExpression, ...]:
    relations: list[TensorExpression] = []
    for pairing in pair_partitions(tuple(range(10))):
        monomial = one_derivative_contraction_from_pairing(pairing)
        for factor_index, factor in enumerate(monomial.factors):
            (divergence_index,) = factor.derivatives
            factors = list(monomial.factors)
            factors[factor_index] = TensorFactor(factor.spec, factor.slots)
            vector = TensorMonomial(tuple(factors))
            relation = total_covariant_derivative(vector, divergence_index)
            if not all(term.is_complete_contraction() for term in relation.terms):
                raise AssertionError("generated IBP relation is not scalar")
            relations.append(relation)
    return _deduplicate_relations(relations)


def _commutator_relations() -> tuple[TensorExpression, ...]:
    cubic = curvature_product_bianchi_analysis(3)
    cubic_coordinates = cubic["pairing_monomial_coordinates"]
    bridge = two_derivative_curvature_analysis()
    relations = [
        commutator_relation_from_pairing(pairing, cubic_coordinates)
        for pairing in bridge["raw_pairings"]
    ]
    return _deduplicate_relations(relations)


def commutator_relation_from_pairing(
    pairing: tuple[tuple[int, int], ...],
    cubic_coordinates: dict[
        tuple[tuple[int, int], ...], tuple[TensorMonomial, int] | None
    ]
    | None = None,
) -> TensorExpression:
    """Generate one contracted commutator relation without cubic brute force."""

    if cubic_coordinates is None:
        cubic_coordinates = curvature_product_bianchi_analysis(3)[
            "pairing_monomial_coordinates"
        ]
    swap_derivatives = SignedPositionPermutation(
        (1, 0, 2, 3, 4, 5, 6, 7, 8, 9), 1
    )
    monomial = two_derivative_contraction_from_pairing(pairing)
    forward_sign, forward = monomial.canonicalize()
    reversed_pairing = transform_pairing(pairing, swap_derivatives)
    reversed_monomial = two_derivative_contraction_from_pairing(reversed_pairing)
    reverse_sign, reverse = reversed_monomial.canonicalize()
    if not forward_sign or forward is None or not reverse_sign or reverse is None:
        return TensorExpression()

    labels = [0] * 10
    for label, (first, second) in enumerate(pairing):
        labels[first] = label
        labels[second] = label
    left, right = labels[0], labels[1]
    if left == right:
        return TensorExpression()
    coefficients: dict[TensorMonomial, int] = {}
    coefficients[forward] = coefficients.get(forward, 0) + forward_sign
    coefficients[reverse] = coefficients.get(reverse, 0) - reverse_sign
    target_slots = labels[2:6]
    spectator_slots = labels[6:10]
    for position, covariant_index in enumerate(target_slots):
        dummy = max(labels) + 1
        acted_slots = list(target_slots)
        acted_slots[position] = dummy
        cubic_labels = (
            acted_slots
            + spectator_slots
            + [dummy, covariant_index, left, right]
        )
        occurrences: dict[int, list[int]] = {}
        for slot, label in enumerate(cubic_labels):
            occurrences.setdefault(label, []).append(slot)
        if any(len(slots) != 2 for slots in occurrences.values()):
            raise AssertionError("commutator curvature action is not contracted")
        cubic_pairing = tuple(sorted(tuple(slots) for slots in occurrences.values()))
        coordinate = cubic_coordinates[cubic_pairing]
        if coordinate is not None:
            cubic_monomial, cubic_sign = coordinate
            coefficients[cubic_monomial] = (
                coefficients.get(cubic_monomial, 0) + cubic_sign
            )
    return TensorExpression(coefficients)


@lru_cache(maxsize=1)
def six_derivative_curvature_analysis() -> dict[str, object]:
    """Join ``R^3``, ``(nabla R)^2``, and ``R nabla^2 R`` exactly."""

    cubic = curvature_product_bianchi_analysis(3)
    derivative = one_derivative_curvature_analysis()
    bridge = two_derivative_curvature_analysis()
    sector_bases = {
        "R3": tuple(cubic["quotient"].basis),
        "nablaR_nablaR": tuple(derivative["quotient"].basis),
        "R_nabla2R": tuple(bridge["quotient"].basis),
    }
    basis = tuple(
        monomial
        for sector in ("R3", "nablaR_nablaR", "R_nabla2R")
        for monomial in sector_bases[sector]
    )
    if len(set(basis)) != len(basis):
        raise AssertionError("six-derivative sector bases overlap")

    intrinsic_relations = {
        "R3_bianchi": tuple(cubic["relations"]),
        "nablaR_nablaR_bianchi": tuple(
            relation
            for relations in derivative["relation_sets"].values()
            for relation in relations
        ),
        "R_nabla2R_bianchi": tuple(
            relation
            for relations in bridge["relation_sets"].values()
            for relation in relations
        ),
    }
    ibp_relations = _ibp_relations()
    commutator_relations = _commutator_relations()
    relation_sets = {
        **intrinsic_relations,
        "integration_by_parts": ibp_relations,
        "covariant_commutators": commutator_relations,
    }
    all_relations = tuple(
        relation
        for name in (
            "R3_bianchi",
            "nablaR_nablaR_bianchi",
            "R_nabla2R_bianchi",
            "integration_by_parts",
            "covariant_commutators",
        )
        for relation in relation_sets[name]
    )
    quotient = RelationQuotient(basis, all_relations)

    intrinsic = tuple(
        relation
        for name in (
            "R3_bianchi",
            "nablaR_nablaR_bianchi",
            "R_nabla2R_bianchi",
        )
        for relation in relation_sets[name]
    )
    local_normal_form = RelationQuotient(
        basis, intrinsic + commutator_relations
    )

    cumulative: dict[str, dict[str, int]] = {}
    accumulated: list[TensorExpression] = []
    for name in relation_sets:
        accumulated.extend(relation_sets[name])
        partial = RelationQuotient(basis, accumulated)
        cumulative[name] = {
            "relation_rank": partial.relation_rank,
            "quotient_dimension": partial.quotient_dimension,
        }
    final_sector_ranks = {
        name: quotient.rank_of_classes(
            TensorExpression.monomial(monomial) for monomial in sector_basis
        )
        for name, sector_basis in sector_bases.items()
    }
    derivative_union_rank = quotient.rank_of_classes(
        TensorExpression.monomial(monomial)
        for name in ("nablaR_nablaR", "R_nabla2R")
        for monomial in sector_bases[name]
    )
    return {
        "sector_basis_dimensions_before_relations": {
            name: len(items) for name, items in sector_bases.items()
        },
        "total_basis_dimension_before_relations": len(basis),
        "relation_counts": {
            name: len(relations) for name, relations in relation_sets.items()
        },
        "cumulative_reduction": cumulative,
        "local_normal_form_before_total_derivatives": {
            "relation_rank": local_normal_form.relation_rank,
            "quotient_dimension": local_normal_form.quotient_dimension,
            "omitted_degree_one_total_divergence_dimension": 1,
            "dimension_with_degree_one_sector": (
                local_normal_form.quotient_dimension + 1
            ),
        },
        "combined_relation_rank": quotient.relation_rank,
        "quotient_dimension": quotient.quotient_dimension,
        "final_sector_ranks": final_sector_ranks,
        "final_derivative_union_rank": derivative_union_rank,
        "derivative_classes_outside_cubic_span": (
            quotient.quotient_dimension - final_sector_ranks["R3"]
        ),
        "quotient": quotient,
        "relation_sets": relation_sets,
        "sector_bases": sector_bases,
    }
