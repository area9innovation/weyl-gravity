#!/usr/bin/env python3
"""Regression and adversarial mutation tests for the Paper 15 claim map."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "paper/generate_15_phase1_synthesis_claim_map.py"
VERIFIER = ROOT / "paper/verify_15_phase1_synthesis_claim_map.py"
CLAIM_MAP = ROOT / "paper/15-four-level-ghost-classification-phase1-synthesis-claim-map.json"


class Paper15ClaimMapTest(unittest.TestCase):
    def test_generator_and_verifier(self) -> None:
        subprocess.run(["python3", str(GENERATOR)], cwd=ROOT, check=True)
        subprocess.run(["python3", str(VERIFIER)], cwd=ROOT, check=True)

    def test_lifecycle_mutation_is_rejected(self) -> None:
        payload = json.loads(CLAIM_MAP.read_text())
        first = payload["theorem_cards"][0]
        claim_id = first["claim_ids"][0]
        first["lifecycles"][claim_id] = "PROMOTED_WITHOUT_EVIDENCE"
        with tempfile.TemporaryDirectory() as directory:
            mutated = Path(directory) / "mutated.json"
            mutated.write_text(json.dumps(payload))
            completed = subprocess.run(
                ["python3", str(VERIFIER), "--claim-map", str(mutated)],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("lifecycle drift", completed.stderr + completed.stdout)


if __name__ == "__main__":
    unittest.main()
