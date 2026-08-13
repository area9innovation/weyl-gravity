from __future__ import annotations

import copy
import unittest

from foundations.build_bt_corner_born_interface import build, canonical_digest
from foundations.check_bt_corner_born_interface import check
from foundations.verify_bt_corner_born_interface import verify


class BtCornerBornInterfaceTests(unittest.TestCase):
    def test_interface_is_certified_and_conditional(self):
        value = build()
        self.assertEqual(value["interface"]["status"], "CERTIFIED")
        self.assertEqual(value["interface"]["relation"], "CONDITIONAL_BRIDGE")
        self.assertEqual(len(value["hypotheses"]), 5)
        self.assertEqual(value["predecessor_source_audit"]["verifier_status"], "PROVENANCE_DRIFT")
        self.assertFalse(value["claim_flags"]["legacy_semifinite_source_verifier_passed"])
        self.assertTrue(value["claim_flags"]["interface_independent_rederivation_passed"])

    def test_exact_probabilities(self):
        errors, summary = check(build())
        self.assertEqual(errors, [])
        self.assertEqual(summary["probabilities"], ["9/25", "16/25", "0"])
        self.assertEqual(summary["sum"], "1")

    def test_unconditional_promotion_fails(self):
        value = copy.deepcopy(build())
        value["claim_flags"]["arbitrary_krein_process_probability_rule"] = True
        value["canonical_digest"] = canonical_digest(value)
        self.assertIn("boundary flag arbitrary_krein_process_probability_rule", check(value)[0])

    def test_independent_verifier(self):
        self.assertEqual(verify()[0], [])


if __name__ == "__main__":
    unittest.main()
