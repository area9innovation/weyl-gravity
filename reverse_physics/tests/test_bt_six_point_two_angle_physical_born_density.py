import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))

from bt_bivariate_rational import T, U, coerce
from verify_bt_six_point_two_angle_physical_born_density import CERT, verify


class BivariateRationalTests(unittest.TestCase):
    def test_field_arithmetic(self):
        left = (1 - T * T) / (1 + T * T)
        right = 2 * T / (1 + T * T)
        self.assertEqual(left * left + right * right, 1)
        tilt_left = (1 - U * U) / (1 + U * U)
        tilt_right = 2 * U / (1 + U * U)
        self.assertEqual(tilt_left * tilt_left + tilt_right * tilt_right, 1)

    def test_cross_cancellation(self):
        value = ((1 + T) / (1 + U)) * ((1 + U) / (1 + T))
        self.assertEqual(value, coerce(1))
        self.assertEqual(value.numerator.total_degree(), 0)
        self.assertEqual(value.denominator.total_degree(), 0)


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_certificate_checks(self):
        self.assertTrue(self.certificate["checks"]["ok"])
        self.assertEqual(self.certificate["checks"]["total"], 16)
        self.assertEqual(self.certificate["checks"]["failures"], [])

    def test_ten_exact_pairs(self):
        rows = self.certificate["exact_two_angle_family"]["middle_coefficients"]
        self.assertEqual(len(rows), 10)
        self.assertTrue(all(row["exactly_equal"] for row in rows))

    def test_claim_boundary(self):
        interpretation = self.certificate["interpretation"]
        self.assertEqual(
            interpretation["possible_isolated_or_lower_dimensional_regular_zero_set"],
            "NOT_EXCLUDED",
        )
        self.assertEqual(
            interpretation["complete_five_dimensional_final_state_phase_space"],
            "NOT_COMPUTED",
        )
        self.assertEqual(interpretation["Eq19_all_orders"], "NOT_PROVED")

    def test_independent_explicit_tree_rail(self):
        checks = verify(self.certificate)
        self.assertTrue(all(checks.values()))


if __name__ == "__main__":
    unittest.main()
