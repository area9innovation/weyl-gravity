"""Regression tests for the harmonic sign-resonance join."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_harmonic_sign_resonance_join import (
    OUTPUT,
    build_certificate,
)


class HarmonicSignResonanceJoinTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build_certificate())

    def test_bounded_and_smooth_classes_stay_distinct(self) -> None:
        classes = build_certificate()["correction_classes"]
        self.assertEqual(classes["BOUNDED_OR_FINITE_QUASIPERIODIC"]["full_finite_carrier_zero_locus"], "OPEN")
        self.assertIn("mu_H", classes["SMOOTH_EXPONENTIAL_POLYNOMIAL"]["complete_zero_locus"])
        self.assertEqual(classes["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")

    def test_maximal_complete_subcarrier_includes_globals_and_all_generic_ells(self) -> None:
        value = build_certificate()["maximal_complete_mixed_subcarrier"]
        self.assertTrue(value["necessity_and_sufficiency"])
        self.assertIn("arbitrary finite sum", value["domain"])
        self.assertIn("homogeneous/twist/Maxwell", value["domain"])

    def test_controls_are_not_crosswalked(self) -> None:
        controls = build_certificate()["separate_nonzero_momentum_controls"]
        self.assertIn("origin", controls["candidate13"])
        self.assertIn("two nonzero", controls["tuned_opposite_momentum"])
        self.assertIn("NO_CERTIFIED_MAP", controls["crosswalk"])


if __name__ == "__main__":
    unittest.main()
