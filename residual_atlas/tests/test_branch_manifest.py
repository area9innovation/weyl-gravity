"""Regression tests for the authoritative residual branch manifest."""

import json
from pathlib import Path
import tempfile
import unittest

from residual_atlas.generate_branch_manifest import OUTPUT, build_manifest
from residual_atlas.verify_branch_manifest import verify


class ResidualBranchManifestTest(unittest.TestCase):
    def test_manifest_is_current(self) -> None:
        self.assertEqual(json.loads(Path(OUTPUT).read_text()), build_manifest())

    def test_complete_eight_axis_trace(self) -> None:
        manifest = build_manifest()
        axes = set(manifest["cell_axes"])
        for branch in manifest["branches"]:
            self.assertEqual(set(branch["cells"]), axes)

    def test_background_crosswalks_fail_closed(self) -> None:
        crosswalks = {row["id"]: row for row in build_manifest()["crosswalks"]}
        self.assertEqual(crosswalks["crosswalk.ph_to_vacuum_cylinder"]["status"], "NO_CERTIFIED_MAP")
        self.assertEqual(crosswalks["crosswalk.ph_to_black_hole"]["status"], "NO_CERTIFIED_MAP")

    def test_berger_projector_obstruction_is_not_a_branch_map(self) -> None:
        crosswalks = {row["id"]: row for row in build_manifest()["crosswalks"]}
        self.assertEqual(crosswalks["crosswalk.berger_unsplit_to_ph_branches"]["status"], "OBSTRUCTED")

    def test_independent_verifier_rejects_source_status_mutation(self) -> None:
        payload = build_manifest()
        payload["branches"][0]["cells"]["linear_operator"]["sources"][0]["observed_status"] = "OPEN"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutated.json"
            path.write_text(json.dumps(payload))
            with self.assertRaises(AssertionError):
                verify(path)

    def test_all_six_fragment_row_inventories_are_pinned(self) -> None:
        coverage = build_manifest()["coverage"]
        self.assertEqual(coverage["fragment_count"], 6)
        self.assertEqual(coverage["total_source_rows"], 309)


if __name__ == "__main__":
    unittest.main()
