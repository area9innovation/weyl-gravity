"""Falsification tests for the BT torus curvature/cut concentration gate."""

from __future__ import annotations

import copy
import json
import unittest

from reverse_physics.bt_euclidean_torus_curvature_cut_concentration import build
from reverse_physics.verify_bt_euclidean_torus_curvature_cut_concentration import (
    DEFAULT_CERTIFICATE,
    verify,
)


class TorusCurvatureCutConcentrationTests(unittest.TestCase):
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

    def test_fixture_checks_close(self) -> None:
        self.assertTrue(all(self.certificate["exact_fixture"]["checks"].values()))

    def test_mutated_energy_identity_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["spectral_flatness_theorem"].__setitem__(
                "energy", "E=+<h,g>"
            )
        )

    def test_mutated_spectral_scale_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["spectral_flatness_theorem"].__setitem__(
                "normalized_flatness", "||h-h_bar||_2/R<=sqrt(Q/omega_L)"
            )
        )

    def test_mutated_cut_factor_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["height_cut_theorem"].__setitem__(
                "normalized_floor", "Q/omega_L^2>=Gamma_K^2/(pi^4*R^2)"
            )
        )

    def test_mutated_mean_bound_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["combined_concentration_theorem"].__setitem__(
                "mean_bound", "|h_bar|*sqrt(m_K)/R<=sqrt(F_K)"
            )
        )

    def test_mutated_fixture_flux_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["exact_fixture"]["cut_flux"].__setitem__(
                "numerator", data["exact_fixture"]["cut_flux"]["numerator"] + 1
            )
        )

    def test_false_all_field_promotion_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["research_disposition"].__setitem__(
                "all_field_torus_scaled_PL", "PROVED"
            )
        )

    def test_counterfamily_promotion_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["research_disposition"].__setitem__(
                "nonseparable_counterfamily", "CONSTRUCTED"
            )
        )

    def test_mutated_input_hash_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["provenance"]["inputs"][0].__setitem__(
                "sha256", "0" * 64
            )
        )

    def test_lorentzian_tag_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL")
        )


if __name__ == "__main__":
    unittest.main()
