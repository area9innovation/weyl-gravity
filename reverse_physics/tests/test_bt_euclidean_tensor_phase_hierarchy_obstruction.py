"""Tests for the BT tensor-phase hierarchy obstruction."""

from __future__ import annotations

import copy
import json
import os
import subprocess
import tempfile
import unittest
from fractions import Fraction

from reverse_physics import bt_euclidean_tensor_phase_hierarchy_obstruction as producer


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VERIFIER = os.path.join(
    ROOT,
    "reverse_physics/verify_bt_euclidean_tensor_phase_hierarchy_obstruction.py",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


class TensorPhaseHierarchyObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = producer.build()

    def verify(self, certificate: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(certificate, handle)
            path = handle.name
        try:
            return subprocess.run(
                ["python3", VERIFIER, "--certificate", path],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        finally:
            os.unlink(path)

    def test_certificate_self_check(self) -> None:
        checks = self.certificate["checks"]
        self.assertTrue(checks["ok"])
        self.assertEqual(checks["passed"], 10)
        self.assertEqual(checks["total"], 10)

    def test_exact_tensor_quotients(self) -> None:
        for fixture in self.certificate["exact_fixtures"]:
            for row in fixture["tensor_rows"]:
                quotient = decode(row["gradient_norm_squared"]) / decode(
                    row["residual_norm_squared"]
                )
                self.assertEqual(quotient, decode(row["quotient"]))
                self.assertEqual(
                    quotient * fixture["member"] ** 6,
                    decode(row["quotient_scaled_by_m6"]),
                )

    def test_all_tensor_rows_clear_analytic_floor(self) -> None:
        for fixture in self.certificate["exact_fixtures"]:
            for row in fixture["tensor_rows"]:
                self.assertGreaterEqual(
                    decode(row["quotient"]), decode(row["analytic_lower_bound"])
                )

    def test_unmodified_certificate_passes_independent_verifier(self) -> None:
        result = self.verify(self.certificate)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_mutated_predecessor_hash_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_mutated_exact_norm_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["exact_fixtures"][0]["tensor_rows"][0][
            "gradient_norm_squared"
        ]["numerator"] += 1
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_mutated_tensor_identity_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["tensor_identity"]["torus_gradient"] = "g=sum_a h_a"
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_mutated_analytic_floor_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["same_sign_bulk_theorem"]["quotient"] = "Q_k>=m^-5"
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_false_all_field_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["research_disposition"]["all_field_torus_scaled_PL"] = "PROVED"
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_lorentzian_tag_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["dependency_tags"].append("LORENTZIAN-CAUSAL")
        self.assertNotEqual(self.verify(mutated).returncode, 0)


if __name__ == "__main__":
    unittest.main()
