"""Falsification tests for the BT torus dyadic stopping-flow theorem."""

from __future__ import annotations

import copy
import json
import unittest

from reverse_physics.bt_euclidean_torus_dyadic_stopping_flow import build
from reverse_physics.verify_bt_euclidean_torus_dyadic_stopping_flow import (
    DEFAULT_CERTIFICATE,
    verify,
)


class TorusDyadicStoppingFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(DEFAULT_CERTIFICATE, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation) -> None:
        candidate = copy.deepcopy(self.certificate)
        mutation(candidate)
        self.assertFalse(all(passed for _, passed in verify(candidate)))

    def test_generated_certificate_matches(self) -> None:
        self.assertEqual(build(), self.certificate)

    def test_unmodified_certificate_passes(self) -> None:
        self.assertTrue(all(passed for _, passed in verify(self.certificate)))

    def test_exact_constant_audit_closes(self) -> None:
        self.assertTrue(all(self.certificate["exact_constant_audit"]["checks"].values()))

    def test_mutated_low_band_mass_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["dyadic_stopping_theorem"].__setitem__(
                "low_band_mass_ceiling", "sum_(e in B_<2) f_e<=q*N/W"
            )
        )

    def test_mutated_divergence_floor_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["dyadic_stopping_theorem"].__setitem__(
                "divergence_floor", "||div(f)||_2>=2*F/(D*log_2(W)*sqrt(N))"
            )
        )

    def test_mutated_cutoff_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["four_torus_corollary"].__setitem__(
                "contrast_hypothesis", "W>=256*L^(10/3)"
            )
        )

    def test_mutated_minimum_side_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["exact_constant_audit"].__setitem__("minimum_side", 2048)
        )

    def test_false_all_field_promotion_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["research_disposition"].__setitem__(
                "all_field_torus_scaled_PL", "PROVED"
            )
        )

    def test_closed_moderate_gate_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["research_disposition"].__setitem__(
                "sub_L_10_over_3_moderate_contrast_sector", "CLOSED"
            )
        )

    def test_mutated_input_hash_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["provenance"]["inputs"][0].__setitem__("sha256", "0" * 64)
        )

    def test_lorentzian_tag_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL")
        )


if __name__ == "__main__":
    unittest.main()
