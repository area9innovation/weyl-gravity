import json
import os
import sys
import unittest
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))

from bt_six_point_full_phase_space_born_positivity import CERT, CHANNELS
from bt_sparse_rational import SparseRationalField
from verify_bt_six_point_full_phase_space_born_positivity import species_incidence, verify


class SparseRationalTests(unittest.TestCase):
    def test_characteristic_zero_cancellation(self):
        field = SparseRationalField(["a", "b"])
        a, b = field.gens
        self.assertEqual(((1 + a) / (1 + b)) * ((1 + b) / (1 + a)), 1)

    def test_finite_field_cancellation(self):
        field = SparseRationalField(["t", "u", "v"], modulus=1_000_003)
        t, u, v = field.gens
        self.assertEqual((1 - t * t) ** 2 + (2 * t) ** 2, (1 + t * t) ** 2)
        self.assertEqual((u + v) / (u + v), 1)

    def test_incompatible_fields_refused(self):
        left = SparseRationalField(["t"])
        right = SparseRationalField(["t"])
        with self.assertRaises(TypeError):
            _ = left.gens[0] + right.gens[0]


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_certificate_checks(self):
        self.assertTrue(self.certificate["checks"]["ok"])
        self.assertEqual(self.certificate["checks"]["total"], 16)

    def test_incidence_has_one_forbidden_channel_per_assignment(self):
        incidence = species_incidence()
        self.assertEqual(len(CHANNELS), 10)
        self.assertTrue(all(row[i] == 0 and sum(row) == 9 for i, row in enumerate(incidence)))

    def test_common_zero_map_is_invertible(self):
        self.assertEqual(self.certificate["universal_complement_formula"]["incidence_determinant"], -9)

    def test_chart_is_full_rank(self):
        chart = self.certificate["full_physical_chart"]["jacobian_certificate"]
        self.assertEqual(chart["rank"], 5)
        self.assertEqual(Fraction(chart["nonzero_minor_determinant"]), Fraction(864, 3125))

    def test_claim_boundary(self):
        result = self.certificate["interpretation"]
        self.assertEqual(result["internal_channel_poles"], "EXCLUDED_NOT_REGULATED")
        self.assertEqual(result["integrated_normalized_probability"], "NOT_COMPUTED")
        self.assertEqual(result["Eq19_all_orders"], "NOT_PROVED")

    def test_independent_explicit_tree_rail(self):
        self.assertTrue(all(verify(self.certificate).values()))


if __name__ == "__main__":
    unittest.main()
