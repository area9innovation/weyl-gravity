"""Regression tests for standard exceptional/global moment maps."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_exceptional_global_moment_maps import DEFAULT_OUTPUT, build_certificate


class ExceptionalGlobalMomentMapsTest(unittest.TestCase):
    def test_certificate_is_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), build_certificate())

    def test_homogeneous_cone(self) -> None:
        block = build_certificate()["homogeneous_ell0"]
        self.assertEqual(block["mu_H"], "-Q_e**2 - a**2 - b**2 + b*d")
        self.assertEqual(block["quadratic_inertia_on_a_b_d_Qe"], {"positive": 1, "negative": 3, "zero": 0})

    def test_twist_zero_locus(self) -> None:
        self.assertEqual(build_certificate()["axial_twist"]["isolated_common_zero_locus"], "B=0 with arbitrary constant twist vector A")


if __name__ == "__main__":
    unittest.main()
