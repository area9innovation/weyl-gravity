from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_ell2_two_abs_momentum_rank_one_branch_zero_varieties import OUTPUT


class RankOneBranchL4ZeroVarietiesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text())

    def test_two_distinct_fibres(self) -> None:
        self.assertEqual(self.value["summary"]["classified_candidates"], [8, 12])

    def test_four_dimension_twenty_components(self) -> None:
        for item in self.value["decompositions"]:
            zero = item["zero_variety"]
            self.assertEqual(zero["spectator_dimension_over_C"], 10)
            self.assertEqual(zero["dimension_per_component_over_C"], 20)
            self.assertEqual(len(zero["irreducible_components_over_C"]), 4)
            self.assertTrue(zero["all_mixed_components_real"])

    def test_exact_active_invariants(self) -> None:
        self.assertEqual([item["r_squared"] for item in self.value["decompositions"]], ["1/3", "1/40"])

    def test_higher_lifecycles_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["same_fibre_quadratic_sources_classified"])
        self.assertFalse(classification["taub_common_zero_intersection_classified"])
        self.assertFalse(classification["complete_two_fibre_tangent_cone_classified"])
        self.assertFalse(classification["causal_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
