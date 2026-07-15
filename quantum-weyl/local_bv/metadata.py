"""Exact metadata for fields in the local coordinate-jet bootstrap."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Iterable, Mapping


class IndexVariance(str, Enum):
    COVARIANT = "covariant"
    CONTRAVARIANT = "contravariant"


class SpacetimeParity(str, Enum):
    EVEN = "even"
    ODD = "odd"


@dataclass(frozen=True)
class FieldSpec:
    """Metadata independent of a particular derivative multi-index.

    All numerical gradings are integral except ``mass_dimension`` and
    ``weyl_weight``, which use :class:`fractions.Fraction`.  This prevents a
    certificate from acquiring floating-point values through serialization.
    """

    name: str
    index_variance: tuple[IndexVariance, ...]
    symmetric_index_pairs: tuple[tuple[int, int], ...]
    ghost_number: int
    antifield_number: int
    form_degree: int
    mass_dimension: Fraction
    grassmann_parity: int
    spacetime_parity: SpacetimeParity
    weyl_weight: Fraction
    provenance: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("field name must be nonempty")
        if self.antifield_number < 0:
            raise ValueError("antifield_number must be nonnegative")
        if self.form_degree < 0:
            raise ValueError("form_degree must be nonnegative")
        if self.grassmann_parity not in (0, 1):
            raise ValueError("grassmann_parity must be 0 or 1")
        rank = len(self.index_variance)
        for left, right in self.symmetric_index_pairs:
            if not (0 <= left < right < rank):
                raise ValueError("invalid symmetric index pair")
        if not self.provenance:
            raise ValueError("provenance must be nonempty")

    @property
    def rank(self) -> int:
        return len(self.index_variance)

    def canonical_components(self, components: Iterable[int], dimension: int) -> tuple[int, ...]:
        values = tuple(components)
        if len(values) != self.rank:
            raise ValueError(f"{self.name} expects {self.rank} tensor indices")
        if any(value < 0 or value >= dimension for value in values):
            raise ValueError(f"component outside dimension {dimension}")
        mutable = list(values)
        for left, right in self.symmetric_index_pairs:
            if mutable[left] > mutable[right]:
                mutable[left], mutable[right] = mutable[right], mutable[left]
        return tuple(mutable)

    @staticmethod
    def _fraction_payload(value: Fraction) -> dict[str, int]:
        return {"numerator": value.numerator, "denominator": value.denominator}

    def canonical_payload(self) -> dict[str, object]:
        return {
            "name": self.name,
            "index_variance": [value.value for value in self.index_variance],
            "symmetric_index_pairs": [list(pair) for pair in self.symmetric_index_pairs],
            "ghost_number": self.ghost_number,
            "antifield_number": self.antifield_number,
            "form_degree": self.form_degree,
            "mass_dimension": self._fraction_payload(self.mass_dimension),
            "grassmann_parity": self.grassmann_parity,
            "spacetime_parity": self.spacetime_parity.value,
            "weyl_weight": self._fraction_payload(self.weyl_weight),
            "provenance": self.provenance,
        }


def minimal_registry() -> Mapping[str, FieldSpec]:
    """Return the minimal Diff x Weyl fields stated in the quantum brief.

    The metric Weyl weight is the coefficient in ``delta_omega g=2 omega g``.
    Coordinate derivatives are assigned mass dimension one by
    :class:`local_bv.algebra.JetVariable`; no unsupported covariant-weight
    rule is inferred for derivative jets.
    """

    provenance = "Quantum programme brief, section 4.2 (minimal transformations)"
    specs = (
        FieldSpec(
            name="g",
            index_variance=(IndexVariance.COVARIANT, IndexVariance.COVARIANT),
            symmetric_index_pairs=((0, 1),),
            ghost_number=0,
            antifield_number=0,
            form_degree=0,
            mass_dimension=Fraction(0),
            grassmann_parity=0,
            spacetime_parity=SpacetimeParity.EVEN,
            weyl_weight=Fraction(2),
            provenance=provenance,
        ),
        FieldSpec(
            name="xi",
            index_variance=(IndexVariance.CONTRAVARIANT,),
            symmetric_index_pairs=(),
            ghost_number=1,
            antifield_number=0,
            form_degree=0,
            mass_dimension=Fraction(-1),
            grassmann_parity=1,
            spacetime_parity=SpacetimeParity.EVEN,
            weyl_weight=Fraction(0),
            provenance=provenance,
        ),
        FieldSpec(
            name="omega",
            index_variance=(),
            symmetric_index_pairs=(),
            ghost_number=1,
            antifield_number=0,
            form_degree=0,
            mass_dimension=Fraction(0),
            grassmann_parity=1,
            spacetime_parity=SpacetimeParity.EVEN,
            weyl_weight=Fraction(0),
            provenance=provenance,
        ),
    )
    return {spec.name: spec for spec in specs}
