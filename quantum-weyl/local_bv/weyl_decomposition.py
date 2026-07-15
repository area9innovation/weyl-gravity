"""Exact Weyl--Schouten--Cotton conventions and Hodge primitives in 4D.

The module keeps the Ricci decomposition explicit.  In particular, it never
identifies a differentiated Riemann tensor with a differentiated Weyl tensor:
the missing terms are represented by Schouten derivatives, equivalently by
the Cotton tensor in the cyclic differential identity.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Literal

from .curvature import EPSILON, RIEMANN
from .hodge import Signature
from .specialization import WEYL, reduce_epsilon_pair_in_monomial
from .tensors import (
    TensorExpression,
    TensorFactor,
    TensorMonomial,
    TensorSpec,
    signed_permutation_group,
)


METRIC = TensorSpec(
    "metric",
    2,
    signed_permutation_group(2, (((1, 0), 1),)),
)

SCHOUTEN = TensorSpec(
    "Schouten",
    2,
    signed_permutation_group(2, (((1, 0), 1),)),
)

# A_{abc} = nabla_b P_{ca} - nabla_c P_{ba}.
COTTON = TensorSpec(
    "Cotton",
    3,
    signed_permutation_group(3, (((0, 2, 1), -1),)),
)


def _single(
    spec: TensorSpec,
    slots: tuple[int, ...],
    derivatives: tuple[int, ...] = (),
) -> TensorMonomial:
    return TensorMonomial((TensorFactor(spec, slots, derivatives),))


def _product(*factors: TensorFactor) -> TensorMonomial:
    return TensorMonomial(tuple(factors))


def _ricci_decomposition_terms(
    slots: tuple[int, int, int, int],
) -> dict[TensorMonomial, Fraction]:
    a, b, c, d = slots
    return {
        _single(RIEMANN, slots): 1,
        _single(WEYL, slots): -1,
        _product(
            TensorFactor(METRIC, (a, c)),
            TensorFactor(SCHOUTEN, (b, d)),
        ): -1,
        _product(
            TensorFactor(METRIC, (a, d)),
            TensorFactor(SCHOUTEN, (b, c)),
        ): 1,
        _product(
            TensorFactor(METRIC, (b, c)),
            TensorFactor(SCHOUTEN, (a, d)),
        ): 1,
        _product(
            TensorFactor(METRIC, (b, d)),
            TensorFactor(SCHOUTEN, (a, c)),
        ): -1,
    }


def ricci_decomposition_relation(
    slots: tuple[int, int, int, int] = (0, 1, 2, 3),
) -> TensorExpression:
    """Return ``R_abcd - C_abcd - (g wedge P)_abcd = 0`` exactly."""

    return TensorExpression(_ricci_decomposition_terms(slots))


def differentiated_ricci_decomposition_relation(
    slots: tuple[int, int, int, int] = (0, 1, 2, 3),
    derivative_index: int = 4,
) -> TensorExpression:
    """Differentiate the Ricci decomposition using ``nabla g = 0``."""

    if derivative_index in slots:
        raise ValueError("the derivative index must be distinct from tensor slots")
    terms: dict[TensorMonomial, Fraction] = {}
    # Differentiate before canonicalization so a caller-supplied derivative
    # label cannot collide with the canonical relabeling of the four free
    # curvature slots.
    for monomial, coefficient in _ricci_decomposition_terms(slots).items():
        differentiated = []
        for factor in monomial.factors:
            if factor.spec == METRIC:
                differentiated.append(factor)
            else:
                differentiated.append(factor.with_added_derivative(derivative_index))
        term = TensorMonomial(tuple(differentiated))
        terms[term] = terms.get(term, Fraction()) + coefficient
    return TensorExpression(terms)


def cotton_definition_relation(
    slots: tuple[int, int, int] = (0, 1, 2),
) -> TensorExpression:
    """Return ``A_abc - nabla_b P_ca + nabla_c P_ba = 0``."""

    a, b, c = slots
    return TensorExpression(
        {
            _single(COTTON, slots): 1,
            _single(SCHOUTEN, (c, a), (b,)): -1,
            _single(SCHOUTEN, (b, a), (c,)): 1,
        }
    )


def cotton_cyclic_relation(
    slots: tuple[int, int, int] = (0, 1, 2),
) -> TensorExpression:
    """Return the algebraic Cotton identity ``A_[abc] = 0``."""

    a, b, c = slots
    return TensorExpression(
        {
            _single(COTTON, (a, b, c)): 1,
            _single(COTTON, (b, c, a)): 1,
            _single(COTTON, (c, a, b)): 1,
        }
    )


def expand_cotton_definitions(expression: TensorExpression) -> TensorExpression:
    """Expand every undifferentiated Cotton factor using the declared convention."""

    output: dict[TensorMonomial, Fraction] = {}
    for monomial, coefficient in expression.terms.items():
        partial: list[tuple[Fraction, tuple[TensorFactor, ...]]] = [
            (coefficient, ())
        ]
        for factor in monomial.factors:
            if factor.spec != COTTON:
                partial = [
                    (value, factors + (factor,)) for value, factors in partial
                ]
                continue
            if factor.derivatives:
                raise ValueError(
                    "differentiated Cotton expansion requires derivative-order bookkeeping"
                )
            a, b, c = factor.slots
            replacements = (
                (Fraction(1), TensorFactor(SCHOUTEN, (c, a), (b,))),
                (Fraction(-1), TensorFactor(SCHOUTEN, (b, a), (c,))),
            )
            partial = [
                (value * replacement_coefficient, factors + (replacement,))
                for value, factors in partial
                for replacement_coefficient, replacement in replacements
            ]
        for value, factors in partial:
            term = TensorMonomial(factors)
            output[term] = output.get(term, Fraction()) + value
    return TensorExpression(output)


def weyl_differential_bianchi_relation(
    slots: tuple[int, int, int, int, int] = (0, 1, 2, 3, 4),
) -> TensorExpression:
    """Return the cyclic differential Weyl identity in the Cotton convention.

    For ``(a,b,c,d,e)`` the first three terms are
    ``nabla_e C_abcd + nabla_a C_becd + nabla_b C_eacd``.  The six metric--
    Cotton terms are obtained by differentiating ``g wedge P``; expanding
    Cotton therefore provides an exact sign audit against the Schouten form.
    """

    a, b, c, d, e = slots
    return TensorExpression(
        {
            _single(WEYL, (a, b, c, d), (e,)): 1,
            _single(WEYL, (b, e, c, d), (a,)): 1,
            _single(WEYL, (e, a, c, d), (b,)): 1,
            _product(
                TensorFactor(METRIC, (a, c)),
                TensorFactor(COTTON, (d, e, b)),
            ): 1,
            _product(
                TensorFactor(METRIC, (a, d)),
                TensorFactor(COTTON, (c, e, b)),
            ): -1,
            _product(
                TensorFactor(METRIC, (b, c)),
                TensorFactor(COTTON, (d, e, a)),
            ): -1,
            _product(
                TensorFactor(METRIC, (b, d)),
                TensorFactor(COTTON, (c, e, a)),
            ): 1,
            _product(
                TensorFactor(METRIC, (e, c)),
                TensorFactor(COTTON, (d, b, a)),
            ): 1,
            _product(
                TensorFactor(METRIC, (e, d)),
                TensorFactor(COTTON, (c, a, b)),
            ): 1,
        }
    )


def tracefree_cotton_reduce(expression: TensorExpression) -> TensorExpression:
    """Impose the irreducible Cotton trace condition on internal contractions."""

    return TensorExpression(
        {
            monomial: coefficient
            for monomial, coefficient in expression.terms.items()
            if not any(
                factor.spec == COTTON
                and len(set(factor.slots)) != len(factor.slots)
                for factor in monomial.factors
            )
        }
    )


def hodge_dualize_weyl_factor(
    monomial: TensorMonomial,
    factor_index: int,
    *,
    pair: Literal["first", "second"] = "first",
) -> TensorExpression:
    """Apply one exact Hodge star to an antisymmetric pair of a Weyl factor."""

    if not 0 <= factor_index < len(monomial.factors):
        raise IndexError("Weyl factor index is outside the monomial")
    factor = monomial.factors[factor_index]
    if factor.spec != WEYL:
        raise ValueError("selected factor must be a Weyl tensor")
    if pair not in ("first", "second"):
        raise ValueError("Weyl Hodge pair must be 'first' or 'second'")
    positions = (0, 1) if pair == "first" else (2, 3)
    next_index = max(
        (index for item in monomial.factors for index in item.all_indices),
        default=-1,
    ) + 1
    fresh = (next_index, next_index + 1)
    original = (factor.slots[positions[0]], factor.slots[positions[1]])
    slots = list(factor.slots)
    slots[positions[0]], slots[positions[1]] = fresh
    factors = list(monomial.factors)
    factors[factor_index] = TensorFactor(
        WEYL, tuple(slots), factor.derivatives
    )
    factors.insert(0, TensorFactor(EPSILON, original + fresh))
    return Fraction(1, 2) * TensorExpression.monomial(
        TensorMonomial(tuple(factors))
    )


def weyl_hodge_square_contraction(signature: Signature) -> TensorExpression:
    """Return a complete exact witness for ``(*^2 C) . C``."""

    double_dual = TensorMonomial(
        (
            TensorFactor(EPSILON, (0, 1, 4, 5)),
            TensorFactor(EPSILON, (4, 5, 6, 7)),
            TensorFactor(WEYL, (6, 7, 2, 3)),
            TensorFactor(WEYL, (0, 1, 2, 3)),
        )
    )
    return Fraction(1, 4) * reduce_epsilon_pair_in_monomial(
        double_dual, 0, 1, signature
    )
