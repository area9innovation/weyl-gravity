import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_regular_pencil_L4_zero_varieties.json"


class RegularPencilL4ZeroVarietiesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text())

    def test_candidate_census_is_exact(self) -> None:
        self.assertEqual(self.value["summary"]["classified_candidates"], [7, 11, 19])
        self.assertEqual(self.value["summary"]["remaining_unclassified_cross_fibre_candidates"], [13])

    def test_every_pencil_has_four_distinct_real_roots(self) -> None:
        for item in self.value["decompositions"]:
            witnesses = item["exact_interval_witnesses"]
            self.assertEqual(witnesses["trace_square_pencil"]["sign"], "positive")
            self.assertEqual(witnesses["determinant_square_pencil"]["sign"], "positive")
            self.assertEqual(witnesses["discriminant_square_pencil"]["sign"], "positive")
            self.assertEqual(item["pencil"]["root_structure"], "four distinct nonzero real roots z_i")

    def test_component_decomposition_is_not_equidimensional(self) -> None:
        for item in self.value["decompositions"]:
            zero = item["zero_variety"]
            self.assertEqual(zero["component_dimensions_over_C"], [20, 10, 10, 10, 10, 10])
            self.assertEqual(len(zero["irreducible_components_over_C"]), 6)
            self.assertTrue(zero["all_mixed_components_real_supported"])

    def test_extension_claims_remain_open(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["candidate_13_zero_variety_classified"])
        self.assertFalse(classification["same_fibre_quadratic_sources_classified"])
        self.assertFalse(classification["taub_common_zero_intersection_classified"])
        self.assertFalse(classification["complete_two_fibre_tangent_cone_classified"])
        self.assertFalse(classification["causal_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
