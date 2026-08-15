from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
SOURCE = HERE / "build_strict_386_source_q3_common_assembly.py"
CHECKER = HERE / "check_strict_386_source_q3_common_assembly.py"
RESULT = HERE / "certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class SourceQ3CommonAssemblyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load(SOURCE, "source_q3_common_builder")
        cls.checker = load(CHECKER, "source_q3_common_checker")
        cls.value = json.loads(RESULT.read_text())

    def test_generated_current(self):
        self.assertEqual(self.source.generated()[0], RESULT.read_bytes())

    def test_independent_checker(self):
        self.assertEqual(self.checker.check(self.value), [])

    def test_complete_common_snapshot(self):
        self.assertEqual(self.value["family_census"]["total_source_q3_families"], 2)
        self.assertEqual(self.value["source_q3_snapshot"]["auxiliary_ordered_component_coefficients"], 5952)
        self.assertTrue(self.value["claim_flags"]["FULL_SOURCE_Q3_ASSEMBLED"])

    def test_identity_and_cyclicity(self):
        self.assertEqual(self.value["arity_three_replay"]["split_386_arity_three_defects"], 0)
        self.assertEqual(self.value["arity_three_replay"]["graph_386_arity_three_defects"], 0)
        self.assertEqual(self.value["q3_cyclicity_replay"]["graph_386_q3_cyclicity_defects_mod_d"], 0)

    def test_gate_remains_fail_closed(self):
        self.assertFalse(self.value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"])
        self.assertFalse(self.value["claim_flags"]["LORENTZIAN_GREEN_Q3_COMPATIBILITY_CERTIFIED"])

    def test_mutation_detected(self):
        changed = json.loads(json.dumps(self.value))
        changed["source_q3_snapshot"]["auxiliary_ordered_component_coefficients"] = 5951
        self.assertTrue(self.checker.check(changed))


if __name__ == "__main__":
    unittest.main()
