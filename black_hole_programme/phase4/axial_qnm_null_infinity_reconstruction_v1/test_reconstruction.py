#!/usr/bin/env python3
"""Mutation tests for the exact null-infinity reconstruction certificate."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


class ReconstructionTests(unittest.TestCase):
    def run_verifier(self, payload: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", dir=HERE, delete=False
        ) as handle:
            json.dump(payload, handle)
            path = Path(handle.name)
        try:
            return subprocess.run(
                [
                    sys.executable,
                    str(HERE / "verify.py"),
                    "--certificate",
                    str(path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        finally:
            path.unlink()

    def data(self) -> dict:
        return json.loads((HERE / "certificate.json").read_text())

    def test_certificate_passes(self) -> None:
        result = self.run_verifier(self.data())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_R_normalization_mutation_rejected(self) -> None:
        data = self.data()
        data["exact_asymptotic_reconstruction"]["R_metric"]["H0"] = (
            "-3*r**2/4-3*r/2+O(1)"
        )
        result = self.run_verifier(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("R metric declaration drift", result.stdout + result.stderr)

    def test_radiation_gauge_sign_mutation_rejected(self) -> None:
        data = self.data()
        data["radiation_gauge"]["E_bondi_shear"] = "2*I*X_AB/omega"
        result = self.run_verifier(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Bondi-shear declaration drift", result.stdout + result.stderr)

    def test_total_frequency_derivative_mutation_rejected(self) -> None:
        data = self.data()
        data["qnm_tangent"]["total_coulomb_exponent_derivative"] = "0"
        result = self.run_verifier(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Coulomb derivative declaration drift", result.stdout + result.stderr)

    def test_source_overlap_promotion_rejected(self) -> None:
        data = self.data()
        data["claim_flags"]["specified_physical_source_overlap_nonzero"] = True
        result = self.run_verifier(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("open claim was improperly promoted", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
