"""Tests for the BT polynomial-contrast hierarchy obstruction."""

from __future__ import annotations

import copy
import json
import os
import subprocess
import tempfile
import unittest
from fractions import Fraction

from reverse_physics import bt_euclidean_polynomial_contrast_hierarchy_obstruction as producer


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VERIFIER = os.path.join(
    ROOT,
    "reverse_physics/verify_bt_euclidean_polynomial_contrast_hierarchy_obstruction.py",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


class PolynomialContrastHierarchyObstructionTests(unittest.TestCase):
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

    def test_exact_fixture_scaling_and_bounds(self) -> None:
        for row in self.certificate["exact_fixtures"]:
            member = row["member"]
            self.assertEqual(row["ramp_length"], member**4)
            self.assertEqual(row["cycle_volume"], 4 * member**4 + 2)
            self.assertEqual(decode(row["maximum_edge_ratio"]), member)
            self.assertLessEqual(
                decode(row["main_transport_coefficient"]),
                Fraction(160, member**6),
            )
            self.assertLessEqual(
                decode(row["full_gradient_quotient"]),
                Fraction(1960, member**6),
            )
            self.assertTrue(all(row["checks"].values()))

    def test_unmodified_certificate_passes_independent_verifier(self) -> None:
        result = self.verify(self.certificate)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_mutated_predecessor_hash_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_mutated_exact_gradient_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["exact_fixtures"][1]["gradient_norm_squared"]["numerator"] += 1
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_weakened_full_quotient_claim_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["full_gradient_theorem"]["quotient_upper_bound"] = (
            "for m>=8, ||g||_2^2/||r||_2^2<=1/m^6"
        )
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_false_four_torus_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["research_disposition"]["isotropic_four_torus_scaled_PL"] = "PROVED"
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_lorentzian_tag_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["dependency_tags"].append("LORENTZIAN-CAUSAL")
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_false_self_check_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["checks"]["details"]["four_torus_scaled_PL_remains_open"] = False
        mutated["checks"]["ok"] = False
        mutated["checks"]["passed"] = 9
        mutated["checks"]["failures"] = ["four_torus_scaled_PL_remains_open"]
        self.assertNotEqual(self.verify(mutated).returncode, 0)


if __name__ == "__main__":
    unittest.main()
