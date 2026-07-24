"""Scoped tests for the centered phase-factored initializer."""
from __future__ import annotations

import json
import unittest

from .centered_initializer import RUN, compute


class CenteredInitializerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = compute()

    def test_all_panel_values_exclude_zero(self) -> None:
        self.assertTrue(all(
            row["base"]["value_ball_excludes_zero"]
            for row in self.document["rows"]
        ))

    def test_all_panel_sensitivities_materialized(self) -> None:
        self.assertTrue(all(
            "eta_ball" in row["tau_sensitivity"]
            and "xi_ball" in row["omega_sensitivity"]
            for row in self.document["rows"]
        ))

    def test_first_segment_passes_and_full_rail_fails_closed(self) -> None:
        self.assertTrue(all(
            row["first_projective_segment"]["certified"]
            for row in self.document["rows"]
        ))
        self.assertTrue(all(
            row["q_only_continuation_preflight"]["terminal_status"]
            == "NONPOSITIVE_MAJORANT_DISCRIMINANT"
            for row in self.document["rows"]
        ))

    def test_materialized_run_schema(self) -> None:
        run = json.loads(RUN.read_text())
        self.assertEqual(run["panel_count"], 16)


if __name__ == "__main__":
    unittest.main()
