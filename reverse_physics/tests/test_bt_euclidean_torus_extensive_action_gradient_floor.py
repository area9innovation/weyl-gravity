"""Falsification tests for the BT torus extensive-action gradient floor."""

from __future__ import annotations

import copy
import json
import unittest

from reverse_physics.bt_euclidean_torus_extensive_action_gradient_floor import build
from reverse_physics.verify_bt_euclidean_torus_extensive_action_gradient_floor import (
    DEFAULT_CERTIFICATE,
    verify,
)


class TorusExtensiveActionGradientFloorTests(unittest.TestCase):
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

    def test_mutated_virial_constant_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["exact_constant_audit"].__setitem__(
                "virial_constant", {"numerator": 487, "denominator": 5}
            )
        )

    def test_mutated_graph_quotient_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["graph_theorem"].__setitem__(
                "quotient_floor", "Q>=A/[N*D^2*log(q+sqrt(2*A))^2]"
            )
        )

    def test_mutated_normalized_floor_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["four_torus_corollary"].__setitem__(
                "normalized_floor", "Q/omega_L^2>=61/(160*pi^4)"
            )
        )

    def test_mutated_contrast_cutoff_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["four_torus_corollary"].__setitem__(
                "counterfamily_contrast_necessity",
                "Q/omega_L^2<61/(320*pi^4) implies W<8*L^2",
            )
        )

    def test_mutated_fixture_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["exact_fixture"]["gradient_norm_squared"].__setitem__(
                "numerator", data["exact_fixture"]["gradient_norm_squared"]["numerator"] + 1
            )
        )

    def test_false_all_field_promotion_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["research_disposition"].__setitem__(
                "all_field_torus_scaled_PL", "PROVED"
            )
        )

    def test_closed_low_action_gate_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["research_disposition"].__setitem__(
                "low_action_sub_16_L_squared_sector", "CLOSED"
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
