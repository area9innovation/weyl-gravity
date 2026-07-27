#!/usr/bin/env python3
"""Regression and adversarial tests for the consolidated Paper 17."""

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


class Paper17ConsolidatedClaimMapTests(unittest.TestCase):
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

    def assert_mutation_rejected(self, mutate, message: str) -> None:
        path = self.mutated_claims(mutate)
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, result.stdout + result.stderr)

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
        self.assert_mutation_rejected(
            lambda data: data["exact_identities"][
                "bach_cocycle_normal_form"
            ].update(
                {"q": "-I*(15*r + 13 + 12/r + 8/r**2)/(120*omega)"}
            ),
            "cocycle normal-form identity failed",
        )

    def test_mass_normalization_mutation_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda data: data["exact_identities"][
                "complete_massive_first_jet"
            ].update(
                {"fixed_frequency_tangent_relation": "m=I*omega*tau/2"}
            ),
            "complete massive first-jet declaration drift",
        )

    def test_physical_mass_crosswalk_demotion_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda data: data["claim_flags"].update(
                {"all_order_differentiated_massive_jost_crosswalk": False}
            ),
            "required scoped claim flag drift",
        )

    def test_physical_mass_velocity_demotion_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda data: data["exact_identities"][
                "complete_massive_first_jet"
            ].update({"physical_mass_velocity_certified": False}),
            "complete massive first-jet declaration drift",
        )

    def test_smith_mutation_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda data: data["exact_identities"]["smith_and_root"].update(
                {"defective_smith_type": [0, 1, 1]}
            ),
            "Smith/root declaration drift",
        )

    def test_green_rank_mutation_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda data: data["exact_identities"][
                "green_principal_coefficient"
            ].update({"rank": 2}),
            "Green-principal declaration drift",
        )

    def test_ecs_domain_demotion_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda data: data["exact_identities"][
                "green_principal_coefficient"
            ].update({"global_ecs_tangent_in_H1": False}),
            "Green-principal declaration drift",
        )

    def test_generalized_falloff_promotion_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda data: data["exact_identities"][
                "null_infinity_reconstruction"
            ].update({"carrier_standard_strain_falloff": True}),
            "generalized falloff promotion",
        )

    def test_source_trace_mutation_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda data: data["exact_identities"][
                "conserved_traceless_source"
            ].update({"traceless": False}),
            "conserved-source declaration drift",
        )

    def test_real_causal_source_promotion_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda data: data["exact_identities"][
                "conserved_traceless_source"
            ].update({"real_causal_temporally_compact": True}),
            "conserved-source declaration drift",
        )

    def test_outgoing_trace_mutation_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda data: data["exact_identities"][
                "outgoing_trace_bridge"
            ].update({"global_causal_trace": True}),
            "outgoing-trace declaration drift",
        )

    def test_causal_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the causal spacetime resolvent has a second-order pole"
        )

    def test_global_ringdown_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "a rigorous \\(t e^{i\\omega_nt}\\) ringdown term"
        )

    def test_specified_source_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "a specified astrophysical source excites the pole"
        )

    def test_higher_programme_section_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paper = Path(directory) / "paper.tex"
            paper.write_text(
                PAPER.read_text()
                + "\n\\section{Finite-time coherent forcing}\n"
            )
            claims = json.loads(CLAIMS.read_text())
            claims["paper_sha256"] = hashlib.sha256(paper.read_bytes()).hexdigest()
            claim_path = Path(directory) / "claims.json"
            claim_path.write_text(json.dumps(claims))
            result = self.run_verifier(
                "--paper", str(paper), "--claim-map", str(claim_path)
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("publication consolidation drift", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
