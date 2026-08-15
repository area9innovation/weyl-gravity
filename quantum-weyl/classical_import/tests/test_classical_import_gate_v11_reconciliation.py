from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "quantum-weyl/classical_import/build_classical_import_gate_v11_reconciliation.py"
CHECKER = ROOT / "quantum-weyl/classical_import/check_classical_import_gate_v11_reconciliation.py"
RESULT = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V11_RECONCILIATION.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class ClassicalImportGateV11Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load(SOURCE, "gate_v11_source")
        cls.checker = load(CHECKER, "gate_v11_checker")
        cls.value = json.loads(RESULT.read_text())

    def test_generated_current(self):
        self.assertEqual(self.source.generated()[0], RESULT.read_bytes())

    def test_independent_checker(self):
        self.assertEqual(self.checker.check(self.value), [])

    def test_quadratic_lift_projection(self):
        result = self.value["m2_hh_hv_cotangent_resolution"]
        self.assertEqual((result["hh_field_coefficients"], result["hv_field_coefficients"], result["combined_cotangent_coefficients"], result["formal_adjoint_defects"]), (1392, 76, 3907, 0))

    def test_gate_stays_fail_closed(self):
        self.assertEqual(self.value["gate_disposition"]["gate_a_status"], "FAIL_CLOSED")
        self.assertEqual(self.value["gate_disposition"]["accepted_common_snapshot_hashes"], 0)
        self.assertFalse(self.value["claim_flags"]["STRICT_386_FULL_SOURCE_Q2_PULLBACK_REPLAYED"])
        self.assertFalse(self.value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"])

    def test_mutation_detected(self):
        changed = json.loads(json.dumps(self.value))
        changed["m2_hh_hv_cotangent_resolution"]["combined_cotangent_coefficients"] += 1
        self.assertTrue(self.checker.check(changed))


if __name__ == "__main__":
    unittest.main()
