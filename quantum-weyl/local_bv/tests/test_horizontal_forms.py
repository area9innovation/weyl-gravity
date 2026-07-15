import unittest

from local_bv.horizontal_forms import (
    STRICT_DENSITY,
    HorizontalForm,
    StrictDensityBRSTDifferential,
    strict_density_algebra,
)


class HorizontalFormTests(unittest.TestCase):
    def setUp(self) -> None:
        self.algebra = strict_density_algebra(4)
        self.brst = StrictDensityBRSTDifferential(self.algebra)

    def test_wedge_signs_include_coefficient_parity(self) -> None:
        dx0 = HorizontalForm.basis(4, (0,))
        dx1 = HorizontalForm.basis(4, (1,))
        self.assertEqual(dx0.wedge(dx1), -dx1.wedge(dx0))
        self.assertFalse(dx0.wedge(dx0))

        omega = HorizontalForm.coefficient(4, self.algebra.var("omega"))
        self.assertEqual(dx0.wedge(omega), -omega.wedge(dx0))

    def test_horizontal_differential_is_nilpotent(self) -> None:
        scalar = HorizontalForm.coefficient(
            4, self.algebra.var("g", (0, 1))
        )
        first = scalar.horizontal_differential(self.algebra)
        self.assertTrue(first)
        self.assertFalse(first.horizontal_differential(self.algebra))

    def test_density_brst_row_is_nilpotent_and_commutes_with_d(self) -> None:
        density = self.algebra.jet(STRICT_DENSITY)
        self.assertFalse(self.brst.nilpotency_residual(density))
        form = HorizontalForm.coefficient(4, self.algebra.var(STRICT_DENSITY))
        self.assertEqual(
            form.horizontal_differential(self.algebra).brst(self.brst),
            form.brst(self.brst).horizontal_differential(self.algebra),
        )

    def test_top_density_obeys_cartan_first_descent(self) -> None:
        top = HorizontalForm.coefficient(
            4, self.algebra.var(STRICT_DENSITY)
        ).wedge(HorizontalForm.basis(4, range(4)))
        contracted = top.interior_xi(self.algebra)
        self.assertEqual(
            top.brst(self.brst),
            contracted.horizontal_differential(self.algebra),
        )


if __name__ == "__main__":
    unittest.main()
