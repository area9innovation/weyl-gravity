from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_strict_386_auxiliary_q_sign_repair.py", "test_strict_q_sign_repair_builder")
checker = module(HERE / "check_strict_386_auxiliary_q_sign_repair.py", "test_strict_q_sign_repair_checker")
RESULT = HERE / "certificates/STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1.json"
REPORT = HERE / "REPORT_STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1.md"


class Strict386AuxiliaryQSignRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])

    def test_generated_current(self) -> None:
        result, report = builder.generated()
        self.assertEqual(RESULT.read_bytes(), result)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_repair_revocation_fails(self) -> None:
        value = deepcopy(self.value)
        value["repair"]["repair_applied"] = False
        self.assertTrue(checker.check(value))

    def test_pairing_regression_fails(self) -> None:
        value = deepcopy(self.value)
        value["exact_replay"]["repaired_plus_sign"]["odd_pairing_cyclicity_defects"] = 8
        self.assertTrue(checker.check(value))

    def test_full_q1_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["STRICT_FULL_386_Q1_PORTABLE_COMPONENT_BYTES"] = True
        self.assertTrue(checker.check(value))

    def test_quantum_promotions_fail(self) -> None:
        for key in ("HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
            value = deepcopy(self.value)
            value["claim_flags"][key] = True
            self.assertTrue(checker.check(value), key)


if __name__ == "__main__":
    unittest.main()
