#!/usr/bin/env python3

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class Phase1ClosureTest(unittest.TestCase):
    def test_generated_outputs_and_independent_verifier(self) -> None:
        subprocess.run(["python3", "planning/paper-coverage/generate_phase1_closure.py", "--check"], cwd=ROOT, check=True)
        subprocess.run(["python3", "planning/paper-coverage/verify_phase1_closure.py"], cwd=ROOT, check=True)

    def test_no_candidate_or_universal_no_go_promotion(self) -> None:
        ledger = json.loads((ROOT / "reports/phase1-closure-claims-ledger-2026-07-22.json").read_text())
        self.assertFalse(ledger["decision"]["robust_phase2_candidate_selected"])
        self.assertTrue(any("universal no-go" in item for item in ledger["does_not_establish"]))


if __name__ == "__main__":
    unittest.main()
