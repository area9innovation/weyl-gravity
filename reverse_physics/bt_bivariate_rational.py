#!/usr/bin/env python3
"""Small exact ``Q(t,u)`` field backed by python-flint.

SymPy's generic multivariate fraction-field normalization is substantially
more expensive than this calculation requires.  This module implements the
standard gcd-cancelled fraction algorithms directly over FLINT's sparse
``fmpq_mpoly`` type.  It is intentionally tiny: only the scalar operations
needed by the BT external-mass jet are exposed.
"""
from __future__ import annotations

from fractions import Fraction

from flint import fmpq_mpoly_ctx


POLYNOMIAL_CONTEXT = fmpq_mpoly_ctx.get(["t", "u"], "lex")
POLYNOMIAL_TYPE = type(POLYNOMIAL_CONTEXT.gen(0))
T_POLYNOMIAL, U_POLYNOMIAL = POLYNOMIAL_CONTEXT.gens()
ZERO_POLYNOMIAL = POLYNOMIAL_CONTEXT.constant(0)
ONE_POLYNOMIAL = POLYNOMIAL_CONTEXT.constant(1)


class BivariateRational:
    """Canonical rational function in ``Q(t,u)``.

    Addition uses the gcd of the denominators and multiplication cancels
    cross factors before multiplying.  These are exact fraction algorithms;
    no floating point or probabilistic identity testing occurs.
    """

    __slots__ = ("numerator", "denominator")

    def __init__(self, value=0, denominator=None):
        if isinstance(value, BivariateRational):
            self.numerator = value.numerator
            self.denominator = value.denominator
            return
        if isinstance(value, POLYNOMIAL_TYPE):
            numerator = value
        else:
            fraction = Fraction(value)
            numerator = POLYNOMIAL_CONTEXT.constant(fraction.numerator)
            if denominator is None:
                denominator = POLYNOMIAL_CONTEXT.constant(fraction.denominator)
        if denominator is None:
            denominator = ONE_POLYNOMIAL
        if not numerator:
            self.numerator = ZERO_POLYNOMIAL
            self.denominator = ONE_POLYNOMIAL
            return
        common = numerator.gcd(denominator)
        self.numerator = numerator / common
        self.denominator = denominator / common

    @classmethod
    def _from_reduced(cls, numerator, denominator):
        value = object.__new__(cls)
        value.numerator = numerator
        value.denominator = denominator
        return value

    def __bool__(self):
        return bool(self.numerator)

    def __neg__(self):
        return self._from_reduced(-self.numerator, self.denominator)

    def __add__(self, other):
        if hasattr(other, "coefficients"):
            return NotImplemented
        other = BivariateRational(other)
        common = self.denominator.gcd(other.denominator)
        left_denominator = self.denominator / common
        right_denominator = other.denominator / common
        numerator = (
            self.numerator * right_denominator
            + other.numerator * left_denominator
        )
        cancellation = numerator.gcd(common)
        return self._from_reduced(
            numerator / cancellation,
            left_denominator * (other.denominator / cancellation),
        )

    __radd__ = __add__

    def __sub__(self, other):
        return self + (-BivariateRational(other))

    def __rsub__(self, other):
        return BivariateRational(other) - self

    def __mul__(self, other):
        if hasattr(other, "coefficients"):
            return NotImplemented
        other = BivariateRational(other)
        left_cancellation = self.numerator.gcd(other.denominator)
        right_cancellation = other.numerator.gcd(self.denominator)
        return self._from_reduced(
            (self.numerator / left_cancellation)
            * (other.numerator / right_cancellation),
            (self.denominator / right_cancellation)
            * (other.denominator / left_cancellation),
        )

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = BivariateRational(other)
        if not other:
            raise ZeroDivisionError("division by the zero rational function")
        numerator_cancellation = self.numerator.gcd(other.numerator)
        denominator_cancellation = other.denominator.gcd(self.denominator)
        return self._from_reduced(
            (self.numerator / numerator_cancellation)
            * (other.denominator / denominator_cancellation),
            (self.denominator / denominator_cancellation)
            * (other.numerator / numerator_cancellation),
        )

    def __rtruediv__(self, other):
        return BivariateRational(other) / self

    def __pow__(self, exponent):
        if exponent < 0:
            return (BivariateRational(1) / self) ** (-exponent)
        return self._from_reduced(
            self.numerator**exponent,
            self.denominator**exponent,
        )

    def __eq__(self, other):
        if hasattr(other, "coefficients"):
            return False
        other = BivariateRational(other)
        return (
            self.numerator * other.denominator
            == other.numerator * self.denominator
        )

    def __repr__(self):
        return f"({self.numerator})/({self.denominator})"


def coerce(value):
    return value if isinstance(value, BivariateRational) else BivariateRational(value)


T = BivariateRational(T_POLYNOMIAL)
U = BivariateRational(U_POLYNOMIAL)
ZERO = BivariateRational(0)
ONE = BivariateRational(1)
