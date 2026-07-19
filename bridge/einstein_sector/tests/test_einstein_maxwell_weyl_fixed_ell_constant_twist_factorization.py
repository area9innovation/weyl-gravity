"""Tests for the fixed-ell constant-twist representation reduction."""

import json
import unittest

from bridge.einstein_sector import einstein_maxwell_weyl_fixed_ell_constant_twist_factorization as theorem


class FixedEllConstantTwistFactorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = theorem.build()

    def test_certificate_is_current(self) -> None:
        self.assertEqual(json.loads(theorem.OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_all_m_factorization_is_certified(self) -> None:
        self.assertTrue(self.value["classification"]["all_fixed_ell_all_m_factorization_certified"])
        self.assertIn("A_hat dot J_ell", self.value["representation_theorem"]["factorization"])

    def test_axis_kernel_is_one_dimensional(self) -> None:
        for fixture in self.value["exact_fixture_ledger"]:
            self.assertEqual(fixture["rank"], 2 * fixture["ell"])
            self.assertEqual(fixture["kernel_dimension"], 1)

    def test_ell2_regression(self) -> None:
        regression = self.value["ell2_regression"]
        self.assertEqual(regression["Einstein_each_shell_kernel_dimension"], 10)
        self.assertEqual(regression["extra_kernel_dimension"], 20)
        self.assertIn("mistyped", regression["repair_disposition"])

    def test_next_calculation_is_finite(self) -> None:
        payload = self.value["minimal_next_computation"]
        self.assertEqual(payload["Einstein_payload"], "two 2x2 matrices Q_(ell,+/-)")
        self.assertEqual(payload["extra_payload"], "one 4x4 matrix P_ell")
        self.assertFalse(payload["all_m_replay_required"])

    def test_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["complete_fixed_ell_constant_twist_cone_classified"])
        self.assertEqual(self.value["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "OPEN")
        self.assertEqual(self.value["correction_classes"]["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
