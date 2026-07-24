"""Scoped tests for the kernel-serialization shortfall."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class JointKernelTimeoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cert = json.loads(
            (HERE / "joint-kernel-serialization-timeout-certificate.json"
             ).read_text()
        )
        cls.receipt = json.loads(
            (HERE / "joint-kernel-serialization-timeout-receipt.json"
             ).read_text()
        )

    def test_bounded_timeouts_are_not_passes(self) -> None:
        self.assertEqual(len(self.receipt["invocations"]), 2)
        for row in self.receipt["invocations"]:
            self.assertLess(row["wall_cap_seconds"], 60)
            self.assertEqual(row["status"], "TIMEOUT_NOT_PASS")

    def test_all_claims_closed(self) -> None:
        self.assertFalse(any(self.cert["claim_flags"].values()))

    def test_exact_resume_hash(self) -> None:
        self.assertEqual(
            self.cert["resume"]["model_content_sha256"],
            "48683b9103b786d0e39022a18b96f3e71a5e6ac0991e6f5bb1d45d074781f250",
        )


if __name__ == "__main__":
    unittest.main()
