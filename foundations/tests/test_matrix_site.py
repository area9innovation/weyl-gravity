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
        self.assertEqual(data["counts"]["coverage_classified"], 371)
        self.assertEqual(data["counts"]["migration_reviewed"], 452)
        self.assertEqual(data["counts"]["migration_pending"], 0)
        self.assertEqual(data["counts"]["reviewed_no_transfer"], 88)

    def test_plain_language_guide_covers_every_axis_option(self):
        data = build_dataset()
        self.assertEqual([len(axis["keys"]) for axis in data["axes"]], [6, 6, 16])
        self.assertTrue(all(axis["plain_name"] and axis["guide_question"] for axis in data["axes"]))
        self.assertTrue(all(key["plain_meaning"] for axis in data["axes"] for key in axis["keys"]))

    def test_not_mapped_partition_is_fail_closed(self):
        data = build_dataset()
        reviewed = [x for x in data["cells"] if x["migration_status"] == "REVIEWED_NO_TRANSFER"]
        synthetic = [x for x in data["cells"] if not x["emitted"]]
        self.assertEqual((len(reviewed), len(synthetic)), (88, 124))
        self.assertEqual(sum(x["status"] == "NOT_MAPPED" for x in reviewed), 81)
        self.assertTrue(all(not x["evidence"] and x["migration_evidence"] for x in reviewed if x["status"] == "NOT_MAPPED"))
        self.assertTrue(all(x["evidence"] and x["migration_evidence"] for x in reviewed if x["status"] != "NOT_MAPPED"))
        self.assertTrue(all(x["status"] == "NOT_MAPPED" and x["migration_status"] == "NOT_REVIEWED" for x in synthetic))

    def test_generated_outputs_are_current(self):
        for path, content in generated().items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(path.read_bytes(), content, path)

    def test_independent_checker(self):
        errors, summary = check()
        self.assertEqual(errors, [])
        self.assertEqual(summary["total_not_mapped"], 205)

    def test_verifier(self):
        self.assertEqual(verify()[0], [])

    def test_absence_promotion_fails(self):
        result = copy.deepcopy(load(RESULT))
        result["claim_flags"]["reviewed_no_transfer_means_absent"] = True
        self.assertTrue(verify(result=result)[0])

    def test_report_boundary_fails(self):
        report = REPORT.read_text().replace("not a literature-absence claim", "a literature-absence claim")
        self.assertTrue(verify(report=report)[0])

    def test_static_shell_exposes_migration_review(self):
        html = (ROOT / "foundations/site/index.html").read_text()
        base_app = (ROOT / "foundations/site/app.js").read_text()
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
        self.assertIn("Coverage readiness map", base_app)
        self.assertIn("Coverage envelope, not a composed theory", base_app)
        self.assertIn("No complete observationally validated theory is certified", base_app)
        self.assertIn("paretoProfiles", base_app)
        self.assertIn("Two cross-cell relations are certified", base_app)
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
        self.assertIn("112-decision audit JSON", app)
        self.assertIn('label !== "Migration unresolved" || count > 0', base_app)
        self.assertIn("repeat(auto-fit, minmax(9rem, 1fr))", css)
        self.assertIn("writing-mode: vertical-rl", css)
        self.assertIn("grid-template-columns: 12rem minmax(0, 1fr)", css)
        manifest = json.loads((ROOT / "foundations/site/manifest.json").read_text())
        self.assertGreaterEqual(len(manifest["outputs"]), 38)
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V4.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V5.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V6.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2.json").is_file())
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2.json").is_file())


if __name__ == "__main__":
    unittest.main()
