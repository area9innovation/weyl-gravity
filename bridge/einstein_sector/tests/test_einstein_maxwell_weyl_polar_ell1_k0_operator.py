"""Regression tests for the exceptional polar ell=1 quotient."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_polar_ell1_k0_operator import DEFAULT_OUTPUT, build_certificate


class PolarEll1K0OperatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), self.payload)

    def test_shells(self) -> None:
        shells = self.payload["operator_theorem"]["physical_shells"]
        self.assertEqual(shells["fourth_order"]["omega_squared"], "4/3")
        self.assertEqual(shells["standard"]["omega_squared"], "4")

    def test_zero_cokernel_absent(self) -> None:
        self.assertTrue(self.payload["classification"]["polar_ell1_zero_frequency_physical_cokernel_absent"])


if __name__ == "__main__":
    unittest.main()
