"""Falsification tests for the BT torus small-action gradient floor."""

from __future__ import annotations

import copy
import json
import unittest

from reverse_physics.bt_euclidean_torus_small_action_gradient_floor import build
from reverse_physics.verify_bt_euclidean_torus_small_action_gradient_floor import (
    DEFAULT_CERTIFICATE,
    verify,
)


class TorusSmallActionGradientFloorTests(unittest.TestCase):
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

    def test_mutated_sobolev_exponent_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["critical_sobolev_lemma"].__setitem__(
                "statement", "||grad psi||_4<=S_4*||Delta psi||_2"
            )
        )

    def test_mutated_edge_ratio_bound_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["nonlinear_remainder_lemma"].__setitem__(
                "edge_bound", "edge ratios are bounded by 8"
            )
        )

    def test_mutated_remainder_constant_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["nonlinear_remainder_lemma"].__setitem__(
                "scalar_remainders", "a(t),b(t)<=t^2"
            )
        )

    def test_mutated_branch_crossing_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["additive_branch_theorem"].__setitem__(
                "branch_selection", "select the small branch by assumption"
            )
        )

    def test_mutated_floor_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["small_action_theorem"].__setitem__(
                "quotient_floor", "Q>=omega_L^2/32"
            )
        )

    def test_mutated_action_escape_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["combined_concentration_alternative"].__setitem__(
                "collapse_action_quantization", "collapse may have A_L->0"
            )
        )

    def test_false_all_field_promotion_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["research_disposition"].__setitem__(
                "all_field_torus_scaled_PL", "PROVED"
            )
        )

    def test_mutated_fixture_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["exact_fixture"]["quotient"].__setitem__(
                "numerator", data["exact_fixture"]["quotient"]["numerator"] + 1
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
