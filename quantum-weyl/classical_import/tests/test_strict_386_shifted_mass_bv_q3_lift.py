from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
SOURCE = HERE / "build_strict_386_shifted_mass_bv_q3_lift.py"
CHECKER = HERE / "check_strict_386_shifted_mass_bv_q3_lift.py"
RESULT = HERE / "certificates/STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class ShiftedMassQ3LiftTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load(SOURCE, "shifted_mass_q3_source")
        cls.checker = load(CHECKER, "shifted_mass_q3_checker")
        cls.value = json.loads(RESULT.read_text())

    def test_generated_current(self):
        self.assertEqual(self.source.generated()[0], RESULT.read_bytes())

    def test_independent_checker(self):
        self.assertEqual(self.checker.check(self.value), [])

    def test_component_counts(self):
        counts = self.value["shifted_mass_q3_lift"]["component_counts"]
        self.assertEqual(counts["q3_h_f_hat_f_hat_to_h_star_all_input_orders"], 2736)
        self.assertEqual(counts["q3_h_h_f_hat_to_f_hat_star_all_input_orders"], 3216)
        self.assertEqual(counts["total_ordered_q3_coefficients"], 5952)

    def test_cyclicity(self):
        self.assertEqual(self.value["exact_replay"]["cyclicity_defects"], 0)
        self.assertEqual(self.value["exact_replay"]["S3_input_symmetry_defects"], 0)

    def test_fail_closed_before_common_assembly(self):
        flags = self.value["claim_flags"]
        self.assertFalse(flags["FULL_SOURCE_Q3_ASSEMBLED"])
        self.assertFalse(flags["FULL_386_ARITY_THREE_IDENTITY_REPLAYED"])
        self.assertFalse(flags["CLASSICAL_IMPORT_GATE_PASSED"])

    def test_mutation_detected(self):
        changed = json.loads(json.dumps(self.value))
        changed["shifted_mass_q3_lift"]["metric_antifield_output_entries"][0]["coefficient"] = "0"
        self.assertTrue(self.checker.check(changed))


if __name__ == "__main__":
    unittest.main()
