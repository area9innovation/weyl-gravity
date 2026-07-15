"""An exact supercommutative coordinate-jet algebra.

This module supplies the algebraic substrate needed to test the minimal
BRST rows.  It does *not* yet quotient by integration by parts, curvature
identities, or equations of motion.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from typing import Iterable, Mapping

from .metadata import FieldSpec, minimal_registry


def canonical_json(value: object) -> str:
    """Serialize a JSON value byte-stably for hashing and receipts."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("ascii")).hexdigest()


@dataclass(frozen=True)
class JetVariable:
    field: str
    components: tuple[int, ...]
    derivatives: tuple[int, ...]
    parity: int
    ghost_number: int
    antifield_number: int
    form_degree: int
    mass_dimension: Fraction
    spacetime_parity: str
    weyl_weight: Fraction

    def sort_key(self) -> tuple[object, ...]:
        return self.field, self.components, self.derivatives

    def canonical_payload(self) -> dict[str, object]:
        return {
            "field": self.field,
            "components": list(self.components),
            "derivatives": list(self.derivatives),
            "parity": self.parity,
            "ghost_number": self.ghost_number,
            "antifield_number": self.antifield_number,
            "form_degree": self.form_degree,
            "mass_dimension": {
                "numerator": self.mass_dimension.numerator,
                "denominator": self.mass_dimension.denominator,
            },
            "spacetime_parity": self.spacetime_parity,
            "weyl_weight": {
                "numerator": self.weyl_weight.numerator,
                "denominator": self.weyl_weight.denominator,
            },
        }


Monomial = tuple[JetVariable, ...]


def _canonical_monomial(factors: Iterable[JetVariable]) -> tuple[int, Monomial | None]:
    """Sort a monomial and return its Koszul sign.

    Only inversions between two odd factors contribute a minus sign.  A
    repeated identical odd jet is zero over characteristic zero.
    """

    original = tuple(factors)
    odd = [factor for factor in original if factor.parity]
    if len({factor.sort_key() for factor in odd}) != len(odd):
        return 0, None
    inversions = 0
    for index, left in enumerate(original):
        if not left.parity:
            continue
        for right in original[index + 1 :]:
            if right.parity and left.sort_key() > right.sort_key():
                inversions += 1
    return (-1 if inversions % 2 else 1), tuple(sorted(original, key=JetVariable.sort_key))


class Expression:
    """Sparse exact linear combination of canonical supermonomials."""

    def __init__(self, terms: Mapping[Monomial, Fraction | int] | None = None):
        reduced: dict[Monomial, Fraction] = {}
        for monomial, coefficient in (terms or {}).items():
            sign, canonical = _canonical_monomial(monomial)
            if not sign or canonical is None:
                continue
            value = reduced.get(canonical, Fraction(0)) + sign * Fraction(coefficient)
            if value:
                reduced[canonical] = value
            else:
                reduced.pop(canonical, None)
        self._terms = reduced

    @classmethod
    def scalar(cls, value: Fraction | int) -> "Expression":
        return cls({(): Fraction(value)}) if value else cls()

    @classmethod
    def variable(cls, value: JetVariable) -> "Expression":
        return cls({(value,): Fraction(1)})

    @property
    def terms(self) -> Mapping[Monomial, Fraction]:
        return dict(self._terms)

    def __bool__(self) -> bool:
        return bool(self._terms)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Expression) and self._terms == other._terms

    def __neg__(self) -> "Expression":
        return Expression({monomial: -coefficient for monomial, coefficient in self._terms.items()})

    def __add__(self, other: "Expression") -> "Expression":
        terms = dict(self._terms)
        for monomial, coefficient in other._terms.items():
            terms[monomial] = terms.get(monomial, Fraction(0)) + coefficient
        return Expression(terms)

    def __sub__(self, other: "Expression") -> "Expression":
        return self + (-other)

    def __mul__(self, other: "Expression" | Fraction | int) -> "Expression":
        if not isinstance(other, Expression):
            other = Expression.scalar(other)
        terms: dict[Monomial, Fraction] = {}
        for left, left_coefficient in self._terms.items():
            for right, right_coefficient in other._terms.items():
                sign, monomial = _canonical_monomial(left + right)
                if sign and monomial is not None:
                    terms[monomial] = terms.get(monomial, Fraction(0)) + (
                        sign * left_coefficient * right_coefficient
                    )
        return Expression(terms)

    def __rmul__(self, other: Fraction | int) -> "Expression":
        return self * other

    def canonical_payload(self) -> dict[str, object]:
        ordered = sorted(self._terms.items(), key=lambda item: tuple(v.sort_key() for v in item[0]))
        return {
            "terms": [
                {
                    "coefficient": {
                        "numerator": coefficient.numerator,
                        "denominator": coefficient.denominator,
                    },
                    "monomial": [variable.canonical_payload() for variable in monomial],
                }
                for monomial, coefficient in ordered
            ]
        }

    def canonical_hash(self) -> str:
        return canonical_sha256(self.canonical_payload())

    def homogeneous_parity(self) -> int:
        parities = {sum(variable.parity for variable in monomial) % 2 for monomial in self._terms}
        if len(parities) != 1:
            raise ValueError("expression is not parity homogeneous")
        return next(iter(parities))


class LocalJetAlgebra:
    """Factory and total derivatives for a fixed spacetime dimension."""

    def __init__(self, dimension: int = 4, registry: Mapping[str, FieldSpec] | None = None):
        if dimension <= 0:
            raise ValueError("dimension must be positive")
        self.dimension = dimension
        self.registry = dict(registry or minimal_registry())

    def jet(
        self,
        field: str,
        components: Iterable[int] = (),
        derivatives: Iterable[int] | None = None,
    ) -> JetVariable:
        spec = self.registry[field]
        canonical_components = spec.canonical_components(components, self.dimension)
        multi_index = tuple(derivatives if derivatives is not None else (0,) * self.dimension)
        if len(multi_index) != self.dimension or any(value < 0 for value in multi_index):
            raise ValueError("derivatives must be a nonnegative multi-index of spacetime dimension")
        derivative_order = sum(multi_index)
        return JetVariable(
            field=field,
            components=canonical_components,
            derivatives=multi_index,
            parity=spec.grassmann_parity,
            ghost_number=spec.ghost_number,
            antifield_number=spec.antifield_number,
            form_degree=spec.form_degree,
            mass_dimension=spec.mass_dimension + derivative_order,
            spacetime_parity=spec.spacetime_parity.value,
            weyl_weight=spec.weyl_weight,
        )

    def var(self, field: str, components: Iterable[int] = (), derivatives: Iterable[int] | None = None) -> Expression:
        return Expression.variable(self.jet(field, components, derivatives))

    def differentiate_variable(self, variable: JetVariable, direction: int) -> JetVariable:
        if direction < 0 or direction >= self.dimension:
            raise ValueError("derivative direction outside spacetime dimension")
        derivatives = list(variable.derivatives)
        derivatives[direction] += 1
        return self.jet(variable.field, variable.components, derivatives)

    def total_derivative(self, expression: Expression, direction: int) -> Expression:
        result = Expression()
        for monomial, coefficient in expression.terms.items():
            for index, variable in enumerate(monomial):
                differentiated = self.differentiate_variable(variable, direction)
                factors = monomial[:index] + (differentiated,) + monomial[index + 1 :]
                result = result + Expression({factors: coefficient})
        return result
