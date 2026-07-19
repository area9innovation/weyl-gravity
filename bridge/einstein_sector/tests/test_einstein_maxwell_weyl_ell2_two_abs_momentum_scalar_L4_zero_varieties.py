from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.verify_einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L4_zero_varieties import (
    CERT,
    verify,
)


class ScalarL4ZeroVarietiesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text())

    def test_independent_replay(self) -> None:
        verify()

    def test_all_five_scalar_fibres_are_decomposed(self) -> None:
        self.assertEqual(
            [item["candidate_index"] for item in self.value["decompositions"]],
            [3, 5, 9, 15, 21],
        )
        self.assertTrue(
            self.value["classification"]["complete_scalar_internal_L4_zero_varieties_classified"]
        )

    def test_each_fibre_has_two_planes_and_two_mixed_sheets(self) -> None:
        for item in self.value["decompositions"]:
            self.assertEqual(
                [component["component_id"] for component in item["irreducible_components_over_C"]],
                ["first_fibre_zero", "second_fibre_zero", "mixed_plus", "mixed_minus"],
            )
            self.assertTrue(item["r_squared_interval"]["positive"])

    def test_remaining_tangent_cone_stays_open(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["remaining_sixteen_cross_fibre_zero_varieties_classified"])
        self.assertFalse(classification["same_fibre_quadratic_sources_classified"])
        self.assertFalse(classification["taub_common_zero_intersection_classified"])
        self.assertFalse(classification["complete_two_fibre_tangent_cone_classified"])


if __name__ == "__main__":
    unittest.main()
