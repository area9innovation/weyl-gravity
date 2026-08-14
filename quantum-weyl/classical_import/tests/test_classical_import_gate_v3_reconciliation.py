from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
VERIFY = ROOT / "quantum-weyl/classical_import/verify_classical_import_gate_v3_reconciliation.py"
spec = importlib.util.spec_from_file_location("classical_import_gate_v3_verifier", VERIFY)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
verify = module.verify
checker = module.checker
RESULT = module.RESULT
REPORT = module.REPORT


class ClassicalImportGateV3ReconciliationTests(unittest.TestCase):
    def value(self) -> dict:
        return json.loads(RESULT.read_text())

    def repin(self, value: dict) -> None:
        value["independent_checker"]["expected_digest"] = checker.digest(value)

    def test_repository_result(self):
        self.assertEqual(verify()[0], [])

    def test_finite_map_full_carrier_relabel_fails(self):
        value = self.value()
        row = next(item for item in value["export_reconciliation"] if item["export_id"] == "classical_inclusion_iota_cl")
        row["boundary"] = "This is the globally complete residual inclusion on every carrier."
        self.repin(value)
        self.assertTrue(verify(result=value)[0])

    def test_scoped_map_evidence_removal_fails(self):
        value = self.value()
        row = next(item for item in value["export_reconciliation"] if item["export_id"] == "classical_projection_pi_cl")
        row["evidence"] = []
        self.repin(value)
        self.assertTrue(verify(result=value)[0])

    def test_unrelated_export_promotion_fails(self):
        value = self.value()
        value["export_reconciliation"][3]["status"] = "RECEIVER_VERIFIED_SCOPED"
        self.repin(value)
        self.assertTrue(verify(result=value)[0])

    def test_gate_promotion_fails(self):
        value = self.value()
        value["gate_disposition"]["gate_a_status"] = "VERIFIED"
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        self.repin(value)
        self.assertTrue(verify(result=value)[0])

    def test_common_hash_invention_fails(self):
        value = self.value()
        value["required_hash_disposition"]["q2_hash"]["accepted"] = "0" * 64
        self.repin(value)
        self.assertTrue(verify(result=value)[0])

    def test_m3_deletion_fails(self):
        value = self.value()
        value["minimal_missing_bundle"] = [
            item for item in value["minimal_missing_bundle"] if item["id"] != "M3_RESIDUAL_SDR"
        ]
        self.repin(value)
        self.assertTrue(verify(result=value)[0])

    def test_scoped_resolution_continuum_promotion_fails(self):
        value = self.value()
        value["m3_scoped_resolution"]["boundary"] = "This proves the complete continuum M3 gate."
        self.repin(value)
        self.assertTrue(verify(result=value)[0])

    def test_predecessor_provenance_drift_fails(self):
        value = self.value()
        value["provenance"]["inputs"][-2]["sha256"] = "0" * 64
        self.assertTrue(verify(result=value)[0])

    def test_report_drift_fails(self):
        self.assertTrue(verify(report=REPORT.read_text() + "drift\n")[0])


if __name__ == "__main__":
    unittest.main()
