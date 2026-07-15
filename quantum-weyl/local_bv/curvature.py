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


def contraction_from_pairing(
    pairing: tuple[tuple[int, int], ...]
) -> TensorMonomial:
    if sorted(position for pair in pairing for position in pair) != list(range(8)):
        raise ValueError("quadratic Riemann pairing must cover eight slots once")
    labels = [0] * 8
    for index, (left, right) in enumerate(pairing):
        labels[left] = index
        labels[right] = index
    return TensorMonomial(
        (
            TensorFactor(RIEMANN, tuple(labels[:4])),
            TensorFactor(RIEMANN, tuple(labels[4:])),
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
