from __future__ import annotations

import copy
from pathlib import Path
import unittest

from foundations.build_matrix_site_v2 import build_dataset
from foundations.theory_viability import build_assessment
from foundations.verify_theory_viability import digest, verify


ROOT = Path(__file__).resolve().parents[2]


class TheoryViabilityTests(unittest.TestCase):
    def test_three_rails_remain_separate(self):
        value = build_assessment(build_dataset())
        self.assertEqual(
            {item["id"]: item["status"] for item in value["global_rails"]},
            {
                "OBLIGATION_COVERAGE": "COMPUTED_FROM_ATLAS",
                "CROSS_OBLIGATION_COMPOSITION": "NOT_ASSESSED",
                "EMPIRICAL_AGREEMENT": "NOT_IN_CURRENT_SCHEMA",
            },
        )
        self.assertFalse(value["claim_flags"]["complete_observationally_valid_theory_identified"])

    def test_profiles_and_portfolios_close(self):
        value = build_assessment(build_dataset())
        self.assertEqual(len(value["profiles"]), 36)
        self.assertEqual(len(value["carrier_envelopes"]), 6)
        self.assertFalse(any(item["default_gate"]["complete_direct"] for item in value["profiles"]))
        self.assertEqual(sum(item["pareto_default"] for item in value["profiles"]), 2)

    def test_independent_verifier(self):
        self.assertEqual(verify()[0], [])

    def test_empirical_promotion_fails(self):
        value = build_assessment(build_dataset())
        value["claim_flags"]["empirical_agreement_assessed"] = True
        value["canonical_digest"] = digest(value)
        self.assertIn("fail-closed flag empirical_agreement_assessed", verify(value=value)[0])

    def test_source_change_changes_assessment(self):
        data = build_dataset()
        original = build_assessment(data)
        changed = copy.deepcopy(data)
        target = next(cell for cell in changed["cells"] if cell["foundation"] == "FINITE_DISCRETE" and cell["carrier"] == "FINITE_EXACT" and cell["obligation"] == "PHYSICAL_STATE_SELECTION")
        target["status"] = "LOCAL_RESULT"
        modified = build_assessment(changed)
        self.assertNotEqual(original["canonical_digest"], modified["canonical_digest"])
        promoted = next(item for item in modified["profiles"] if item["foundation"] == "FINITE_DISCRETE" and item["carrier"] == "FINITE_EXACT")
        self.assertTrue(promoted["default_gate"]["complete_direct"])


if __name__ == "__main__":
    unittest.main()
