from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bridge.einstein_sector import compensated_einstein_local_projectors


class CompensatedEinsteinLocalProjectorTests(unittest.TestCase):
    def test_canonical_certificate_is_current(self) -> None:
        compensated_einstein_local_projectors.verify_certificate()

    def test_polynomial_projectors_are_complete_and_on_shell_idempotent(self) -> None:
        result = compensated_einstein_local_projectors.build_certificate()
        theorem = result["quotient_polynomial_theorem"]
        self.assertEqual(theorem["completeness"], "Pi_E+Pi_M=1 exactly")
        self.assertEqual(len(theorem["on_shell_idempotence"]), 2)
        self.assertIn("=0 mod L", theorem["on_shell_orthogonality"])

    def test_cauchy_projectors_commute_with_evolution(self) -> None:
        result = compensated_einstein_local_projectors.build_certificate()
        theorem = result["cauchy_projector_theorem"]
        self.assertEqual(theorem["evolution"], ["[P_E,A_4]=0", "[P_M,A_4]=0"])
        self.assertEqual(len(theorem["branch_action"]), 4)

    def test_symplectic_block_decomposition_is_exact(self) -> None:
        result = compensated_einstein_local_projectors.build_certificate()
        theorem = result["symplectic_projector_theorem"]
        self.assertEqual(theorem["cross_block"], "P_E^T Omega P_M=0")
        self.assertIn("(c1/2)J_2", theorem["einstein_block"])
        self.assertIn("-(c1/2)J_2", theorem["massive_block"])

    def test_projectors_are_local_but_tt_reduction_is_not_promoted(self) -> None:
        result = compensated_einstein_local_projectors.build_certificate()
        support = result["support_and_ir_audit"]
        locality = result["tt_locality_audit"]
        self.assertEqual(support["differential_order"], 2)
        self.assertIn("subset", support["support_property"])
        self.assertIn("inverse elliptic", locality["nonlocal_step_not_used"])
        self.assertFalse(result["claim_flags"]["local_projector_on_unreduced_metric_bv_complex"])

    def test_q_zero_is_not_a_projector_singularity(self) -> None:
        result = compensated_einstein_local_projectors.build_certificate()
        audit = result["support_and_ir_audit"]
        self.assertIn("no inverse q", audit["q_zero"])
        self.assertIn("helicity frame", audit["existing_q_zero_exclusion"])

    def test_generic_source_splits_into_both_branches(self) -> None:
        result = compensated_einstein_local_projectors.build_certificate()
        source = result["source_audit"]
        self.assertEqual(source["projected_equations"], ["Box(Pi_E h)=J/M2", "(Box+M2)(Pi_M h)=-J/M2"])
        self.assertTrue(result["claim_flags"]["generic_source_excites_massive_branch"])
        self.assertFalse(result["claim_flags"]["generic_source_preserves_einstein_only_sector"])

    def test_forged_full_bv_projector_is_rejected(self) -> None:
        payload = compensated_einstein_local_projectors.build_certificate()
        payload["claim_flags"]["full_metric_diff_weyl_bv_projector_constructed"] = True
        with self.assertRaises(
            compensated_einstein_local_projectors.CompensatedEinsteinLocalProjectorError
        ):
            compensated_einstein_local_projectors._validate_contract(payload)

    def test_forged_source_closure_is_rejected(self) -> None:
        payload = compensated_einstein_local_projectors.build_certificate()
        payload["claim_flags"]["generic_source_preserves_einstein_only_sector"] = True
        with self.assertRaises(
            compensated_einstein_local_projectors.CompensatedEinsteinLocalProjectorError
        ):
            compensated_einstein_local_projectors._validate_contract(payload)

    def test_forged_certificate_is_rejected(self) -> None:
        payload = compensated_einstein_local_projectors.build_certificate()
        payload["verdict"] = "FULL_BV_PROJECTOR"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(
                compensated_einstein_local_projectors.CompensatedEinsteinLocalProjectorError
            ):
                compensated_einstein_local_projectors.verify_certificate(path)


if __name__ == "__main__":
    unittest.main()
