"""Regression tests for the fixed-ell k=0 combined cone theorem."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order import DEFAULT_OUTPUT, build_certificate


class FixedEllK0CombinedConeSecondOrderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), self.payload)

    def test_fixed_ell_cone_promoted(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["every_fixed_ell_at_least_2_combined_common_zero_cone_second_order_extendible"])
        self.assertTrue(classification["zero_frequency_scalar_source_rank_one_and_moment_map_factored"])

    def test_ell3_fixture_exact(self) -> None:
        fixture = self.payload["exact_ell3_fixture"]
        self.assertTrue(fixture["exact_ell3_fixture"])
        self.assertEqual(fixture["E00_source_matrix"][0][0], "-73440/7")

    def test_cross_ell_scope_remains_open(self) -> None:
        self.assertFalse(self.payload["classification"]["cross_ell_superpositions_classified"])


if __name__ == "__main__":
    unittest.main()
