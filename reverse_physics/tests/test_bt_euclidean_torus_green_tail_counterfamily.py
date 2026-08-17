"""Falsification tests for the BT torus Green-tail counterfamily."""

from __future__ import annotations

import copy
import json
import unittest

from reverse_physics.bt_euclidean_torus_green_tail_counterfamily import build
from reverse_physics.verify_bt_euclidean_torus_green_tail_counterfamily import (
    DEFAULT_CERTIFICATE,
    verify,
)


class TorusGreenTailCounterfamilyTests(unittest.TestCase):
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

    def test_exact_fixture_closes(self) -> None:
        self.assertTrue(all(self.certificate["exact_fixture"]["checks"].values()))

    def test_mutated_side_scale_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["family"].__setitem__("side", "L_n=n^20")
        )

    def test_mutated_green_gradient_term_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["discrete_green_annular_lemma"].__setitem__(
                "base_gradient_bound", "||g||^2<=C*lambda^-4"
            )
        )

    def test_mutated_perturbation_rate_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["perturbation_theorem"].__setitem__(
                "stability", "||g(u)-g(u0)||=O(delta)"
            )
        )

    def test_mutated_power_balance_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["power_balance"][
                "base_terms_after_free_normalization"
            ].__setitem__("background_transition", "n^8")
        )

    def test_mutated_scale_exponent_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["power_balance"]["scale_exponents_in_n"].__setitem__(
                "tail_scale", 20
            )
        )

    def test_mutated_limit_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["power_balance"].__setitem__(
                "limit", "liminf Q/omega^2>0"
            )
        )

    def test_mutated_fixture_minor_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["exact_fixture"]["mixed_product_minor"].__setitem__(
                "numerator",
                data["exact_fixture"]["mixed_product_minor"]["numerator"] + 1,
            )
        )

    def test_false_all_field_bound_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["research_disposition"].__setitem__(
                "all_field_torus_scaled_PL", "PROVED"
            )
        )

    def test_witten_promotion_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["research_disposition"].__setitem__(
                "witten_poincare_transfer", "PROVED"
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
