"""Tests for the constant-twist wave counterexample."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_constant_twist_wave_counterexample import OUTPUT, build


class ConstantTwistWaveCounterexampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_prior_member_is_explicit(self) -> None:
        self.assertTrue(self.value["classification"]["explicit_prior_cone_member_constructed"])
        self.assertIn("occupation rho_extra", self.value["first_order_fixture"]["wave"])
        self.assertIn("|C_minus|", self.value["first_order_fixture"]["wave"])

    def test_adjoint_pairing_nonzero(self) -> None:
        self.assertEqual(self.value["adjoint_obstruction"]["nonzero_witness"], "24*sqrt(3)")
        self.assertTrue(self.value["classification"]["moment_maps_vanish_but_bounded_resonance_nonzero"])

    def test_safe_strata_retained(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["wave_free_constant_twist_modulus_retained"])
        self.assertTrue(classification["A_zero_wave_subcone_retained"])

    def test_full_nonzero_A_locus_remains_open(self) -> None:
        self.assertFalse(self.value["classification"]["complete_constant_twist_wave_zero_locus_classified"])


if __name__ == "__main__":
    unittest.main()
