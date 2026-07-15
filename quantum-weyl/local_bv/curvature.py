"""Generated quadratic curvature contractions and algebraic Bianchi quotient."""

from __future__ import annotations

from functools import lru_cache
from itertools import product
from typing import Iterable

from .quotient import RelationQuotient
from .tensors import (
    TensorExpression,
    TensorFactor,
    TensorMonomial,
    TensorSpec,
    signed_permutation_group,
)


RIEMANN = TensorSpec(
    "Riemann",
    4,
    signed_permutation_group(
        4,
        (
            ((1, 0, 2, 3), -1),
            ((0, 1, 3, 2), -1),
            ((2, 3, 0, 1), 1),
        ),
    ),
)

EPSILON = TensorSpec(
    "epsilon",
    4,
    signed_permutation_group(
        4,
        (
            ((1, 0, 2, 3), -1),
            ((0, 2, 1, 3), -1),
            ((0, 1, 3, 2), -1),
        ),
    ),
    spacetime_parity=1,
)


def pair_partitions(items: tuple[int, ...]) -> Iterable[tuple[tuple[int, int], ...]]:
    """Generate every perfect matching in a fixed deterministic order."""

    if not items:
        yield ()
        return
    first = items[0]
    for position in range(1, len(items)):
        partner = items[position]
        remaining = items[1:position] + items[position + 1 :]
        for rest in pair_partitions(remaining):
            yield ((first, partner),) + rest


def riemann_product_contraction_from_pairing(
    pairing: tuple[tuple[int, int], ...], factor_count: int
) -> TensorMonomial:
    """Build a Riemann product from a complete contraction of its slots."""

    if factor_count < 1:
        raise ValueError("Riemann factor count must be positive")
    slot_count = 4 * factor_count
    if sorted(position for pair in pairing for position in pair) != list(
        range(slot_count)
    ):
        raise ValueError(f"Riemann pairing must cover {slot_count} slots once")
    labels = [0] * slot_count
    for index, (left, right) in enumerate(pairing):
        labels[left] = index
        labels[right] = index
    return TensorMonomial(
        tuple(
            TensorFactor(RIEMANN, tuple(labels[4 * index : 4 * index + 4]))
            for index in range(factor_count)
        )
    )


def contraction_from_pairing(
    pairing: tuple[tuple[int, int], ...]
) -> TensorMonomial:
    """Build one quadratic Riemann monomial from an eight-slot pairing."""

    return riemann_product_contraction_from_pairing(pairing, 2)


def one_derivative_contraction_from_pairing(
    pairing: tuple[tuple[int, int], ...]
) -> TensorMonomial:
    """Build a complete contraction of two once-differentiated Riemann tensors."""

    if sorted(position for pair in pairing for position in pair) != list(range(10)):
        raise ValueError("quadratic derivative pairing must cover ten slots once")
    labels = [0] * 10
    for index, (left, right) in enumerate(pairing):
        labels[left] = index
        labels[right] = index
    return TensorMonomial(
        (
            TensorFactor(RIEMANN, tuple(labels[1:5]), (labels[0],)),
            TensorFactor(RIEMANN, tuple(labels[6:10]), (labels[5],)),
        )
    )


def bianchi_relation(monomial: TensorMonomial, factor_index: int) -> TensorExpression:
    """Return R[a b c d] + R[a c d b] + R[a d b c]."""

    factor = monomial.factors[factor_index]
    if factor.spec != RIEMANN:
        raise ValueError("algebraic Bianchi relation requires a Riemann factor")
    a, b, c, d = factor.slots
    cyclic_slots = ((a, b, c, d), (a, c, d, b), (a, d, b, c))
    terms: dict[TensorMonomial, int] = {}
    for slots in cyclic_slots:
        factors = list(monomial.factors)
        factors[factor_index] = TensorFactor(RIEMANN, slots, factor.derivatives)
        term = TensorMonomial(tuple(factors))
        terms[term] = terms.get(term, 0) + 1
    return TensorExpression(terms)


def differential_bianchi_relation(
    monomial: TensorMonomial, factor_index: int
) -> TensorExpression:
    """Return nabla_e R_abcd + nabla_a R_becd + nabla_b R_eacd."""

    factor = monomial.factors[factor_index]
    if factor.spec != RIEMANN or len(factor.derivatives) != 1:
        raise ValueError("differential Bianchi requires one derivative on Riemann")
    (e,) = factor.derivatives
    a, b, c, d = factor.slots
    variants = (
        (e, (a, b, c, d)),
        (a, (b, e, c, d)),
        (b, (e, a, c, d)),
    )
    terms: dict[TensorMonomial, int] = {}
    for derivative, slots in variants:
        factors = list(monomial.factors)
        factors[factor_index] = TensorFactor(RIEMANN, slots, (derivative,))
        term = TensorMonomial(tuple(factors))
        terms[term] = terms.get(term, 0) + 1
    return TensorExpression(terms)


def named_quadratic_representatives() -> dict[str, TensorExpression]:
    """Return conventional representatives for an independence cross-check."""

    representatives = {
        "Riemann_squared": TensorMonomial(
            (
                TensorFactor(RIEMANN, (0, 1, 2, 3)),
                TensorFactor(RIEMANN, (0, 1, 2, 3)),
            )
        ),
        "Ricci_squared": TensorMonomial(
            (
                TensorFactor(RIEMANN, (0, 1, 0, 2)),
                TensorFactor(RIEMANN, (3, 1, 3, 2)),
            )
        ),
        "scalar_curvature_squared": TensorMonomial(
            (
                TensorFactor(RIEMANN, (0, 1, 0, 1)),
                TensorFactor(RIEMANN, (2, 3, 2, 3)),
            )
        ),
    }
    return {
        name: TensorExpression.monomial(monomial)
        for name, monomial in representatives.items()
    }


@lru_cache(maxsize=1)
def quadratic_curvature_analysis() -> dict[str, object]:
    raw_pairings = tuple(pair_partitions(tuple(range(8))))
    raw_monomials = tuple(contraction_from_pairing(pairing) for pairing in raw_pairings)
    canonical_monomials: set[TensorMonomial] = set()
    for monomial in raw_monomials:
        sign, canonical = monomial.canonicalize()
        if sign and canonical is not None:
            canonical_monomials.add(canonical)

    relations = []
    relation_hashes = set()
    for monomial, factor_index in product(raw_monomials, range(2)):
        relation = bianchi_relation(monomial, factor_index)
        if relation:
            digest = relation.canonical_hash()
            if digest not in relation_hashes:
                relation_hashes.add(digest)
                relations.append(relation)

    quotient = RelationQuotient(canonical_monomials, relations)
    named = named_quadratic_representatives()
    named_rank = quotient.rank_of_classes(named.values())
    return {
        "raw_pairing_count": len(raw_pairings),
        "symmetry_canonical_monomial_count": len(canonical_monomials),
        "nonzero_unique_bianchi_relation_count": len(relations),
        "bianchi_relation_rank": quotient.relation_rank,
        "quotient_dimension": quotient.quotient_dimension,
        "named_representative_rank": named_rank,
        "named_representatives": tuple(named),
        "quotient": quotient,
        "relations": tuple(relations),
    }


@lru_cache(maxsize=1)
def one_derivative_curvature_analysis() -> dict[str, object]:
    """Generate the finite (nabla Riemann)^2 quotient exactly.

    This quotient uses intrinsic Riemann symmetries plus algebraic and
    differential Bianchi relations.  It does not use integration by parts or
    derivative commutators, which mix this sector with cubic curvature.
    """

    raw_pairings = tuple(pair_partitions(tuple(range(10))))
    raw_monomials = tuple(
        one_derivative_contraction_from_pairing(pairing) for pairing in raw_pairings
    )
    canonical_monomials: set[TensorMonomial] = set()
    for monomial in raw_monomials:
        sign, canonical = monomial.canonicalize()
        if sign and canonical is not None:
            canonical_monomials.add(canonical)

    relation_sets: dict[str, list[TensorExpression]] = {
        "algebraic_bianchi": [],
        "differential_bianchi": [],
    }
    relation_hashes: dict[str, set[str]] = {name: set() for name in relation_sets}
    for monomial, factor_index in product(raw_monomials, range(2)):
        for name, relation in (
            ("algebraic_bianchi", bianchi_relation(monomial, factor_index)),
            (
                "differential_bianchi",
                differential_bianchi_relation(monomial, factor_index),
            ),
        ):
            if relation:
                digest = relation.canonical_hash()
                if digest not in relation_hashes[name]:
                    relation_hashes[name].add(digest)
                    relation_sets[name].append(relation)

    all_relations = relation_sets["algebraic_bianchi"] + relation_sets[
        "differential_bianchi"
    ]
    algebraic_quotient = RelationQuotient(
        canonical_monomials, relation_sets["algebraic_bianchi"]
    )
    differential_quotient = RelationQuotient(
        canonical_monomials, relation_sets["differential_bianchi"]
    )
    quotient = RelationQuotient(canonical_monomials, all_relations)
    return {
        "raw_pairing_count": len(raw_pairings),
        "symmetry_canonical_monomial_count": len(canonical_monomials),
        "algebraic_bianchi_relation_count": len(
            relation_sets["algebraic_bianchi"]
        ),
        "algebraic_bianchi_rank": algebraic_quotient.relation_rank,
        "differential_bianchi_relation_count": len(
            relation_sets["differential_bianchi"]
        ),
        "differential_bianchi_rank": differential_quotient.relation_rank,
        "combined_relation_rank": quotient.relation_rank,
        "quotient_dimension": quotient.quotient_dimension,
        "quotient": quotient,
        "relation_sets": {
            name: tuple(relations) for name, relations in relation_sets.items()
        },
    }
