#!/usr/bin/env python3
"""Regression and adversarial tests for Paper 17."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "paper/generate_17_pure_weyl_extension_claim_map.py"
VERIFIER = ROOT / "paper/verify_17_pure_weyl_extension_claim_map.py"
PAPER = ROOT / "paper/17-pure-weyl-schwarzschild-extension-structure.tex"
CLAIMS = ROOT / "paper/17-pure-weyl-schwarzschild-extension-structure-claim-map.json"


class Paper17ClaimMapTests(unittest.TestCase):
    def run_verifier(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(VERIFIER), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def mutated_claims(self, mutate) -> Path:
        data = json.loads(CLAIMS.read_text())
        mutate(data)
        handle = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        with handle:
            json.dump(data, handle)
        return Path(handle.name)

    def assert_promotion_rejected(self, phrase: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paper = Path(directory) / "paper.tex"
            paper.write_text(PAPER.read_text() + "\n" + phrase + "\n")
            claims = json.loads(CLAIMS.read_text())
            claims["paper_sha256"] = hashlib.sha256(paper.read_bytes()).hexdigest()
            claim_path = Path(directory) / "claims.json"
            claim_path.write_text(json.dumps(claims))
            result = self.run_verifier(
                "--paper", str(paper), "--claim-map", str(claim_path)
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("forbidden promotion", result.stdout + result.stderr)

    def test_generator_and_verifier(self) -> None:
        subprocess.run(["python3", str(GENERATOR), "--check"], cwd=ROOT, check=True)
        subprocess.run(["python3", str(VERIFIER)], cwd=ROOT, check=True)

    def test_cocycle_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["bach_cocycle_normal_form"].update(
                {"q": "-I*(15*r + 13 + 12/r + 8/r**2)/(120*omega)"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cocycle normal-form identity failed", result.stdout + result.stderr)

    def test_period_matrix_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"].update(
                {
                    "period_matrix": [
                        ["y1*y2", "y2**2"],
                        ["y1**2", "-y1*y2"],
                    ]
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("period matrix drift", result.stdout + result.stderr)

    def test_root_sign_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["generalized_root"].update(
                {"carrier_quotient": "a1/b0"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("root carrier quotient", result.stdout + result.stderr)

    def test_resonant_chain_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["resonant_evaluation"].update(
                {"resonance_velocity": "kappa"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("resonant evaluation chain", result.stdout + result.stderr)

    def test_mass_parameter_relation_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["critical_mass_jet"].update(
                {"parameter_relation": "m = -I*omega*tau/2"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("mass-jet declaration drift", result.stdout + result.stderr)

    def test_forced_gauge_slope_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["forced_gauge_asymptotic"].update(
                {"q_slope_at_infinity": "-I/(4*omega)"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("gauge slope identity failed", result.stdout + result.stderr)

    def test_boundary_gauge_factor_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["boundary_transgression"].update(
                {"commutator_gauge": "Qhat=Q(q)"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("boundary-transgression normalization", result.stdout + result.stderr)

    def test_causal_resolvent_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the causal spacetime resolvent has a second-order pole"
        )

    def test_ringdown_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "a rigorous \\(t e^{i\\omega_nt}\\) ringdown term"
        )

    def test_mass_identification_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the intrinsic radial parameter \\(\\tau\\) is the physical squared mass"
        )

    def test_physical_mass_slope_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the physical massive QNM slope is certified"
        )

    def test_endpoint_transgression_vanishing_rejected(self) -> None:
        self.assert_promotion_rejected("the endpoint transgression vanishes")

    def test_all_ell_nonsplitting_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the Bach self-extension is nonsplit for every \\(\\ell\\ge2\\)"
        )

    def test_fail_closed_claim_flag_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["fail_closed_scope"].update(
                {"causal_exterior_spacetime_resolvent": True}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fail-closed promotion", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
