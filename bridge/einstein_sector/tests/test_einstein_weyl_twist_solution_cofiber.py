from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/einstein_weyl_twist_solution_cofiber.json"


class TwistSolutionCofiberTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text(encoding="utf-8"))

    def test_twist_primary_is_the_source_image(self) -> None:
        self.assertTrue(self.value["classification"]["twist_solution_cofiber_zero"])
        self.assertTrue(self.value["solution_map"]["target_twist_primary_equals_Einstein_image"])

    def test_pairing_and_open_gates_are_separate(self) -> None:
        self.assertEqual(self.value["action_derived_pairing"]["relative_endomorphism"], "-2*I")
        flags = self.value["classification"]
        self.assertFalse(flags["twist_offshell_chain_map_certified"])
        self.assertFalse(flags["global_moduli_or_final_residual_descent_certified"])


if __name__ == "__main__":
    unittest.main()
