"""Fast component-level tests for the action-derived Lee--Wald evaluator."""

from __future__ import annotations

import unittest

import sympy as sp

from bridge.einstein_sector.weyl_maxwell_lee_wald_current import (
    einstein_maxwell_current_component,
    einstein_maxwell_current_time,
    weyl_maxwell_current_component,
    weyl_maxwell_current_time,
)


class LeeWaldCurrentComponentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.coordinates = sp.symbols("t x y z", real=True)
        self.metric = sp.diag(-1, 1, 1, 1)
        self.field = sp.zeros(4)
        h1 = sp.diag(1, 2, 3, 4)
        h2 = sp.diag(4, 3, 2, 1)
        a1 = sp.zeros(4, 1)
        a2 = sp.zeros(4, 1)
        self.first = (h1, a1)
        self.second = (h2, a2)

    def test_all_components_exist_and_constant_fixture_vanishes(self) -> None:
        for component in range(4):
            self.assertEqual(
                weyl_maxwell_current_component(
                    self.metric, self.field, self.first, self.second, self.coordinates, component
                ),
                0,
            )
            self.assertEqual(
                einstein_maxwell_current_component(
                    self.metric, self.field, self.first, self.second, self.coordinates, component
                ),
                0,
            )

    def test_time_wrappers_are_exact_aliases(self) -> None:
        self.assertEqual(
            weyl_maxwell_current_time(self.metric, self.field, self.first, self.second, self.coordinates),
            weyl_maxwell_current_component(self.metric, self.field, self.first, self.second, self.coordinates, 0),
        )
        self.assertEqual(
            einstein_maxwell_current_time(self.metric, self.field, self.first, self.second, self.coordinates),
            einstein_maxwell_current_component(self.metric, self.field, self.first, self.second, self.coordinates, 0),
        )

    def test_component_bounds_are_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            weyl_maxwell_current_component(
                self.metric, self.field, self.first, self.second, self.coordinates, 4
            )
        with self.assertRaises(ValueError):
            einstein_maxwell_current_component(
                self.metric, self.field, self.first, self.second, self.coordinates, -1
            )


if __name__ == "__main__":
    unittest.main()
