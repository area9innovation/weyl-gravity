from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_ell2_two_abs_momentum_odd_L_highest_weight_zero_subspaces import (
    OUTPUT,
    build,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_ell2_two_abs_momentum_odd_L_highest_weight_zero_subspaces import verify


class OddLHighestWeightZeroSubspacesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text())

    def test_certificate_is_current(self) -> None:
        self.assertEqual(build(), self.value)

    def test_independent_verifier(self) -> None:
        verify()

    def test_all_nine_fibres_have_mixed_zero_subspaces(self) -> None:
        self.assertEqual(len(self.value["witnesses"]), 9)
        self.assertTrue(all(item["highest_weight_subspace_dimension_over_C"] >= 4 for item in self.value["witnesses"]))
        self.assertTrue(self.value["classification"]["mixed_nonzero_points_certified_on_every_odd_L_fibre"])

    def test_difference_carriers_are_typed(self) -> None:
        rows = [item for item in self.value["witnesses"] if item["output_ell"] == 1]
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(item["temporal_signs"] == [1, -1] for item in rows))
        self.assertTrue(all("positive-frequency reality partner has m=-2" in item["real_tangent_completion"] for item in rows))

    def test_lifecycles_remain_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["complete_odd_L_zero_varieties_classified"])
        self.assertFalse(classification["taub_common_zero_intersection_classified"])
        self.assertFalse(classification["complete_two_fibre_tangent_cone_classified"])
        self.assertFalse(classification["causal_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
