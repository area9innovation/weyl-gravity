"""Exact declared-sign covariant derivative commutator relations."""

from __future__ import annotations

from .curvature import RIEMANN
from .tensors import TensorExpression, TensorFactor, TensorMonomial


COMMUTATOR_CONVENTION = (
    "[nabla_a,nabla_b] T_{c1...cr} = "
    "-sum_i R^d{}_{ci ab} T_{c1...d...cr}"
)


def covariant_commutator_relation(
    factor: TensorFactor, left: int, right: int
) -> TensorExpression:
    """Return the commutator identity as a relation equal to zero.

    Every tensor slot is treated as covariant.  The input factor must carry no
    pre-existing derivative indices; commutators acting on derivative slots
    require the corresponding higher-rank curvature action and are outside
    this scoped constructor.
    """

    if factor.derivatives:
        raise ValueError("commutator input must have no existing derivatives")
    if left == right:
        raise ValueError("commutator derivative indices must be distinct")
    if left in factor.slots or right in factor.slots:
        raise ValueError("derivative and tensor free indices must be distinct")
    return covariant_commutator_relation_in_monomial(
        TensorMonomial((factor,)), 0, left, right
    )


def covariant_commutator_relation_in_monomial(
    monomial: TensorMonomial,
    factor_index: int,
    left: int,
    right: int,
) -> TensorExpression:
    """Apply the commutator to one factor inside a contraction pattern.

    Unlike the free witness constructor, derivative labels may already occur
    on tensor slots or spectator factors.  This is the form needed to emit
    relations mixing ``R nabla^2 R`` and ``R^3`` without losing contraction
    provenance.
    """

    if not 0 <= factor_index < len(monomial.factors):
        raise IndexError("commutator factor index is out of range")
    factor = monomial.factors[factor_index]
    if factor.derivatives:
        raise ValueError("commutator input must have no existing derivatives")
    if left == right:
        raise ValueError("commutator derivative indices must be distinct")
    existing = monomial.index_multiplicities()
    if existing.get(left, 0) >= 2 or existing.get(right, 0) >= 2:
        raise ValueError("commutator derivative would overuse an abstract index")

    used = set(existing) | {left, right}
    dummy = max(used, default=-1) + 1
    forward = list(monomial.factors)
    forward[factor_index] = TensorFactor(
        factor.spec, factor.slots, (left, right)
    )
    reverse = list(monomial.factors)
    reverse[factor_index] = TensorFactor(
        factor.spec, factor.slots, (right, left)
    )
    terms: dict[TensorMonomial, int] = {
        TensorMonomial(tuple(forward)): 1,
        TensorMonomial(tuple(reverse)): -1,
    }
    for position, covariant_index in enumerate(factor.slots):
        acted_slots = list(factor.slots)
        acted_slots[position] = dummy
        acted_factors = list(monomial.factors)
        acted_factors[factor_index] = TensorFactor(
            factor.spec, tuple(acted_slots)
        )
        acted_factors.append(
            TensorFactor(RIEMANN, (dummy, covariant_index, left, right))
        )
        curvature_action = TensorMonomial(
            tuple(acted_factors)
        )
        # Moving the negative curvature action to the left side gives +R*T.
        terms[curvature_action] = terms.get(curvature_action, 0) + 1
        dummy += 1
    return TensorExpression(terms)
