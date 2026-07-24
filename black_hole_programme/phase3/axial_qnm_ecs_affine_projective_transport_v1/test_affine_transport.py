"""Scoped tests for affine projective transport."""
from __future__ import annotations

import json
import unittest

from .affine_transport import RUN, compute


class AffineTransportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = compute()

    def test_all_panels_reach_r32(self) -> None:
        self.assertTrue(all(
            row["match_radius_certified"] for row in self.document["rows"]
        ))

    def test_all_sensitivities_present_at_r32(self) -> None:
        self.assertTrue(all(
            row["match_snapshot"]["eta_remainder_radius"]
            and row["match_snapshot"]["xi_remainder_radius"]
            for row in self.document["rows"]
        ))

    def test_inward_failure_is_fail_closed(self) -> None:
        self.assertTrue(all(
            row["first_terminal_obstruction"]["failure"]
            == "AFFINE_Q_REMAINDER_DISCRIMINANT"
            for row in self.document["rows"]
        ))

    def test_materialized_run(self) -> None:
        self.assertEqual(json.loads(RUN.read_text())["panel_count"], 16)


if __name__ == "__main__":
    unittest.main()
