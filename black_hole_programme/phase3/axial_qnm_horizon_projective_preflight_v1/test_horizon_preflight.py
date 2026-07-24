"""Scoped tests for the horizon projective preflight."""
from __future__ import annotations

import json
import unittest

from .horizon_preflight import RUN, compute


class HorizonPreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = compute()

    def test_moving_phase_and_seed(self) -> None:
        self.assertEqual(self.document["dot_lambda_H"], "0")
        self.assertTrue(all(
            row["coefficient_majorant_seed_gate"]
            for row in self.document["rows"]
        ))

    def test_transport_refuses_fail_closed(self) -> None:
        self.assertFalse(any(
            row["reached_r32"] for row in self.document["rows"]
        ))
        self.assertTrue(all(
            row["terminal"]["failure"] == "REFERENCE_Q_MAJORANT_DISCRIMINANT"
            for row in self.document["rows"]
        ))

    def test_no_mismatch_is_assembled(self) -> None:
        self.assertTrue(all(
            row["projective_mismatch"] is None
            for row in self.document["rows"]
        ))

    def test_materialized_run(self) -> None:
        self.assertEqual(json.loads(RUN.read_text())["panel_count"], 16)


if __name__ == "__main__":
    unittest.main()
