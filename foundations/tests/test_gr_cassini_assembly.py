from __future__ import annotations

import copy
from fractions import Fraction
import unittest

from foundations.build_gr_cassini_assembly import build, canonical_digest
from foundations.check_gr_cassini_assembly import check
from foundations.verify_gr_cassini_assembly import verify


class GrCassiniAssemblyTests(unittest.TestCase):
    def test_bounded_end_to_end_assembly_is_complete(self):
        value = build()
        disposition = value["assembly_disposition"]
        self.assertTrue(disposition["complete_within_declared_scope"])
        self.assertTrue(disposition["empirically_supported_within_declared_scope"])
        self.assertFalse(disposition["complete_theory"])
        self.assertEqual(len(value["stages"]), 6)
        self.assertEqual(len(value["interfaces"]), 5)

    def test_exact_ppn_and_cassini_comparison(self):
        value = build()
        ppn = value["exact_prediction_rail"]["ppn_identification"]
        self.assertEqual(Fraction(**ppn["beta"]), 1)
        self.assertEqual(Fraction(**ppn["gamma"]), 1)
        empirical = value["empirical_comparison_rail"]
        self.assertTrue(empirical["prediction_inside_reported_band"])
        self.assertEqual(Fraction(**empirical["absolute_standardized_distance"]), Fraction(21, 23))

    def test_applicability_mask_prevents_quantum_overreach(self):
        value = build()
        required = {item["obligation"] for item in value["applicability_mask"] if item["status"] == "IN_SCOPE_REQUIRED"}
        self.assertEqual(required, {"KINEMATICS_OBSERVABLES", "INTERACTION_CONSTRUCTION", "RECONSTRUCTION_LIMITS"})
        quantum = {"COUNTERTERM_CLASSIFICATION", "ANOMALY_CLASSIFICATION", "RENORMALIZED_PRODUCTS", "QME_RESTORATION", "RESIDUAL_QUANTUM_TRANSFER"}
        status = {item["obligation"]: item["status"] for item in value["applicability_mask"]}
        self.assertTrue(all(status[item] == "OUT_OF_SCOPE" for item in quantum))

    def test_false_complete_theory_promotion_fails(self):
        value = copy.deepcopy(build())
        value["assembly_disposition"]["complete_theory"] = True
        value["canonical_digest"] = canonical_digest(value)
        self.assertIn("bounded assembly disposition", check(value)[0])

    def test_raw_data_promotion_fails(self):
        value = copy.deepcopy(build())
        value["claim_flags"]["raw_cassini_data_reanalysed"] = True
        value["canonical_digest"] = canonical_digest(value)
        self.assertIn("boundary flag raw_cassini_data_reanalysed", check(value)[0])

    def test_independent_verifier(self):
        self.assertEqual(verify()[0], [])


if __name__ == "__main__":
    unittest.main()
