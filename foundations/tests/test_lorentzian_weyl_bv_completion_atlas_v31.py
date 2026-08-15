from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from foundations.build_lorentzian_weyl_bv_completion_atlas_v31 import build, generated
from foundations.check_lorentzian_weyl_bv_completion_atlas_v31 import check


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V31.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v31.md"


class AtlasV31Tests(unittest.TestCase):
    def test_generated_current(self):
        result, report = generated()
        self.assertEqual(RESULT.read_bytes(), result)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_projection_and_boundary(self):
        value = build()
        self.assertEqual(check(value), [])
        self.assertEqual(len(value["route_selection"]), 10)
        self.assertTrue(value["claim_flags"]["strict_386_exhaustive_full_nonlinear_bv_family_census"])
        self.assertFalse(value["claim_flags"]["strict_386_full_source_q2_assembled"])

    def test_source_assembly_promotion_rejected(self):
        value = json.loads(RESULT.read_text())
        value["claim_flags"]["strict_386_full_source_q2_assembled"] = True
        self.assertTrue(check(value))

    def test_route_mutation_rejected(self):
        value = copy.deepcopy(build())
        value["route_selection"][0]["route"] = "STRICT_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST"
        self.assertTrue(check(value))


if __name__ == "__main__":
    unittest.main()
