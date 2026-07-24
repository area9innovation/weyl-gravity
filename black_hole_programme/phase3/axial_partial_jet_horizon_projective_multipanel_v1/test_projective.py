"""Scoped tests for the bounded projective transport attempts."""
from __future__ import annotations

import json
import unittest

from . import produce, verify


class ProjectiveShortfallTest(unittest.TestCase):
    def test_fixed_pivot_refusal(self) -> None:
        doc = json.loads(produce.OUTPUT.read_text())
        fixed = doc["fixed_full_pivot_attempt"]
        self.assertEqual(fixed["gate"], "pivot_solve")
        self.assertEqual((fixed["shell"], fixed["panel"]), (0, 5))
        self.assertEqual(fixed["refusal_code_name"], "IVTAY_KRAWCZYK_UNCERTIFIED")

    def test_midpoint_timeout_is_fail_closed(self) -> None:
        doc = json.loads(produce.OUTPUT.read_text())
        self.assertEqual(doc["midpoint_lohner_attempt"]["run_exit"], 124)
        self.assertFalse(any(doc["claim_flags"].values()))

    def test_independent_verifier(self) -> None:
        verify.verify()


if __name__ == "__main__":
    unittest.main()
