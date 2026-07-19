"""Tests for the global five-charge current replay."""

import unittest

from d_quotient_classical.relative import einstein_weyl_relative_global_five_charge_replay as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_global_five_charge_replay import verify


class GlobalFiveChargeReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = producer.build()

    def test_global_descent_and_replay(self) -> None:
        producer.validate(self.value)
        self.assertTrue(self.value["classification"]["global_smooth_horizontal_improvement_exists"])
        self.assertTrue(self.value["classification"]["slice_integral_matches_complete_five_charge_q2"])
        self.assertEqual(len(self.value["complete_replay"]["blocks"]), 4)

    def test_coordinate_and_locality_boundaries(self) -> None:
        self.assertFalse(self.value["classification"]["serialized_coordinate_primitive_global_smoothness_asserted"])
        self.assertFalse(self.value["classification"]["direct_support_local_map_to_constant_charges"])
        self.assertFalse(self.value["classification"]["direct_f2_repaired"])

    def test_independent_replay(self) -> None:
        if producer.OUTPUT.exists():
            self.assertEqual(verify()["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
