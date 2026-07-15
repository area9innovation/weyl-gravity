from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bridge.einstein_sector import compensated_einstein_causal_subsector


class CompensatedEinsteinCausalSubsectorTests(unittest.TestCase):
    def test_canonical_certificate_is_current(self) -> None:
        compensated_einstein_causal_subsector.verify_certificate()

    def test_local_constraints_propagate_without_future_data(self) -> None:
        result = compensated_einstein_causal_subsector.build_certificate()
        causal = result["causal_constraint_theorem"]
        self.assertEqual(causal["constraint_rank"], 2)
        self.assertEqual(causal["kernel_identity"], "ker C=im I_E")
        self.assertEqual(causal["future_boundary_data"], "NOT_REQUIRED")
        self.assertTrue(result["claim_flags"]["source_free_causal_propagation_proved"])

    def test_massive_branch_is_detected_and_removed(self) -> None:
        result = compensated_einstein_causal_subsector.build_certificate()
        causal = result["causal_constraint_theorem"]
        self.assertEqual(causal["massive_embedding_defect"], "C I_M=-M2 I_2")
        self.assertEqual(causal["branch_basis_determinant"], "det[I_E I_M]=M2^2")
        self.assertFalse(result["claim_flags"]["massive_branch_absent_from_full_theory"])

    def test_restricted_current_is_nonzero_einstein_hilbert(self) -> None:
        result = compensated_einstein_causal_subsector.build_certificate()
        current = result["symplectic_restriction_theorem"]
        self.assertEqual(current["restricted_ranks"]["einstein"], 2)
        self.assertIn("(c1/2)omega_EH", current["einstein_restriction"])
        self.assertEqual(current["cross_branch_matrix"], [["0", "0"], ["0", "0"]])

    def test_P0_energy_matches_healthy_einstein_wave(self) -> None:
        result = compensated_einstein_causal_subsector.build_certificate()
        energy = result["time_translation_theorem"]
        self.assertEqual(energy["repository_healthy_sign"], "c1=-1 gives positive H_P0")
        self.assertEqual(energy["einstein_hilbert_match"], "exact with the action normalization c1 R")

    def test_pure_weyl_limit_remains_degenerate(self) -> None:
        result = compensated_einstein_causal_subsector.build_certificate()
        self.assertIn("rank zero", result["symplectic_restriction_theorem"]["pure_weyl_limit"])
        self.assertTrue(result["claim_flags"]["pure_weyl_limit_recovers_zero_pairing"])

    def test_forged_sourced_promotion_is_rejected(self) -> None:
        payload = compensated_einstein_causal_subsector.build_certificate()
        payload["claim_flags"]["constraint_compatible_with_arbitrary_sources"] = True
        with self.assertRaises(
            compensated_einstein_causal_subsector.CompensatedEinsteinCausalSubsectorError
        ):
            compensated_einstein_causal_subsector._validate_contract(payload)

    def test_forged_scattering_promotion_is_rejected(self) -> None:
        payload = compensated_einstein_causal_subsector.build_certificate()
        payload["claim_flags"]["einstein_scattering_equivalence_proved"] = True
        with self.assertRaises(
            compensated_einstein_causal_subsector.CompensatedEinsteinCausalSubsectorError
        ):
            compensated_einstein_causal_subsector._validate_contract(payload)

    def test_forged_certificate_is_rejected(self) -> None:
        payload = compensated_einstein_causal_subsector.build_certificate()
        payload["verdict"] = "FULL_EINSTEIN_SCATTERING"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(
                compensated_einstein_causal_subsector.CompensatedEinsteinCausalSubsectorError
            ):
                compensated_einstein_causal_subsector.verify_certificate(path)


if __name__ == "__main__":
    unittest.main()
