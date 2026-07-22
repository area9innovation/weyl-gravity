"""Independent verification and mutation tests for Nariai Phase 2."""

from __future__ import annotations

import json
import unittest

from d_quotient_classical.phase2.nariai_sign_mechanism_v2 import generate, verify


class NariaiSignMechanismTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(generate.OUTPUT.read_text(encoding="utf-8"))

    def reject(self, path: tuple[object, ...], value: object) -> None:
        candidate = verify.mutated(self.payload, path, value)
        with self.assertRaises(Exception):
            verify.verify_payload(candidate)

    def test_independent_verifier_accepts_certificate(self) -> None:
        verify.verify_payload(self.payload)
        verify.verify_atlas(self.payload)

    def test_producer_regenerates_exactly(self) -> None:
        self.assertEqual(generate.build_certificate(), self.payload)

    def test_mutated_factor_gap_rejected(self) -> None:
        self.reject(
            ("exact_factorization_and_projectors", "factor_definitions", "scalar_gap_L_E_minus_L_C"),
            "1/3",
        )

    def test_mutated_channel_rank_rejected(self) -> None:
        self.reject(("exact_factorization_and_projectors", "curvature_channels", "ranks"), [3, 2, 4])

    def test_swapped_residue_sign_rejected(self) -> None:
        self.reject(
            ("static_patch_residue_theorem", "lee_wald_concomitant", "Einstein_residue_multiplier"),
            "1/3",
        )

    def test_global_timelike_promotion_rejected(self) -> None:
        self.reject(
            ("static_patch_residue_theorem", "sign_structure", "global_timelike_generator_claimed"),
            True,
        )

    def test_horizon_omission_rejected(self) -> None:
        self.reject(("classification", "horizon_boundaries_omitted"), True)

    def test_zero_flux_assumption_rejected(self) -> None:
        self.reject(("classification", "zero_horizon_flux_assumed"), True)

    def test_weyl_maxwell_family_relabel_rejected(self) -> None:
        self.reject(("classification", "same_Weyl_Maxwell_family_claimed"), True)

    def test_real_symplectic_inertia_promotion_rejected(self) -> None:
        self.reject(("classification", "real_symplectic_inertia_claimed"), True)

    def test_positive_energy_promotion_rejected(self) -> None:
        self.reject(("classification", "positive_energy_claimed"), True)

    def test_input_hash_mutation_rejected(self) -> None:
        self.reject(("provenance", "imported_artifacts", 0, "sha256"), "0" * 64)


if __name__ == "__main__":
    unittest.main()

