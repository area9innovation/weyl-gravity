"""Target-native four-dimensional Weyl--Cotton invariant carriers.

The quotient in this module is generated from Weyl symmetries, trace
freeness, and algebraic Bianchi identities directly.  It does not define its
relations by mapping a Riemann quotient.  At mass dimension four Cotton can
enter the differential identity audit, but it cannot form a nonzero scalar
by itself.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache

from .curvature import EPSILON, pair_partitions
from .hodge import Signature
from .quotient import RelationQuotient
from .specialization import WEYL
from .tensors import TensorExpression, TensorFactor, TensorMonomial, TensorSpec
from .weyl_decomposition import (
    COTTON,
    cotton_cyclic_relation,
    hodge_dualize_weyl_factor,
    tracefree_cotton_reduce,
    weyl_differential_bianchi_relation,
    weyl_hodge_square_contraction,
)


DUAL_WEYL = TensorSpec(
    "DualWeyl",
    4,
    WEYL.intrinsic_symmetries,
    spacetime_parity=1,
)

WEYL_GHOST = TensorSpec.without_slot_symmetry(
    "omega",
    0,
    grassmann_parity=1,
)


def _quadratic_contraction(
    pairing: tuple[tuple[int, int], ...],
    specs: tuple[TensorSpec, TensorSpec],
) -> TensorMonomial:
    if sorted(position for pair in pairing for position in pair) != list(range(8)):
        raise ValueError("quadratic curvature pairing must cover eight slots")
    labels = [0] * 8
    for index, (left, right) in enumerate(pairing):
        labels[left] = labels[right] = index
    return TensorMonomial(
        (
            TensorFactor(specs[0], tuple(labels[:4])),
            TensorFactor(specs[1], tuple(labels[4:])),
        )
    )


def _tracefree_reduce(expression: TensorExpression) -> TensorExpression:
    return TensorExpression(
        {
            monomial: coefficient
            for monomial, coefficient in expression.terms.items()
            if not any(
                factor.spec in (WEYL, DUAL_WEYL)
                and len(set(factor.slots)) != len(factor.slots)
                for factor in monomial.factors
            )
        }
    )


def _bianchi_relation(
    monomial: TensorMonomial, factor_index: int
) -> TensorExpression:
    factor = monomial.factors[factor_index]
    if factor.spec not in (WEYL, DUAL_WEYL):
        raise ValueError("target Bianchi relation requires a Weyl carrier")
    a, b, c, d = factor.slots
    terms: dict[TensorMonomial, int] = {}
    for slots in ((a, b, c, d), (a, c, d, b), (a, d, b, c)):
        factors = list(monomial.factors)
        factors[factor_index] = TensorFactor(factor.spec, slots)
        term = TensorMonomial(tuple(factors))
        terms[term] = terms.get(term, 0) + 1
    return _tracefree_reduce(TensorExpression(terms))


def _deduplicate(
    expressions: list[TensorExpression],
) -> tuple[TensorExpression, ...]:
    unique = {
        expression.canonical_hash(): expression
        for expression in expressions
        if expression
    }
    return tuple(unique[digest] for digest in sorted(unique))


@lru_cache(maxsize=2)
def target_native_quadratic_quotient(
    parity: str,
) -> dict[str, object]:
    """Generate the exact even or odd quadratic Weyl quotient.

    The odd calculation uses one abstract ``DualWeyl`` carrier.  Its
    connection with the explicit epsilon-over-two Hodge definition is
    checked separately and is not assumed from the carrier name.
    """

    if parity == "even":
        specs = (WEYL, WEYL)
    elif parity == "odd":
        specs = (DUAL_WEYL, WEYL)
    else:
        raise ValueError("parity must be 'even' or 'odd'")

    pairings = tuple(pair_partitions(tuple(range(8))))
    raw_monomials = tuple(_quadratic_contraction(pairing, specs) for pairing in pairings)
    basis = {
        monomial
        for raw in raw_monomials
        for monomial in _tracefree_reduce(TensorExpression.monomial(raw)).terms
    }
    relations = _deduplicate(
        [
            _bianchi_relation(monomial, factor_index)
            for monomial in raw_monomials
            for factor_index in range(2)
        ]
    )
    quotient = RelationQuotient(basis, relations)
    if quotient.quotient_dimension != 1:
        raise AssertionError("target-native quadratic Weyl dimension drifted")
    representative = quotient.basis[quotient.free_columns[0]]
    return {
        "parity": parity,
        "raw_pairing_count": len(pairings),
        "tracefree_ambient_dimension": len(basis),
        "relation_count": len(relations),
        "relation_rank": quotient.relation_rank,
        "quotient_dimension": quotient.quotient_dimension,
        "basis": tuple(sorted(basis, key=TensorMonomial.sort_key)),
        "relations": relations,
        "quotient": quotient,
        "representative": representative,
    }


def expand_dual_weyl_factor(
    monomial: TensorMonomial, factor_index: int
) -> TensorExpression:
    """Expand one compressed dual carrier as epsilon-over-two times Weyl."""

    if not 0 <= factor_index < len(monomial.factors):
        raise IndexError("dual Weyl factor index is outside the monomial")
    factor = monomial.factors[factor_index]
    if factor.spec != DUAL_WEYL:
        raise ValueError("selected factor must be DualWeyl")
    next_index = max(
        (index for item in monomial.factors for index in item.all_indices),
        default=-1,
    ) + 1
    fresh = (next_index, next_index + 1)
    first_pair = factor.slots[:2]
    factors = list(monomial.factors)
    factors[factor_index] = TensorFactor(
        WEYL,
        fresh + factor.slots[2:],
        factor.derivatives,
    )
    factors.insert(0, TensorFactor(EPSILON, first_pair + fresh))
    return Fraction(1, 2) * TensorExpression.monomial(
        TensorMonomial(tuple(factors))
    )


def _cotton_dimension_four_scalar_count() -> int:
    """Enumerate complete contractions of one derivative of Cotton."""

    surviving: set[TensorMonomial] = set()
    for pairing in pair_partitions(tuple(range(4))):
        labels = [0] * 4
        for index, (left, right) in enumerate(pairing):
            labels[left] = labels[right] = index
        monomial = TensorMonomial(
            (TensorFactor(COTTON, tuple(labels[1:]), (labels[0],)),)
        )
        surviving.update(
            tracefree_cotton_reduce(TensorExpression.monomial(monomial)).terms
        )
    return len(surviving)


@lru_cache(maxsize=1)
def dimension_four_weyl_target_analysis() -> dict[str, object]:
    """Return the independently generated dimension-four target ledger."""

    even = target_native_quadratic_quotient("even")
    odd = target_native_quadratic_quotient("odd")

    full_contraction = TensorMonomial(
        (
            TensorFactor(WEYL, (0, 1, 2, 3)),
            TensorFactor(WEYL, (0, 1, 2, 3)),
        )
    )
    explicit_duals = tuple(
        hodge_dualize_weyl_factor(full_contraction, factor, pair=pair)
        for factor in (0, 1)
        for pair in ("first", "second")
    )
    if len({expression.canonical_hash() for expression in explicit_duals}) != 1:
        raise AssertionError("explicit Hodge placements do not agree")

    compressed_full = TensorMonomial(
        (
            TensorFactor(DUAL_WEYL, (0, 1, 2, 3)),
            TensorFactor(WEYL, (0, 1, 2, 3)),
        )
    )
    compressed_expansion = expand_dual_weyl_factor(compressed_full, 0)
    if compressed_expansion != explicit_duals[0]:
        raise AssertionError("compressed dual carrier disagrees with epsilon Hodge")

    full_expression = TensorExpression.monomial(full_contraction)
    hodge_square = {
        "euclidean": weyl_hodge_square_contraction(Signature.EUCLIDEAN),
        "lorentzian": weyl_hodge_square_contraction(Signature.LORENTZIAN),
    }
    if hodge_square["euclidean"] != full_expression:
        raise AssertionError("Euclidean Weyl Hodge square drifted")
    if hodge_square["lorentzian"] != -full_expression:
        raise AssertionError("Lorentzian Weyl Hodge square drifted")

    cyclic = cotton_cyclic_relation()
    differential = weyl_differential_bianchi_relation()
    if not cyclic or not differential:
        raise AssertionError("target-native Cotton relations vanished")

    return {
        "even": even,
        "odd": odd,
        "cotton_dimension_four_scalar_count": _cotton_dimension_four_scalar_count(),
        "cotton_cyclic_relation": cyclic,
        "weyl_cotton_differential_relation": differential,
        "explicit_hodge_companion": explicit_duals[0],
        "compressed_hodge_expansion": compressed_expansion,
        "hodge_square": hodge_square,
    }
