"""Exact unit tests for the local polarized relative current."""

from __future__ import annotations

import unittest

import sympy as sp

from d_quotient_classical.relative.einstein_weyl_relative_noether_current import (
    gauge_covariant_lie_derivative_potential,
    lie_derivative_metric,
    polarized_relative_noether_current_component,
)


class RelativeNoetherCurrentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.coordinates = sp.symbols("t x y z")
        self.t, self.x, self.y, self.z = self.coordinates
        self.metric = sp.diag(-1, 1, 1, 1)
        self.field = sp.zeros(4)
        self.generator = sp.Matrix([1, 0, 0, 0])
        self.zero_potential = sp.zeros(4, 1)

    def test_gauge_covariant_lift_is_cartan_formula(self) -> None:
        potential = sp.Matrix([
            self.t * self.x,
            self.t**2 + self.y,
            self.x * self.z,
            self.t * self.y,
        ])
        covariant = gauge_covariant_lie_derivative_potential(
            potential, self.generator, self.coordinates
        )
        coordinate_lie = potential.applyfunc(lambda entry: sp.diff(entry, self.t))
        contraction = potential[0]
        exact = sp.Matrix([sp.diff(contraction, coordinate) for coordinate in self.coordinates])
        self.assertEqual((covariant - coordinate_lie + exact).applyfunc(sp.simplify), sp.zeros(4, 1))

    def test_metric_lift_is_tensor_lie_derivative(self) -> None:
        variation = sp.zeros(4)
        variation[1, 2] = variation[2, 1] = self.t * self.x
        result = lie_derivative_metric(variation, self.generator, self.coordinates)
        self.assertEqual(result[1, 2], self.x)
        self.assertEqual(result, result.T)

    def test_polarization_is_symmetric_and_nonzero(self) -> None:
        first_metric = sp.zeros(4)
        second_metric = sp.zeros(4)
        first_metric[1, 2] = first_metric[2, 1] = self.t * self.x
        second_metric[1, 2] = second_metric[2, 1] = self.t**2 * self.x
        first = (first_metric, self.zero_potential)
        second = (second_metric, self.zero_potential)
        forward = polarized_relative_noether_current_component(
            self.metric,
            self.field,
            first,
            second,
            self.generator,
            self.coordinates,
            1,
        )
        reverse = polarized_relative_noether_current_component(
            self.metric,
            self.field,
            second,
            first,
            self.generator,
            self.coordinates,
            1,
        )
        self.assertEqual(sp.factor(forward), 3 * self.x / 8)
        self.assertEqual(sp.simplify(forward - reverse), 0)

    def test_component_bounds_fail_closed(self) -> None:
        zero = (sp.zeros(4), self.zero_potential)
        with self.assertRaises(ValueError):
            polarized_relative_noether_current_component(
                self.metric,
                self.field,
                zero,
                zero,
                self.generator,
                self.coordinates,
                4,
            )


if __name__ == "__main__":
    unittest.main()
