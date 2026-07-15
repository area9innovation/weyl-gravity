"""Canonical exact AST for versioned local-expression payloads.

The AST records rational linear combinations of declared local monomials.
It canonicalizes derivative multi-indices and contractions, combines duplicate
terms, and rejects floating point.  Composition/evaluation is delegated to a
versioned evaluator; this module does not guess the semantics of an unknown
classical expression language.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import json
from typing import Any, Iterable


EXPRESSION_SCHEMA_VERSION = "quantum-weyl-canonical-local-expression-v1"


def exact_fraction(value: object) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError("local-expression coefficients must be exact")
    if isinstance(value, int):
        return Fraction(value)
    if (
        isinstance(value, dict)
        and set(value) == {"numerator", "denominator"}
        and isinstance(value["numerator"], int)
        and not isinstance(value["numerator"], bool)
        and isinstance(value["denominator"], int)
        and not isinstance(value["denominator"], bool)
        and value["denominator"] != 0
    ):
        return Fraction(value["numerator"], value["denominator"])
    raise ValueError("invalid exact local-expression coefficient")


def fraction_payload(value: Fraction) -> int | dict[str, int]:
    if value.denominator == 1:
        return value.numerator
    return {"numerator": value.numerator, "denominator": value.denominator}


@dataclass(frozen=True, order=True)
class LocalMonomial:
    """One canonical basis monomial in a declared local expression language."""

    operator_id: str
    input_jets: tuple[tuple[int, ...], ...]
    free_indices: tuple[str, ...]
    contractions: tuple[tuple[str, str], ...]

    @classmethod
    def from_payload(
        cls,
        payload: object,
        *,
        arity: int,
        spacetime_dimension: int,
    ) -> "LocalMonomial":
        fields = {"operator_id", "input_jets", "free_indices", "contractions"}
        if not isinstance(payload, dict) or set(payload) != fields:
            raise ValueError("local monomial has the wrong field set")
        operator_id = payload["operator_id"]
        if not isinstance(operator_id, str) or not operator_id:
            raise ValueError("local monomial operator_id is required")
        jets = payload["input_jets"]
        if not isinstance(jets, list) or len(jets) != arity:
            raise ValueError("local monomial input_jets do not match operator arity")
        canonical_jets = []
        for multiindex in jets:
            if (
                not isinstance(multiindex, list)
                or len(multiindex) != spacetime_dimension
                or any(
                    not isinstance(order, int)
                    or isinstance(order, bool)
                    or order < 0
                    for order in multiindex
                )
            ):
                raise ValueError("local monomial has an invalid jet multi-index")
            canonical_jets.append(tuple(multiindex))
        free_indices = payload["free_indices"]
        if not isinstance(free_indices, list) or any(
            not isinstance(index, str) or not index for index in free_indices
        ):
            raise ValueError("local monomial free indices are invalid")
        contractions = payload["contractions"]
        if not isinstance(contractions, list):
            raise ValueError("local monomial contractions must be a list")
        canonical_contractions = []
        for pair in contractions:
            if (
                not isinstance(pair, list)
                or len(pair) != 2
                or any(not isinstance(index, str) or not index for index in pair)
            ):
                raise ValueError("local monomial contraction is invalid")
            canonical_contractions.append(tuple(sorted(pair)))
        if len(canonical_contractions) != len(set(canonical_contractions)):
            raise ValueError("local monomial repeats a contraction")
        return cls(
            operator_id,
            tuple(canonical_jets),
            tuple(free_indices),
            tuple(sorted(canonical_contractions)),
        )

    def to_payload(self) -> dict[str, object]:
        return {
            "operator_id": self.operator_id,
            "input_jets": [list(multiindex) for multiindex in self.input_jets],
            "free_indices": list(self.free_indices),
            "contractions": [list(pair) for pair in self.contractions],
        }

    def canonical_key(self) -> str:
        return json.dumps(self.to_payload(), sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class LocalExpression:
    """A canonical rational linear combination of local monomials."""

    terms: tuple[tuple[LocalMonomial, Fraction], ...]

    def __post_init__(self) -> None:
        if any(coefficient == 0 for _, coefficient in self.terms):
            raise ValueError("canonical local expressions cannot retain zero terms")
        keys = [monomial.canonical_key() for monomial, _ in self.terms]
        if keys != sorted(keys) or len(keys) != len(set(keys)):
            raise ValueError("local-expression terms are not canonical and unique")

    @classmethod
    def from_payload(
        cls,
        payload: object,
        *,
        arity: int,
        spacetime_dimension: int,
    ) -> "LocalExpression":
        if not isinstance(payload, dict) or set(payload) != {"terms"}:
            raise ValueError("local expression must contain only a terms list")
        raw_terms = payload["terms"]
        if not isinstance(raw_terms, list):
            raise ValueError("local expression terms must be a list")
        coefficients: dict[LocalMonomial, Fraction] = {}
        for term in raw_terms:
            if not isinstance(term, dict) or set(term) != {"coefficient", "monomial"}:
                raise ValueError("local-expression term has the wrong field set")
            monomial = LocalMonomial.from_payload(
                term["monomial"],
                arity=arity,
                spacetime_dimension=spacetime_dimension,
            )
            coefficients[monomial] = coefficients.get(monomial, Fraction(0)) + exact_fraction(
                term["coefficient"]
            )
        terms = tuple(
            sorted(
                (
                    (monomial, coefficient)
                    for monomial, coefficient in coefficients.items()
                    if coefficient
                ),
                key=lambda item: item[0].canonical_key(),
            )
        )
        return cls(terms)

    @classmethod
    def zero(cls) -> "LocalExpression":
        return cls(())

    def to_payload(self) -> dict[str, object]:
        return {
            "terms": [
                {
                    "coefficient": fraction_payload(coefficient),
                    "monomial": monomial.to_payload(),
                }
                for monomial, coefficient in self.terms
            ]
        }

    def scaled(self, scalar: int | Fraction) -> "LocalExpression":
        coefficient = exact_fraction(scalar)
        if coefficient == 0:
            return LocalExpression.zero()
        return LocalExpression(
            tuple((monomial, coefficient * value) for monomial, value in self.terms)
        )

    def added(self, other: "LocalExpression") -> "LocalExpression":
        coefficients: dict[LocalMonomial, Fraction] = {}
        for expression in (self, other):
            for monomial, coefficient in expression.terms:
                coefficients[monomial] = coefficients.get(monomial, Fraction(0)) + coefficient
        return LocalExpression(
            tuple(
                sorted(
                    (
                        (monomial, coefficient)
                        for monomial, coefficient in coefficients.items()
                        if coefficient
                    ),
                    key=lambda item: item[0].canonical_key(),
                )
            )
        )


@dataclass(frozen=True)
class CanonicalExpressionComponent:
    component_id: str
    output: str
    inputs: tuple[str, ...]
    max_jet_orders: tuple[int, ...]
    expression: LocalExpression


def parse_operator_components(
    operator_payload: object,
    *,
    spacetime_dimension: int,
) -> tuple[CanonicalExpressionComponent, ...]:
    if not isinstance(operator_payload, dict):
        raise ValueError("operator payload must be an object")
    arity = operator_payload.get("arity")
    components = operator_payload.get("components")
    if not isinstance(arity, int) or not isinstance(components, list):
        raise ValueError("operator payload is missing arity or components")
    parsed = []
    for component in components:
        parsed.append(
            CanonicalExpressionComponent(
                component_id=component["component_id"],
                output=component["output"],
                inputs=tuple(component["inputs"]),
                max_jet_orders=tuple(component["max_jet_orders"]),
                expression=LocalExpression.from_payload(
                    component["expression"],
                    arity=arity,
                    spacetime_dimension=spacetime_dimension,
                ),
            )
        )
    return tuple(parsed)


def canonical_expression_hash(expressions: Iterable[LocalExpression]) -> str:
    import hashlib

    payload = [expression.to_payload() for expression in expressions]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
