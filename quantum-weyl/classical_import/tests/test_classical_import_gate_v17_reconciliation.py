from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
SOURCE = HERE / "build_classical_import_gate_v17_reconciliation.py"
CHECKER = HERE / "check_classical_import_gate_v17_reconciliation.py"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V17_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V17.md"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "classical_import_gate_v17_source")
checker = load(CHECKER, "classical_import_gate_v17_checker")


class ClassicalImportGateV17Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_generated_current(self):
        certificate, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_repository_gate_replays(self):
        self.assertEqual(checker.check(copy.deepcopy(self.value)), [])
        self.assertEqual(len(self.value["minimal_missing_bundle"]), 3)

    def test_false_hash_acceptance_fails(self):
        value = copy.deepcopy(self.value)
        value["required_hash_disposition"]["representative_hash"]["accepted"] = value["required_hash_disposition"]["representative_hash"]["candidate"]
        self.assertTrue(checker.check(value, replay_centered=False))

    def test_m6_reintroduction_fails(self):
        value = copy.deepcopy(self.value)
        value["minimal_missing_bundle"].append({"id": "M6_CENTERED_REPRESENTATIVES"})
        self.assertTrue(checker.check(value, replay_centered=False))

    def test_false_gate_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        self.assertTrue(checker.check(value, replay_centered=False))


if __name__ == "__main__":
    unittest.main()
