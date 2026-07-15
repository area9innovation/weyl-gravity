"""Exact horizontal differential forms over the coordinate-jet algebra."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Mapping

from .algebra import Expression, LocalJetAlgebra
from .brst import MinimalBRSTDifferential
from .metadata import FieldSpec, SpacetimeParity, minimal_registry


STRICT_DENSITY = "strict_density"


def strict_density_registry() -> Mapping[str, FieldSpec]:
    """Extend the minimal registry by one weight-one coordinate density.

    The atom represents the coefficient of a covariant top form after all
    curvature indices have been contracted.  It is Weyl invariant; its BRST
    row is therefore only the diffeomorphism density Lie derivative.
    """

    registry = dict(minimal_registry())
    registry[STRICT_DENSITY] = FieldSpec(
        name=STRICT_DENSITY,
        index_variance=(),
        symmetric_index_pairs=(),
        ghost_number=0,
        antifield_number=0,
        form_degree=0,
        mass_dimension=Fraction(4),
        grassmann_parity=0,
        spacetime_parity=SpacetimeParity.EVEN,
        weyl_weight=Fraction(0),
        provenance=(
            "Generated dimension-four strict Weyl-density carrier; its "
            "coordinate BRST row is the weight-one density Lie derivative."
        ),
    )
    return registry


class StrictDensityBRSTDifferential(MinimalBRSTDifferential):
    """Minimal Diff x Weyl BRST differential plus a strict density atom."""

    def _base_variation(self, variable):  # type: ignore[override]
        if variable.field != STRICT_DENSITY:
            return super()._base_variation(variable)
        algebra = self.algebra
        density = algebra.var(STRICT_DENSITY)
        result = Expression()
        for mu in range(algebra.dimension):
            xi = algebra.var("xi", (mu,))
            result += xi * algebra.total_derivative(density, mu)
            result += algebra.total_derivative(xi, mu) * density
        return result


def _wedge_sign(indices: tuple[int, ...]) -> tuple[int, tuple[int, ...] | None]:
    if len(set(indices)) != len(indices):
        return 0, None
    inversions = sum(
        left > right
        for position, left in enumerate(indices)
        for right in indices[position + 1 :]
    )
    return (-1 if inversions % 2 else 1), tuple(sorted(indices))


@dataclass(frozen=True)
class HorizontalForm:
    """Sparse exact form with supercommutative jet-polynomial coefficients."""

    dimension: int
    terms: Mapping[tuple[int, ...], Expression]

    def __post_init__(self) -> None:
        if self.dimension <= 0:
            raise ValueError("form dimension must be positive")
        reduced: dict[tuple[int, ...], Expression] = {}
        for indices, coefficient in self.terms.items():
            if any(index < 0 or index >= self.dimension for index in indices):
                raise ValueError("horizontal form index outside dimension")
            sign, canonical = _wedge_sign(tuple(indices))
            if not sign or canonical is None or not coefficient:
                continue
            value = reduced.get(canonical, Expression()) + sign * coefficient
            if value:
                reduced[canonical] = value
            else:
                reduced.pop(canonical, None)
        object.__setattr__(self, "terms", reduced)

    @classmethod
    def coefficient(cls, dimension: int, coefficient: Expression) -> "HorizontalForm":
        return cls(dimension, {(): coefficient})

    @classmethod
    def basis(cls, dimension: int, indices: Iterable[int]) -> "HorizontalForm":
        return cls(dimension, {tuple(indices): Expression.scalar(1)})

    def __bool__(self) -> bool:
        return bool(self.terms)

    def __neg__(self) -> "HorizontalForm":
        return HorizontalForm(
            self.dimension,
            {indices: -coefficient for indices, coefficient in self.terms.items()},
        )

    def __add__(self, other: "HorizontalForm") -> "HorizontalForm":
        if self.dimension != other.dimension:
            raise ValueError("cannot add forms in different dimensions")
        terms = dict(self.terms)
        for indices, coefficient in other.terms.items():
            terms[indices] = terms.get(indices, Expression()) + coefficient
        return HorizontalForm(self.dimension, terms)

    def __sub__(self, other: "HorizontalForm") -> "HorizontalForm":
        return self + (-other)

    def __mul__(self, scalar: Fraction | int) -> "HorizontalForm":
        return HorizontalForm(
            self.dimension,
            {indices: coefficient * scalar for indices, coefficient in self.terms.items()},
        )

    def __rmul__(self, scalar: Fraction | int) -> "HorizontalForm":
        return self * scalar

    @property
    def form_degrees(self) -> set[int]:
        return {len(indices) for indices in self.terms}

    def homogeneous_form_degree(self) -> int:
        degrees = self.form_degrees
        if len(degrees) != 1:
            raise ValueError("form is not homogeneous in horizontal degree")
        return next(iter(degrees))

    def wedge(self, other: "HorizontalForm") -> "HorizontalForm":
        if self.dimension != other.dimension:
            raise ValueError("cannot wedge forms in different dimensions")
        output: dict[tuple[int, ...], Expression] = {}
        for left_indices, left_coefficient in self.terms.items():
            for right_indices, right_coefficient in other.terms.items():
                coefficient_sign = (
                    -1
                    if len(left_indices) * right_coefficient.homogeneous_parity() % 2
                    else 1
                )
                wedge_sign, canonical = _wedge_sign(left_indices + right_indices)
                if not wedge_sign or canonical is None:
                    continue
                coefficient = (
                    coefficient_sign
                    * wedge_sign
                    * left_coefficient
                    * right_coefficient
                )
                output[canonical] = output.get(canonical, Expression()) + coefficient
        return HorizontalForm(self.dimension, output)

    def horizontal_differential(self, algebra: LocalJetAlgebra) -> "HorizontalForm":
        if algebra.dimension != self.dimension:
            raise ValueError("algebra and form dimensions disagree")
        output = HorizontalForm(self.dimension, {})
        for indices, coefficient in self.terms.items():
            for mu in range(self.dimension):
                differentiated = algebra.total_derivative(coefficient, mu)
                output += HorizontalForm(
                    self.dimension,
                    {(mu,) + indices: differentiated},
                )
        return output

    def brst(self, differential: MinimalBRSTDifferential) -> "HorizontalForm":
        if differential.algebra.dimension != self.dimension:
            raise ValueError("BRST algebra and form dimensions disagree")
        return HorizontalForm(
            self.dimension,
            {
                indices: differential(coefficient)
                for indices, coefficient in self.terms.items()
            },
        )

    def interior_xi(self, algebra: LocalJetAlgebra) -> "HorizontalForm":
        """Contract with the odd diffeomorphism ghost vector field."""

        if algebra.dimension != self.dimension:
            raise ValueError("algebra and form dimensions disagree")
        output: dict[tuple[int, ...], Expression] = {}
        for indices, coefficient in self.terms.items():
            for position, mu in enumerate(indices):
                remaining = indices[:position] + indices[position + 1 :]
                term = (
                    (-1 if position % 2 else 1)
                    * algebra.var("xi", (mu,))
                    * coefficient
                )
                output[remaining] = output.get(remaining, Expression()) + term
        return HorizontalForm(self.dimension, output)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "dimension": self.dimension,
            "terms": [
                {
                    "form_indices": list(indices),
                    "coefficient": coefficient.canonical_payload(),
                }
                for indices, coefficient in sorted(self.terms.items())
            ],
        }


def strict_density_algebra(dimension: int = 4) -> LocalJetAlgebra:
    return LocalJetAlgebra(dimension, strict_density_registry())
