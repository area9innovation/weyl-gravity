from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "quantum-weyl/classical_import/build_classical_import_gate_v13_reconciliation.py"
CHECKER = ROOT / "quantum-weyl/classical_import/check_classical_import_gate_v13_reconciliation.py"
RESULT = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V13_RECONCILIATION.json"
REPORT = ROOT / "quantum-weyl/classical_import/REPORT_GATE_V13.md"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "gate_v13_source")
checker = load(CHECKER, "gate_v13_checker")


class GateV13Tests(unittest.TestCase):
    def test_generated_current(self):
        certificate, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_gate_boundary(self):
        value = producer.build()
        self.assertEqual(checker.check(value), [])
        self.assertTrue(value["claim_flags"]["STRICT_386_EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS"])
        self.assertFalse(value["claim_flags"]["STRICT_386_FULL_SOURCE_Q2_ASSEMBLED"])
        self.assertEqual(value["gate_disposition"]["accepted_common_snapshot_hashes"], 0)

    def test_exhaustive_mutation_rejected(self):
        value = json.loads(RESULT.read_text())
        value["m2_shifted_cubic_inventory_resolution"]["exhaustive_full_nonlinear_BV_family_census"] = False
        self.assertTrue(checker.check(value))

    def test_q2_promotion_rejected(self):
        value = copy.deepcopy(producer.build())
        value["claim_flags"]["STRICT_386_FULL_SOURCE_Q2_ASSEMBLED"] = True
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
