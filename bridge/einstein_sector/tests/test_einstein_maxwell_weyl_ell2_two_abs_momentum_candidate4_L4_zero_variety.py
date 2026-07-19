from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.verify_einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_L4_zero_variety import (
    CERT,
    verify,
)


class Candidate4L4ZeroVarietyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text())

    def test_independent_replay(self) -> None:
        verify()

    def test_target_doublet_reduces_to_two_equations(self) -> None:
        self.assertEqual(self.value["candidate_index"], 4)
        self.assertTrue(self.value["classification"]["two_target_components_reduced_exactly"])
        self.assertEqual(len(self.value["exact_target_relations"]["independent_equations"]), 2)

    def test_four_components_are_exact_and_real(self) -> None:
        components = self.value["zero_variety"]["irreducible_components_over_C"]
        self.assertEqual(
            [component["component_id"] for component in components],
            ["first_fibre_zero", "second_fibre_zero", "mixed_plus", "mixed_minus"],
        )
        self.assertTrue(self.value["zero_variety"]["all_mixed_components_real"])

    def test_remaining_tangent_cone_stays_open(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["other_twenty_parent_fibre_zero_varieties_classified"])
        self.assertFalse(classification["same_fibre_quadratic_sources_classified"])
        self.assertFalse(classification["taub_common_zero_intersection_classified"])
        self.assertFalse(classification["complete_two_fibre_tangent_cone_classified"])


if __name__ == "__main__":
    unittest.main()
