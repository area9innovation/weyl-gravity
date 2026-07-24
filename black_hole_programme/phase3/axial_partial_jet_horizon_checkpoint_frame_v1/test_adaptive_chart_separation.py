from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from . import adaptive_chart_separation as audit

HERE = Path(__file__).resolve().parent


class AdaptiveChartSeparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(
            (HERE / "adaptive-chart-separation-run.json").read_text()
        )

    def test_zero_vector_belongs_to_cartesian_enclosure(self) -> None:
        enclosure = self.data["terminal_raw_enclosure"]
        self.assertTrue(enclosure["state_finite"])
        self.assertTrue(all(enclosure["base_component_zero_membership"]))
        self.assertTrue(enclosure["zero_vector_in_cartesian_base_enclosure"])

    def test_midpoint_derived_gl_chart_fails_full_ball_gate(self) -> None:
        chart = self.data["midpoint_adaptive_chart"]
        self.assertEqual(chart["determinant"], "1")
        self.assertTrue(chart["candidate"]["midpoint_modulus_nonzero"])
        self.assertFalse(chart["candidate"]["excludes_zero"])
        self.assertFalse(chart["certified"])

    def test_midpoint_only_mutant_is_killed(self) -> None:
        mutation = self.data["mutation_witness"]
        self.assertTrue(mutation["mutant_accepts"])
        self.assertFalse(mutation["correct_full_ball_gate_accepts"])
        self.assertTrue(mutation["mutation_killed"])

    def test_enclosure_content_mutation_is_detected(self) -> None:
        enclosure = self.data["terminal_raw_enclosure"]
        payload = copy.deepcopy(enclosure["payload"])
        payload["base"][0]["ball"] = "0"
        self.assertNotEqual(audit.canonical_hash(payload), enclosure["content_sha256"])

    def test_recompute(self) -> None:
        self.assertEqual(audit.compute(), self.data)


if __name__ == "__main__":
    unittest.main()
