from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bridge.einstein_sector import d_quotient_asymptotic_seed


class DQuotientAsymptoticSeedTests(unittest.TestCase):
    def test_canonical_certificate_is_current(self) -> None:
        d_quotient_asymptotic_seed.verify_certificate()

    def test_real_generator_dictionary_separates_three_notions(self) -> None:
        result = d_quotient_asymptotic_seed.build_certificate()
        dictionary = result["generator_dictionary"]
        self.assertEqual(dictionary["lie_D_metric"], "2 g")
        self.assertEqual(dictionary["lie_P0_metric"], "0")
        self.assertEqual(dictionary["bracket"], "[D_M,P_0]=-P_0")
        self.assertIn("H_ESU(Omega)=-1", dictionary["H_ESU_scri_test"])
        self.assertEqual(dictionary["D_M_scri_restriction"], "u d_u")

    def test_reduced_radiative_core_is_preserved_kinematically(self) -> None:
        result = d_quotient_asymptotic_seed.build_certificate()
        seed = result["flat_dilation_radiative_seed"]
        self.assertEqual(seed["infinitesimal_shear"], "delta_D C=u d_u C-C")
        self.assertEqual(seed["infinitesimal_news"], "delta_D N=u d_u N")
        self.assertEqual(seed["status"], "PASS_REDUCED_KINEMATICS")

    def test_triangular_green_identity_is_only_formal(self) -> None:
        result = d_quotient_asymptotic_seed.build_certificate()
        seed = result["triangular_einstein_defect_seed"]
        self.assertEqual(seed["operator"], [["Box", "-1"], ["0", "Box"]])
        self.assertEqual(seed["status"], "FORMAL_OPERATOR_IDENTITY_ONLY")
        self.assertFalse(result["claim_flags"]["null_infinity_green_complex_constructed"])

    def test_verdict_fails_closed(self) -> None:
        result = d_quotient_asymptotic_seed.build_certificate()
        self.assertEqual(result["verdicts"]["asymptotically_flat_D"], "PHASE_SPACE_NOT_CLOSED")
        self.assertEqual(result["verdicts"]["einstein_sector"], "EINSTEIN_OPEN")
        self.assertFalse(result["claim_flags"]["D_proved_proper_gauge"])
        self.assertFalse(result["claim_flags"]["D_proved_charged"])

    def test_forged_charge_promotion_is_rejected(self) -> None:
        payload = d_quotient_asymptotic_seed.build_certificate()
        payload["claim_flags"]["D_proved_charged"] = True
        with self.assertRaises(d_quotient_asymptotic_seed.DQuotientAsymptoticSeedError):
            d_quotient_asymptotic_seed._validate_contract(payload)

    def test_forged_certificate_is_rejected(self) -> None:
        payload = d_quotient_asymptotic_seed.build_certificate()
        payload["radial_quantization_warning"]["time_translation_charge_rule"] = "forged"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(d_quotient_asymptotic_seed.DQuotientAsymptoticSeedError):
                d_quotient_asymptotic_seed.verify_certificate(path)


if __name__ == "__main__":
    unittest.main()
