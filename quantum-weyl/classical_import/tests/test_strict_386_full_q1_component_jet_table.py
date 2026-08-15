from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_strict_386_full_q1_component_jet_table.py", "test_strict_full_q1_builder")
checker = module(HERE / "check_strict_386_full_q1_component_jet_table.py", "test_strict_full_q1_checker")
RESULT = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
REPORT = HERE / "REPORT_STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.md"


class Strict386FullQ1ComponentJetTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])

    def test_generated_current(self) -> None:
        result, report = builder.generated()
        self.assertEqual(RESULT.read_bytes(), result)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_coefficient_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        entry = value["q1_serialization"]["tables"][0]["coefficients"][0]["entries"][0]
        entry[2] = str(Fraction(entry[2]) + 1)
        self.assertTrue(checker.check(value))

    def test_suspension_binding_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["unary_snapshot"]["suspension_sha256"] = "0" * 64
        self.assertTrue(checker.check(value))

    def test_gate_a_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["gate_disposition"]["one_common_gate_a_snapshot_hash_accepted"] = True
        value["gate_disposition"]["classical_import_gate_a_status"] = "PASS"
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        self.assertTrue(checker.check(value))

    def test_quantum_promotions_fail(self) -> None:
        for key in ("HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
            value = deepcopy(self.value)
            value["claim_flags"][key] = True
            self.assertTrue(checker.check(value), key)


if __name__ == "__main__":
    unittest.main()
