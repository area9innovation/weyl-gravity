"""Regression tests for the exceptional axial ell=1 operator."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_axial_ell1_k0_operator import DEFAULT_OUTPUT, build_certificate


class AxialEll1K0OperatorTest(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), build_certificate())

    def test_extra_primary(self) -> None:
        c = build_certificate()["classification"]
        self.assertTrue(c["extra_fourth_order_ell1_shell_discovered"])
        self.assertEqual(c["extra_shell_frequency_squared"], "4/3")

    def test_fail_closed_current(self) -> None:
        self.assertFalse(build_certificate()["classification"]["ell1_positive_frequency_Lee_Wald_inertia_of_extra_mode"])


if __name__ == "__main__":
    unittest.main()
