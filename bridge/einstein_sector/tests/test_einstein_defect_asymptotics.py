from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bridge.einstein_sector import einstein_defect_asymptotics


class EinsteinDefectAsymptoticsTests(unittest.TestCase):
    def test_canonical_certificate_is_current(self) -> None:
        einstein_defect_asymptotics.verify_certificate()

    def test_factorization_and_direct_series_checks_pass(self) -> None:
        result = einstein_defect_asymptotics.build_certificate()
        recurrence = result["defect_wave_recurrence"]
        self.assertEqual(recurrence["factorization_check"]["status"], "PASS")
        self.assertEqual(
            recurrence["direct_series_check"]["defect_wave_recurrence"],
            "PASS",
        )

    def test_p0_and_p1_defect_coefficients(self) -> None:
        result = einstein_defect_asymptotics.build_certificate()
        self.assertEqual(
            result["p0_defect"]["leading_coefficients"],
            ["g_0=-2 d_u f_0", "g_1=-L f_0"],
        )
        self.assertEqual(
            result["p1_defect_tower"]["first_defect_rows"],
            ["4 d_u kappa=0", "6 d_u rho+(6-L) kappa=0"],
        )

    def test_kappa_zero_is_not_promoted(self) -> None:
        result = einstein_defect_asymptotics.build_certificate()
        self.assertFalse(result["claim_flags"]["kappa_zero_sufficient_for_einstein"])
        self.assertIn("does not imply rho=0", result["p1_defect_tower"]["kappa_zero_consequence"])

    def test_full_tensor_and_causal_claims_remain_open(self) -> None:
        result = einstein_defect_asymptotics.build_certificate()
        self.assertEqual(
            result["full_tensor_completion_gate"]["status"],
            "OPEN_FAIL_CLOSED",
        )
        self.assertFalse(
            result["claim_flags"]["full_tensor_defect_expansion_constructed"]
        )
        self.assertFalse(result["claim_flags"]["causal_zero_defect_theorem_proved"])

    def test_forged_kappa_sufficiency_is_rejected(self) -> None:
        payload = einstein_defect_asymptotics.build_certificate()
        payload["claim_flags"]["kappa_zero_sufficient_for_einstein"] = True
        with self.assertRaises(
            einstein_defect_asymptotics.EinsteinDefectAsymptoticsError
        ):
            einstein_defect_asymptotics._validate_contract(payload)

    def test_forged_certificate_is_rejected(self) -> None:
        payload = einstein_defect_asymptotics.build_certificate()
        payload["claim_flags"]["einstein_scattering_equivalence_proved"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(
                einstein_defect_asymptotics.EinsteinDefectAsymptoticsError
            ):
                einstein_defect_asymptotics.verify_certificate(path)


if __name__ == "__main__":
    unittest.main()
