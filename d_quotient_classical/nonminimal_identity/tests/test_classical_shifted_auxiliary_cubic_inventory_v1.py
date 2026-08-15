from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "d_quotient_classical/nonminimal_identity/classical_shifted_auxiliary_cubic_inventory_v1.py"
CHECKER = ROOT / "d_quotient_classical/nonminimal_identity/check_classical_shifted_auxiliary_cubic_inventory_v1.py"
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class CubicInventoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load(SOURCE, "cubic_inventory_source")
        cls.checker = load(CHECKER, "cubic_inventory_checker")
        cls.value = json.loads(RESULT.read_text())

    def test_generated_current(self):
        self.assertEqual(self.source.generated()[0], RESULT.read_bytes())

    def test_independent_checker(self):
        self.assertEqual(self.checker.check(self.value), [])

    def test_exact_counts(self):
        self.assertEqual(len(self.value["shifted_auxiliary_mass_vertex"]["entries"]), 72)
        self.assertEqual(len(self.value["quadratic_vv_field_map"]["entries"]), 22)

    def test_conformal_trace(self):
        self.assertEqual(self.value["shifted_auxiliary_mass_vertex"]["pure_trace_h_defects"], 0)

    def test_fail_closed(self):
        flags = self.value["claim_flags"]
        self.assertFalse(flags["EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS"])
        self.assertFalse(flags["FULL_COMPONENT_COEFFICIENT_INVENTORY"])
        self.assertFalse(flags["CLASSICAL_IMPORT_GATE_PASSED"])

    def test_mutation_detected(self):
        changed = json.loads(json.dumps(self.value))
        changed["shifted_auxiliary_mass_vertex"]["entries"][0]["homogeneous_polynomial_coefficient"] = "0"
        self.assertTrue(self.checker.check(changed))


if __name__ == "__main__":
    unittest.main()
