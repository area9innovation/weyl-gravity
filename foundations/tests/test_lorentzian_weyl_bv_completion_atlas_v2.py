from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
VERIFY = ROOT / "foundations/verify_lorentzian_weyl_bv_completion_atlas_v2.py"
spec = importlib.util.spec_from_file_location("completion_atlas_v2_verifier", VERIFY)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
verify = module.verify
RESULT = module.RESULT
REPORT = module.REPORT


class CompletionAtlasV2Tests(unittest.TestCase):
    def value(self) -> dict:
        return json.loads(RESULT.read_text())

    def test_repository_result(self):
        self.assertEqual(verify()[0], [])

    def test_general_noncone_no_go_promotion_fails(self):
        value = self.value()
        value["claim_flags"]["general_noncone_104_row_no_go"] = True
        self.assertTrue(verify(value=value)[0])

    def test_berger_hadamard_promotion_fails(self):
        value = self.value()
        value["claim_flags"]["berger_brst_hadamard_state_constructed"] = True
        self.assertTrue(verify(value=value)[0])

    def test_rank_feasibility_cannot_be_relabelled_no_go(self):
        value = self.value()
        value["berger_h26_c26_decision_chain"][8]["classification"] = "GLOBAL_NONCONE_NO_GO"
        self.assertTrue(verify(value=value)[0])

    def test_berger_first_gate_cannot_skip_normalization(self):
        value = self.value()
        next(item for item in value["branches"] if item["id"] == "BERGER_POSITIVE_CLOCK_54")["first_unclosed_gate"] = "S5_BRST_WARD"
        self.assertTrue(verify(value=value)[0])

    def test_route_order_is_guarded(self):
        value = self.value()
        value["route_selection"][0], value["route_selection"][1] = value["route_selection"][1], value["route_selection"][0]
        self.assertTrue(verify(value=value)[0])

    def test_provenance_drift_fails(self):
        value = self.value()
        value["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.assertTrue(verify(value=value)[0])

    def test_report_drift_fails(self):
        self.assertTrue(verify(report=REPORT.read_text() + "drift\n")[0])


if __name__ == "__main__":
    unittest.main()
