import json
import unittest

from d_quotient_classical.atlas import generate_nonlinear_atlas_fragment as atlas
from residual_atlas.validate_fragment import validate


class NonlinearAtlasFragmentTests(unittest.TestCase):
    def test_generated_fragment_is_current(self):
        self.assertEqual(json.loads(atlas.OUTPUT.read_text()), atlas.build())
        validate(atlas.OUTPUT)

    def test_branch_crosswalk_fails_closed(self):
        entry = next(item for item in atlas.build()["entries"] if ".crosswalk." in item["id"])
        self.assertTrue(all(status == "NO_CERTIFIED_MAP" for status in entry["descriptions"].values()))

    def test_obstruction_is_not_particle_claim(self):
        entry = next(item for item in atlas.build()["entries"] if "filtered_cyclic_obstruction" in item["id"])
        self.assertEqual(entry["mode_data"]["dispersion"]["status"], "NOT_APPLICABLE")
        self.assertEqual(entry["descriptions"]["quantum"], "OPEN")

    def test_product_source_row_does_not_crosswalk_to_berger(self):
        entry = next(item for item in atlas.build()["entries"] if "axial_polar_einstein_minus" in item["id"])
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["second_order"]["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertEqual(entry["descriptions"]["quantum"], "NO_CERTIFIED_MAP")
        self.assertIn("not a cyclic L_infinity field redefinition", entry["claim_boundary"])
        self.assertIn("Berger retained carrier", entry["claim_boundary"])

    def test_bridge_two_is_fail_closed(self):
        entry = next(item for item in atlas.build()["entries"] if ".bridge2." in item["id"])
        self.assertTrue(all(status == "NO_CERTIFIED_MAP" for status in entry["descriptions"].values()))
        self.assertIn("INPUT_BLOCKED", entry["claim_boundary"])
        self.assertIn("q4 is not authorized", entry["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
