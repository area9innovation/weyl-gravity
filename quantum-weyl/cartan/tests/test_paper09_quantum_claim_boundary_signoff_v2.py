"""Tests for the post-freeze Paper IX quantum signoff."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "paper09_quantum_claim_boundary_signoff_v2.py"
SPEC = importlib.util.spec_from_file_location("paper09_quantum_signoff_v2", PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PostFreezeSignoffTests(unittest.TestCase):
    def test_only_classical_k_is_accepted(self) -> None:
        value = MODULE.build()
        flags = value["theorem_flags"]
        self.assertTrue(flags["PAPER09_FROZEN_CLASSICAL_K_CARTAN_ACCEPTED"])
        self.assertTrue(flags["PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF_V2"])
        for key, flag in flags.items():
            if key not in {
                "PAPER09_FROZEN_CLASSICAL_K_CARTAN_ACCEPTED",
                "PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF_V2",
            }:
                self.assertFalse(flag, key)

    def test_frozen_snapshot_and_maxwell_exclusion(self) -> None:
        value = MODULE.build()
        self.assertTrue(value["freeze_snapshot"]["theorem_frozen"])
        self.assertFalse(value["approved_classical_scope"]["maxwell_in_main_theorem"])
        self.assertEqual(value["quantum_lifecycle"]["QME_RESTORED"], "NOT_REACHED")


if __name__ == "__main__":
    unittest.main()
