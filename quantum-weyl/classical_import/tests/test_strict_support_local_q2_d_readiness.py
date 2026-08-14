from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
VERIFY = ROOT / "quantum-weyl/classical_import/verify_strict_support_local_q2_d_readiness.py"
spec = importlib.util.spec_from_file_location("strict_q2_d_readiness_verifier", VERIFY)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
verify = module.verify
checker = module.checker
RESULT = module.RESULT
REPORT = module.REPORT


class StrictSupportLocalQ2DReadinessTests(unittest.TestCase):
    def value(self) -> dict:
        return json.loads(RESULT.read_text())

    def repin(self, value: dict) -> None:
        value["independent_checker"]["expected_digest"] = checker.digest(value)

    def test_repository_result(self):
        self.assertEqual(verify()[0], [])

    def test_component_payload_promotion_fails(self):
        value = self.value()
        value["claim_flags"]["STRICT_SUPPORT_LOCAL_Q2_COMPONENT_PAYLOAD_CERTIFIED"] = True
        self.assertTrue(verify(value=value)[0])

    def test_hard_bach_kernel_erasure_fails(self):
        value = self.value()
        value["q2_row_readiness"][3]["portable_component_status"] = "NOT_COMPONENT_SERIALIZED"
        self.repin(value)
        self.assertTrue(verify(value=value)[0])

    def test_action_source_term_mutation_fails(self):
        value = self.value()
        value["q2_row_readiness"][0]["source_terms"] = ["invented"]
        self.repin(value)
        self.assertTrue(verify(value=value)[0])

    def test_interaction_identity_promotion_fails(self):
        value = self.value()
        value["proof_gate_readiness"][1]["status"] = "VERIFIED"
        self.repin(value)
        self.assertTrue(verify(value=value)[0])

    def test_all_energy_q2_no_go_promotion_fails(self):
        value = self.value()
        value["claim_flags"]["ALL_ENERGY_SUPPORT_LOCAL_Q2_OBSTRUCTED"] = True
        self.assertTrue(verify(value=value)[0])

    def test_receiver_rank_mutation_fails(self):
        value = self.value()
        value["finite_receiver_obstruction"]["minimum_sdr_defect_rank"] = 63
        self.repin(value)
        self.assertTrue(verify(value=value)[0])

    def test_provenance_drift_fails(self):
        value = self.value()
        value["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.assertTrue(verify(value=value)[0])

    def test_report_drift_fails(self):
        self.assertTrue(verify(report=REPORT.read_text() + "drift\n")[0])


if __name__ == "__main__":
    unittest.main()
