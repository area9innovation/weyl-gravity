"""Tests for the twist-position/velocity ell2 bounded cone."""

from __future__ import annotations

import json
import unittest

from bridge.einstein_sector import einstein_maxwell_weyl_twist_position_velocity_ell2_complete_bounded_cone as theorem


class TwistPositionVelocityEll2BoundedConeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = theorem.build()

    def test_generated_certificate_is_current(self) -> None:
        stored = json.loads(theorem.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(stored, self.value)

    def test_velocity_is_forced_zero(self) -> None:
        self.assertEqual(self.value["complete_bounded_zero_locus"]["first_equation"], "B=0")
        self.assertTrue(self.value["classification"]["twist_velocity_forced_zero_in_bounded_class"])

    def test_velocity_obstruction_is_bound_to_direct_source_certificate(self) -> None:
        obstruction = self.value["twist_velocity_elimination"]
        self.assertEqual(obstruction["direct_aligned_metric_00_coefficient"], "-7*B**2")
        self.assertEqual(obstruction["source_certificate_result_id"], "EINSTEIN_MAXWELL_WEYL_STANDARD_GLOBAL_BOUNDED_SECOND_ORDER")

    def test_position_cone_survives(self) -> None:
        zero_locus = self.value["complete_bounded_zero_locus"]
        self.assertIn("m_A=+2,-2", zero_locus["nonaxisymmetric_survivor"])
        self.assertIn("span{polar_e1", zero_locus["A_nonzero_branch"])

    def test_bounded_claim_is_complete_only_on_declared_carrier(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["bounded_zero_locus_necessary_and_sufficient"])
        self.assertFalse(classification["other_homogeneous_tangents_classified"])
        self.assertFalse(classification["other_ell_or_nonzero_momentum_classified"])

    def test_larger_secular_and_causal_classes_remain_fail_closed(self) -> None:
        self.assertFalse(self.value["classification"]["unrestricted_smooth_secular_cone_classified"])
        self.assertEqual(self.value["correction_classes"]["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
