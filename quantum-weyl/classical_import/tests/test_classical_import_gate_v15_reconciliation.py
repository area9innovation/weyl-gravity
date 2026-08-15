from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
SOURCE = HERE / "build_classical_import_gate_v15_reconciliation.py"
CHECKER = HERE / "check_classical_import_gate_v15_reconciliation.py"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V15_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V15.md"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "gate_v15_source")
checker = load(CHECKER, "gate_v15_checker")


class GateV15Tests(unittest.TestCase):
    def test_generated_current(self):
        certificate, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_q3_accepted_gate_still_closed(self):
        value = producer.build()
        self.assertEqual(checker.check(value), [])
        self.assertTrue(value["claim_flags"]["STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED"])
        self.assertFalse(value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"])
        self.assertEqual(len(value["minimal_missing_bundle"]), 5)

    def test_false_gate_promotion_rejected(self):
        value = copy.deepcopy(producer.build())
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        self.assertTrue(checker.check(value))

    def test_q3_hash_mutation_rejected(self):
        value = json.loads(RESULT.read_text())
        value["m2_source_q3_assembly_resolution"]["accepted_q3_sha256"] = "0" * 64
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
