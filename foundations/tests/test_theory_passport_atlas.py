from __future__ import annotations

import copy
import unittest

from foundations.build_theory_passport_atlas import build, canonical_digest
from foundations.check_theory_passport_atlas import check
from foundations.verify_theory_passport_atlas import verify


class TheoryPassportAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = build()

    def test_eight_fixed_six_stage_passports(self):
        self.assertEqual(len(self.value["passports"]), 8)
        self.assertTrue(all(len(item["stages"]) == 6 and len(item["joins"]) == 5 for item in self.value["passports"]))

    def test_empirical_outcomes_remain_scoped(self):
        summary = self.value["atlas_summary"]
        self.assertEqual(summary["reaches_empirical_benchmark"], 4)
        self.assertEqual(summary["passes_declared_empirical_gate"], 2)
        self.assertEqual(summary["fails_declared_empirical_gate"], 2)
        self.assertEqual(summary["complete_theories"], 0)

    def test_stage_local_result_does_not_hide_earlier_blocker(self):
        weyl = next(item for item in self.value["passports"] if item["id"] == "PURE_WEYL_BV_CAUSAL")
        self.assertEqual(weyl["stages"][1]["status"], "PARTIAL")
        self.assertEqual(weyl["stages"][2]["status"], "ESTABLISHED_EXACT")
        self.assertEqual(weyl["journey_summary"]["first_blocker_or_failure"], "STATE_SPACE")
        self.assertEqual(weyl["journey_summary"]["furthest_stage_with_evidence"], "DYNAMICS")

    def test_false_complete_theory_promotion_fails(self):
        tampered = copy.deepcopy(self.value)
        tampered["passports"][0]["journey_summary"]["complete_theory"] = True
        tampered["canonical_digest"] = canonical_digest(tampered)
        self.assertIn("derived journey summary STANDARD_GR_CASSINI", check(tampered)[0])

    def test_status_promotion_fails_even_with_recomputed_digest(self):
        tampered = copy.deepcopy(self.value)
        bt = next(item for item in tampered["passports"] if item["id"] == "BATEMAN_TUROK_EUCLIDEAN")
        bt["stages"][2]["status"] = "ESTABLISHED_EXACT"
        tampered["canonical_digest"] = canonical_digest(tampered)
        self.assertIn("independent status contract BATEMAN_TUROK_EUCLIDEAN", check(tampered)[0])

    def test_source_assertion_mutation_fails(self):
        tampered = copy.deepcopy(self.value)
        tampered["passports"][0]["stages"][0]["source_assertions"][0]["expected"] = "A_DIFFERENT_MODEL"
        tampered["canonical_digest"] = canonical_digest(tampered)
        self.assertTrue(any("source assertion drift STANDARD_GR_CASSINI" in item for item in check(tampered)[0]))

    def test_independent_verifier(self):
        self.assertEqual(verify()[0], [])


if __name__ == "__main__":
    unittest.main()
