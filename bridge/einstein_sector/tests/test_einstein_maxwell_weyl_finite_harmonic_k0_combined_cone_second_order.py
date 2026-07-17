"""Tests for the finite-harmonic k0 combined cone theorem."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order import DEFAULT_OUTPUT, build_certificate


class FiniteHarmonicK0ConeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), self.payload)

    def test_complete_finite_harmonic_cone(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["all_finite_cross_ell_superpositions_classified"])
        self.assertTrue(classification["complete_common_stabilizer_zero_cone_second_order_extendible"])

    def test_cross_source_coefficients_not_needed(self) -> None:
        self.assertFalse(self.payload["classification"]["cross_ell_source_coefficients_required_for_existence"])

    def test_next_scopes_remain_open(self) -> None:
        self.assertFalse(self.payload["classification"]["infinite_harmonic_completion_classified"])
        self.assertFalse(self.payload["classification"]["opposite_momentum_phases_classified"])


if __name__ == "__main__":
    unittest.main()
