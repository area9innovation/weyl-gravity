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


builder = module(HERE / "build_strict_386_full_q1_split_sign_gate.py", "strict_q1_sign_gate_builder_test")
checker = module(HERE / "check_strict_386_full_q1_split_sign_gate.py", "strict_q1_sign_gate_checker_test")


class Strict386FullQ1SplitSignGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads((HERE / "certificates/STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1.json").read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])

    def test_generated_current(self) -> None:
        result, report = builder.generated()
        self.assertEqual(result, (HERE / "certificates/STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1.json").read_bytes())
        self.assertEqual(report, (HERE / "REPORT_STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1.md").read_bytes())

    def test_plus_sign_cyclicity_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["exact_replay"]["executable_plus_sign"]["cyclicity_defects"] = 1
        self.assertTrue(checker.check(value))

    def test_minus_sign_cyclicity_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["exact_replay"]["declared_minus_sign"]["cyclicity_defects"] = 0
        self.assertTrue(checker.check(value))

    def test_text_matrix_consistency_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["sign_conflict"]["text_matrix_consistent"] = True
        self.assertTrue(checker.check(value))

    def test_unapplied_repair_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["repair_analysis"]["repair_applied"] = True
        self.assertTrue(checker.check(value))

    def test_full_q1_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["STRICT_FULL_386_Q1_PORTABLE_COMPONENT_BYTES"] = True
        self.assertTrue(checker.check(value))

    def test_quantum_promotions_fail(self) -> None:
        for key in ("CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
            value = deepcopy(self.value)
            value["claim_flags"][key] = True
            self.assertTrue(checker.check(value), key)


if __name__ == "__main__":
    unittest.main()
