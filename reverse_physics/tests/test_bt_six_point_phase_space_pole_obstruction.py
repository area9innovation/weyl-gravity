import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from bt_six_point_phase_space_pole_obstruction import CERT
from verify_bt_six_point_phase_space_pole_obstruction import verify


class PoleObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_unique_transverse_pole(self):
        pole = self.certificate["exact_transverse_physical_pole"]
        self.assertEqual(pole["unique_zero_channel"], 11)
        self.assertEqual(pole["transverse_derivative"], "-1152/425")
        self.assertEqual(pole["chart_rank"], 5)

    def test_integrability_boundary(self):
        result = self.certificate["interpretation"]
        self.assertEqual(result["ordinary_exclusive_tree_phase_space_integral"], "DIVERGES_LOCALLY")
        self.assertEqual(result["regulated_or_inclusive_probability"], "NOT_COMPUTED")


if __name__ == "__main__":
    unittest.main()
