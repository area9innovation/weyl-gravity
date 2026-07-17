"""Tests for the Paper IX quantum claim-boundary signoff."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "paper09_quantum_claim_boundary_signoff.py"
SPEC = importlib.util.spec_from_file_location("paper09_quantum_signoff", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Paper09QuantumClaimBoundarySignoffTests(unittest.TestCase):
    def test_signoff_accepts_only_classical_k(self) -> None:
        cert = MODULE.build_certificate()
        flags = cert["theorem_flags"]
        self.assertTrue(flags["PAPER09_CLASSICAL_K_CARTAN_THROUGH_ARITY_THREE_ACCEPTED"])
        self.assertTrue(flags["PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF"])
        self.assertFalse(flags["PAPER09_AFFINE_D_CARTAN_ACCEPTED"])
        self.assertFalse(flags["PAPER09_HADAMARD_ACCEPTED"])
        self.assertFalse(flags["PAPER09_QME_ACCEPTED"])
        self.assertFalse(flags["PAPER09_ANOMALY_CANCELLATION_ACCEPTED"])
        self.assertFalse(flags["PAPER09_QUANTUM_PROMOTION_ACCEPTED"])

    def test_quantum_lifecycle_remains_blocked(self) -> None:
        lifecycle = MODULE.build_certificate()["quantum_lifecycle"]
        self.assertEqual(lifecycle["QME_RESTORED"], "NOT_REACHED")
        self.assertEqual(
            lifecycle["RESIDUAL_TRANSFERRED"], "BLOCKED_PENDING_QME_RESTORED"
        )


if __name__ == "__main__":
    unittest.main()
