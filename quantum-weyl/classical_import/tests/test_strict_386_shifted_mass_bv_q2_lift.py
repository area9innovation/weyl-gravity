from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
BUILDER = ROOT / "quantum-weyl/classical_import/build_strict_386_shifted_mass_bv_q2_lift.py"
CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_386_shifted_mass_bv_q2_lift.py"
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class Strict386ShiftedMassBVQ2LiftTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load(BUILDER, "strict_386_shifted_mass_builder")
        cls.checker = load(CHECKER, "strict_386_shifted_mass_checker")
        cls.value = json.loads(RESULT.read_text())

    def test_generated_current(self):
        self.assertEqual(self.builder.generated()[0], RESULT.read_bytes())

    def test_independent_formula_and_pairing_replay(self):
        self.assertEqual(self.checker.check(self.value), [])

    def test_exact_cyclicity(self):
        self.assertEqual(self.value["exact_replay"]["cyclicity_equalities_checked"], 3000)
        self.assertEqual(self.value["exact_replay"]["cyclicity_defects"], 0)

    def test_full_assembly_remains_fail_closed(self):
        self.assertTrue(self.value["claim_flags"]["SHIFTED_MASS_Q2_COMPONENT_TABLES_SERIALIZED"])
        self.assertFalse(self.value["claim_flags"]["FULL_SOURCE_Q2_ASSEMBLED"])
        self.assertFalse(self.value["claim_flags"]["FULL_Q1_Q2_IDENTITY_REPLAYED"])

    def test_mutation_detected(self):
        changed = json.loads(json.dumps(self.value))
        changed["shifted_mass_q2_lift"]["metric_antifield_output_entries"][0]["coefficient"] = "29"
        self.assertTrue(self.checker.check(changed))


if __name__ == "__main__":
    unittest.main()
