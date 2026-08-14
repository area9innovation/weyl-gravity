from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
VERIFY = ROOT / "foundations/verify_lorentzian_weyl_bv_completion_atlas_v3.py"
spec = importlib.util.spec_from_file_location("completion_atlas_v3_verifier", VERIFY)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
verify = module.verify
checker = module.checker
RESULT = module.RESULT
REPORT = module.REPORT


class CompletionAtlasV3Tests(unittest.TestCase):
    def value(self) -> dict:
        return json.loads(RESULT.read_text())

    def repin(self, value: dict) -> None:
        value["independent_checker"]["expected_digest"] = checker.digest(value)

    def test_repository_result(self):
        self.assertEqual(verify()[0], [])

    def test_gate_a_promotion_fails(self):
        value = self.value()
        value["classical_import_reconciliation"]["gate"] = "VERIFIED"
        value["claim_flags"]["strict_pure_weyl_classical_gate_passed"] = True
        self.repin(value)
        self.assertTrue(verify(value=value)[0])

    def test_finite_sdr_continuum_promotion_fails(self):
        value = self.value()
        value["claim_flags"]["strict_full_support_local_residual_sdr_constructed"] = True
        self.assertTrue(verify(value=value)[0])

    def test_missing_portable_objects_cannot_reopen(self):
        value = self.value()
        value["classical_import_reconciliation"]["missing_portable_objects"] = 3
        self.repin(value)
        self.assertTrue(verify(value=value)[0])

    def test_unrelated_branch_mutation_fails(self):
        value = self.value()
        value["branches"][1]["stages"][0]["statement"] += " drift"
        self.repin(value)
        self.assertTrue(verify(value=value)[0])

    def test_berger_chain_mutation_fails(self):
        value = self.value()
        value["berger_h26_c26_decision_chain"][8]["classification"] = "GLOBAL_NO_GO"
        self.repin(value)
        self.assertTrue(verify(value=value)[0])

    def test_route_order_guarded(self):
        value = self.value()
        value["route_selection"][0], value["route_selection"][1] = value["route_selection"][1], value["route_selection"][0]
        self.repin(value)
        self.assertTrue(verify(value=value)[0])

    def test_provenance_drift_fails(self):
        value = self.value()
        value["provenance"]["inputs"][-1]["sha256"] = "0" * 64
        self.assertTrue(verify(value=value)[0])

    def test_report_drift_fails(self):
        self.assertTrue(verify(report=REPORT.read_text() + "drift\n")[0])


if __name__ == "__main__":
    unittest.main()
