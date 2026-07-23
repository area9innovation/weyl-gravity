#!/usr/bin/env python3
"""Mutation tests for the frozen shortfall verifier."""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from black_hole_programme.phase3.axial_horizon_grassmann_mobius_to_r4.verify import (
    HERE,
    verify,
)


class VerifyShortfallTests(unittest.TestCase):
    def staged(self) -> Path:
        root = Path(tempfile.mkdtemp()) / "case"
        shutil.copytree(HERE, root, ignore=shutil.ignore_patterns("__pycache__"))
        self.addCleanup(shutil.rmtree, root.parent)
        return root

    def mutate(self, root: Path, relative: str, old: str, new: str) -> None:
        path = root / relative
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1))

    def test_frozen_package(self) -> None:
        self.assertTrue(verify()["verified"])

    def test_rejects_false_pass(self) -> None:
        root = self.staged()
        self.mutate(root, "sentinel_q00.log", "REFUSE amplitude-rank", "PASS")
        with self.assertRaises(AssertionError):
            verify(root)

    def test_rejects_stale_exit(self) -> None:
        root = self.staged()
        (root / "sentinel_q00.exit").write_text("127\n")
        with self.assertRaises(AssertionError):
            verify(root)

    def test_rejects_missing_centre_entry(self) -> None:
        root = self.staged()
        self.mutate(root, "sentinel_q00.log", "AC 0 0 ", "XX 0 0 ")
        with self.assertRaises(AssertionError):
            verify(root)

    def test_rejects_wrong_side_gauge(self) -> None:
        root = self.staged()
        self.mutate(
            root,
            "transport_c00.forge",
            "ivam_mul_checked(s.amplitude,hr_gauge())",
            "ivam_mul_checked(hr_gauge(),s.amplitude)",
        )
        with self.assertRaises(AssertionError):
            verify(root)

    def test_rejects_radial_policy_drift(self) -> None:
        root = self.staged()
        self.mutate(root, "transport_c00.forge", "while(panel<256)",
                    "while(panel<512)")
        with self.assertRaises(AssertionError):
            verify(root)

    def test_rejects_dropped_chart(self) -> None:
        root = self.staged()
        self.mutate(root, "transport_c00.forge", "while(c<20)", "while(c<19)")
        with self.assertRaises(AssertionError):
            verify(root)

    def test_rejects_unevaluated_child_artifact(self) -> None:
        root = self.staged()
        (root / "transport_c01.forge").write_text("// unevaluated\n")
        with self.assertRaises(AssertionError):
            verify(root)


if __name__ == "__main__":
    unittest.main()
