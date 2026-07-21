from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE.parent / "verify_scalar_flat_berger_vector_schur_high_mode_trace_obstruction.py"
SPEC = importlib.util.spec_from_file_location("verify_berger_high_mode_trace_obstruction", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
CERTIFICATE = HERE.parent / "certificates/SCALAR_FLAT_BERGER_VECTOR_SCHUR_HIGH_MODE_TRACE_MAJORANT_OBSTRUCTION_V1.json"


class HighModeTraceObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = json.loads(CERTIFICATE.read_text())

    def test_independent_replay(self) -> None:
        MODULE.verify(copy.deepcopy(self.certificate))

    def test_wrong_insertion_coefficient_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["first_insertion"]["first_insertion_eigenvalue"] = "b1_jm=-p_jm/(2*q_jm^2)"
        with self.assertRaises(AssertionError):
            MODULE.verify(mutated)

    def test_false_shell_bound_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["exact_shell_witnesses"][0]["absolute_shell_contribution"] = "0"
        with self.assertRaises(AssertionError):
            MODULE.verify(mutated)

    def test_qme_promotion_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["claim_flags"]["ANOMALY_COEFFICIENT_OR_QME_COMPUTED"] = True
        with self.assertRaises(ValueError):
            MODULE.verify(mutated)

    def test_lorentzian_promotion_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["claim_flags"]["LORENTZIAN_OR_HADAMARD_PROMOTED"] = True
        with self.assertRaises(ValueError):
            MODULE.verify(mutated)


if __name__ == "__main__":
    unittest.main()
