import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate16_occupation_gluing import OUTPUT, build


class Candidate16OccupationGluingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_normalized_scalar_base_is_connected_polygon(self) -> None:
        base = self.payload["normalized_scalar_base"]
        self.assertEqual(base["affine_cone_dimension"], 3)
        self.assertEqual(base["positive_extreme_rays"], 4)
        self.assertTrue(base["compact"])
        self.assertTrue(base["connected"])

    def test_proper_connected_fibre_gluing(self) -> None:
        total = self.payload["total_zero_link"]
        self.assertTrue(total["projection_proper"])
        self.assertTrue(total["projection_surjective"])
        self.assertTrue(total["every_fibre_connected"])
        self.assertTrue(total["complete_normalized_zero_link_connected"])

    def test_scope_remains_candidate_specific(self) -> None:
        flags = self.payload["classification"]
        self.assertTrue(flags["candidate16_active_occupation_gluing_closed"])
        self.assertFalse(flags["origin_adjoined"])
        self.assertFalse(flags["cross_candidate_gluing"])
        self.assertFalse(flags["final_residual_descent"])
        self.assertFalse(flags["causal_residual_observational_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
