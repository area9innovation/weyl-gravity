"""Tests for the homogeneous common-zero quadric extension."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_quadric_second_order import DEFAULT_OUTPUT, build_certificate


class HomogeneousQuadricSecondOrderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8")), self.payload)

    def test_constraint_is_complete_source_obstruction(self) -> None:
        self.assertTrue(self.payload["classification"]["homogeneous_Taub_pairing_equals_moment_map_quadric"])

    def test_entire_quadric_extends(self) -> None:
        self.assertTrue(self.payload["classification"]["complete_standard_homogeneous_common_zero_quadric_second_order_extendible"])
        self.assertTrue(self.payload["second_order_correction"]["remainder_vanishes_modulo_common_zero_equation"])

    def test_spectators_survive(self) -> None:
        self.assertTrue(self.payload["classification"]["circumference_and_Wilson_spectators_retained"])


if __name__ == "__main__":
    unittest.main()
