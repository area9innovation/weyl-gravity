"""Tests for the c/W_x spectator extension of the twist-wave cone."""

from __future__ import annotations

import json
import unittest

from bridge.einstein_sector import einstein_maxwell_weyl_twist_circumference_wilson_ell2_complete_bounded_cone as theorem


class TwistCircumferenceWilsonEll2ConeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = theorem.build()

    def test_certificate_is_current(self) -> None:
        self.assertEqual(json.loads(theorem.OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_spectator_product_is_explicit(self) -> None:
        zero_locus = self.value["complete_bounded_zero_locus"]
        self.assertEqual(zero_locus["free_spectators"], "c and W_x are arbitrary real tangent coordinates")
        self.assertIn("R_c x R_Wx", zero_locus["product_structure"])

    def test_twist_velocity_remains_zero(self) -> None:
        self.assertEqual(self.value["complete_bounded_zero_locus"]["twist_velocity"], "B=0")

    def test_spectator_primitives_are_explicit(self) -> None:
        proof = self.value["source_decomposition_proof"]
        self.assertIn("k=0", proof["circumference_times_wave"])
        self.assertEqual(proof["Wilson_times_wave"], "CERTIFIED identically zero")

    def test_dynamical_globals_are_not_promoted(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["radion_circumference_velocity_or_electric_tangents_classified"])
        self.assertFalse(classification["other_ell_or_nonzero_momentum_classified"])

    def test_causal_class_is_fail_closed(self) -> None:
        self.assertEqual(self.value["correction_classes"]["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
