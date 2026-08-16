from __future__ import annotations

import copy
import json
import os
import subprocess
import tempfile
import unittest
from fractions import Fraction

from reverse_physics import bt_euclidean_high_contrast_flow_closure as producer


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_euclidean_high_contrast_flow_closure.py"
)


class HighContrastFlowClosureTests(unittest.TestCase):
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
        self.assertTrue(self.certificate["checks"]["ok"])
        self.assertEqual(self.certificate["checks"]["passed"], 9)

    def test_all_finite_amplitude_fixture_checks_pass(self) -> None:
        for row in self.certificate["exact_fixtures"]:
            self.assertTrue(all(row["checks"].values()))
            flow_mass = Fraction(
                row["norms"]["flow_mass"]["numerator"],
                row["norms"]["flow_mass"]["denominator"],
            )
            divergence_l1 = Fraction(
                row["norms"]["divergence_l1"]["numerator"],
                row["norms"]["divergence_l1"]["denominator"],
            )
            self.assertGreaterEqual(
                (row["vertex_count"] - 1) * divergence_l1,
                2 * flow_mass,
            )

    def test_exact_torus_tail_constant(self) -> None:
        self.assertEqual(
            Fraction(4 * Fraction(16176, 25), 192**2),
            Fraction(337, 4800),
        )

    def test_unmodified_certificate_passes_independent_verifier(self) -> None:
        result = self.verify(self.certificate)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_mutated_predecessor_hash_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["provenance"]["inputs"][1]["sha256"] = "0" * 64
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_weakened_threshold_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["finite_amplitude_theorem"]["threshold"] = "W>=2*q^2*N*(N-1)"
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_mutated_edge_error_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["exact_fixtures"][1]["edges"][0]["error_current"]["numerator"] += 1
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_mutated_flow_divergence_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["exact_fixtures"][2]["main_flow_divergence"][0]["numerator"] += 1
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_false_polynomial_sector_closure_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["research_disposition"]["polynomial_contrast_dense_multiscale_sector"] = "PROVED"
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_false_h_minus_one_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["research_disposition"]["actual_interacting_h_minus_one"] = "PROVED"
        self.assertNotEqual(self.verify(mutated).returncode, 0)


if __name__ == "__main__":
    unittest.main()
