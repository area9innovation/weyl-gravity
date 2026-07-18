"""Unit tests for the coefficient-jet PBW algebra."""

from __future__ import annotations

import unittest

import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    FibrePBW,
)
from d_quotient_classical.causal_transfer.coefficient_jet_pbw import (
    CoefficientJetPBW,
    JetLinearizedOperator,
    MissingCoefficientJet,
    jet_add,
    jet_scale,
    parallel_zero_variation,
    point_value_only,
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
    base = FibrePBW(zero, _FlatLineBackground(), "flat-line")
    linearized = FirstVariationPBW(
        base,
        zero,
        zero,
        lambda _word: sp.Integer(0),
        "flat-line-linearized",
    )
    return CoefficientJetPBW(linearized)


def _scalar_table(coefficients: dict[tuple[int, ...], sp.Expr]):
    return {word: sp.Matrix([[value]]) for word, value in coefficients.items()}


def _exp_jet(scale: sp.Expr):
    def provider(word: tuple[int, ...]):
        if any(axis != 0 for axis in word):
            return {}
        return _scalar_table({(): scale})

    return provider


class CoefficientJetPBWTests(unittest.TestCase):
    def test_point_value_only_fails_closed(self) -> None:
        operator = point_value_only(
            _scalar_table({(): 1}), _scalar_table({(): 2}), "point-only"
        )
        self.assertEqual(operator.delta(())[()][0, 0], 2)
        with self.assertRaises(MissingCoefficientJet):
            operator.delta((0,))

    def test_flat_nonparallel_associator_vanishes(self) -> None:
        algebra = _flat_algebra()
        a = parallel_zero_variation(
            _scalar_table({(0, 0): 1, (): 2}), "A"
        )
        b = JetLinearizedOperator(
            _scalar_table({(0,): 3, (): 5}), _exp_jet(7), "B"
        )
        c = JetLinearizedOperator(
            _scalar_table({(0,): 11, (): 13}), _exp_jet(17), "C"
        )

        left = algebra.compose(algebra.compose(a, b, "AB"), c, "(AB)C")
        right = algebra.compose(a, algebra.compose(b, c, "BC"), "A(BC)")
        for word in ((), (0,), (0, 0), (0, 0, 0)):
            defect = jet_add(left, jet_scale(right, -1), name="associator")
            self.assertEqual(defect.base, {})
            self.assertEqual(defect.delta(word), {})

    def test_leibniz_binomial_coefficients(self) -> None:
        algebra = _flat_algebra()
        second_derivative = parallel_zero_variation(
            _scalar_table({(0, 0): 1}), "D2"
        )

        def polynomial_jet(word: tuple[int, ...]):
            values = {0: 2, 1: 3, 2: 5, 3: 7}
            if any(axis != 0 for axis in word):
                return {}
            return _scalar_table({(): values[len(word)]})

        multiplier = JetLinearizedOperator(
            _scalar_table({(): 1}), polynomial_jet, "f"
        )
        product = algebra.compose(second_derivative, multiplier)
        value = product.delta(())
        self.assertEqual(value[()][0, 0], 5)
        self.assertEqual(value[(0,)][0, 0], 6)
        self.assertEqual(value[(0, 0)][0, 0], 2)


if __name__ == "__main__":
    unittest.main()
