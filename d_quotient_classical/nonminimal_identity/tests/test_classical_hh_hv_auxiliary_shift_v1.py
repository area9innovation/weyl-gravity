from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "d_quotient_classical/nonminimal_identity/classical_hh_hv_auxiliary_shift_v1.py"
CHECKER = ROOT / "d_quotient_classical/nonminimal_identity/check_classical_hh_hv_auxiliary_shift_v1.py"
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_HH_HV_AUXILIARY_SHIFT_V1.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class HhHvAuxiliaryShiftTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load(SOURCE, "classical_hh_hv_source")
        cls.checker = load(CHECKER, "classical_hh_hv_checker")
        cls.value = json.loads(RESULT.read_text())

    def test_generated_current(self):
        self.assertEqual(self.source.generated()[0], RESULT.read_bytes())

    def test_fast_independent_bivariate_replay(self):
        self.assertEqual(self.checker.check(self.value), [])

    def test_exact_counts_and_curvature(self):
        tables = self.value["field_component_tables"]
        self.assertEqual(len(tables["hh_second_Frechet"]["entries"]), 1392)
        self.assertEqual(len(tables["hv_second_Frechet"]["entries"]), 76)
        self.assertTrue(tables["cylinder_curvature_regression"]["matches_unit_cylinder"])

    def test_nonlinear_weyl_identity(self):
        regression = self.value["field_component_tables"]["nonlinear_Weyl_second_variation_regression"]
        self.assertEqual((regression["component_checks"], regression["defects"]), (1200, 0))

    def test_fail_closed_receiver_boundary(self):
        flags = self.value["claim_flags"]
        self.assertFalse(flags["HH_HV_COTANGENT_PARTNERS_SERIALIZED"])
        self.assertFalse(flags["FULL_386_QUADRATIC_BV_COTANGENT_LIFT_SERIALIZED"])
        self.assertFalse(flags["CLASSICAL_IMPORT_GATE_PASSED"])

    def test_mutation_detected(self):
        changed = json.loads(json.dumps(self.value))
        changed["field_component_tables"]["hv_second_Frechet"]["entries"][0]["second_Frechet_coefficient"] = "99"
        self.assertTrue(self.checker.check(changed))


if __name__ == "__main__":
    unittest.main()
