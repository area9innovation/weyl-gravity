from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bridge.einstein_sector import flat_einstein_symplectic_restriction


class FlatEinsteinSymplecticRestrictionTests(unittest.TestCase):
    def test_canonical_certificate_is_current(self) -> None:
        flat_einstein_symplectic_restriction.verify_certificate()

    def test_weyl_restriction_is_zero_but_eh_is_not(self) -> None:
        result = flat_einstein_symplectic_restriction.build_certificate()
        matrices = result["cauchy_matrix_test"]
        self.assertEqual(matrices["ranks"], {"restricted_weyl": 0, "einstein_hilbert": 2})
        self.assertEqual(matrices["nonzero_proportionality"], "IMPOSSIBLE")
        self.assertIn(
            "omega_W^mu=0 pointwise",
            result["action_current_derivation"]["einstein_restriction"],
        )

    def test_schwartz_boundary_improvements_do_not_repair_pairing(self) -> None:
        result = flat_einstein_symplectic_restriction.build_certificate()
        improvement = result["boundary_improvement_test"]
        self.assertIn("=0", improvement["spatial_boundary"])
        self.assertIn("no allowed local improvement", improvement["conclusion"])
        self.assertFalse(result["claim_flags"]["all_boundary_counterterms_classified"])

    def test_P0_charge_mismatch_is_scoped(self) -> None:
        result = flat_einstein_symplectic_restriction.build_certificate()
        charge = result["time_translation_test"]
        self.assertEqual(charge["restricted_charge"], "H_P0=0 on the connected Schwartz Einstein-wave core")
        self.assertFalse(result["claim_flags"]["full_einstein_scattering_no_go_proved"])

    def test_cylinder_pairing_is_not_overwritten(self) -> None:
        result = flat_einstein_symplectic_restriction.build_certificate()
        self.assertIn("do not map into", result["cylinder_non_contradiction"]["reason"])

    def test_forged_full_no_go_is_rejected(self) -> None:
        payload = flat_einstein_symplectic_restriction.build_certificate()
        payload["claim_flags"]["full_einstein_scattering_no_go_proved"] = True
        with self.assertRaises(
            flat_einstein_symplectic_restriction.FlatEinsteinSymplecticRestrictionError
        ):
            flat_einstein_symplectic_restriction._validate_contract(payload)

    def test_forged_certificate_is_rejected(self) -> None:
        payload = flat_einstein_symplectic_restriction.build_certificate()
        payload["verdict"] = "FORGED"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(
                flat_einstein_symplectic_restriction.FlatEinsteinSymplecticRestrictionError
            ):
                flat_einstein_symplectic_restriction.verify_certificate(path)


if __name__ == "__main__":
    unittest.main()
