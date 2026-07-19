"""Exact normal form for Berger apparatus differential coefficient jets."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from typing import Iterable

Scalar = tuple[Fraction, Fraction]  # a+b*sqrt(10)
Generator = tuple[str, str, tuple[int, ...], tuple[int, int, int, int]]
Monomial = tuple[Generator, ...]
Polynomial = dict[Monomial, Scalar]

ZERO_SCALAR: Scalar = (Fraction(0), Fraction(0))
ONE_SCALAR: Scalar = (Fraction(1), Fraction(0))
U_BERGER: Scalar = (Fraction(0), Fraction(3, 20))
V_BERGER: Scalar = (Fraction(0), Fraction(2, 3))


def scalar_add(left: Scalar, right: Scalar) -> Scalar:
    return left[0] + right[0], left[1] + right[1]


def scalar_mul(left: Scalar, right: Scalar) -> Scalar:
    return left[0] * right[0] + 10 * left[1] * right[1], left[0] * right[1] + left[1] * right[0]


def scalar_scale(value: Scalar, factor: int) -> Scalar:
    return factor * value[0], factor * value[1]


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
    output: dict[Monomial, Scalar] = defaultdict(lambda: ZERO_SCALAR)
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


def add(*values: Polynomial) -> Polynomial:
    return normalize(
        (coefficient, monomial)
        for value in values
        for monomial, coefficient in value.items()
    )


def scale(value: Polynomial, coefficient: Scalar) -> Polynomial:
    return normalize(
        (scalar_mul(coefficient, value_coefficient), monomial)
        for monomial, value_coefficient in value.items()
    )


def subtract(left: Polynomial, right: Polynomial) -> Polynomial:
    return add(left, scale(right, scalar_scale(ONE_SCALAR, -1)))


def _structure(first: int, second: int, variant: str) -> dict[int, Scalar]:
    table = {
        (1, 2): {3: U_BERGER},
        (2, 1): {3: scalar_scale(U_BERGER, -1)},
        (2, 3): {1: V_BERGER},
        (3, 2): {1: scalar_scale(V_BERGER, -1)},
        (3, 1): {2: V_BERGER},
        (1, 3): {2: scalar_scale(V_BERGER, -1)},
    }
    if variant == "drop_e1_e2":
        table[(1, 2)] = {}
        table[(2, 1)] = {}
    elif variant == "flip_e1_e2":
        table[(1, 2)] = {3: scalar_scale(U_BERGER, -1)}
        table[(2, 1)] = {3: U_BERGER}
    elif variant != "canonical":
        raise ValueError("unknown Berger structure variant")
    return table.get((first, second), {})


@lru_cache(maxsize=None)
def _pbw_word(word: tuple[int, ...], variant: str = "canonical") -> tuple[tuple[tuple[int, ...], Scalar], ...]:
    """Reduce a left-invariant frame word to e0^n0 e1^n1 e2^n2 e3^n3."""

    inversion = next(
        (index for index in range(len(word) - 1) if word[index] > word[index + 1]),
        None,
    )
    if inversion is None:
        return ((word, ONE_SCALAR),)
    left, right = word[inversion], word[inversion + 1]
    swapped = word[:inversion] + (right, left) + word[inversion + 2 :]
    output: dict[tuple[int, ...], Scalar] = dict(_pbw_word(swapped, variant))
    for target, structure_coefficient in _structure(left, right, variant).items():
        shorter = word[:inversion] + (target,) + word[inversion + 2 :]
        for reduced, nested_coefficient in _pbw_word(shorter, variant):
            output[reduced] = scalar_add(
                output.get(reduced, ZERO_SCALAR),
                scalar_mul(structure_coefficient, nested_coefficient),
            )
    return tuple(
        (reduced, coefficient)
        for reduced, coefficient in sorted(output.items())
        if coefficient != ZERO_SCALAR
    )


def _word_from_multiindex(multiindex: tuple[int, int, int, int]) -> tuple[int, ...]:
    return tuple(axis for axis, power in enumerate(multiindex) for _ in range(power))


def _multiindex_from_word(word: tuple[int, ...]) -> tuple[int, int, int, int]:
    return tuple(word.count(axis) for axis in range(4))


def derivative(value: Polynomial, axis: int, *, structure_variant: str = "canonical") -> Polynomial:
    if axis not in range(4):
        raise ValueError("Berger derivative axis must be 0,1,2,3")
    terms = []
    for monomial, coefficient in value.items():
        for position, factor in enumerate(monomial):
            kind, name, vertical, spacetime = factor
            if kind == "parameter":
                continue
            differentiated_word = (axis,) + _word_from_multiindex(spacetime)
            for reduced_word, pbw_coefficient in _pbw_word(
                differentiated_word, structure_variant
            ):
                factors = list(monomial)
                factors[position] = generator(
                    kind,
                    name,
                    vertical,
                    _multiindex_from_word(reduced_word),
                )
                terms.append((scalar_mul(coefficient, pbw_coefficient), factors))
    return normalize(terms)


def commutator(
    value: Polynomial,
    left_axis: int,
    right_axis: int,
    *,
    structure_variant: str = "canonical",
) -> Polynomial:
    return subtract(
        derivative(
            derivative(value, right_axis, structure_variant=structure_variant),
            left_axis,
            structure_variant=structure_variant,
        ),
        derivative(
            derivative(value, left_axis, structure_variant=structure_variant),
            right_axis,
            structure_variant=structure_variant,
        ),
    )


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
