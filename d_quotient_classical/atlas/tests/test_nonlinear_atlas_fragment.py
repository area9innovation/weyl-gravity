import copy
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
        self.assertIn("complete atlas mode scope", entry["claim_boundary"])
        self.assertIn("q4 is not authorized", entry["claim_boundary"])

    def test_bridge_two_activation_opens_only_the_projected_calculation(self):
        importer = json.loads(atlas.CERTS["branch_importer"].read_text())
        importer = copy.deepcopy(importer)
        importer["claim_flags"]["BRIDGE_2_ACTIVATED"] = True
        importer["imported_branch_map"] = {
            "result_id": "BERGER_ADMISSIBLE_SAME_BACKGROUND_BRANCH_MAP_V1",
            "map_category": "NONCONTRACTIBLE_COFIBER",
            "branch_ids": ["Einstein_like", "extra_Weyl", "Maxwell", "gauge_nondynamical"],
            "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            "mode_scope": {
                "theory": "pure-Weyl gravity with Berger clock and Maxwell apparatus",
                "background": "fixed_rational_positive_Berger_clock",
                "boundaries": "R_t x compact Berger S3; no spatial boundary",
                "charge_sector": "fixed-coupling retained sector",
                "carrier": "certified synthetic branch carrier",
                "degree": "all declared BV degrees",
                "parity": "all declared parities",
                "ell": "all declared harmonics",
                "m": "all declared harmonics",
                "k": "NOT_APPLICABLE",
                "omega": "all declared K_Berger frequencies",
            },
        }
        entry = atlas.bridge2_entry(importer, {})
        self.assertEqual(entry["descriptions"]["symplectic"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["descriptions"]["causal"], "NO_CERTIFIED_MAP")
        self.assertEqual(entry["mode_data"]["lee_wald"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OPEN")
        self.assertIn("projected ell2/ell3 operation", entry["claim_boundary"])
        self.assertIn("q4 is not authorized", entry["claim_boundary"])
        importer["imported_branch_map"]["dependency_tags"].append("LORENTZIAN-CAUSAL")
        causal_entry = atlas.bridge2_entry(importer, {})
        self.assertEqual(causal_entry["descriptions"]["causal"], "OPEN")
        self.assertEqual(causal_entry["mode_data"]["second_order"]["causal_retarded"]["status"], "OPEN")

    def test_product_branch_dictionary_is_sectoral_only(self):
        value = atlas.build()["entries"]
        axial = next(item for item in value if "generic_axial_relative_branch_map" in item["id"])
        polar = next(item for item in value if "generic_polar_relative_branch_map" in item["id"])
        self.assertEqual(axial["descriptions"]["symplectic"], "OBSTRUCTED")
        self.assertEqual(axial["descriptions"]["nonlinear"], "OPEN")
        self.assertIn("not the all-sector", axial["claim_boundary"])
        self.assertIn("inertia mismatch", axial["claim_boundary"])
        self.assertEqual(polar["descriptions"]["nonlinear"], "OPEN")
        self.assertIn("cyclic correction is obstructed", polar["claim_boundary"])
        self.assertIn("incompatible inertia", polar["claim_boundary"])

    def test_complete_homogeneous_twist_matrix_still_leaves_zero_locus_open(self):
        entry = next(item for item in atlas.build()["entries"] if "homogeneous_twist_times" in item["id"])
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("rank two", entry["mode_data"]["resonance"]["statement"])
        self.assertIn("rank four", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OPEN")
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(entry["descriptions"]["causal"], "NO_CERTIFIED_MAP")
        self.assertIn("does not solve", entry["claim_boundary"])
        self.assertIn("activate Berger or compact-product Bridge 2", entry["claim_boundary"])

    def test_homogeneous_twist_tangent_cone_has_bounded_obstruction(self):
        entry = next(item for item in atlas.build()["entries"] if "bounded_tangent_cone" in item["id"])
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertIn("no off-axis branch", entry["mode_data"]["taub_maps"]["statement"])
        bounded = entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]
        self.assertEqual(bounded["status"], "OBSTRUCTED")
        self.assertIn("-7*B^2*t^2", bounded["statement"])
        smooth = entry["mode_data"]["second_order"]["smooth_secular"]
        expected = "CERTIFIED" if atlas.smooth_extension_import_ready() else "OPEN"
        self.assertEqual(smooth["status"], expected)
        if expected == "CERTIFIED":
            self.assertIn("coefficient-explicit ordinary harmonic primitive", smooth["statement"])
            paths = {evidence["path"] for evidence in entry["evidence"]}
            self.assertIn(
                "bridge/certificates/einstein_maxwell_weyl_circumference_ell2_extra_transport_primitive.json",
                paths,
            )
        if expected == "OPEN":
            self.assertIn("full eight-row", smooth["statement"])
            self.assertIn("PASS Tier-1 receipt", smooth["statement"])
        self.assertEqual(entry["descriptions"]["causal"], "NO_CERTIFIED_MAP")
        self.assertIn("correction-class-specific", entry["claim_boundary"])
        self.assertIn("activate either cyclic Bridge 2", entry["claim_boundary"])

    def test_smooth_extension_import_requires_complete_pass_receipt(self):
        payload = {
            "result_id": "EINSTEIN_MAXWELL_WEYL_GLOBAL_EXTRA_SMOOTH_SECULAR_SECOND_ORDER",
            "lifecycle_state": "CERTIFIED",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            "scope": {"background": "compact magnetically supported Plebanski-Hacyan product", "k": 0},
            "classification": {
                "complete_nonzero_extra_common_zero_orbit_covered": True,
                "complete_quadratic_channel_ledger": True,
                "all_nonstabilizer_smooth_secular_cokernels_zero": True,
                "smooth_exponential_polynomial_second_order_correction_exists": True,
                "coefficient_explicit_correction_printed": False,
                "bounded_correction_exists": False,
                "causal_retarded_map_certified": False,
                "all_orders_integrability": False,
            },
            "correction_classes": {
                "bounded_or_finite_quasiperiodic": "OBSTRUCTED",
                "smooth_exponential_polynomial": "CERTIFIED",
                "causal_or_retarded": "NO_CERTIFIED_MAP",
            },
            "verification_receipt": {"tier_1": {"status": "PENDING"}},
            "verification_commands": [
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_global_extra_smooth_secular_second_order.py"
            ],
            "source_manifest": {path: "unused-in-structural-test" for path in atlas.SMOOTH_REQUIRED_MANIFEST_PATHS},
        }
        self.assertFalse(atlas.smooth_extension_payload_ready(payload, verify_manifest=False))
        payload["verification_receipt"]["tier_1"]["status"] = "PASS"
        self.assertTrue(atlas.smooth_extension_payload_ready(payload, verify_manifest=False))
        self.assertFalse(atlas.smooth_extension_payload_ready(payload, verify_manifest=True))
        payload["classification"]["bounded_correction_exists"] = True
        self.assertFalse(atlas.smooth_extension_payload_ready(payload, verify_manifest=False))

    def test_exceptional_solution_cofiber_does_not_activate_bridge_two(self):
        entry = next(item for item in atlas.build()["entries"] if "exceptional_ell1_k0_solution_cofiber" in item["id"])
        self.assertEqual(entry["descriptions"]["symplectic"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["dispersion"]["status"], "CERTIFIED")
        self.assertIn("natural support-local minimal chain map", entry["claim_boundary"])
        self.assertIn("does not activate Bridge 2", entry["claim_boundary"])

    def test_nonzero_k_exceptional_cofiber_is_a_linear_handoff_only(self):
        entry = next(item for item in atlas.build()["entries"] if "exceptional_ell1_nonzero_k_solution_cofiber" in item["id"])
        self.assertEqual(entry["descriptions"]["symplectic"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["dispersion"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["second_order"]["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("does not", entry["claim_boundary"])
        self.assertIn("activate Bridge 2", entry["claim_boundary"])

    def test_product_relative_linfinity_receiver_is_fail_closed(self):
        entry = next(item for item in atlas.build()["entries"] if "relative_linfinity_through_arity_three_preflight" in item["id"])
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["descriptions"]["symplectic"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["dispersion"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["second_order"]["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "OBSTRUCTED")
        self.assertIn("obstructed at arity two", entry["claim_boundary"])
        self.assertIn("no f2 extends", entry["claim_boundary"])
        self.assertIn("Taub-zero", entry["claim_boundary"])
        self.assertIn("remains OPEN or NO_CERTIFIED_MAP", entry["claim_boundary"])
        self.assertIn("same-background", entry["claim_boundary"])
        self.assertIn("all Berger tensors remain ineligible", entry["claim_boundary"])
        self.assertIn("NONCYCLIC_THREE_FORM", entry["claim_boundary"])
        self.assertIn("both complete same-background", entry["claim_boundary"])
        self.assertIn("q4 is not authorized", entry["claim_boundary"])

    def test_generic_standard_pairing_cyclic_obstruction_is_scoped(self):
        entry = next(item for item in atlas.build()["entries"] if "generic_standard_pairing_cyclic_map_inertia_obstruction" in item["id"])
        self.assertEqual(entry["descriptions"]["symplectic"], "OBSTRUCTED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "NO_CERTIFIED_MAP")
        self.assertEqual(entry["mode_data"]["lee_wald"]["status"], "OBSTRUCTED")
        self.assertIn("Every real-structure-preserving", entry["claim_boundary"])
        self.assertIn("noncyclic off-shell triangle", entry["claim_boundary"])
        self.assertIn("remain OPEN", entry["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
