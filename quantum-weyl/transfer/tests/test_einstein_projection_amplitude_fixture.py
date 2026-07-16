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

    def test_projection_and_G5_remain_blocked(self) -> None:
        result = CERT.build_certificate()
        self.assertFalse(result["projection_contract"]["execution_authorized"])
        self.assertFalse(
            result["einstein_input"]["nonlinear_support_local_projection_available"]
        )
        self.assertFalse(
            result["claim_flags"]["PHYSICAL_TRANSFERRED_Q2_PROJECTED"]
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


if __name__ == "__main__":
    unittest.main()
