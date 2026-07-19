from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties import OUTPUT


class MultiplicityTwoL3ZeroVarietiesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text())

    def test_three_distinct_fibres(self) -> None:
        self.assertEqual([item["candidate_index"] for item in self.value["decompositions"]], [6, 10, 18])

    def test_spectator_and_active_dimensions(self) -> None:
        for item in self.value["decompositions"]:
            zero = item["zero_variety"]
            self.assertEqual((zero["active_dimension_over_C"], zero["spectator_dimension_over_C"]), (12, 10))
            self.assertEqual((zero["dimension_over_C"], zero["ambient_dimension_over_C"]), (22, 30))
            self.assertEqual(zero["irreducible_components_over_C"], 1)

    def test_real_pencil_square(self) -> None:
        self.assertTrue(all(item["reduced_parity_pencil"]["lambda_squared"] == "384" for item in self.value["decompositions"]))

    def test_higher_lifecycles_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["same_fibre_quadratic_sources_classified"])
        self.assertFalse(classification["taub_common_zero_intersection_classified"])
        self.assertFalse(classification["complete_two_fibre_tangent_cone_classified"])
        self.assertFalse(classification["causal_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
