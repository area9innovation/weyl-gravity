from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json"


class NonzeroKExceptionalCofiberTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text(encoding="utf-8"))

    def test_cofiber_and_pairing_are_certified(self) -> None:
        flags = self.value["classification"]
        self.assertTrue(flags["nonzero_k_exceptional_solution_cofiber_certified"])
        self.assertTrue(flags["action_pairing_nonradical_positive_on_extra_cofiber"])
        self.assertTrue(flags["standard_extra_action_orthogonality"])

    def test_covariant_glue_and_residual_endpoints_remain_open(self) -> None:
        flags = self.value["classification"]
        self.assertFalse(flags["single_covariant_support_local_map_reconstructed"])
        self.assertFalse(flags["finite_residual_endpoint_descent_certified"])

    def test_no_differential_inverse_is_used(self) -> None:
        self.assertTrue(self.value["classification"]["polynomial_representatives_without_differential_inverse"])


if __name__ == "__main__":
    unittest.main()
