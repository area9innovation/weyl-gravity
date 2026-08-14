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
        self.assertEqual(len(certified), 4)
        self.assertTrue(all(interface["relation"] == "CONDITIONAL_BRIDGE" for interface in certified))
        self.assertEqual(value["empirical_ledger"]["records"], [])
        self.assertEqual(len(value["calibration_controls"]), 1)
        self.assertEqual(len(value["calibration_controls"][0]["records"]), 4)
        self.assertTrue(all(rail["status"] not in {"BLOCKED", "FAILED"} for item in value["assemblies"] for rail in item["maturity_rails"]))

    def test_classical_reference_reports_complete_coverage_and_partial_composition(self):
        value = build_assembly_assessment(build_dataset())
        assembly = next(item for item in value["assemblies"] if item["id"] == "STANDARD_MIXED_REFERENCE")
        rails = {item["id"]: item["status"] for item in assembly["maturity_rails"]}
        self.assertEqual(assembly["coverage"], {"direct": 16, "assessed": 16, "total": 16, "complete_direct": True})
        self.assertEqual(rails["OBLIGATION_COVERAGE"], "SATISFIED")
        self.assertEqual(rails["CROSS_CELL_COMPOSITION"], "PARTIALLY_CERTIFIED")
        self.assertEqual(rails["PREDICTION_DERIVATION"], "NOT_EVALUABLE")

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
