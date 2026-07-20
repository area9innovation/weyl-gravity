from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
MODULE_PATH = (
    HERE.parent / "verify_parameterized_five_form_factor_independent_audit.py"
)
SPEC = importlib.util.spec_from_file_location("parameterized_audit_verify", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

CERTIFICATE = (
    HERE.parent
    / "certificates/PARAMETERIZED_PARITY_EVEN_FIVE_FORM_FACTOR_FAMILY_INDEPENDENT_AUDIT.json"
)


class ParameterizedFiveFormFactorIndependentAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(CERTIFICATE.read_text())

    def assert_rejected(self, payload: dict) -> None:
        with self.assertRaises((AssertionError, ValueError)):
            MODULE.verify(payload)

    def test_exact_replay(self) -> None:
        MODULE.verify(copy.deepcopy(self.payload))

    def test_rank_drop_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["global_completion_audit"]["ambiguity_matrix"][9] = [0] * 10
        self.assert_rejected(payload)

    def test_relation_mutation_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["carrier_quotient_audit"]["relation_vector"][7] = 0
        self.assert_rejected(payload)

    def test_zero_third_variation_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["global_completion_audit"]["finite_matrix_model"][
            "mixed_third_log_determinant_shift"
        ]["numerator"] = 0
        self.assert_rejected(payload)

    def test_special_background_interpolation_promotion_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["zero_mode_and_holdout_audit"][
            "special_background_interpolation_used"
        ] = True
        self.assert_rejected(payload)

    def test_universal_table_promotion_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["claim_flags"][
            "COMPLETE_UNIVERSAL_BV_FIVE_FUNCTION_TABLE_COMPUTED"
        ] = True
        self.assert_rejected(payload)

    def test_qme_promotion_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["claim_flags"]["QME_OR_LORENTZIAN_PROMOTED"] = True
        self.assert_rejected(payload)


if __name__ == "__main__":
    unittest.main()
