from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from foundations.build_lorentzian_weyl_bv_completion_atlas_v33 import build, generated
from foundations.check_lorentzian_weyl_bv_completion_atlas_v33 import check


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V33.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v33.md"


class AtlasV33Tests(unittest.TestCase):
    def test_generated_current(self):
        result, report = generated()
        self.assertEqual(RESULT.read_bytes(), result)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_q3_projection_and_gate_boundary(self):
        value = build()
        self.assertEqual(check(value), [])
        self.assertTrue(value["claim_flags"]["strict_386_full_source_q3_pullback_replayed"])
        self.assertFalse(value["claim_flags"]["strict_pure_weyl_classical_gate_passed"])
        self.assertEqual(value["strict_gate_v15_reconciliation"]["remaining_top_level_hashes"], 6)

    def test_false_gate_promotion_rejected(self):
        value = json.loads(RESULT.read_text())
        value["claim_flags"]["strict_pure_weyl_classical_gate_passed"] = True
        self.assertTrue(check(value))

    def test_route_mutation_rejected(self):
        value = copy.deepcopy(build())
        value["route_selection"][0]["route"] = "STRICT_AUXILIARY_Q3_COMMON_ASSEMBLY_AND_ARITY3_IDENTITIES"
        self.assertTrue(check(value))


if __name__ == "__main__":
    unittest.main()
