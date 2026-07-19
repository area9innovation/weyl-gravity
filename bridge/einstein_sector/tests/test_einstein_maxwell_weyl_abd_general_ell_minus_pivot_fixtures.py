"""Tests for the multi-ell Einstein-minus pivot fixtures."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_abd_general_ell_minus_pivot_fixtures import OUTPUT, build


class GeneralEllPivotFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_three_physical_fibres(self) -> None:
        self.assertEqual([row["ell"] for row in self.value["fixtures"]], [2, 3, 4])
        self.assertEqual([row["polar_b_t3"] for row in self.value["fixtures"]], ["66", "552", "2600"])

    def test_candidate_is_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["candidate_functional_laws_reconstructed"])
        self.assertFalse(classification["symbolic_functional_form_or_degree_bound_proved"])
        self.assertFalse(classification["general_ell_pivot_theorem"])

    def test_scope_excludes_nonzero_momentum(self) -> None:
        self.assertFalse(self.value["classification"]["nonzero_momentum_classified"])


if __name__ == "__main__":
    unittest.main()
