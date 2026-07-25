#!/usr/bin/env python3
"""Regression and adversarial tests for Paper 16."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "paper/generate_16_lorentzian_endpoint_nonselection_claim_map.py"
VERIFIER = ROOT / "paper/verify_16_lorentzian_endpoint_nonselection_claim_map.py"
PAPER = ROOT / "paper/16-lorentzian-endpoint-nonselection-pure-weyl.tex"
CLAIM_MAP = ROOT / "paper/16-lorentzian-endpoint-nonselection-pure-weyl-claim-map.json"
COVERAGE = ROOT / "planning/paper-coverage/phase4-paper16-endpoint-nonselection-overlay-2026-07-24.json"


class Paper16ClaimMapTests(unittest.TestCase):
    def run_verifier(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(VERIFIER), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def mutated_paper(
        self, insertion: str, directory: str
    ) -> tuple[Path, Path, Path]:
        paper = Path(directory) / "paper.tex"
        paper.write_text(PAPER.read_text() + "\n" + insertion + "\n")
        claims = json.loads(CLAIM_MAP.read_text())
        claims["paper_sha256"] = hashlib.sha256(paper.read_bytes()).hexdigest()
        claim_path = Path(directory) / "claim-map.json"
        claim_path.write_text(json.dumps(claims))
        coverage = json.loads(COVERAGE.read_text())
        coverage["claim_map"] = str(claim_path)
        coverage["claim_map_sha256"] = hashlib.sha256(
            claim_path.read_bytes()
        ).hexdigest()
        coverage_path = Path(directory) / "coverage.json"
        coverage_path.write_text(json.dumps(coverage))
        return paper, claim_path, coverage_path

    def assert_promotion_rejected(self, phrase: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paper, claims, coverage = self.mutated_paper(phrase, directory)
            result = self.run_verifier(
                "--paper",
                str(paper),
                "--claim-map",
                str(claims),
                "--coverage",
                str(coverage),
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("forbidden promotion", result.stdout + result.stderr)

    def test_generator_and_verifier(self) -> None:
        subprocess.run(["python3", str(GENERATOR), "--check"], cwd=ROOT, check=True)
        subprocess.run(["python3", str(VERIFIER)], cwd=ROOT, check=True)

    def test_green_resolvent_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the full Bach resolvent has a genuine second-order pole"
        )

    def test_all_frequency_tplus_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "T_+(\\omega)\\in GL(3,\\C) for every real \\(\\omega>0\\)"
        )

    def test_simultaneous_two_ended_mode_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "a non-Einstein separated mode is simultaneously "
            "future-horizon regular and purely outgoing"
        )

    def test_time_domain_promotion_rejected(self) -> None:
        self.assert_promotion_rejected("time-domain stability is established")

    def test_nonlocal_intertwiner_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "No nonlocal spin-one/spin-two intertwiner exists"
        )

    def test_euler_boundary_promotion_rejected(self) -> None:
        self.assert_promotion_rejected("the Euler term has no endpoint contribution")

    def test_pointwise_einstein_current_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the literal monochromatic current vanishes pointwise"
        )

    def test_polar_global_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the polar associated graded is globally certified"
        )

    def test_generic_radial_time_jordan_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "generic radial nonsplitting is a time-Jordan block"
        )

    def test_complete_polar_parent_gram_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the complete polar parent Gram is certified"
        )

    def test_all_ell_bach_nonsplitting_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the Bach self-extension is nonsplit for every \\(\\ell\\ge2\\)"
        )

    def test_complex_frequency_rw_simplicity_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the Regge--Wheeler differential module is simple at every complex frequency"
        )

    def test_schwarzschild_retarded_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the Schwarzschild retarded propagator is established"
        )

    def test_parent_overlap_shortcut_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the parent overlap equals the radial overlap without endpoint terms"
        )

    def test_physical_mass_crosswalk_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the intrinsic radial parameter \\(\\tau\\) equals the physical squared mass"
        )

    def test_canonical_causal_spectral_c_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the spectral fundamental symmetry is canonical and causal"
        )

    def test_full_six_state_commutant_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the full six-state commutant is the dual-number algebra"
        )

    def test_factorized_future_c_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the combined-future fundamental symmetry automatically factorizes"
        )

    def test_complete_quarter_lattice_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the complete complex reducibility locus is the quarter-integer lattice"
        )

    def test_claim_flag_promotion_rejected(self) -> None:
        claims = json.loads(CLAIM_MAP.read_text())
        claims["fail_closed_scope"]["green_resolvent_second_order_pole"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "claims.json"
            path.write_text(json.dumps(claims))
            result = self.run_verifier("--claim-map", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fail-closed promotion", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
