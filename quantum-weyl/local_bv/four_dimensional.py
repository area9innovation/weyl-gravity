"""Exact four-dimensional Schouten specialization of order-six curvature scalars."""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations, permutations, product
from typing import Callable, Iterable

from .curvature import (
    curvature_product_bianchi_analysis,
    one_derivative_contraction_from_pairing,
    pair_partitions,
    two_derivative_contraction_from_pairing,
)
from .pairing_orbits import Pairing, normalize_pairing
from .quotient import RelationQuotient
from .six_derivative import six_derivative_curvature_analysis
from .specialization import RelationFamily, SpecializationTower
from .tensors import TensorExpression, TensorMonomial


PairingCoordinate = tuple[TensorMonomial, int] | None


def _permutation_sign(permutation: tuple[int, ...]) -> int:
    inversions = sum(
        left > right
        for position, left in enumerate(permutation)
        for right in permutation[position + 1 :]
    )
    return -1 if inversions % 2 else 1


def pairing_coordinate_ledger(
    pairings: Iterable[Pairing],
    constructor: Callable[[Pairing], TensorMonomial],
) -> dict[Pairing, PairingCoordinate]:
    """Map every raw pairing to its signed canonical tensor monomial."""

    ledger: dict[Pairing, PairingCoordinate] = {}
    for pairing in pairings:
        normalized = normalize_pairing(pairing, 2 * len(pairing))
        sign, canonical = constructor(normalized).canonicalize()
        ledger[normalized] = (
            None if not sign or canonical is None else (canonical, sign)
        )
    return ledger


def pairing_schouten_relation(
    pairing: Pairing,
    selected_positions: tuple[int, ...],
    coordinates: dict[Pairing, PairingCoordinate],
    *,
    dimension: int = 4,
) -> TensorExpression:
    """Antisymmetrize ``dimension + 1`` selected pairing endpoints exactly."""

    slot_count = 2 * len(pairing)
    normalized = normalize_pairing(pairing, slot_count)
    selected = tuple(selected_positions)
    if len(selected) != dimension + 1:
        raise ValueError("a Schouten relation requires dimension + 1 positions")
    if len(set(selected)) != len(selected) or any(
        position < 0 or position >= slot_count for position in selected
    ):
        raise ValueError("selected positions must be distinct valid slots")
    partner: dict[int, int] = {}
    for first, second in normalized:
        partner[first] = second
        partner[second] = first
    partners = tuple(partner[position] for position in selected)
    if set(selected) & set(partners):
        raise ValueError("select exactly one endpoint from each contraction pair")

    selected_set = set(selected)
    fixed_pairs = tuple(
        pair for pair in normalized if not selected_set.intersection(pair)
    )
    coefficients: dict[TensorMonomial, int] = {}
    for permutation in permutations(range(len(selected))):
        rewired = normalize_pairing(
            fixed_pairs
            + tuple(
                (selected[target], partners[source])
                for target, source in enumerate(permutation)
            ),
            slot_count,
        )
        coordinate = coordinates[rewired]
        if coordinate is None:
            continue
        monomial, canonical_sign = coordinate
        coefficient = _permutation_sign(permutation) * canonical_sign
        coefficients[monomial] = coefficients.get(monomial, 0) + coefficient
    return TensorExpression(coefficients)


def schouten_endpoint_selections(
    pairing: Pairing, *, dimension: int = 4
) -> tuple[tuple[int, ...], ...]:
    """Enumerate one endpoint from each choice of ``dimension + 1`` pairs."""

    normalized = normalize_pairing(pairing, 2 * len(pairing))
    if len(normalized) < dimension + 1:
        return ()
    return tuple(
        tuple(pair[choice] for pair, choice in zip(chosen_pairs, choices))
        for chosen_pairs in combinations(normalized, dimension + 1)
        for choices in product((0, 1), repeat=dimension + 1)
    )


def _representative_pairings(
    basis: tuple[TensorMonomial, ...],
    coordinates: dict[Pairing, PairingCoordinate],
) -> dict[TensorMonomial, Pairing]:
    representatives: dict[TensorMonomial, Pairing] = {}
    basis_set = set(basis)
    for pairing in sorted(coordinates):
        coordinate = coordinates[pairing]
        if coordinate is None:
            continue
        monomial, _ = coordinate
        if monomial in basis_set:
            representatives.setdefault(monomial, pairing)
    missing = basis_set - set(representatives)
    if missing:
        raise AssertionError("pairing coordinates do not cover the sector basis")
    return representatives


def _sector_schouten_relations(
    basis: tuple[TensorMonomial, ...],
    coordinates: dict[Pairing, PairingCoordinate],
) -> dict[str, object]:
    representatives = _representative_pairings(basis, coordinates)
    unique: dict[str, TensorExpression] = {}
    candidate_count = 0
    nonzero_candidate_count = 0
    for monomial in basis:
        pairing = representatives[monomial]
        for selection in schouten_endpoint_selections(pairing):
            candidate_count += 1
            relation = pairing_schouten_relation(pairing, selection, coordinates)
            if relation:
                nonzero_candidate_count += 1
                unique.setdefault(relation.canonical_hash(), relation)
    return {
        "basis_dimension": len(basis),
        "candidate_count": candidate_count,
        "nonzero_candidate_count": nonzero_candidate_count,
        "unique_nonzero_relation_count": len(unique),
        "relations": tuple(unique[digest] for digest in sorted(unique)),
        "representative_pairings": representatives,
    }


def universal_order_six_tower() -> SpecializationTower:
    """Import the existing universal quotient as named relation families."""

    analysis = six_derivative_curvature_analysis()
    provenance = {
        "R3_bianchi": "generated algebraic Bianchi action on all cubic pairing orbits",
        "nablaR_nablaR_bianchi": "generated algebraic and differential Bianchi action on the once-differentiated sector",
        "R_nabla2R_bianchi": "generated algebraic and outer-differential Bianchi action on the second-derivative bridge",
        "integration_by_parts": "generated covariant total divergences",
        "covariant_commutators": "generated declared-sign contracted derivative commutators",
    }
    families = tuple(
        RelationFamily(name, tuple(relations), provenance[name])
        for name, relations in analysis["relation_sets"].items()
    )
    return SpecializationTower.start(
        "dimension_independent_integrated",
        analysis["quotient"].basis,
        families,
    )


def _kernel_expressions(
    tower: SpecializationTower,
) -> tuple[TensorExpression, ...]:
    if len(tower.stages) < 2:
        return ()
    source = tower.stages[-2]
    target = tower.current
    expressions = []
    for vector in target.projection_kernel:
        expression = TensorExpression(
            {
                source.quotient.basis[column]: coefficient
                for column, coefficient in zip(source.quotient.free_columns, vector)
                if coefficient
            }
        )
        if any(target.quotient.free_coordinates(expression)):
            raise AssertionError("specialization kernel witness does not project to zero")
        expressions.append(expression)
    return tuple(expressions)


@lru_cache(maxsize=1)
def four_dimensional_schouten_analysis() -> dict[str, object]:
    """Generate and apply every scalar five-index Schouten relation at order six."""

    combined = six_derivative_curvature_analysis()
    sector_bases = combined["sector_bases"]
    cubic_coordinates = curvature_product_bianchi_analysis(3)[
        "pairing_monomial_coordinates"
    ]
    derivative_pairings = tuple(pair_partitions(tuple(range(10))))
    derivative_coordinates = pairing_coordinate_ledger(
        derivative_pairings, one_derivative_contraction_from_pairing
    )
    bridge_coordinates = pairing_coordinate_ledger(
        derivative_pairings, two_derivative_contraction_from_pairing
    )
    coordinate_ledgers = {
        "R3": cubic_coordinates,
        "nablaR_nablaR": derivative_coordinates,
        "R_nabla2R": bridge_coordinates,
    }
    sectors = {
        name: _sector_schouten_relations(
            tuple(sector_bases[name]), coordinate_ledgers[name]
        )
        for name in ("R3", "nablaR_nablaR", "R_nabla2R")
    }
    intrinsic_names = {
        "R3": "R3_bianchi",
        "nablaR_nablaR": "nablaR_nablaR_bianchi",
        "R_nabla2R": "R_nabla2R_bianchi",
    }
    for name, sector in sectors.items():
        basis = tuple(sector_bases[name])
        intrinsic = tuple(combined["relation_sets"][intrinsic_names[name]])
        schouten = tuple(sector["relations"])
        sector["schouten_relation_rank_in_ambient_sector"] = RelationQuotient(
            basis, schouten
        ).relation_rank
        sector["intrinsic_quotient_dimension_before_schouten"] = (
            RelationQuotient(basis, intrinsic).quotient_dimension
        )
        sector["intrinsic_quotient_dimension_after_schouten"] = (
            RelationQuotient(basis, intrinsic + schouten).quotient_dimension
        )
    unique: dict[str, TensorExpression] = {}
    for sector in sectors.values():
        for relation in sector["relations"]:
            unique.setdefault(relation.canonical_hash(), relation)
    relations = tuple(unique[digest] for digest in sorted(unique))
    family = RelationFamily(
        "dimension_4_schouten",
        relations,
        "exhaustive five-index antisymmetrization of one endpoint from five distinct contraction pairs on every signed-symmetry orbit representative",
        ("spacetime_dimension=4",),
    )
    universal = universal_order_six_tower()
    if universal.current.dimension != 10:
        raise AssertionError("universal order-six quotient dimension drifted")
    tower = universal.extend("dimension_4_integrated", (family,))
    kernel_expressions = _kernel_expressions(tower)
    sector_ranks = {
        name: tower.current.quotient.rank_of_classes(
            TensorExpression.monomial(monomial)
            for monomial in sector_bases[name]
        )
        for name in sector_bases
    }
    return {
        "dimension": 4,
        "sector_generation": sectors,
        "total_candidate_count": sum(
            sector["candidate_count"] for sector in sectors.values()
        ),
        "total_nonzero_candidate_count": sum(
            sector["nonzero_candidate_count"] for sector in sectors.values()
        ),
        "unique_nonzero_relation_count": len(relations),
        "schouten_relation_rank_in_ambient_basis": RelationQuotient(
            universal.current.quotient.basis, relations
        ).relation_rank,
        "universal_quotient_dimension": universal.current.dimension,
        "four_dimensional_quotient_dimension": tower.current.dimension,
        "schouten_rank_on_universal_quotient": (
            universal.current.dimension - tower.current.dimension
        ),
        "sector_ranks_after_specialization": sector_ranks,
        "kernel_expressions": kernel_expressions,
        "relation_family": family,
        "tower": tower,
    }
