"""Falsification tests for the BT torus quadratic virial-density gate."""

from __future__ import annotations

import copy
import json
import unittest

from reverse_physics.bt_euclidean_torus_quadratic_virial_density_gate import build
from reverse_physics.verify_bt_euclidean_torus_quadratic_virial_density_gate import (
    DEFAULT_CERTIFICATE,
    verify,
)


class TorusQuadraticVirialDensityGateTests(unittest.TestCase):
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

    def test_mutated_quadratic_coefficient_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["exact_constant_audit"].__setitem__(
                "quadratic_coefficient", {"numerator": 1, "denominator": 8}
            )
        )

    def test_mutated_low_taylor_witness_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["exact_constant_audit"][
                "low_degree_6_exponential_taylor_sum"
            ].__setitem__("numerator", 0)
        )

    def test_mutated_high_atanh_witness_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["exact_constant_audit"][
                "high_two_term_log_lower"
            ].__setitem__("numerator", 0)
        )

    def test_mutated_global_virial_coefficient_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["global_graph_theorem"].__setitem__(
                "global_virial_bound",
                "<psi,g>>=(15/8)*A-17*N",
            )
        )

    def test_mutated_normalized_floor_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["four_torus_theorem"].__setitem__(
                "bounded_density_normalized_branch",
                "272/29<x<64 implies Q/omega_L^2>=841*(x-272/29)^2/(4194304*pi^4)",
            )
        )

    def test_mutated_contrast_coefficient_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["four_torus_theorem"].__setitem__(
                "collapsing_contrast_necessity",
                "Q/omega_L^2->0 implies limsup W^2/L^4<=18",
            )
        )

    def test_mutated_fixture_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["exact_fixture"][
                "quadratic_density_branch_floor"
            ].__setitem__(
                "numerator",
                data["exact_fixture"]["quadratic_density_branch_floor"]["numerator"]
                + 1,
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
                "action_density_at_most_272_over_29_sector", "CLOSED"
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
