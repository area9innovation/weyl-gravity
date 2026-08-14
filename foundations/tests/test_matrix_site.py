from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from foundations.build_matrix_site_v2 import build_dataset, generated
from foundations.check_matrix_site_v2 import check
from foundations.verify_matrix_site_v2 import RESULT, REPORT, load, verify

ROOT = Path(__file__).resolve().parents[2]


class MatrixSiteTests(unittest.TestCase):
    def test_dataset_separates_coverage_and_migration(self):
        data = build_dataset()
        self.assertEqual(len(data["cells"]), 576)
        self.assertEqual(data["counts"]["coverage_classified"], 576)
        self.assertEqual(data["counts"]["migration_reviewed"], 576)
        self.assertEqual(data["counts"]["migration_pending"], 0)
        self.assertEqual(data["counts"]["reviewed_no_transfer"], 88)

    def test_plain_language_guide_covers_every_axis_option(self):
        data = build_dataset()
        self.assertEqual([len(axis["keys"]) for axis in data["axes"]], [6, 6, 16])
        self.assertTrue(all(axis["plain_name"] and axis["guide_question"] for axis in data["axes"]))
        self.assertTrue(all(key["plain_meaning"] for axis in data["axes"] for key in axis["keys"]))

    def test_reviewed_gap_partition_is_fail_closed(self):
        data = build_dataset()
        reviewed = [x for x in data["cells"] if x["migration_status"] == "REVIEWED_NO_TRANSFER"]
        synthetic = [x for x in data["cells"] if not x["emitted"]]
        self.assertEqual((len(reviewed), len(synthetic)), (88, 0))
        self.assertEqual(sum(x["status"] == "REVIEWED_GAP" for x in data["cells"]), 172)
        self.assertEqual(sum(x["status"] == "NOT_MAPPED" for x in data["cells"]), 0)
        self.assertTrue(all(x["evidence"] and x["migration_evidence"] for x in reviewed))
        self.assertEqual(sum(x["migration_status"] == "DIRECT_COORDINATE_REVIEW" for x in data["cells"]), 124)

    def test_generated_outputs_are_current(self):
        for path, content in generated().items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(path.read_bytes(), content, path)

    def test_independent_checker(self):
        errors, summary = check()
        self.assertEqual(errors, [])
        self.assertEqual(summary["total_not_mapped"], 0)

    def test_verifier(self):
        self.assertEqual(verify()[0], [])

    def test_absence_promotion_fails(self):
        result = copy.deepcopy(load(RESULT))
        result["claim_flags"]["reviewed_gap_means_absent"] = True
        self.assertTrue(verify(result=result)[0])

    def test_report_boundary_fails(self):
        report = REPORT.read_text().replace("it is not a result", "it is a result")
        self.assertTrue(verify(report=report)[0])

    def test_static_shell_exposes_migration_review(self):
        html = (ROOT / "foundations/site/index.html").read_text()
        base_app = (ROOT / "foundations/site/app.js").read_text()
        assembly_data = (ROOT / "foundations/site/assemblies.js").read_text()
        app = (ROOT / "foundations/site/migration-review.js").read_text()
        css = (ROOT / "foundations/site/styles.css").read_text()
        self.assertNotIn("https://", html)
        self.assertIn('<script src="migration-review.js"></script>', html)
        self.assertIn('data-view="guide"', html)
        self.assertIn('data-view="viability"', html)
        self.assertIn('data-view="assemblies"', html)
        self.assertIn('id="viabilityView"', html)
        self.assertIn('<script src="viability.js"></script>', html)
        self.assertIn('id="dimensionGuide"', html)
        self.assertIn("Regime × carrier × obligation", base_app)
        self.assertIn("Every result answers three different questions", base_app)
        self.assertIn("Why “general relativity works” is too compressed", base_app)
        self.assertIn('["viability", "assemblies", "guide", "graph", "ladder"]', base_app)
        self.assertIn("The question changes even when the equation does not", base_app)
        self.assertIn("Small glossary", base_app)
        self.assertIn("For reviewers: how the evidence letters and migration audit work", base_app)
        self.assertIn("Coverage readiness map", base_app)
        self.assertIn("Coverage envelope, not a composed theory", base_app)
        self.assertIn("No complete observationally validated theory is certified", base_app)
        self.assertIn("paretoProfiles", base_app)
        self.assertIn("Seven independent maturity rails", base_app)
        self.assertIn("Numerical reproduction is not empirical validation", base_app)
        self.assertIn("Euclidean/Krein carrier boundary", base_app)
        self.assertIn("Bounded assembly complete", base_app)
        self.assertIn("Field equations to Cassini", base_app)
        self.assertIn("Bounded model tests", base_app)
        self.assertIn("Research programmes", base_app)
        self.assertIn("Interfaces & calibration", base_app)
        self.assertIn('params.set("panel", state.assemblyPanel)', base_app)
        self.assertIn("Weyl action to NGC 3198", base_app)
        self.assertIn("random-error gate failed", base_app)
        self.assertIn("No parameter is refitted", base_app)
        self.assertIn("mannheimCurveSvg", base_app)
        self.assertIn("FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1", assembly_data)
        self.assertIn("commonFitCurveSvg", base_app)
        self.assertIn("NGC 3198 head-to-head control", base_app)
        self.assertIn("Scoped winner: GR + NFW", base_app)
        self.assertIn("FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1", assembly_data)
        self.assertIn("Meet the research programmes", base_app)
        self.assertIn("Bateman–Turok", assembly_data)
        self.assertIn("Mannheim conformal gravity", assembly_data)
        self.assertIn("Pure-Weyl BV–BFV", assembly_data)
        self.assertIn("camp-profile", base_app)
        self.assertIn("Applicability mask", base_app)
        self.assertIn("External positive control", base_app)
        self.assertIn("red is reserved for an explicit incompatibility", base_app.lower())
        self.assertIn("CERTIFIED ·", base_app)
        self.assertIn("GRAPH_PATHWAYS", base_app)
        self.assertIn("Relation ledger", base_app)
        self.assertIn("graph-edge-hit", base_app)
        self.assertIn("No direct certificate yet", base_app)
        self.assertNotIn("No stronger interpretation is licensed", base_app)
        self.assertNotIn("Open but seeded", html)
        self.assertIn("Open cells with a starting point", html)
        self.assertIn("Pieces only and Priority gap cells", html)
        self.assertIn("migration_evidence", app)
        self.assertIn("175-coordinate surface audit", app)
        self.assertIn('!["Migration unresolved", "Not mapped"].includes(label) || count > 0', base_app)
        self.assertIn("Reviewed gap versus priority gap", base_app)
        self.assertIn("repeat(auto-fit, minmax(9rem, 1fr))", css)
        self.assertIn("writing-mode: vertical-rl", css)
        self.assertIn("grid-template-columns: 12rem minmax(0, 1fr)", css)
        self.assertIn(".camp-gallery", css)
        self.assertIn(".curve-prediction", css)
        self.assertIn(".assembly-subtabs", css)
        self.assertIn(".assembly-panel.active", css)
        self.assertIn(".guide-equation", css)
        manifest = json.loads((ROOT / "foundations/site/manifest.json").read_text())
        self.assertGreaterEqual(len(manifest["outputs"]), 38)
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V4.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V5.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V6.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V7.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V8.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V9.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V10.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2.json").is_file())


if __name__ == "__main__":
    unittest.main()
