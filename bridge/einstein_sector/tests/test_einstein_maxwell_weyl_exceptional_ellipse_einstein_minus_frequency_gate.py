from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_einstein_minus_frequency_gate.json"


class EinsteinMinusFrequencyGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text(encoding="utf-8"))

    def test_declared_fixture(self) -> None:
        self.assertEqual(self.value["scope"]["ell"], "inputs 1 and 2; every angularly allowed output")
        self.assertEqual(self.value["scope"]["m"], 0)
        self.assertEqual(self.value["scope"]["k"], 0)

    def test_exact_balance(self) -> None:
        balance = self.value["normalized_balance"]
        self.assertIn("W_1=1/3 and W_2=1/5", balance["harmonic_convention"])
        self.assertEqual(balance["negative_H_deficit"], "(312650/243)d^2")
        self.assertIn("120250/729", balance["required_source_normalized_Einstein_minus_occupation"])
        self.assertEqual(balance["source_to_direct_representative_map"], "|e_-|^2=48*|A_-|^2")
        self.assertTrue(self.value["classification"]["mixed_ell_harmonic_normalization_directly_audited"])
        self.assertTrue(self.value["classification"]["mu_H_mu_Px_mu_Ji_all_zero_on_balanced_axisymmetric_fixture"])

    def test_frequency_census_is_complete(self) -> None:
        records = self.value["frequency_census"]["records"]
        self.assertEqual(len(records), 40)
        self.assertEqual({record["pair"] for record in records}, {"exceptional", "ell2_extra"})

    def test_all_new_cross_shells_are_off_shell(self) -> None:
        self.assertTrue(self.value["frequency_census"]["all_new_cross_frequencies_off_shell"])
        self.assertTrue(all(not record["collision"] for record in self.value["frequency_census"]["records"]))

    def test_fail_closed_at_source_gate(self) -> None:
        flags = self.value["classification"]
        self.assertFalse(flags["complete_quadratic_source_solved"])
        self.assertFalse(flags["zero_frequency_source_completed"])
        self.assertFalse(flags["bounded_second_order_extension_certified"])
        self.assertFalse(flags["causal_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
