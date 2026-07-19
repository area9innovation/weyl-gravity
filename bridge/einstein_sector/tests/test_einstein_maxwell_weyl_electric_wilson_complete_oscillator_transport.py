"""Tests for complete electric/Wilson oscillator transport."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport import OUTPUT, build


class CompleteElectricWilsonTransportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_complete_oscillator_scope(self) -> None:
        self.assertTrue(self.value["classification"]["complete_certified_nonzero_frequency_inventory_covered"])
        self.assertIn("exceptional ell=1", self.value["scope"]["ell"])
        self.assertIn("every allowed compact momentum", self.value["scope"]["k"])

    def test_bounded_transport(self) -> None:
        self.assertTrue(self.value["classification"]["Q_e_times_every_oscillator_bounded_removable"])
        self.assertTrue(self.value["classification"]["W_x_times_every_oscillator_source_zero"])
        self.assertEqual(self.value["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "CERTIFIED")

    def test_fail_closed_boundary(self) -> None:
        self.assertFalse(self.value["classification"]["full_bounded_cone_solved"])
        self.assertFalse(self.value["classification"]["all_orders_fixed_bundle_duality_orbit"])
        self.assertEqual(self.value["correction_classes"]["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
