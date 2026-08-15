from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
VERIFY = ROOT / "foundations/verify_lorentzian_weyl_bv_completion_atlas_v4.py"
spec = importlib.util.spec_from_file_location("completion_atlas_v4_verifier", VERIFY)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
verify = module.verify
checker = module.checker
RESULT = module.RESULT
REPORT = module.REPORT


class CompletionAtlasV4Tests(unittest.TestCase):
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

    def test_common_byte_promotion_fails(self):
        value = self.value()
        value["strict_causal_sign_transport"]["common_bytes_identified"] = True
        value["claim_flags"]["strict_386_common_bytes_identified"] = True
        self.repin(value)
        self.assertTrue(verify(value=value)[0])

    def test_nonlinear_promotion_fails(self):
        value = self.value()
        value["strict_causal_sign_transport"]["nonlinear_stage_preserved"] = True
        value["claim_flags"]["strict_386_q2_green_compatibility_certified"] = True
        self.repin(value)
        self.assertTrue(verify(value=value)[0])

    def test_cyclic_count_mutation_fails(self):
        value = self.value()
        value["strict_gate_a_progress"]["minimal_cyclic_control"]["translated_defects"] = 1
        self.repin(value)
        self.assertTrue(verify(value=value)[0])

    def test_sign_count_mutation_fails(self):
        value = self.value()
        value["strict_causal_sign_transport"]["negative_signs"] = 4
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

    def test_report_drift_fails(self):
        self.assertTrue(verify(report=REPORT.read_text() + "drift\n")[0])


if __name__ == "__main__":
    unittest.main()
