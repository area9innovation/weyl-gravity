#!/usr/bin/env python3
"""Mutation test for the fast paper manuscript-pin audit."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "verify_paper_manuscript_pins",
    HERE / "verify_paper_manuscript_pins.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class PaperPinAuditTests(unittest.TestCase):
    def test_repository_pins_pass(self) -> None:
        self.assertGreater(len(MODULE.verify()), 0)

    def test_mutated_hash_is_rejected(self) -> None:
        original_paper = MODULE.PAPER
        original_root = MODULE.ROOT
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paper = root / "paper"
            paper.mkdir()
            manuscript = paper / "x.tex"
            manuscript.write_text("unchanged\n", encoding="utf-8")
            claim = {
                "manuscript": "paper/x.tex",
                "manuscript_sha256": "0" * 64,
            }
            (paper / "x-claim-map.json").write_text(
                json.dumps(claim),
                encoding="utf-8",
            )
            MODULE.ROOT = root
            MODULE.PAPER = paper
            try:
                with self.assertRaises(MODULE.PinDriftError):
                    MODULE.verify()
            finally:
                MODULE.ROOT = original_root
                MODULE.PAPER = original_paper


if __name__ == "__main__":
    unittest.main()
