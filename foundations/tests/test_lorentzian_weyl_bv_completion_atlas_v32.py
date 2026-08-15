from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from foundations.build_lorentzian_weyl_bv_completion_atlas_v32 import build, generated
from foundations.check_lorentzian_weyl_bv_completion_atlas_v32 import check


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V32.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v32.md"


class AtlasV32Tests(unittest.TestCase):
    def test_generated_current(self):
        result, report = generated()
        self.assertEqual(RESULT.read_bytes(), result)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_q2_projection_and_q3_boundary(self):
        value = build()
        self.assertEqual(check(value), [])
        self.assertTrue(value["claim_flags"]["strict_386_full_source_q2_assembled"])
        self.assertFalse(value["claim_flags"]["strict_386_full_source_q3_pullback_replayed"])
        self.assertEqual(value["strict_gate_v14_reconciliation"]["accepted_top_level_hashes"], 1)

    def test_q3_promotion_rejected(self):
        value = json.loads(RESULT.read_text())
        value["claim_flags"]["strict_386_full_source_q3_pullback_replayed"] = True
        self.assertTrue(check(value))

    def test_route_mutation_rejected(self):
        value = copy.deepcopy(build())
        value["route_selection"][0]["route"] = "STRICT_SOURCE_Q2_Q3_COMMON_ASSEMBLY_AND_IDENTITIES"
        self.assertTrue(check(value))


if __name__ == "__main__":
    unittest.main()
