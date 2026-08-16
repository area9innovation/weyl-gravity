from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
SOURCE = HERE / "build_classical_import_gate_v16_reconciliation.py"
CHECKER = HERE / "check_classical_import_gate_v16_reconciliation.py"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V16_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V16.md"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "gate_v16_source")
checker = load(CHECKER, "gate_v16_checker")


class GateV16Tests(unittest.TestCase):
    def test_generated_current(self):
        certificate, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_m5_payload_ready_gate_still_closed(self):
        value = producer.build()
        self.assertEqual(checker.check(value), [])
        self.assertTrue(value["claim_flags"]["M5_RESIDUAL_EXACT_PAYLOAD_COMPLETE"])
        self.assertFalse(value["claim_flags"]["COMMON_GATE_A_FREEZE_BOUND"])
        self.assertFalse(value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"])
        self.assertEqual(len(value["minimal_missing_bundle"]), 4)

    def test_candidate_cannot_be_silently_accepted(self):
        value = copy.deepcopy(json.loads(RESULT.read_text()))
        value["required_hash_disposition"]["zero_mode_basis_hash"]["accepted"] = value["required_hash_disposition"]["zero_mode_basis_hash"]["candidate"]
        self.assertTrue(checker.check(value))

    def test_false_gate_promotion_rejected(self):
        value = copy.deepcopy(json.loads(RESULT.read_text()))
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        self.assertTrue(checker.check(value))

    def test_status_count_drift_rejected(self):
        value = copy.deepcopy(json.loads(RESULT.read_text()))
        value["gate_disposition"]["same_theory_receiver_verified_scoped"] = 19
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
