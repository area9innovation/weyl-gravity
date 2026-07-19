"""Tests for complete circumference oscillator bounded classification."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_circumference_complete_oscillator_bounded_classification import OUTPUT, build


class CompleteCircumferenceClassificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_k_strata_are_distinct(self) -> None:
        bounded = self.value["bounded_classification"]
        self.assertEqual(bounded["k_zero"]["status"], "CERTIFIED")
        self.assertEqual(bounded["k_nonzero"]["status"], "OBSTRUCTED")

    def test_obstruction_is_resonant(self) -> None:
        self.assertTrue(self.value["classification"]["circumference_obstruction_is_resonant_not_polynomial"])
        self.assertFalse(self.value["bounded_classification"]["k_nonzero"]["polynomial_source"])
        self.assertEqual(self.value["bounded_classification"]["k_nonzero"]["ledger_location"], "R_(j,a), not P_(j,r)")

    def test_smooth_and_fail_closed(self) -> None:
        self.assertEqual(self.value["correction_classes"]["SMOOTH_SECULAR"]["status"], "CERTIFIED")
        self.assertEqual(self.value["correction_classes"]["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")
        self.assertFalse(self.value["classification"]["complete_bounded_cone_solved"])


if __name__ == "__main__":
    unittest.main()
