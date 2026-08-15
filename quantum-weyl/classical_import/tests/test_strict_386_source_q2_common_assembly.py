from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
BUILDER = ROOT / "quantum-weyl/classical_import/build_strict_386_source_q2_common_assembly.py"
CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_386_source_q2_common_assembly.py"
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class Strict386SourceQ2CommonAssemblyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load(BUILDER, "strict_386_source_q2_builder")
        cls.checker = load(CHECKER, "strict_386_source_q2_checker")
        cls.value = json.loads(RESULT.read_text())

    def test_generated_current(self):
        self.assertEqual(self.builder.generated()[0], RESULT.read_bytes())

    def test_independent_common_snapshot_replay(self):
        self.assertEqual(self.checker.check(self.value), [])

    def test_q2_common_union_and_identities(self):
        self.assertTrue(self.value["claim_flags"]["FULL_SHIFTED_SOURCE_Q2_COMMON_UNION_ASSEMBLED"])
        self.assertEqual(self.value["source_q2_snapshot"]["auxiliary_ordered_component_coefficients"], 2064)
        self.assertEqual(self.value["q1_q2_replay"]["graph_386_q1_q2_defects"], 0)
        self.assertEqual(self.value["q2_cyclicity_replay"]["graph_386_q2_cyclicity_defects"], 0)

    def test_q3_and_gate_remain_fail_closed(self):
        self.assertFalse(self.value["claim_flags"]["FULL_SOURCE_Q3_ASSEMBLED"])
        self.assertFalse(self.value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"])
        self.assertEqual(self.value["q3_boundary"]["Gate_A_disposition"], "FAIL_CLOSED")

    def test_mutation_detected(self):
        changed = json.loads(json.dumps(self.value))
        changed["source_q2_snapshot"]["auxiliary_ordered_component_coefficients"] = 2063
        self.assertTrue(self.checker.check(changed))


if __name__ == "__main__":
    unittest.main()
