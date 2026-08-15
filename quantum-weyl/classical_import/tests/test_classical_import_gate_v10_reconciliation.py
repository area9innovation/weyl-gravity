from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V10_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V10.md"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


CHECK = module("gate_v10_check_test", HERE / "check_classical_import_gate_v10_reconciliation.py")
VERIFY = module("gate_v10_verify_test", HERE / "verify_classical_import_gate_v10_reconciliation.py")


class GateV10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text())
        cls.report = REPORT.read_text()

    def test_repository(self):
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_generated(self):
        result = subprocess.run([sys.executable, str(HERE / "build_classical_import_gate_v10_reconciliation.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def mutation_fails(self, mutate):
        value = copy.deepcopy(self.value)
        mutate(value)
        self.assertTrue(CHECK.check(value))

    def test_family_count_mutation(self):
        self.mutation_fails(lambda value: value["m2_shifted_cubic_inventory_resolution"].__setitem__("known_required_cubic_block_families", 8))

    def test_canonicality_mutation(self):
        self.mutation_fails(lambda value: value["m2_shifted_cubic_inventory_resolution"].__setitem__("vv_canonicality_defects", 1))

    def test_full_lift_overclaim(self):
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("STRICT_386_FULL_BV_COTANGENT_LIFT_SERIALIZED", True))

    def test_gate_promotion(self):
        self.mutation_fails(lambda value: value["gate_disposition"].__setitem__("gate_a_status", "PASS"))

    def test_float_fails(self):
        value = copy.deepcopy(self.value)
        value["m2_shifted_cubic_inventory_resolution"]["carrier_rows"] = 386.0
        self.assertTrue(VERIFY.verify(value, self.report))


if __name__ == "__main__":
    unittest.main()
