"""Exact normal form for Berger apparatus differential coefficient jets."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from typing import Iterable

Scalar = tuple[Fraction, Fraction]  # a+b*sqrt(10)
Generator = tuple[str, str, tuple[int, ...], tuple[int, int, int, int]]
Monomial = tuple[Generator, ...]
Polynomial = dict[Monomial, Scalar]


def scalar_add(left: Scalar, right: Scalar) -> Scalar:
    return left[0] + right[0], left[1] + right[1]


def scalar_mul(left: Scalar, right: Scalar) -> Scalar:
    return left[0] * right[0] + 10 * left[1] * right[1], left[0] * right[1] + left[1] * right[0]


def generator(kind: str, name: str, vertical: Iterable[int] = (), spacetime: Iterable[int] = (0, 0, 0, 0)) -> Generator:
    vertical_tuple = tuple(vertical)
    spacetime_tuple = tuple(spacetime)
    if kind not in {"parameter", "profile", "background"}:
        raise ValueError("unknown coefficient generator kind")
    if len(spacetime_tuple) != 4 or any(value < 0 for value in vertical_tuple + spacetime_tuple):
        raise ValueError("jet multiindices must be nonnegative and spacetime rank four")
    if kind == "parameter" and (vertical_tuple or any(spacetime_tuple)):
        raise ValueError("formal parameters have no jet indices")
    return kind, name, vertical_tuple, spacetime_tuple


def normalize(terms: Iterable[tuple[Scalar, Iterable[Generator]]]) -> Polynomial:
    output: dict[Monomial, Scalar] = defaultdict(lambda: (Fraction(0), Fraction(0)))
    for coefficient, factors in terms:
        monomial = tuple(sorted(tuple(factors)))
        output[monomial] = scalar_add(output[monomial], coefficient)
    return {monomial: coefficient for monomial, coefficient in sorted(output.items()) if coefficient != (0, 0)}


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    return normalize(
        (scalar_mul(left_coefficient, right_coefficient), left_monomial + right_monomial)
        for left_monomial, left_coefficient in left.items()
        for right_monomial, right_coefficient in right.items()
    )


def derivative(value: Polynomial, axis: int) -> Polynomial:
    if axis not in range(4):
        raise ValueError("Berger derivative axis must be 0,1,2,3")
    terms = []
    for monomial, coefficient in value.items():
        for position, factor in enumerate(monomial):
            kind, name, vertical, spacetime = factor
            if kind == "parameter":
                continue
            shifted = list(spacetime)
            shifted[axis] += 1
            factors = list(monomial)
            factors[position] = generator(kind, name, vertical, shifted)
            terms.append((coefficient, factors))
    return normalize(terms)


def serialize(value: Polynomial) -> list[dict]:
    def rational(number: Fraction) -> dict[str, int]:
        return {"numerator": number.numerator, "denominator": number.denominator}

    return [
        {
            "coefficient": {"rational": rational(coefficient[0]), "sqrt10": rational(coefficient[1])},
            "factors": [
                {"kind": kind, "name": name, "vertical_multiindex": list(vertical), "spacetime_multiindex": list(spacetime)}
                for kind, name, vertical, spacetime in monomial
            ],
        }
        for monomial, coefficient in value.items()
    ]
