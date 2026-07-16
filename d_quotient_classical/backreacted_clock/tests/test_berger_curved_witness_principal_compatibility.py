from copy import deepcopy
import unittest

from d_quotient_classical.backreacted_clock.berger_curved_witness_principal_compatibility import (
    BergerCurvedWitnessPrincipalCompatibility,
)


class BergerCurvedWitnessPrincipalCompatibilityTests(unittest.TestCase):
    def test_submitted_candidate_is_scoped_and_fail_closed(self) -> None:
        payload = BergerCurvedWitnessPrincipalCompatibility.build().payload
        self.assertTrue(payload["flags"]["BERGER_CURVED_WITNESS_ALGEBRAIC_IDENTITY"])
        self.assertFalse(payload["flags"]["BERGER_CURVED_WITNESS_PRINCIPAL_COMPATIBILITY"])
        self.assertFalse(payload["flags"]["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"])
        self.assertEqual(payload["normalized_obstruction"]["defect"], "-1")

    def test_green_promotion_is_rejected(self) -> None:
        payload = deepcopy(BergerCurvedWitnessPrincipalCompatibility.build().payload)
        payload["flags"]["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"] = True
        with self.assertRaises(AssertionError):
            BergerCurvedWitnessPrincipalCompatibility(payload).verify()

    def test_erasing_normalized_defect_is_rejected(self) -> None:
        payload = deepcopy(BergerCurvedWitnessPrincipalCompatibility.build().payload)
        payload["normalized_obstruction"]["defect"] = "0"
        with self.assertRaises(AssertionError):
            BergerCurvedWitnessPrincipalCompatibility(payload).verify()


if __name__ == "__main__":
    unittest.main()
