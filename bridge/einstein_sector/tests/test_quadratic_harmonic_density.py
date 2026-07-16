from __future__ import annotations

import unittest

import sympy as sp

from bridge.einstein_sector.quadratic_harmonic_density import (
    quadratic_normal_form,
)


class QuadraticHarmonicDensityTests(unittest.TestCase):
    def test_axial_weyl_density_reproduces_certified_normal_form(self) -> None:
        theta = sp.symbols("theta", real=True)
        eigenvalue, mass = sp.symbols("lambda mu", real=True)
        metric_pair, maxwell_pair = sp.symbols("HH QQ", real=True)
        harmonic = sp.Function("Y")(theta)
        first = sp.diff(harmonic, theta)
        second = sp.diff(harmonic, theta, 2)
        sine, cosine = sp.sin(theta), sp.cos(theta)
        density = metric_pair * (
            -3 * mass * sine * first**2
            + sp.Rational(1, 2) * sine * first**2
            + 3 * sine * second**2
            + 3 * cosine * first * second
            + 3 * cosine**2 * first**2 / sine
        ) - 2 * maxwell_pair * sine * harmonic**2
        normal = quadratic_normal_form(
            density, harmonic, theta, eigenvalue
        )
        expected = (
            eigenvalue * (3 * eigenvalue - 1 - 3 * mass) * metric_pair
            - 2 * maxwell_pair
        )
        self.assertEqual(sp.simplify(normal.canonical_coefficient - expected), 0)
        self.assertEqual(normal.remainder, 0)


if __name__ == "__main__":
    unittest.main()
