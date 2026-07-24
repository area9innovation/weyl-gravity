"""Scoped tests for the regular partial-jet multipanel preflight."""
from __future__ import annotations

import json
import unittest

from . import produce, verify


class MultipanelPreflightTest(unittest.TestCase):
    def test_refusal_is_state_width_not_local_tail(self) -> None:
        doc = json.loads(produce.OUTPUT.read_text())
        parsed = doc["attempt"]["parsed"]
        self.assertEqual(parsed["status"], "REFUSED")
        self.assertEqual(parsed["refusal"]["gate"], "state_width")
        self.assertEqual(parsed["refusal"]["shell"], 6)
        self.assertEqual(parsed["refusal"]["panel"], 3)
        self.assertEqual(parsed["refusal"]["details"]["total_panels"], 27)
        self.assertTrue(parsed["refusal"]["details"]["overlap"])
        self.assertEqual(len(parsed["shell_records"]), 6)

    def test_claims_remain_fail_closed(self) -> None:
        doc = json.loads(produce.OUTPUT.read_text())
        self.assertFalse(any(doc["claim_flags"].values()))
        self.assertIn(
            "K_H or a tau-analytic endpoint normalizer identification",
            doc["does_not_establish"],
        )

    def test_independent_verifier(self) -> None:
        verify.verify()


if __name__ == "__main__":
    unittest.main()
