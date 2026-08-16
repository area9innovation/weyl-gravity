from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from foundations.build_lorentzian_weyl_bv_completion_atlas_v35 import build, generated
from foundations.check_lorentzian_weyl_bv_completion_atlas_v35 import check


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V35.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v35.md"


class AtlasV35Tests(unittest.TestCase):
    def test_generated_current(self):
        result, report = generated()
        self.assertEqual(RESULT.read_bytes(), result)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_centered_projection_and_gate_boundary(self):
        value = build()
        self.assertEqual(check(value), [])
        self.assertTrue(value["claim_flags"]["strict_M6_centered_representatives_complete"])
        self.assertFalse(value["claim_flags"]["strict_representative_hash_common_bound"])
        self.assertEqual(value["strict_gate_v17_reconciliation"]["accepted_top_level_hashes"], 1)

    def test_false_gate_promotion_rejected(self):
        value = json.loads(RESULT.read_text())
        value["claim_flags"]["strict_pure_weyl_classical_gate_passed"] = True
        self.assertTrue(check(value))

    def test_route_mutation_rejected(self):
        value = copy.deepcopy(build())
        value["route_selection"][0]["route"] = "STRICT_CENTERED_H3_H4_H5_REPRESENTATIVE_PAYLOAD"
        self.assertTrue(check(value))


if __name__ == "__main__":
    unittest.main()
