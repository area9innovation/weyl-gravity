"""Falsification tests for the BT reciprocal-virial localization gate."""

from __future__ import annotations

import copy
import json
import unittest

from reverse_physics.bt_euclidean_torus_reciprocal_virial_localization import build
from reverse_physics.verify_bt_euclidean_torus_reciprocal_virial_localization import (
    DEFAULT_CERTIFICATE,
    verify,
)


class TorusReciprocalVirialLocalizationTests(unittest.TestCase):
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

    def test_mutated_inverse_identity_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["exact_graph_theorem"].__setitem__(
                "inverse_direction_identity", "(Jv)_x=+r_x/u_x"
            )
        )

    def test_mutated_popoviciu_factor_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["exact_graph_theorem"].__setitem__(
                "popoviciu_floor",
                "||v-v_bar||_2^2<=N and therefore Q>=B^2/(N*R^2)",
            )
        )

    def test_mutated_threshold_floor_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["four_torus_theorem"].__setitem__(
                "threshold_floor", "Q/omega_L^2>=A*F_K/(2*pi^4*K)"
            )
        )

    def test_mutated_fixture_moment_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["exact_fixture"]["reciprocal_residual_moment"].__setitem__(
                "numerator",
                data["exact_fixture"]["reciprocal_residual_moment"]["numerator"] + 1,
            )
        )

    def test_numeric_scout_promotion_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["numerical_scout_disposition"].__setitem__(
                "status", "CERTIFICATE_EVIDENCE"
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
