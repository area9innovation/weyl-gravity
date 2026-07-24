"""Scoped tests for the chunk-03 bounded runtime refusal."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from .verify import verify


HERE = Path(__file__).resolve().parent


class Chunk03Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((HERE / "certificate.json").read_text())

    def test_independent_verifier(self) -> None:
        verify(self.document)

    def test_runtime_is_terminal_gate(self) -> None:
        adaptive = self.document["adaptive_chunk"]
        self.assertEqual(adaptive["terminal_gate"], "RUNTIME_TIMEOUT")
        self.assertEqual(adaptive["run_exit_code"], 124)

    def test_no_checkpoint(self) -> None:
        self.assertFalse((HERE / "checkpoint.json").exists())

    def test_direct_gate_fail_closed(self) -> None:
        self.assertFalse(
            self.document["claim_flags"]["boundary_direct_gate_certified"]
        )

    def test_downstream_claims_false(self) -> None:
        flags = self.document["claim_flags"]
        self.assertFalse(flags["full_Bplus4_at_r4_certified"])
        self.assertFalse(flags["T_plus_certified"])
        self.assertFalse(flags["stokes_or_scattering_certified"])


if __name__ == "__main__":
    unittest.main()
