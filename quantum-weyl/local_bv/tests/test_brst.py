import unittest

from local_bv import LocalJetAlgebra, MinimalBRSTDifferential


class MinimalBRSTTests(unittest.TestCase):
    def setUp(self) -> None:
        self.algebra = LocalJetAlgebra(4)
        self.s = MinimalBRSTDifferential(self.algebra)

    def base_generators(self):
        yield self.algebra.jet("omega")
        for mu in range(4):
            yield self.algebra.jet("xi", (mu,))
        for mu in range(4):
            for nu in range(mu, 4):
                yield self.algebra.jet("g", (mu, nu))

    def test_nilpotent_on_every_independent_minimal_generator(self) -> None:
        generators = list(self.base_generators())
        self.assertEqual(len(generators), 15)
        for generator in generators:
            with self.subTest(field=generator.field, components=generator.components):
                self.assertFalse(self.s.nilpotency_residual(generator))

    def test_rows_are_the_declared_diff_times_weyl_transformations(self) -> None:
        expected_omega = sum(
            (
                self.algebra.var("xi", (rho,))
                * self.algebra.total_derivative(self.algebra.var("omega"), rho)
                for rho in range(4)
            ),
            start=self.algebra.var("omega") * 0,
        )
        self.assertEqual(self.s.on_variable(self.algebra.jet("omega")), expected_omega)

        expected_xi = sum(
            (
                self.algebra.var("xi", (rho,))
                * self.algebra.total_derivative(self.algebra.var("xi", (2,)), rho)
                for rho in range(4)
            ),
            start=self.algebra.var("omega") * 0,
        )
        self.assertEqual(self.s.on_variable(self.algebra.jet("xi", (2,))), expected_xi)

        expected_metric = 2 * self.algebra.var("omega") * self.algebra.var("g", (0, 1))
        for rho in range(4):
            expected_metric += self.algebra.var("xi", (rho,)) * self.algebra.total_derivative(
                self.algebra.var("g", (0, 1)), rho
            )
            expected_metric += self.algebra.total_derivative(self.algebra.var("xi", (rho,)), 0) * self.algebra.var(
                "g", (rho, 1)
            )
            expected_metric += self.algebra.total_derivative(self.algebra.var("xi", (rho,)), 1) * self.algebra.var(
                "g", (0, rho)
            )
        self.assertEqual(self.s.on_variable(self.algebra.jet("g", (0, 1))), expected_metric)

    def test_commutes_with_coordinate_total_derivatives(self) -> None:
        for generator in self.base_generators():
            for direction in range(4):
                differentiated = self.algebra.differentiate_variable(generator, direction)
                expected = self.algebra.total_derivative(self.s.on_variable(generator), direction)
                with self.subTest(field=generator.field, components=generator.components, direction=direction):
                    self.assertEqual(self.s.on_variable(differentiated), expected)

    def test_odd_graded_leibniz_rule(self) -> None:
        xi = self.algebra.var("xi", (0,))
        omega = self.algebra.var("omega")
        metric = self.algebra.var("g", (1, 2))
        self.assertEqual(self.s(xi * metric), self.s(xi) * metric - xi * self.s(metric))
        self.assertEqual(self.s(metric * omega), self.s(metric) * omega + metric * self.s(omega))

    def test_nilpotent_on_representative_derivative_jets(self) -> None:
        jets = (
            self.algebra.jet("omega", derivatives=(1, 1, 0, 0)),
            self.algebra.jet("xi", (2,), derivatives=(0, 0, 1, 0)),
            self.algebra.jet("g", (1, 3), derivatives=(0, 1, 0, 0)),
        )
        for jet in jets:
            with self.subTest(field=jet.field, components=jet.components, derivatives=jet.derivatives):
                self.assertFalse(self.s.nilpotency_residual(jet))


if __name__ == "__main__":
    unittest.main()
