from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
VERIFY = ROOT / "quantum-weyl/classical_import/verify_classical_import_gate_v2_reconciliation.py"
spec = importlib.util.spec_from_file_location("classical_import_gate_v2_verifier", VERIFY)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
verify = module.verify
RESULT = module.RESULT
REPORT = module.REPORT


class ClassicalImportGateV2ReconciliationTests(unittest.TestCase):
    def value(self) -> dict:
        return json.loads(RESULT.read_text())

    def test_repository_result(self):
        self.assertEqual(verify()[0], [])

    def test_berger_q2_relabel_fails(self):
        value = self.value()
        value["export_reconciliation"][3]["status"] = "RECEIVER_VERIFIED_SCOPED"
        self.assertTrue(verify(result=value)[0])

    def test_auxiliary_projection_relabel_fails(self):
        value = self.value()
        value["export_reconciliation"][11]["status"] = "RECEIVER_VERIFIED_SCOPED"
        self.assertTrue(verify(result=value)[0])

    def test_causal_homotopy_relabel_fails(self):
        value = self.value()
        value["export_reconciliation"][12]["status"] = "RECEIVER_VERIFIED_SCOPED"
        self.assertTrue(verify(result=value)[0])

    def test_gate_promotion_fails(self):
        value = self.value()
        value["gate_disposition"]["gate_a_status"] = "VERIFIED"
        self.assertTrue(verify(result=value)[0])

    def test_common_hash_invention_fails(self):
        value = self.value()
        value["required_hash_disposition"]["q2_hash"]["accepted"] = "0" * 64
        self.assertTrue(verify(result=value)[0])

    def test_publishability_promotion_fails(self):
        value = self.value()
        value["claim_flags"]["PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A"] = True
        self.assertTrue(verify(result=value)[0])

    def test_standalone_replay_hash_drift_fails(self):
        value = self.value()
        value["standalone_history_replay"]["verifier_sources"][0]["sha256"] = "0" * 64
        self.assertTrue(verify(result=value)[0])

    def test_report_drift_fails(self):
        self.assertTrue(verify(report=REPORT.read_text() + "drift\n")[0])


if __name__ == "__main__":
    unittest.main()
