from __future__ import annotations

import json
import hashlib
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L1_zero_varieties import OUTPUT, ROOT, SCHEMA


class ScalarL1ZeroVarietiesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text())

    def test_certificate_provenance_hashes_are_current(self) -> None:
        self.assertEqual(self.value["schema_sha256"], hashlib.sha256(SCHEMA.read_bytes()).hexdigest())
        parent = ROOT / self.value["provenance"]["parent"]
        self.assertEqual(self.value["provenance"]["parent_sha256"], hashlib.sha256(parent.read_bytes()).hexdigest())

    def test_three_difference_fibres_are_classified(self) -> None:
        self.assertEqual([item["candidate_index"] for item in self.value["decompositions"]], [14, 17, 20])
        self.assertTrue(all(item["temporal_signs"] == [1, -1] for item in self.value["decompositions"]))

    def test_each_variety_is_irreducible_dimension_fourteen(self) -> None:
        for item in self.value["decompositions"]:
            self.assertEqual(item["zero_variety"]["dimension_over_C"], 14)
            self.assertEqual(item["zero_variety"]["irreducible_components_over_C"], 1)

    def test_rank_stratification_is_exact(self) -> None:
        certificate = self.value["third_transvectant_certificate"]
        self.assertEqual(len(certificate["rank_at_most_two_monic_groebner_basis"]), 7)
        self.assertEqual(len(certificate["rank_at_most_one_monic_groebner_basis"]), 15)

    def test_higher_lifecycles_remain_open(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["other_eighteen_parent_fibre_zero_varieties_classified"])
        self.assertFalse(classification["same_fibre_quadratic_sources_classified"])
        self.assertFalse(classification["taub_common_zero_intersection_classified"])
        self.assertFalse(classification["complete_two_fibre_tangent_cone_classified"])
        self.assertFalse(classification["causal_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
