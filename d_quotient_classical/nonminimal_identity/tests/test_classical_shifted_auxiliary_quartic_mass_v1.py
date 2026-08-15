from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "d_quotient_classical/nonminimal_identity/classical_shifted_auxiliary_quartic_mass_v1.py"
CHECKER = ROOT / "d_quotient_classical/nonminimal_identity/check_classical_shifted_auxiliary_quartic_mass_v1.py"
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class QuarticMassTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load(SOURCE, "quartic_mass_source")
        cls.checker = load(CHECKER, "quartic_mass_checker")
        cls.value = json.loads(RESULT.read_text())

    def test_generated_current(self):
        self.assertEqual(self.source.generated()[0], RESULT.read_bytes())

    def test_independent_checker(self):
        self.assertEqual(self.checker.check(self.value), [])

    def test_exact_component_counts(self):
        vertex = self.value["shifted_auxiliary_quartic_mass_vertex"]
        self.assertEqual(len(vertex["entries"]), 321)
        self.assertEqual(vertex["nonzero_ordered_fourth_variation_coefficients"], 912)

    def test_conformal_ward_recursion(self):
        replay = self.value["exact_replay"]
        self.assertEqual(replay["pure_trace_second_variation_defects"], 0)
        self.assertEqual(replay["mixed_conformal_recursion_defects"], 0)

    def test_fail_closed_before_bv_lift(self):
        flags = self.value["claim_flags"]
        self.assertFalse(flags["AUTHORITATIVE_AUXILIARY_Q3_BV_LIFTED"])
        self.assertFalse(flags["FULL_SOURCE_Q3_ASSEMBLED"])
        self.assertFalse(flags["CLASSICAL_IMPORT_GATE_PASSED"])

    def test_mutation_detected(self):
        changed = json.loads(json.dumps(self.value))
        changed["shifted_auxiliary_quartic_mass_vertex"]["entries"][0]["D_h_left_D_h_right_D_f_left_D_f_right"] = "0"
        self.assertTrue(self.checker.check(changed))


if __name__ == "__main__":
    unittest.main()
