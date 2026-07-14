"""Tiny exact noncommutative calculus for the minimal witness matrix.

The purpose of this module is deliberately narrow.  It checks the block
normalization of ``QW+WQ`` without pretending that symbolic operator names
establish analytic properties.  In particular, the middle backward arrow
must be ``2 sharp^{-1}`` when the action-normalized field block is written

``H = B + (1/2) K T``.

With that choice the degreewise witness operator is

``diag(TK, 2B+KT, 2B+T^sharp K^sharp, K^sharp T^sharp)``.

Thus the metric block is ``2H`` while the ghost block remains ``TK``.  The
factor two is invertible and has no effect on Green hyperbolicity, but it is
essential for an exact graded matrix identity.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class OperatorPolynomial:
    """A finite exact sum of noncommuting operator words."""

    terms: tuple[tuple[tuple[str, ...], Fraction], ...] = ()

    @staticmethod
    def zero() -> "OperatorPolynomial":
        return OperatorPolynomial()

    @staticmethod
    def identity(coefficient: Fraction | int = 1) -> "OperatorPolynomial":
        value = Fraction(coefficient)
        if value == 0:
            return OperatorPolynomial.zero()
        return OperatorPolynomial((((), value),))

    @staticmethod
    def atom(name: str, coefficient: Fraction | int = 1) -> "OperatorPolynomial":
        value = Fraction(coefficient)
        if value == 0:
            return OperatorPolynomial.zero()
        return OperatorPolynomial((((name,), value),))

    @staticmethod
    def _from_dict(values: dict[tuple[str, ...], Fraction]) -> "OperatorPolynomial":
        return OperatorPolynomial(
            tuple(
                sorted(
                    ((word, coefficient) for word, coefficient in values.items() if coefficient),
                    key=lambda item: item[0],
                )
            )
        )

    def as_dict(self) -> dict[tuple[str, ...], Fraction]:
        return dict(self.terms)

    def __add__(self, other: "OperatorPolynomial") -> "OperatorPolynomial":
        values = self.as_dict()
        for word, coefficient in other.terms:
            values[word] = values.get(word, Fraction(0)) + coefficient
        return self._from_dict(values)

    def __mul__(self, other: "OperatorPolynomial") -> "OperatorPolynomial":
        """Composition: a left word acts after a right word."""

        values: dict[tuple[str, ...], Fraction] = {}
        for left, left_coefficient in self.terms:
            for right, right_coefficient in other.terms:
                word = left + right
                values[word] = values.get(word, Fraction(0)) + left_coefficient * right_coefficient
        return self._from_dict(values)

    def scale(self, coefficient: Fraction | int) -> "OperatorPolynomial":
        value = Fraction(coefficient)
        return self._from_dict(
            {word: value * term_coefficient for word, term_coefficient in self.terms}
        )

    def adjoint(self) -> "OperatorPolynomial":
        adjoints = {
            "K": "Ksharp",
            "Ksharp": "K",
            "T": "Tsharp",
            "Tsharp": "T",
            "B": "B",
        }
        return self._from_dict(
            {
                tuple(adjoints[name] for name in reversed(word)): coefficient
                for word, coefficient in self.terms
            }
        )

    def display(self) -> str:
        if not self.terms:
            return "0"
        pieces: list[str] = []
        for word, coefficient in self.terms:
            operator = " ".join(word) if word else "I"
            if coefficient == 1:
                pieces.append(operator)
            else:
                pieces.append(f"{coefficient} {operator}")
        return " + ".join(pieces)


def zero_matrix(size: int) -> list[list[OperatorPolynomial]]:
    return [
        [OperatorPolynomial.zero() for _ in range(size)] for _ in range(size)
    ]


def matrix_add(left, right):
    return [
        [left[row][column] + right[row][column] for column in range(len(left))]
        for row in range(len(left))
    ]


def matrix_multiply(left, right):
    size = len(left)
    output = zero_matrix(size)
    for row in range(size):
        for column in range(size):
            value = OperatorPolynomial.zero()
            for middle in range(size):
                value = value + left[row][middle] * right[middle][column]
            output[row][column] = value
    return output
