from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE.parent / "verify_berger_schur_spectral_receiver_nondefinition.py"
SPEC = importlib.util.spec_from_file_location("verify_berger_receiver_nondefinition", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
CERTIFICATE = HERE.parent / "certificates/BERGER_SCHUR_SPECTRAL_RECEIVER_NONDEFINITION_V1.json"


class BergerReceiverNondefinitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = json.loads(CERTIFICATE.read_text())

    def test_independent_replay(self) -> None:
        MODULE.verify(copy.deepcopy(self.certificate))

    def test_computed_carrier_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["receiver"]["carrier_ledger"][0]["complete_function_status"] = "COMPUTED"
        with self.assertRaises(ValueError):
            MODULE.verify(mutated)

    def test_landed_m23_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["external_math_requests"]["M23"]["status"] = "LANDED"
        with self.assertRaises(ValueError):
            MODULE.verify(mutated)

    def test_scalar_surrogate_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["claim_flags"]["SCALAR_SURROGATE_USED"] = True
        with self.assertRaises(ValueError):
            MODULE.verify(mutated)

    def test_qme_promotion_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["claim_flags"]["QME_OR_LORENTZIAN_HADAMARD_PROMOTED"] = True
        with self.assertRaises(ValueError):
            MODULE.verify(mutated)

    def test_rank_change_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["receiver"]["ambiguity_matrix"][0][0] = 0
        with self.assertRaises(AssertionError):
            MODULE.verify(mutated)


if __name__ == "__main__":
    unittest.main()
