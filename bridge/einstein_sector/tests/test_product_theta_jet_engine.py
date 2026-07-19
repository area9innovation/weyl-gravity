import unittest

import sympy as sp

from bridge.einstein_sector.product_theta_jet_engine import (
    COEFFICIENT_JET_ORDER,
    COS,
    COT,
    ONE,
    SIN,
    THETA_AXIS,
    LinearOperator,
    TaylorJet,
    ThetaJet,
    formal_adjoint_scalar,
    operation_record,
)


class ProductThetaJetEngineTests(unittest.TestCase):
    def test_elementary_equatorial_jets_are_exact_through_depth_ten(self):
        expected_cot = (0, -1, 0, -2, 0, -16, 0, -272, 0, -7936, 0)
        self.assertEqual(
            tuple(COT.jet((THETA_AXIS,) * order) for order in range(11)),
            expected_cot,
        )
        self.assertEqual(COT * SIN, COS)
        self.assertEqual(SIN / SIN, ONE)
        self.assertEqual((SIN * SIN).sqrt(), SIN)

    def test_exhausted_derivative_depth_raises_instead_of_padding_zero(self):
        current = COT
        for _ in range(COEFFICIENT_JET_ORDER):
            current = current.derivative(THETA_AXIS)
        self.assertEqual(current.valid_through, 0)
        with self.assertRaises(ValueError):
            current.derivative(THETA_AXIS)
        with self.assertRaises(ValueError):
            current.jet((THETA_AXIS,))

    def test_validity_propagates_through_arithmetic(self):
        partial = ThetaJet.from_derivatives((1, 2, 3))
        self.assertEqual(partial.valid_through, 2)
        for value in (partial + SIN, partial * SIN, partial.reciprocal(), partial.sqrt()):
            self.assertEqual(value.valid_through, 2)
            with self.assertRaises(ValueError):
                value.jet((THETA_AXIS,) * 3)

    def test_transient_arithmetic_is_not_retained_by_unbounded_method_caches(self):
        for method in (
            ThetaJet.__add__,
            ThetaJet.__neg__,
            ThetaJet.__mul__,
            ThetaJet.reciprocal,
            ThetaJet.derivative,
        ):
            self.assertFalse(hasattr(method, "cache_info"))

    def test_taylor_power_and_fourth_order_export_preserve_cubic_cosine(self):
        field = TaylorJet.field(0, 1)
        self.assertEqual(field.power(3), field * field * field)
        operator = LinearOperator.from_terms(((0, (), COS.power(3)),))
        records = operation_record(operator, output_row=0, coefficient_jet_order=4)
        self.assertEqual(len(records), 1)
        jets = {
            tuple(item["word"]): sp.Rational(item["coefficient"])
            for item in records[0]["coefficient_jets"]
        }
        self.assertEqual(jets[(THETA_AXIS,) * 3], -6)

    def test_formal_adjoint_uses_product_measure_divergence(self):
        derivative = LinearOperator.from_terms(((0, (THETA_AXIS,), ONE),))
        adjoint = formal_adjoint_scalar(derivative)
        table = {(word): coefficient for _row, word, coefficient in adjoint.terms}
        self.assertEqual(table[(THETA_AXIS,)], -ONE)
        self.assertEqual(table[()].valid_through, COEFFICIENT_JET_ORDER - 1)
        for order in range(table[()].valid_through + 1):
            self.assertEqual(
                table[()].jet((THETA_AXIS,) * order),
                (-COT).jet((THETA_AXIS,) * order),
            )

    def test_depth_budget_covers_construction_and_export_with_margin(self):
        construction_order = 4
        export_or_composition_order = 4
        safety_margin = 2
        self.assertGreaterEqual(
            COEFFICIENT_JET_ORDER,
            construction_order + export_or_composition_order + safety_margin,
        )


if __name__ == "__main__":
    unittest.main()
