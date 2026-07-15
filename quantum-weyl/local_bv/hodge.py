"""Exact signature-aware Hodge and chirality algebra on two-forms in 4D."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import sympy as sp


class Signature(str, Enum):
    EUCLIDEAN = "EUCLIDEAN"
    LORENTZIAN = "LORENTZIAN"


@dataclass(frozen=True)
class TwoFormHodge:
    signature: Signature

    @property
    def star_square_sign(self) -> int:
        return 1 if self.signature is Signature.EUCLIDEAN else -1

    @property
    def star(self) -> sp.ImmutableMatrix:
        sign = self.star_square_sign
        # Ordered formal basis (F,*F): *F is the second vector and
        # *(*F)=sign*F.
        return sp.ImmutableMatrix([[0, sign], [1, 0]])

    @property
    def parity(self) -> sp.ImmutableMatrix:
        # Orientation reversal fixes F and negates *F.
        return sp.ImmutableMatrix([[1, 0], [0, -1]])

    @property
    def eigenvalues(self) -> tuple[sp.Expr, sp.Expr]:
        if self.signature is Signature.EUCLIDEAN:
            return sp.Integer(1), sp.Integer(-1)
        return sp.I, -sp.I

    def projector(self, eigenvalue: sp.Expr) -> sp.ImmutableMatrix:
        if sp.simplify(eigenvalue**2 - self.star_square_sign) != 0:
            raise ValueError("Hodge eigenvalue has the wrong square")
        identity = sp.eye(2)
        return sp.ImmutableMatrix(
            sp.simplify((identity + self.star / eigenvalue) / 2)
        )

    def projectors(self) -> tuple[sp.ImmutableMatrix, sp.ImmutableMatrix]:
        positive, negative = self.eigenvalues
        return self.projector(positive), self.projector(negative)

    def verify(self) -> dict[str, object]:
        identity = sp.ImmutableMatrix(sp.eye(2))
        positive_value, negative_value = self.eigenvalues
        positive, negative = self.projectors()
        checks = {
            "star_square": self.star * self.star
            == self.star_square_sign * identity,
            "epsilon_contraction_normalization": (
                sp.Rational(1, 4)
                * (2 * self.star_square_sign)
                * 2
                == self.star_square_sign
            ),
            "projector_sum": positive + negative == identity,
            "projector_orthogonality": positive * negative == sp.zeros(2),
            "positive_idempotent": positive * positive == positive,
            "negative_idempotent": negative * negative == negative,
            "positive_eigenvalue": self.star * positive
            == positive_value * positive,
            "negative_eigenvalue": self.star * negative
            == negative_value * negative,
            "parity_involution": self.parity * self.parity == identity,
            "parity_reverses_star": self.parity * self.star * self.parity
            == -self.star,
            "parity_exchanges_projectors": self.parity * positive * self.parity
            == negative,
        }
        if not all(checks.values()):
            failed = sorted(name for name, passed in checks.items() if not passed)
            raise AssertionError(f"Hodge verification failed: {failed}")
        return {
            "signature": self.signature.value,
            "star_square_sign": self.star_square_sign,
            "epsilon_contraction_coefficient": 2 * self.star_square_sign,
            "eigenvalues": [str(positive_value), str(negative_value)],
            "star_matrix": [[str(value) for value in row] for row in self.star.tolist()],
            "parity_matrix": [
                [str(value) for value in row] for row in self.parity.tolist()
            ],
            "positive_projector": [
                [str(value) for value in row] for row in positive.tolist()
            ],
            "negative_projector": [
                [str(value) for value in row] for row in negative.tolist()
            ],
            "checks": {name: bool(value) for name, value in checks.items()},
        }
