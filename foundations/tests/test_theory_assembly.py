from __future__ import annotations

import copy
from pathlib import Path
import unittest

from foundations.build_matrix_site_v2 import build_dataset
from foundations.theory_assembly import build_assembly_assessment, canonical_digest
from foundations.verify_theory_assembly import verify


ROOT = Path(__file__).resolve().parents[2]


class TheoryAssemblyTests(unittest.TestCase):
    def test_prototypes_fail_closed(self):
        value = build_assembly_assessment(build_dataset())
        self.assertEqual(len(value["assemblies"]), 7)
        self.assertTrue(all(not item["complete_theory"] for item in value["assemblies"]))
        certified = [interface for item in value["assemblies"] for interface in item["interfaces"] if interface["certification_status"] == "CERTIFIED"]
        self.assertEqual(len(certified), 2)
        self.assertTrue(all(interface["relation"] == "CONDITIONAL_BRIDGE" for interface in certified))
        self.assertEqual(value["empirical_ledger"]["records"], [])

    def test_selected_cells_cover_all_obligations(self):
        value = build_assembly_assessment(build_dataset())
        self.assertTrue(all(len(item["selected_cells"]) == 16 for item in value["assemblies"]))
        self.assertTrue(all(len({cell["obligation"] for cell in item["selected_cells"]}) == 16 for item in value["assemblies"]))

    def test_independent_verifier(self):
        self.assertEqual(verify()[0], [])

    def test_empirical_promotion_without_record_fails(self):
        value = build_assembly_assessment(build_dataset())
        promoted = copy.deepcopy(value)
        promoted["claim_flags"]["empirical_agreement_assessed"] = True
        promoted["canonical_digest"] = canonical_digest(promoted)
        self.assertIn("fail-closed flag empirical_agreement_assessed", verify(value=promoted)[0])


if __name__ == "__main__":
    unittest.main()
