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
    used = set(factor.slots) | {left, right}
    dummy = max(used, default=-1) + 1
    terms: dict[TensorMonomial, int] = {
        TensorMonomial(
            (TensorFactor(factor.spec, factor.slots, (left, right)),)
        ): 1,
        TensorMonomial(
            (TensorFactor(factor.spec, factor.slots, (right, left)),)
        ): -1,
    }
    for position, covariant_index in enumerate(factor.slots):
        acted_slots = list(factor.slots)
        acted_slots[position] = dummy
        curvature_action = TensorMonomial(
            (
                TensorFactor(RIEMANN, (dummy, covariant_index, left, right)),
                TensorFactor(factor.spec, tuple(acted_slots)),
            )
        )
        # Moving the negative curvature action to the left side gives +R*T.
        terms[curvature_action] = terms.get(curvature_action, 0) + 1
        dummy += 1
    return TensorExpression(terms)
