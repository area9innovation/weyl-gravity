"""Regression tests for the harmonic Taub-sign classification."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_harmonic_taub_sign_classification import (
    DEFAULT_OUTPUT,
    build_certificate,
)


class HarmonicTaubSignClassificationTest(unittest.TestCase):
    def test_certificate_is_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), build_certificate())

    def test_complete_certified_extra_cofiber_is_negative(self) -> None:
        classification = build_certificate()["classification"]
        self.assertTrue(classification["generic_extra_all_ell_all_k_both_parities_negative"])
        self.assertTrue(classification["exceptional_extra_ell1_all_k_both_parities_negative"])
        self.assertTrue(classification["finite_pure_extra_harmonic_sums_negative"])

    def test_global_blocks_are_not_extra_cofiber_counterexamples(self) -> None:
        ledger = build_certificate()["harmonic_sign_ledger"]
        self.assertTrue(ledger["homogeneous_generalized_zero"]["solution_cofiber"].startswith("0;"))
        self.assertTrue(ledger["axial_twist_generalized_zero"]["solution_cofiber"].startswith("0;"))

    def test_charge_boundary_is_fail_closed(self) -> None:
        charge = build_certificate()["charge_fibre_theorem"]
        self.assertEqual(charge["enlarged_continuous_flux_family"]["status"], "OPEN")
        self.assertEqual(charge["enlarged_continuous_flux_family"]["full_second_order_extension"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
