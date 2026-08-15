from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "quantum-weyl/classical_import/build_classical_import_gate_v14_reconciliation.py"
CHECKER = ROOT / "quantum-weyl/classical_import/check_classical_import_gate_v14_reconciliation.py"
RESULT = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V14_RECONCILIATION.json"
REPORT = ROOT / "quantum-weyl/classical_import/REPORT_GATE_V14.md"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "gate_v14_source")
checker = load(CHECKER, "gate_v14_checker")


class GateV14Tests(unittest.TestCase):
    def test_generated_current(self):
        certificate, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_q2_hash_accepted_gate_still_closed(self):
        value = producer.build()
        self.assertEqual(checker.check(value), [])
        self.assertTrue(value["claim_flags"]["STRICT_386_FULL_SOURCE_Q2_ASSEMBLED"])
        self.assertFalse(value["claim_flags"]["STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED"])
        self.assertEqual(value["gate_disposition"]["accepted_common_snapshot_hashes"], 1)
        self.assertEqual(value["gate_disposition"]["gate_a_status"], "FAIL_CLOSED")

    def test_q3_mutation_rejected(self):
        value = copy.deepcopy(producer.build())
        value["claim_flags"]["STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED"] = True
        self.assertTrue(checker.check(value))

    def test_hash_mutation_rejected(self):
        value = json.loads(RESULT.read_text())
        value["required_hash_disposition"]["q2_hash"]["accepted"] = "0" * 64
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
