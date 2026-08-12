#!/usr/bin/env python3
"""Exact sparse multivariate rational fields for bounded BT calculations."""
from __future__ import annotations

from fractions import Fraction

from flint import fmpq_mpoly_ctx, nmod_mpoly_ctx


class SparseRationalField:
    """A small gcd-cancelled fraction field over a FLINT polynomial ring."""

    def __init__(self, names, modulus=None, ordering="degrevlex"):
        self.modulus = modulus
        if modulus is None:
            self.context = fmpq_mpoly_ctx.get(list(names), ordering)
        else:
            self.context = nmod_mpoly_ctx.get(list(names), modulus, ordering)
        self.polynomial_type = type(self.context.gen(0))
        self.zero_polynomial = self.context.constant(0)
        self.one_polynomial = self.context.constant(1)
        self.zero = SparseRational(self, 0)
        self.one = SparseRational(self, 1)
        self.gens = tuple(SparseRational(self, value) for value in self.context.gens())

    def constant_polynomial(self, value):
        fraction = Fraction(value)
        if self.modulus is None:
            numerator = self.context.constant(fraction.numerator)
            denominator = self.context.constant(fraction.denominator)
        else:
            numerator = self.context.constant(fraction.numerator % self.modulus)
            denominator = self.context.constant(fraction.denominator % self.modulus)
        return numerator, denominator

    def coerce(self, value):
        if isinstance(value, SparseRational):
            if value.field is not self:
                raise TypeError("incompatible sparse rational fields")
            return value
        return SparseRational(self, value)


class SparseRational:
    """Canonical scalar in a :class:`SparseRationalField`."""

    __slots__ = ("field", "numerator", "denominator")

    def __init__(self, field, value=0, denominator=None):
        self.field = field
        if isinstance(value, SparseRational):
            if value.field is not field:
                raise TypeError("incompatible sparse rational fields")
            self.numerator = value.numerator
            self.denominator = value.denominator
            return
        if isinstance(value, field.polynomial_type):
            numerator = value
        else:
            numerator, default_denominator = field.constant_polynomial(value)
            if denominator is None:
                denominator = default_denominator
        if denominator is None:
            denominator = field.one_polynomial
        if not numerator:
            self.numerator = field.zero_polynomial
            self.denominator = field.one_polynomial
            return
        common = numerator.gcd(denominator)
        self.numerator = numerator / common
        self.denominator = denominator / common

    @classmethod
    def _from_reduced(cls, field, numerator, denominator):
        value = object.__new__(cls)
        value.field = field
        value.numerator = numerator
        value.denominator = denominator
        return value

    def _coerce(self, other):
        return self.field.coerce(other)

    def __bool__(self):
        return bool(self.numerator)

    def __neg__(self):
        return self._from_reduced(self.field, -self.numerator, self.denominator)

    def __add__(self, other):
        if hasattr(other, "coefficients"):
            return NotImplemented
        other = self._coerce(other)
        common = self.denominator.gcd(other.denominator)
        left_denominator = self.denominator / common
        right_denominator = other.denominator / common
        numerator = (
            self.numerator * right_denominator
            + other.numerator * left_denominator
        )
        cancellation = numerator.gcd(common)
        return self._from_reduced(
            self.field,
            numerator / cancellation,
            left_denominator * (other.denominator / cancellation),
        )

    __radd__ = __add__

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __rsub__(self, other):
        return self._coerce(other) - self

    def __mul__(self, other):
        if hasattr(other, "coefficients"):
            return NotImplemented
        other = self._coerce(other)
        left_cancellation = self.numerator.gcd(other.denominator)
        right_cancellation = other.numerator.gcd(self.denominator)
        return self._from_reduced(
            self.field,
            (self.numerator / left_cancellation)
            * (other.numerator / right_cancellation),
            (self.denominator / right_cancellation)
            * (other.denominator / left_cancellation),
        )

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self._coerce(other)
        if not other:
            raise ZeroDivisionError("division by zero")
        numerator_cancellation = self.numerator.gcd(other.numerator)
        denominator_cancellation = other.denominator.gcd(self.denominator)
        return self._from_reduced(
            self.field,
            (self.numerator / numerator_cancellation)
            * (other.denominator / denominator_cancellation),
            (self.denominator / denominator_cancellation)
            * (other.numerator / numerator_cancellation),
        )

    def __rtruediv__(self, other):
        return self._coerce(other) / self

    def __pow__(self, exponent):
        if exponent < 0:
            return (self.field.one / self) ** (-exponent)
        return self._from_reduced(
            self.field,
            self.numerator**exponent,
            self.denominator**exponent,
        )

    def __eq__(self, other):
        if hasattr(other, "coefficients"):
            return False
        try:
            other = self._coerce(other)
        except (TypeError, ValueError):
            return False
        return (
            self.numerator * other.denominator
            == other.numerator * self.denominator
        )

    def __repr__(self):
        return f"({self.numerator})/({self.denominator})"
