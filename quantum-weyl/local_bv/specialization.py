"""Exact staged specialization foundations for local curvature quotients.

The universal tensor quotient and each dimension-, trace-, or parity-specific
specialization remain separate stages over one fixed ambient monomial basis.
No four-dimensional identity is installed by this module itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations
from typing import Iterable, Mapping, Sequence

from .algebra import canonical_sha256
from .curvature import EPSILON, RIEMANN
from .hodge import Signature, TwoFormHodge
from .quotient import RelationQuotient, exact_nullspace, exact_rank
from .tensors import TensorExpression, TensorFactor, TensorMonomial, TensorSpec


WEYL = TensorSpec("Weyl", 4, RIEMANN.intrinsic_symmetries)


def _fraction_payload(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _matrix_payload(
    matrix: Sequence[Sequence[Fraction]],
) -> list[list[dict[str, int]]]:
    return [[_fraction_payload(value) for value in row] for row in matrix]


def _permutation_sign(permutation: Sequence[int]) -> int:
    inversions = sum(
        left > right
        for position, left in enumerate(permutation)
        for right in permutation[position + 1 :]
    )
    return -1 if inversions % 2 else 1


@dataclass(frozen=True, order=True)
class TensorOccurrence:
    """One auditable derivative or tensor-slot occurrence in a monomial."""

    factor_index: int
    part: str
    position: int

    def __post_init__(self) -> None:
        if self.factor_index < 0 or self.position < 0:
            raise ValueError("occurrence positions must be nonnegative")
        if self.part not in ("derivatives", "slots"):
            raise ValueError("occurrence part must be 'derivatives' or 'slots'")


def antisymmetrize_occurrences(
    monomial: TensorMonomial,
    occurrences: Sequence[TensorOccurrence],
) -> TensorExpression:
    """Antisymmetrize selected index occurrences without sampling components.

    Only the selected occurrences are permuted; their contracted partners stay
    fixed. Selecting five occurrences therefore supplies the exact primitive
    needed to generate four-dimensional Schouten identities.
    """

    selected = tuple(occurrences)
    if not selected:
        raise ValueError("at least one occurrence is required")
    if len(set(selected)) != len(selected):
        raise ValueError("antisymmetrized occurrences must be distinct")

    labels: list[int] = []
    for occurrence in selected:
        if occurrence.factor_index >= len(monomial.factors):
            raise IndexError("factor occurrence is outside the monomial")
        factor = monomial.factors[occurrence.factor_index]
        values = getattr(factor, occurrence.part)
        if occurrence.position >= len(values):
            raise IndexError("slot occurrence is outside the tensor factor")
        labels.append(values[occurrence.position])

    terms: dict[TensorMonomial, int] = {}
    for permutation in permutations(range(len(selected))):
        factors = list(monomial.factors)
        replacements: dict[int, tuple[list[int], list[int]]] = {}
        for occurrence, source in zip(selected, permutation):
            slots, derivatives = replacements.setdefault(
                occurrence.factor_index,
                (
                    list(factors[occurrence.factor_index].slots),
                    list(factors[occurrence.factor_index].derivatives),
                ),
            )
            target = slots if occurrence.part == "slots" else derivatives
            target[occurrence.position] = labels[source]
        for factor_index, (slots, derivatives) in replacements.items():
            original = factors[factor_index]
            factors[factor_index] = TensorFactor(
                original.spec, tuple(slots), tuple(derivatives)
            )
        term = TensorMonomial(tuple(factors))
        terms[term] = terms.get(term, 0) + _permutation_sign(permutation)
    return TensorExpression(terms)


def schouten_antisymmetrization(
    monomial: TensorMonomial,
    occurrences: Sequence[TensorOccurrence],
    *,
    dimension: int,
) -> TensorExpression:
    """Generate the dimension-dependent antisymmetry over ``dimension + 1`` slots."""

    if dimension < 1:
        raise ValueError("dimension must be positive")
    if len(occurrences) != dimension + 1:
        raise ValueError("a Schouten identity antisymmetrizes dimension + 1 slots")
    return antisymmetrize_occurrences(monomial, occurrences)


@dataclass(frozen=True)
class EpsilonMatching:
    """One term in epsilon_abcd epsilon^efgh as a signed index matching."""

    coefficient: int
    pairs: tuple[tuple[int, int], ...]

    def canonical_payload(self) -> dict[str, object]:
        return {
            "coefficient": self.coefficient,
            "pairs": [list(pair) for pair in self.pairs],
        }


def epsilon_pair_expansion(signature: Signature) -> tuple[EpsilonMatching, ...]:
    """Return the exact 24-term generalized-delta epsilon-pair expansion."""

    signature_sign = TwoFormHodge(signature).star_square_sign
    return tuple(
        EpsilonMatching(
            signature_sign * _permutation_sign(permutation),
            tuple((left, right) for left, right in enumerate(permutation)),
        )
        for permutation in permutations(range(4))
    )


def reduce_epsilon_pair_in_monomial(
    monomial: TensorMonomial,
    left_factor: int,
    right_factor: int,
    signature: Signature,
    *,
    dimension: int = 4,
) -> TensorExpression:
    """Eliminate two epsilon factors through the generalized Kronecker delta.

    Delta matchings identify the corresponding abstract labels. Components
    with no surviving tensor occurrence are closed delta loops and contribute
    one factor of ``dimension``. This handles complete epsilon contractions as
    well as epsilon pairs attached to spectator tensors.
    """

    if dimension != 4:
        raise ValueError("the declared epsilon tensor has rank four")
    if left_factor == right_factor:
        raise ValueError("two distinct epsilon factors are required")
    if not 0 <= left_factor < len(monomial.factors) or not 0 <= right_factor < len(
        monomial.factors
    ):
        raise IndexError("epsilon factor index is outside the monomial")
    left = monomial.factors[left_factor]
    right = monomial.factors[right_factor]
    if left.spec != EPSILON or right.spec != EPSILON:
        raise ValueError("selected factors must both be epsilon tensors")
    if left.derivatives or right.derivatives:
        raise ValueError("covariant derivatives of epsilon reduce to zero separately")

    remaining = tuple(
        factor
        for index, factor in enumerate(monomial.factors)
        if index not in (left_factor, right_factor)
    )
    external_counts: dict[int, int] = {}
    for factor in remaining:
        for label in factor.all_indices:
            external_counts[label] = external_counts.get(label, 0) + 1

    terms: dict[TensorMonomial, int] = {}
    for matching in epsilon_pair_expansion(signature):
        parent: dict[int, int] = {
            label: label for label in set(left.slots + right.slots)
        }

        def root(label: int) -> int:
            while parent[label] != label:
                parent[label] = parent[parent[label]]
                label = parent[label]
            return label

        def union(first: int, second: int) -> None:
            first_root, second_root = root(first), root(second)
            if first_root == second_root:
                return
            low, high = sorted((first_root, second_root))
            parent[high] = low

        for left_position, right_position in matching.pairs:
            union(left.slots[left_position], right.slots[right_position])

        components: dict[int, set[int]] = {}
        for label in parent:
            components.setdefault(root(label), set()).add(label)
        coefficient = matching.coefficient
        replacements: dict[int, int] = {}
        next_label = max(
            (index for factor in remaining for index in factor.all_indices),
            default=-1,
        ) + 1
        for labels in components.values():
            surviving = sum(external_counts.get(label, 0) for label in labels)
            if surviving == 0:
                coefficient *= dimension
                continue
            if surviving != 2:
                raise ValueError(
                    "epsilon reduction produced a component with neither zero nor two external occurrences"
                )
            target = next_label
            next_label += 1
            for label in labels:
                replacements[label] = target
        reduced_factors = tuple(
            TensorFactor(
                factor.spec,
                tuple(replacements.get(label, label) for label in factor.slots),
                tuple(
                    replacements.get(label, label) for label in factor.derivatives
                ),
            )
            for factor in remaining
        )
        reduced = TensorMonomial(reduced_factors)
        terms[reduced] = terms.get(reduced, 0) + coefficient
    return TensorExpression(terms)


def replace_riemann_by_weyl(expression: TensorExpression) -> TensorExpression:
    """Apply the formal Riemann-to-tracefree-Weyl tensor replacement."""

    terms: dict[TensorMonomial, Fraction] = {}
    for monomial, coefficient in expression.terms.items():
        replaced = TensorMonomial(
            tuple(
                TensorFactor(
                    WEYL if factor.spec == RIEMANN else factor.spec,
                    factor.slots,
                    factor.derivatives,
                )
                for factor in monomial.factors
            )
        )
        terms[replaced] = terms.get(replaced, Fraction()) + coefficient
    return tracefree_weyl_reduce(TensorExpression(terms))


def tracefree_weyl_reduce(expression: TensorExpression) -> TensorExpression:
    """Set every internal contraction of a Weyl tensor factor exactly to zero."""

    return TensorExpression(
        {
            monomial: coefficient
            for monomial, coefficient in expression.terms.items()
            if not any(
                factor.spec == WEYL and len(set(factor.slots)) != len(factor.slots)
                for factor in monomial.factors
            )
        }
    )


@dataclass(frozen=True)
class RelationFamily:
    """A deterministic named family of generated specialization relations."""

    name: str
    relations: tuple[TensorExpression, ...]
    provenance: str
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name or not self.provenance:
            raise ValueError("relation family name and provenance are required")
        unique = {
            relation.canonical_hash(): relation
            for relation in self.relations
            if relation
        }
        ordered = tuple(unique[digest] for digest in sorted(unique))
        for relation in ordered:
            parities = {monomial.spacetime_parity() for monomial in relation.terms}
            if len(parities) > 1:
                raise ValueError("each specialization relation must have fixed parity")
        object.__setattr__(self, "relations", ordered)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "name": self.name,
            "provenance": self.provenance,
            "assumptions": list(self.assumptions),
            "relation_count": len(self.relations),
            "relation_hashes": [
                relation.canonical_hash() for relation in self.relations
            ],
        }


def _projection_matrix(
    source: RelationQuotient, target: RelationQuotient
) -> tuple[tuple[Fraction, ...], ...]:
    columns = [
        target.free_coordinates(TensorExpression.monomial(source.basis[column]))
        for column in source.free_columns
    ]
    return tuple(
        tuple(column[row] for column in columns)
        for row in range(target.quotient_dimension)
    )


@dataclass(frozen=True)
class SpecializationStage:
    """One exact quotient and its induced map from the preceding stage."""

    name: str
    families: tuple[RelationFamily, ...]
    new_family_names: tuple[str, ...]
    quotient: RelationQuotient
    source_name: str | None = None
    projection_matrix: tuple[tuple[Fraction, ...], ...] = ()
    projection_source_dimension: int | None = None
    projection_kernel: tuple[tuple[Fraction, ...], ...] = ()

    @property
    def dimension(self) -> int:
        return self.quotient.quotient_dimension

    @property
    def parity_block_dimensions(self) -> dict[str, int]:
        ranks = {
            parity: self.quotient.rank_of_classes(
                TensorExpression.monomial(monomial)
                for monomial in self.quotient.basis
                if monomial.spacetime_parity() == value
            )
            for parity, value in (("even", 0), ("odd", 1))
        }
        if sum(ranks.values()) != self.dimension:
            raise AssertionError("specialization relations do not preserve parity blocks")
        return ranks

    def representative_ledger(
        self, representatives: Mapping[str, TensorExpression]
    ) -> dict[str, dict[str, object]]:
        ledger: dict[str, dict[str, object]] = {}
        for name in sorted(representatives):
            expression = representatives[name]
            coordinates = self.quotient.free_coordinates(expression)
            ledger[name] = {
                "expression_sha256": expression.canonical_hash(),
                "coordinates": [_fraction_payload(value) for value in coordinates],
                "status": "ZERO" if not any(coordinates) else "NONZERO",
            }
        return ledger

    def canonical_payload(self) -> dict[str, object]:
        source_dimension = self.projection_source_dimension
        projection_rank = (
            exact_rank(self.projection_matrix) if source_dimension is not None else None
        )
        return {
            "name": self.name,
            "source_name": self.source_name,
            "dimension": self.dimension,
            "relation_rank": self.quotient.relation_rank,
            "families": [family.canonical_payload() for family in self.families],
            "new_family_names": list(self.new_family_names),
            "parity_block_dimensions": self.parity_block_dimensions,
            "projection": None
            if source_dimension is None
            else {
                "source_dimension": source_dimension,
                "target_dimension": self.dimension,
                "rank": projection_rank,
                "kernel_dimension": len(self.projection_kernel),
                "matrix": _matrix_payload(self.projection_matrix),
                "kernel_basis": _matrix_payload(self.projection_kernel),
            },
        }


@dataclass(frozen=True)
class SpecializationTower:
    """An immutable sequence of exact quotients over one ambient basis."""

    ambient_basis: tuple[TensorMonomial, ...]
    stages: tuple[SpecializationStage, ...]

    @classmethod
    def start(
        cls,
        name: str,
        ambient_basis: Iterable[TensorMonomial],
        families: Iterable[RelationFamily] = (),
    ) -> "SpecializationTower":
        family_tuple = tuple(families)
        cls._validate_family_names(family_tuple)
        quotient = RelationQuotient(
            ambient_basis,
            (relation for family in family_tuple for relation in family.relations),
        )
        stage = SpecializationStage(
            name=name,
            families=family_tuple,
            new_family_names=tuple(family.name for family in family_tuple),
            quotient=quotient,
        )
        return cls(tuple(quotient.basis), (stage,))

    @staticmethod
    def _validate_family_names(families: Sequence[RelationFamily]) -> None:
        names = [family.name for family in families]
        if len(names) != len(set(names)):
            raise ValueError("relation family names must be unique")

    @property
    def current(self) -> SpecializationStage:
        return self.stages[-1]

    def extend(
        self, name: str, families: Iterable[RelationFamily]
    ) -> "SpecializationTower":
        if any(stage.name == name for stage in self.stages):
            raise ValueError("specialization stage names must be unique")
        additions = tuple(families)
        all_families = self.current.families + additions
        self._validate_family_names(all_families)
        quotient = RelationQuotient(
            self.ambient_basis,
            (relation for family in all_families for relation in family.relations),
        )
        projection = _projection_matrix(self.current.quotient, quotient)
        source_dimension = self.current.dimension
        kernel = exact_nullspace(projection, column_count=source_dimension)
        rank = exact_rank(projection)
        if rank != quotient.quotient_dimension:
            raise AssertionError("specialization projection is not surjective")
        if len(kernel) != source_dimension - quotient.quotient_dimension:
            raise AssertionError("specialization rank-nullity check failed")
        stage = SpecializationStage(
            name=name,
            families=all_families,
            new_family_names=tuple(family.name for family in additions),
            quotient=quotient,
            source_name=self.current.name,
            projection_matrix=projection,
            projection_source_dimension=source_dimension,
            projection_kernel=kernel,
        )
        return SpecializationTower(self.ambient_basis, self.stages + (stage,))

    def canonical_payload(self) -> dict[str, object]:
        payload = {
            "ambient_basis_dimension": len(self.ambient_basis),
            "ambient_basis_sha256": canonical_sha256(
                [monomial.canonical_payload() for monomial in self.ambient_basis]
            ),
            "stages": [stage.canonical_payload() for stage in self.stages],
        }
        return {**payload, "tower_sha256": canonical_sha256(payload)}
