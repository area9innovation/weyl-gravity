from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "quantum-weyl/classical_import/build_classical_import_gate_v12_reconciliation.py"
CHECKER = ROOT / "quantum-weyl/classical_import/check_classical_import_gate_v12_reconciliation.py"
RESULT = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V12_RECONCILIATION.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class ClassicalImportGateV12Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load(SOURCE, "gate_v12_source")
        cls.checker = load(CHECKER, "gate_v12_checker")
        cls.value = json.loads(RESULT.read_text())

    def test_generated_current(self):
        self.assertEqual(self.source.generated()[0], RESULT.read_bytes())

    def test_independent_checker(self):
        self.assertEqual(self.checker.check(self.value), [])

    def test_diff_projection(self):
        result = self.value["m2_diff_auxiliary_resolution"]
        self.assertEqual((result["master_density_coefficients"], result["field_output_coefficients"], result["antifield_output_coefficients"], result["c_star_output_coefficients"]), (264, 336, 632, 704))

    def test_known_complete_but_gate_fail_closed(self):
        self.assertEqual(self.value["m2_shifted_cubic_inventory_resolution"]["component_complete_families"], 7)
        self.assertFalse(self.value["m2_shifted_cubic_inventory_resolution"]["exhaustive_full_nonlinear_BV_family_census"])
        self.assertEqual(self.value["gate_disposition"]["gate_a_status"], "FAIL_CLOSED")
        self.assertEqual(self.value["gate_disposition"]["accepted_common_snapshot_hashes"], 0)

    def test_mutation_detected(self):
        changed = json.loads(json.dumps(self.value))
        changed["m2_diff_auxiliary_resolution"]["c_star_output_coefficients"] += 1
        self.assertTrue(self.checker.check(changed))


if __name__ == "__main__":
    unittest.main()
