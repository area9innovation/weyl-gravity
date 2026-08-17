"""Falsification tests for the BT torus global virial compatibility."""

from __future__ import annotations

import copy
import json
import unittest

from reverse_physics.bt_euclidean_torus_global_virial_compatibility import build
from reverse_physics.verify_bt_euclidean_torus_global_virial_compatibility import (
    DEFAULT_CERTIFICATE,
    verify,
)


class TorusGlobalVirialCompatibilityTests(unittest.TestCase):
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

    def test_mutated_majorant_slope_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["exact_constant_audit"].__setitem__(
                "affine_majorant_slope", {"numerator": 5, "denominator": 1}
            )
        )

    def test_mutated_global_defect_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["global_graph_theorem"].__setitem__(
                "global_virial_bound", "<psi,g>>=2*A-21*N"
            )
        )

    def test_mutated_density_floor_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["four_torus_theorem"].__setitem__(
                "bounded_density_branch", "11<x<64 implies N*Q>=(x-11)^2/256"
            )
        )

    def test_mutated_contrast_square_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["four_torus_theorem"].__setitem__(
                "collapsing_contrast_necessity",
                "Q/omega_L^2->0 implies limsup W^2/L^4<=21",
            )
        )

    def test_mutated_fixture_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["exact_fixture"]["edge_reciprocal_excess"].__setitem__(
                "numerator", data["exact_fixture"]["edge_reciprocal_excess"]["numerator"] + 1
            )
        )

    def test_false_all_field_promotion_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["research_disposition"].__setitem__(
                "all_field_torus_scaled_PL", "PROVED"
            )
        )

    def test_closed_sub_11_gate_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["research_disposition"].__setitem__(
                "action_density_at_most_11_sector", "CLOSED"
            )
        )

    def test_mutated_input_hash_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["provenance"]["inputs"][0].__setitem__(
                "sha256", "0" * 64
            )
        )

    def test_lorentzian_tag_is_rejected(self) -> None:
        self.assert_rejected(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))


if __name__ == "__main__":
    unittest.main()
