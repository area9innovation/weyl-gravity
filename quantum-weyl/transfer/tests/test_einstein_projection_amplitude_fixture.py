from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PATH = ROOT / "einstein_projection_amplitude_fixture_certificate.py"
SPEC = importlib.util.spec_from_file_location(
    "einstein_projection_amplitude_fixture_certificate_test", PATH
)
assert SPEC is not None and SPEC.loader is not None
CERT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERT
SPEC.loader.exec_module(CERT)
FIXTURE = sys.modules[CERT.build_certificate_payload.__module__]


class EinsteinProjectionAmplitudeFixtureTests(unittest.TestCase):
    def test_checked_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(CERT.OUTPUT.read_text()), CERT.build_certificate())

    def test_exact_MHV_reference(self) -> None:
        fixture = CERT.build_certificate()["reference_fixture"]
        self.assertEqual(fixture["helicities"], [-2, -2, 2])
        self.assertEqual(fixture["stripped_value"], "1")
        self.assertTrue(fixture["momentum_sum_zero"])
        self.assertTrue(fixture["all_momenta_null"])
        self.assertTrue(fixture["negative_leg_exchange_symmetric"])
        self.assertEqual(fixture["little_group_factor"], "t1^4*t2^4*t3^-4")

    def test_exact_parity_conjugate_reference(self) -> None:
        fixture = CERT.build_certificate()["parity_conjugate_fixture"]
        self.assertEqual(fixture["helicities"], [2, 2, -2])
        self.assertEqual(fixture["stripped_value"], "1")
        self.assertEqual(fixture["angle_brackets_12_23_31"], ["0", "0", "0"])
        self.assertEqual(fixture["square_brackets_12_23_31"], ["1", "1", "1"])
        self.assertEqual(fixture["little_group_factor"], "t1^-4*t2^-4*t3^4")
        self.assertTrue(fixture["parity_conjugate_of_reference_fixture"])

    def test_setting_gate_routes_berger_away_from_flat_amplitude(self) -> None:
        for setting_id in FIXTURE.BERGER_SETTING_IDS:
            verdict = FIXTURE.classify_setting({"setting_id": setting_id})
            self.assertFalse(verdict["compatible"])
            self.assertEqual(verdict["route"], "BERGER_REDUCED_MODE_CARTAN_RAIL")
        accepted = FIXTURE.classify_setting(dict(FIXTURE.REFERENCE_SETTING))
        self.assertTrue(accepted["compatible"])
        self.assertEqual(accepted["route"], "EINSTEIN_DEFECT_TANGENCY_GATE")
        mismatched = dict(FIXTURE.REFERENCE_SETTING)
        mismatched["background_id"] = "compact_positive_berger"
        self.assertFalse(FIXTURE.classify_setting(mismatched)["compatible"])

    def test_projection_and_G5_remain_blocked(self) -> None:
        result = CERT.build_certificate()
        self.assertFalse(result["projection_contract"]["execution_authorized"])
        self.assertFalse(
            result["einstein_input"]["nonlinear_support_local_projection_available"]
        )
        self.assertFalse(
            result["claim_flags"]["PHYSICAL_TRANSFERRED_Q2_PROJECTED"]
        )
        self.assertFalse(
            result["setting_compatibility_contract"]["execution_authorized"]
        )
        self.assertFalse(
            result["einstein_defect_tangency_contract"][
                "full_BV_defect_chain_map_available"
            ]
        )
        self.assertFalse(
            result["einstein_defect_tangency_contract"][
                "reduced_TT_projector_used_for_full_BV_projection"
            ]
        )
        self.assertFalse(
            result["normalization_contract"]["overall_coefficient_match_authorized"]
        )
        self.assertFalse(result["claim_flags"]["G5_PROMOTED"])

    def test_einstein_input_promotions_fail_closed(self) -> None:
        theorem = FIXTURE._git_json(FIXTURE.EINSTEIN_CERTIFICATE)
        forged = deepcopy(theorem)
        forged["claim_flags"]["asymptotically_flat_scattering_recovered"] = True
        with self.assertRaisesRegex(ValueError, "projection boundary"):
            FIXTURE.validate_einstein_input(forged)

        forged = deepcopy(theorem)
        forged["one_particle_before_residual_quotient"]["helicity_weights"] = ["+2"]
        with self.assertRaisesRegex(ValueError, "helicity input"):
            FIXTURE.validate_einstein_input(forged)

    def test_defect_and_projector_promotions_fail_closed(self) -> None:
        defect = FIXTURE._git_json(FIXTURE.DEFECT_CERTIFICATE, FIXTURE.DEFECT_COMMIT)
        forged = deepcopy(defect)
        forged["claim_flags"]["einstein_defect_chain_map_constructed"] = True
        with self.assertRaisesRegex(ValueError, "defect boundary"):
            FIXTURE.validate_defect_input(forged)

        projector = FIXTURE._git_json(
            FIXTURE.PROJECTOR_CERTIFICATE, FIXTURE.PROJECTOR_COMMIT
        )
        forged = deepcopy(projector)
        forged["claim_flags"]["nonlinear_projector_constructed"] = True
        with self.assertRaisesRegex(ValueError, "projector boundary"):
            FIXTURE.validate_projector_input(forged)


if __name__ == "__main__":
    unittest.main()
