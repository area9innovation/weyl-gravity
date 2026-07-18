from __future__ import annotations

import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_formal_metric_green_variation import (
    build,
    exact_fixture,
    tangent_family_check,
    verify,
)


class FormalMetricGreenVariationTests(unittest.TestCase):
    def test_differentiated_green_algebra(self) -> None:
        fixture = exact_fixture()
        self.assertTrue(all(value == 0 for value in fixture["identity_defects"].values()))
        self.assertGreater(fixture["qdot_nonzero"], 0)
        self.assertGreater(fixture["pdot_nonzero"], 0)
        self.assertGreater(fixture["gdot_nonzero"], 0)

    def test_slabwise_einstein_family(self) -> None:
        family = tangent_family_check()
        self.assertEqual(family["first_integral_defect_through_epsilon2"], 0)
        self.assertEqual(family["evolution_defect_through_epsilon2"], 0)
        self.assertEqual(family["exact_Einstein_component_defects"], 0)
        self.assertIn("sinh(2t)", family["tangent"])

    def test_fail_closed_scope(self) -> None:
        payload = build()
        verify(payload)
        self.assertTrue(payload["flags"]["TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION"])
        self.assertFalse(payload["flags"]["TRANSVERSE_FORMAL_RANK310_CAUSAL_VARIATION"])
        self.assertFalse(payload["flags"]["TRANSVERSE_CAUSAL_TRANSFER"])
        self.assertFalse(
            payload["rank310_globalization_audit"]["global_smooth_coefficient_export_present"]
        )


if __name__ == "__main__":
    unittest.main()
