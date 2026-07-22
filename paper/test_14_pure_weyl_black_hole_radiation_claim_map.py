#!/usr/bin/env python3
"""Regression and adversarial tests for corrected Paper 14."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "paper/generate_14_pure_weyl_black_hole_radiation_claim_map.py"
VERIFIER = ROOT / "paper/verify_14_pure_weyl_black_hole_radiation_claim_map.py"
PAPER = ROOT / "paper/14-pure-weyl-black-hole-radiation.tex"
CLAIM_MAP = ROOT / "paper/14-pure-weyl-black-hole-radiation-claim-map.json"


class Paper14CorrectedClaimMapTest(unittest.TestCase):
    def run_verifier(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(VERIFIER), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def mutated_paper(self, old: str, new: str, directory: str) -> tuple[Path, Path]:
        text = PAPER.read_text()
        self.assertIn(old, text)
        paper = Path(directory) / "paper.tex"
        paper.write_text(text.replace(old, new, 1))
        payload = json.loads(CLAIM_MAP.read_text())
        payload["paper_sha256"] = hashlib.sha256(paper.read_bytes()).hexdigest()
        claim_map = Path(directory) / "claim-map.json"
        claim_map.write_text(json.dumps(payload))
        return paper, claim_map

    def test_generator_check_and_verifier(self) -> None:
        subprocess.run(["python3", str(GENERATOR), "--check"], cwd=ROOT, check=True)
        subprocess.run(["python3", str(VERIFIER)], cwd=ROOT, check=True)

    def test_selection_promotion_is_rejected(self) -> None:
        payload = json.loads(CLAIM_MAP.read_text())
        payload["certified_scope"]["formal_radial_einstein_only_selection"] = True
        with tempfile.TemporaryDirectory() as directory:
            claim_map = Path(directory) / "mutated.json"
            claim_map.write_text(json.dumps(payload))
            completed = self.run_verifier("--claim-map", str(claim_map))
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("formal_radial_einstein_only_selection", completed.stdout + completed.stderr)

    def test_wrong_q21_fixture_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paper, claim_map = self.mutated_paper(
                "Q_{21}(6,9/25)=", "Q_{21}(6,81/625)=", directory
            )
            completed = self.run_verifier(
                "--paper", str(paper), "--claim-map", str(claim_map)
            )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Q_{21}(6,9/25)=", completed.stdout + completed.stderr)

    def test_legacy_selection_sentence_is_rejected(self) -> None:
        marker = "This is an exact formal asymptotic coefficient audit."
        old_sentence = (
            "The finite-slice-norm asymptotic class of the sphere-integrated "
            "presymplectic density contains exactly the Einstein sector."
        )
        with tempfile.TemporaryDirectory() as directory:
            paper, claim_map = self.mutated_paper(
                marker, marker + "\n" + old_sentence, directory
            )
            completed = self.run_verifier(
                "--paper", str(paper), "--claim-map", str(claim_map)
            )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("superseded or overbroad", completed.stdout + completed.stderr)

    def test_unrestricted_representative_independence_is_rejected(self) -> None:
        payload = json.loads(CLAIM_MAP.read_text())
        payload["certified_scope"]["axial_l2_unrestricted_representative_independence"] = True
        with tempfile.TemporaryDirectory() as directory:
            claim_map = Path(directory) / "mutated.json"
            claim_map.write_text(json.dumps(payload))
            completed = self.run_verifier("--claim-map", str(claim_map))
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("axial_l2_unrestricted_representative_independence", completed.stdout + completed.stderr)

    def test_global_matching_promotion_is_rejected(self) -> None:
        marker = "The next decisive map is global:"
        with tempfile.TemporaryDirectory() as directory:
            paper, claim_map = self.mutated_paper(
                marker,
                "A global horizon-to-infinity solution is established.\n" + marker,
                directory,
            )
            completed = self.run_verifier(
                "--paper", str(paper), "--claim-map", str(claim_map)
            )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("superseded or overbroad", completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
