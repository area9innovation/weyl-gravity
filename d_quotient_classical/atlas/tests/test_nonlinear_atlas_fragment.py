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

    def test_product_branch_dictionary_is_sectoral_only(self):
        value = atlas.build()["entries"]
        axial = next(item for item in value if "generic_axial_relative_branch_map" in item["id"])
        polar = next(item for item in value if "generic_polar_relative_branch_map" in item["id"])
        self.assertEqual(axial["descriptions"]["symplectic"], "CERTIFIED")
        self.assertEqual(axial["descriptions"]["nonlinear"], "OPEN")
        self.assertIn("not the all-sector", axial["claim_boundary"])
        self.assertIn("fixed identity", axial["claim_boundary"])
        self.assertEqual(polar["descriptions"]["nonlinear"], "OPEN")
        self.assertIn("fixed identity", polar["claim_boundary"])
        self.assertIn("corrected nonidentity", polar["claim_boundary"])

    def test_abd_source_matrix_is_not_an_obstruction_verdict(self):
        entry = next(item for item in atlas.build()["entries"] if "homogeneous_abd" in item["id"])
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OPEN")
        self.assertIn("on-shell map lifecycle", entry["claim_boundary"])
        self.assertIn("No individual mode is declared obstructed", entry["claim_boundary"])

    def test_exceptional_solution_cofiber_does_not_activate_bridge_two(self):
        entry = next(item for item in atlas.build()["entries"] if "exceptional_ell1_k0_solution_cofiber" in item["id"])
        self.assertEqual(entry["descriptions"]["symplectic"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["dispersion"]["status"], "CERTIFIED")
        self.assertIn("does not activate cyclic Bridge 2", entry["claim_boundary"])

    def test_product_relative_linfinity_receiver_is_fail_closed(self):
        entry = next(item for item in atlas.build()["entries"] if "relative_linfinity_through_arity_three_preflight" in item["id"])
        self.assertTrue(all(status == "NO_CERTIFIED_MAP" for status in entry["descriptions"].values()))
        self.assertIn("INPUT_BLOCKED", entry["claim_boundary"])
        self.assertIn("same-background", entry["claim_boundary"])
        self.assertIn("Berger tensors are ineligible", entry["claim_boundary"])
        self.assertIn("q4 is not authorized", entry["claim_boundary"])

    def test_fixed_identity_cyclic_obstruction_is_scoped(self):
        entry = next(item for item in atlas.build()["entries"] if "generic_identity_cyclic_compatibility_obstruction" in item["id"])
        self.assertEqual(entry["descriptions"]["symplectic"], "OBSTRUCTED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "NO_CERTIFIED_MAP")
        self.assertEqual(entry["mode_data"]["lee_wald"]["status"], "OBSTRUCTED")
        self.assertIn("fixed identity", entry["claim_boundary"])
        self.assertIn("Corrected nonidentity", entry["claim_boundary"])
        self.assertIn("remain OPEN", entry["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
