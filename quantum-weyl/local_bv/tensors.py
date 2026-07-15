"""Exact abstract-index tensor monomials for local BV canonicalization.

The implementation treats repeated lowered index labels as contractions with
the background inverse metric.  It is deliberately finite and algebraic: no
coordinate components, floating-point comparisons, or dimension-sampled
tensor identities enter the canonical form.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import permutations, product
from typing import Iterable, Mapping, Sequence

from .algebra import canonical_sha256


SignedPermutation = tuple[tuple[int, ...], int]


def signed_permutation_group(
    rank: int, generators: Iterable[SignedPermutation]
) -> tuple[SignedPermutation, ...]:
    """Close signed slot permutations under composition exactly."""

    identity = tuple(range(rank))
    signs: dict[tuple[int, ...], int] = {identity: 1}
    pending = [(identity, 1), *generators]
    while pending:
        permutation, sign = pending.pop()
        if sorted(permutation) != list(range(rank)) or sign not in (-1, 1):
            raise ValueError("invalid signed permutation")
        previous = signs.get(permutation)
        if previous is not None:
            if previous != sign:
                raise ValueError("symmetry generators force the tensor to vanish")
            continue
        signs[permutation] = sign
        known = list(signs.items())
        for other, other_sign in known:
            for left, left_sign, right, right_sign in (
                (permutation, sign, other, other_sign),
                (other, other_sign, permutation, sign),
            ):
                composed = tuple(left[right[index]] for index in range(rank))
                composed_sign = left_sign * right_sign
                if composed not in signs:
                    pending.append((composed, composed_sign))
                elif signs[composed] != composed_sign:
                    raise ValueError("inconsistent signed symmetry group")
    return tuple(sorted(signs.items()))


@dataclass(frozen=True)
class TensorSpec:
    name: str
    rank: int
    intrinsic_symmetries: tuple[SignedPermutation, ...]
    grassmann_parity: int = 0
    spacetime_parity: int = 0

    def __post_init__(self) -> None:
        if not self.name or self.rank < 0:
            raise ValueError("tensor name and nonnegative rank are required")
        if self.grassmann_parity not in (0, 1):
            raise ValueError("Grassmann parity must be zero or one")
        if self.spacetime_parity not in (0, 1):
            raise ValueError("spacetime parity must be zero or one")
        identity = (tuple(range(self.rank)), 1)
        if identity not in self.intrinsic_symmetries:
            raise ValueError("intrinsic symmetry group must contain the identity")

    @classmethod
    def without_slot_symmetry(
        cls,
        name: str,
        rank: int,
        *,
        grassmann_parity: int = 0,
        spacetime_parity: int = 0,
    ) -> "TensorSpec":
        return cls(
            name,
            rank,
            ((tuple(range(rank)), 1),),
            grassmann_parity,
            spacetime_parity,
        )


@dataclass(frozen=True)
class TensorFactor:
    spec: TensorSpec
    slots: tuple[int, ...]
    derivatives: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if len(self.slots) != self.spec.rank:
            raise ValueError(f"{self.spec.name} expects {self.spec.rank} slots")
        if any(not isinstance(index, int) or index < 0 for index in self.all_indices):
            raise ValueError("abstract indices must be nonnegative integers")

    @property
    def all_indices(self) -> tuple[int, ...]:
        return self.derivatives + self.slots

    def intrinsic_variants(self) -> tuple[tuple[int, "TensorFactor"], ...]:
        return tuple(
            (
                sign,
                TensorFactor(
                    self.spec,
                    tuple(self.slots[index] for index in permutation),
                    self.derivatives,
                ),
            )
            for permutation, sign in self.spec.intrinsic_symmetries
        )

    def with_added_derivative(self, index: int) -> "TensorFactor":
        return TensorFactor(self.spec, self.slots, (index,) + self.derivatives)

    def sort_key(self) -> tuple[object, ...]:
        return self.spec.name, self.derivatives, self.slots

    def canonical_payload(self) -> dict[str, object]:
        return {
            "tensor": self.spec.name,
            "derivatives": list(self.derivatives),
            "slots": list(self.slots),
            "grassmann_parity": self.spec.grassmann_parity,
            "spacetime_parity": self.spec.spacetime_parity,
        }


def _koszul_permutation_sign(
    factors: Sequence[TensorFactor], order: Sequence[int]
) -> int:
    inversions = 0
    for left_position, left_original in enumerate(order):
        if not factors[left_original].spec.grassmann_parity:
            continue
        for right_original in order[left_position + 1 :]:
            if (
                factors[right_original].spec.grassmann_parity
                and left_original > right_original
            ):
                inversions += 1
    return -1 if inversions % 2 else 1


def _first_occurrence_relabel(
    factors: Sequence[TensorFactor],
) -> tuple[TensorFactor, ...]:
    counts: dict[int, int] = {}
    for factor in factors:
        for index in factor.all_indices:
            counts[index] = counts.get(index, 0) + 1
    if any(count > 2 for count in counts.values()):
        raise ValueError("an abstract index may occur at most twice")
    free = sorted(index for index, count in counts.items() if count == 1)
    labels: dict[int, int] = {index: position for position, index in enumerate(free)}

    def relabel(index: int) -> int:
        if index not in labels:
            labels[index] = len(labels)
        return labels[index]

    return tuple(
        TensorFactor(
            factor.spec,
            tuple(relabel(index) for index in factor.slots),
            tuple(relabel(index) for index in factor.derivatives),
        )
        for factor in factors
    )


@dataclass(frozen=True)
class TensorMonomial:
    factors: tuple[TensorFactor, ...]

    @lru_cache(maxsize=None)
    def canonicalize(self) -> tuple[int, "TensorMonomial | None"]:
        """Return the signed canonical orbit representative.

        The orbit includes every intrinsic signed slot symmetry, every graded
        factor permutation, and deterministic first-occurrence dummy-index
        renaming.  Opposite signs on the same representative certify zero.
        """

        if not self.factors:
            return 1, self
        best_key: tuple[object, ...] | None = None
        best_monomial: TensorMonomial | None = None
        best_signs: set[int] = set()
        variant_lists = [factor.intrinsic_variants() for factor in self.factors]
        for variants in product(*variant_lists):
            intrinsic_sign = 1
            intrinsic_factors = []
            for sign, factor in variants:
                intrinsic_sign *= sign
                intrinsic_factors.append(factor)
            for order in permutations(range(len(intrinsic_factors))):
                sign = intrinsic_sign * _koszul_permutation_sign(
                    intrinsic_factors, order
                )
                ordered = tuple(intrinsic_factors[index] for index in order)
                relabeled = _first_occurrence_relabel(ordered)
                key = tuple(factor.sort_key() for factor in relabeled)
                if best_key is None or key < best_key:
                    best_key = key
                    best_monomial = TensorMonomial(relabeled)
                    best_signs = {sign}
                elif key == best_key:
                    best_signs.add(sign)
        if best_signs == {-1, 1}:
            return 0, None
        assert best_monomial is not None and len(best_signs) == 1
        return next(iter(best_signs)), best_monomial

    def index_multiplicities(self) -> dict[int, int]:
        counts: dict[int, int] = {}
        for factor in self.factors:
            for index in factor.all_indices:
                counts[index] = counts.get(index, 0) + 1
        return counts

    def is_complete_contraction(self) -> bool:
        return all(count == 2 for count in self.index_multiplicities().values())

    def spacetime_parity(self) -> int:
        return sum(factor.spec.spacetime_parity for factor in self.factors) % 2

    def canonical_payload(self) -> dict[str, object]:
        return {"factors": [factor.canonical_payload() for factor in self.factors]}

    def sort_key(self) -> tuple[object, ...]:
        return tuple(factor.sort_key() for factor in self.factors)


class TensorExpression:
    """Sparse exact linear combination of canonical tensor monomials."""

    def __init__(
        self,
        terms: Mapping[TensorMonomial, Fraction | int] | None = None,
    ) -> None:
        reduced: dict[TensorMonomial, Fraction] = {}
        for monomial, coefficient in (terms or {}).items():
            sign, canonical = monomial.canonicalize()
            if not sign or canonical is None:
                continue
            value = reduced.get(canonical, Fraction()) + sign * Fraction(coefficient)
            if value:
                reduced[canonical] = value
            else:
                reduced.pop(canonical, None)
        self._terms = reduced

    @classmethod
    def monomial(cls, monomial: TensorMonomial) -> "TensorExpression":
        return cls({monomial: 1})

    @property
    def terms(self) -> Mapping[TensorMonomial, Fraction]:
        return dict(self._terms)

    def __bool__(self) -> bool:
        return bool(self._terms)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, TensorExpression) and self._terms == other._terms

    def __neg__(self) -> "TensorExpression":
        return TensorExpression(
            {monomial: -coefficient for monomial, coefficient in self._terms.items()}
        )

    def __add__(self, other: "TensorExpression") -> "TensorExpression":
        terms = dict(self._terms)
        for monomial, coefficient in other._terms.items():
            terms[monomial] = terms.get(monomial, Fraction()) + coefficient
        return TensorExpression(terms)

    def __sub__(self, other: "TensorExpression") -> "TensorExpression":
        return self + (-other)

    def __mul__(self, coefficient: Fraction | int) -> "TensorExpression":
        return TensorExpression(
            {
                monomial: value * Fraction(coefficient)
                for monomial, value in self._terms.items()
            }
        )

    def __rmul__(self, coefficient: Fraction | int) -> "TensorExpression":
        return self * coefficient

    def canonical_payload(self) -> dict[str, object]:
        return {
            "terms": [
                {
                    "coefficient": {
                        "numerator": coefficient.numerator,
                        "denominator": coefficient.denominator,
                    },
                    "monomial": monomial.canonical_payload(),
                }
                for monomial, coefficient in sorted(
                    self._terms.items(), key=lambda item: item[0].sort_key()
                )
            ]
        }

    def canonical_hash(self) -> str:
        return canonical_sha256(self.canonical_payload())

    def parity_transform(self) -> "TensorExpression":
        return TensorExpression(
            {
                monomial: coefficient * (-1 if monomial.spacetime_parity() else 1)
                for monomial, coefficient in self._terms.items()
            }
        )


def total_covariant_derivative(
    monomial: TensorMonomial, divergence_index: int
) -> TensorExpression:
    """Apply the even covariant Leibniz rule to a vector monomial.

    The divergence index must occur exactly once before differentiation.  The
    returned scalar expression is therefore a complete contraction whenever
    every other index was already paired.
    """

    if monomial.index_multiplicities().get(divergence_index) != 1:
        raise ValueError("divergence index must be the unique free index")
    terms: dict[TensorMonomial, int] = {}
    for position, factor in enumerate(monomial.factors):
        differentiated = list(monomial.factors)
        differentiated[position] = factor.with_added_derivative(divergence_index)
        term = TensorMonomial(tuple(differentiated))
        terms[term] = terms.get(term, 0) + 1
    return TensorExpression(terms)
