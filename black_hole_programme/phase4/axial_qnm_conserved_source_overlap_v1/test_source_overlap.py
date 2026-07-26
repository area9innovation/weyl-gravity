#!/usr/bin/env python3
"""Mutation tests for the conserved odd-source certificate."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


class ConservedSourceTests(unittest.TestCase):
    def data(self) -> dict:
        return json.loads((HERE / "certificate.json").read_text())

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

    def test_certificate_passes(self) -> None:
        result = self.run_verifier(self.data())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_source_sign_mutation_rejected(self) -> None:
        data = self.data()
        data["source_realization"]["P_r_covariant"] = (
            "-mu*F/(2*I*omega*r*f)"
        )
        result = self.run_verifier(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source declaration drift", result.stdout + result.stderr)

    def test_conservation_mutation_rejected(self) -> None:
        data = self.data()
        data["source_realization"]["P_tensor"] = (
            "-d_r(r*F)/(2*I*omega)"
        )
        result = self.run_verifier(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source declaration drift", result.stdout + result.stderr)

    def test_point_particle_promotion_rejected(self) -> None:
        data = self.data()
        data["conformal_source_audit"][
            "massive_point_particle_directly_admissible"
        ] = True
        result = self.run_verifier(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "point-particle claim improperly promoted",
            result.stdout + result.stderr,
        )

    def test_plunge_overlap_promotion_rejected(self) -> None:
        data = self.data()
        data["claim_flags"]["specified_geodesic_plunge_overlap_nonzero"] = True
        result = self.run_verifier(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("open claim was improperly promoted", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
