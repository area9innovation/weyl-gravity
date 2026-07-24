#!/usr/bin/env python3
"""Tests for the fail-closed correlated multipanel throughput result."""
from __future__ import annotations

import json
import unittest

from . import correlated_multipanel_throughput_shortfall as audit


class CorrelatedMultipanelThroughputShortfallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = audit.compute()

    def test_no_multipanel_output_exists(self) -> None:
        self.assertFalse(audit.ABSENT_RUN.exists())
        self.assertFalse(
            self.result["observed_attempt"]["run_artifact_written"]
        )

    def test_timeout_is_not_pass(self) -> None:
        self.assertEqual(
            self.result["observed_attempt"]["termination"],
            "FAST_RAIL_TIMEOUT",
        )
        self.assertFalse(self.result["claim_flags"]["timeout_treated_as_pass"])

    def test_one_step_resume_model_is_retained(self) -> None:
        one_step = json.loads(audit.ONE_STEP.read_text())
        resume = self.result["split_contract"]["resume_source"]
        self.assertEqual(
            resume["content_sha256"],
            one_step["successor_model"]["content_sha256"],
        )

    def test_split_is_kernel_then_one_step(self) -> None:
        contract = self.result["split_contract"]
        self.assertEqual(
            contract["checkpoint_stage"]["work_unit"],
            "exactly one radial step per invocation",
        )
        self.assertEqual(contract["driver_stage"]["time_budget_seconds"], 60)

    def test_no_cartesian_removal_claim(self) -> None:
        flags = self.result["claim_flags"]
        self.assertFalse(flags["multipanel_result_certified"])
        self.assertFalse(flags["former_cartesian_obstruction_crossed"])
        self.assertFalse(flags["cartesian_wrapping_obstruction_removed"])


if __name__ == "__main__":
    unittest.main()
