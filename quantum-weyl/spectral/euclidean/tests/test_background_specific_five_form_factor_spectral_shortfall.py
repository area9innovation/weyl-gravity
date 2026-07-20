from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
MODULE_PATH = (
    HERE.parent
    / "verify_background_specific_five_form_factor_spectral_shortfall.py"
)
SPEC = importlib.util.spec_from_file_location("background_spectral_shortfall", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

CERTIFICATE = (
    HERE.parent
    / "certificates/BACKGROUND_SPECIFIC_FIVE_FORM_FACTOR_SPECTRAL_REALIZATION_SHORTFALL.json"
)


class BackgroundSpecificFiveFormFactorSpectralShortfallTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(CERTIFICATE.read_text())

    def assert_rejected(self, payload: dict) -> None:
        with self.assertRaises((AssertionError, ValueError)):
            MODULE.verify(payload)

    def test_exact_replay(self) -> None:
        MODULE.verify(copy.deepcopy(self.payload))

    def test_scalar_flatness_mutation_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["candidate_background"]["scalar_curvature"]["numerator"] = 1
        self.assert_rejected(payload)

    def test_resolvent_promotion_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["receiver_audit"][
            "complete_primed_resolvent_or_spectral_measure"
        ] = True
        self.assert_rejected(payload)

    def test_five_function_promotion_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["claim_flags"][
            "BACKGROUND_SPECIFIC_FIVE_FUNCTION_VALUES_COMPUTED"
        ] = True
        self.assert_rejected(payload)

    def test_special_interpolation_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["claim_flags"]["SPECIAL_BACKGROUND_INTERPOLATION_USED"] = True
        self.assert_rejected(payload)

    def test_qme_promotion_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["claim_flags"]["QME_OR_LORENTZIAN_PROMOTED"] = True
        self.assert_rejected(payload)


if __name__ == "__main__":
    unittest.main()
