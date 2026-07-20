from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
MODULE_PATH = (
    HERE.parent / "verify_scalar_flat_berger_schur_surrogate_obstruction.py"
)
SPEC = importlib.util.spec_from_file_location(
    "verify_scalar_flat_berger_schur_surrogate_obstruction", MODULE_PATH
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

CERTIFICATE = (
    HERE.parent
    / "certificates/SCALAR_FLAT_BERGER_SCHUR_SURROGATE_OBSTRUCTION.json"
)


class ScalarFlatBergerSchurSurrogateObstructionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(CERTIFICATE.read_text())

    def assert_rejected(self, payload: dict) -> None:
        with self.assertRaises((AssertionError, ValueError)):
            MODULE.verify(payload)

    def test_independent_replay(self) -> None:
        MODULE.verify(copy.deepcopy(self.payload))

    def test_principal_symbol_mutation_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["operator_obstruction"]["surrogate_principal_symbol_witnesses"][
            1
        ]["surrogate_principal_symbol"]["numerator"] = 4
        self.assert_rejected(payload)

    def test_lowest_block_mutation_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["operator_obstruction"]["lowest_block"][
            "one_inverse_surrogate_t_derivative"
        ]["numerator"] = 5
        self.assert_rejected(payload)

    def test_true_resolvent_promotion_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["claim_flags"][
            "COMPLETE_PRIMED_SCHUR_RESOLVENT_COMPUTED"
        ] = True
        self.assert_rejected(payload)

    def test_five_functions_promotion_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["claim_flags"][
            "FIVE_BACKGROUND_SPECIFIC_FUNCTIONS_COMPUTED"
        ] = True
        self.assert_rejected(payload)

    def test_qme_or_lorentzian_promotion_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["claim_flags"]["QME_OR_LORENTZIAN_PROMOTED"] = True
        self.assert_rejected(payload)


if __name__ == "__main__":
    unittest.main()
