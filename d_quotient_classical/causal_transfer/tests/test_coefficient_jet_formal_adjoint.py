"""Unit tests for coefficient-jet formal adjunction."""

from __future__ import annotations

import unittest

import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    FibrePBW,
)
from d_quotient_classical.causal_transfer.coefficient_jet_formal_adjoint import (
    formal_adjoint,
)
from d_quotient_classical.causal_transfer.coefficient_jet_pbw import (
    CoefficientJetPBW,
    JetLinearizedOperator,
)
from d_quotient_classical.causal_transfer.first_variation_pbw import (
    FirstVariationPBW,
)


class _FlatLineBackground:
    @staticmethod
    def covector_commutator(_left: int, _right: int) -> sp.Matrix:
        return sp.zeros(1)


def _flat_algebra() -> CoefficientJetPBW:
    zero = tuple(tuple(sp.zeros(1) for _ in range(4)) for _ in range(4))
    base = FibrePBW(zero, _FlatLineBackground(), "flat-adjoint")
    return CoefficientJetPBW(
        FirstVariationPBW(
            base,
            zero,
            zero,
            lambda _word: sp.Integer(0),
            "flat-adjoint-linearized",
        )
    )


def _table(values: dict[tuple[int, ...], sp.Expr]):
    return {word: sp.Matrix([[value]]) for word, value in values.items()}


class CoefficientJetFormalAdjointTests(unittest.TestCase):
    def test_derivatives_hit_varied_coefficients(self) -> None:
        algebra = _flat_algebra()
        derivatives = {
            (): {0: 2, 1: 3, 2: 5},
            (0,): {0: 7, 1: 11, 2: 13},
            (1,): {0: 17, 1: 19, 2: 23},
            (1, 0): {0: 29, 1: 31, 2: 37},
            (2,): {0: 41, 1: 43, 2: 47},
            (2, 0): {0: 53, 1: 59, 2: 61},
            (2, 1): {0: 67, 1: 71, 2: 73},
            (2, 1, 0): {0: 79, 1: 83, 2: 89},
        }

        def provider(jet: tuple[int, ...]):
            if jet not in derivatives:
                return {}
            values = derivatives[jet]
            return _table({
                (0, 1): values[2],
                (0,): values[1],
                (): values[0],
            })

        operator = JetLinearizedOperator(
            _table({(0, 1): 1, (0,): 1, (): 1}), provider, "A"
        )
        adjoint = formal_adjoint(
            operator, sp.eye(1), sp.eye(1), algebra
        )
        point = adjoint.delta(())
        self.assertEqual(point[(0, 1)][0, 0], 5)
        self.assertEqual(point[(0,)][0, 0], 23 - 3)
        self.assertEqual(point[(1,)][0, 0], 13)
        self.assertEqual(point[()][0, 0], 37 - 11 + 2)

        first = adjoint.delta((2,))
        self.assertEqual(first[(0, 1)][0, 0], 47)
        self.assertEqual(first[(0,)][0, 0], 73 - 43)
        self.assertEqual(first[(1,)][0, 0], 61)
        self.assertEqual(first[()][0, 0], 89 - 59 + 41)

    def test_formal_adjoint_is_involutive_on_scalar_fixture(self) -> None:
        algebra = _flat_algebra()

        def provider(jet: tuple[int, ...]):
            if any(axis != 0 for axis in jet):
                return {}
            value = sp.Integer(2) ** len(jet)
            return _table({(0, 0): value, (0,): 2 * value, (): 3 * value})

        operator = JetLinearizedOperator(
            _table({(0, 0): 1, (0,): 2, (): 3}), provider, "A"
        )
        twice = formal_adjoint(
            formal_adjoint(operator, sp.eye(1), sp.eye(1), algebra),
            sp.eye(1),
            sp.eye(1),
            algebra,
        )
        self.assertEqual(twice.base, operator.base)
        self.assertEqual(twice.delta(()), operator.delta(()))
        self.assertEqual(twice.delta((0,)), operator.delta((0,)))


if __name__ == "__main__":
    unittest.main()
