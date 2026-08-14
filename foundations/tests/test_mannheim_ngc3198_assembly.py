from __future__ import annotations

import copy
import unittest

from foundations.build_mannheim_ngc3198_assembly import build, canonical_digest
from foundations.check_mannheim_ngc3198_assembly import check
from foundations.verify_mannheim_ngc3198_assembly import verify


class MannheimNgc3198AssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = build()

    def test_endpoint_is_coarse_reproduction_not_empirical_completion(self):
        numeric = self.value["numerical_reproduction_rail"]
        disposition = self.value["assembly_disposition"]
        self.assertTrue(numeric["gate_passed"])
        self.assertLess(numeric["endpoint_relative_velocity_residual"], 0.05)
        self.assertTrue(disposition["formula_endpoint_coarsely_reproduced"])
        self.assertFalse(disposition["complete_within_declared_scope"])
        self.assertFalse(disposition["empirically_supported_within_declared_scope"])

    def test_sparc_pass_and_failure_remain_separate(self):
        empirical = self.value["empirical_comparison_rail"]
        self.assertEqual(empirical["points_inside_published_radius"], 39)
        self.assertTrue(empirical["coarse_rms_gate_passed"])
        self.assertFalse(empirical["random_error_reduced_chi2_gate_passed"])
        self.assertGreater(empirical["reduced_chi_squared_no_refit"], 2.0)

    def test_no_refit_or_matter_resolution_is_claimed(self):
        flags = self.value["claim_flags"]
        self.assertFalse(flags["mass_to_light_ratio_refit"])
        self.assertFalse(flags["original_fit_likelihood_reproduced"])
        self.assertFalse(flags["matter_coupling_dispute_resolved"])
        self.assertFalse(flags["galaxy_population_claim_assessed"])

    def test_applicability_masks_quantum_obligations(self):
        by_id = {item["obligation"]: item["status"] for item in self.value["applicability_mask"]}
        self.assertEqual({key for key, status in by_id.items() if status == "IN_SCOPE_REQUIRED"}, {"KINEMATICS_OBSERVABLES", "INTERACTION_CONSTRUCTION", "RECONSTRUCTION_LIMITS"})
        for key in ("ANOMALY_CLASSIFICATION", "RENORMALIZED_PRODUCTS", "QME_RESTORATION", "RESIDUAL_QUANTUM_TRANSFER"):
            self.assertEqual(by_id[key], "OUT_OF_SCOPE")

    def test_false_empirical_promotion_fails(self):
        tampered = copy.deepcopy(self.value)
        tampered["assembly_disposition"]["empirically_supported_within_declared_scope"] = True
        tampered["canonical_digest"] = canonical_digest(tampered)
        self.assertIn("fail-closed disposition", check(tampered)[0])

    def test_independent_verifier(self):
        self.assertEqual(verify()[0], [])


if __name__ == "__main__":
    unittest.main()
