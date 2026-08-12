from __future__ import annotations

import json
from pathlib import Path
import unittest

from foundations.build_matrix_site import build_dataset, generated
from foundations.check_matrix_site import check
from foundations.verify_matrix_site import verify

ROOT = Path(__file__).resolve().parents[2]


class MatrixSiteTests(unittest.TestCase):
    def test_dataset_closes_entire_surface(self) -> None:
        data = build_dataset()
        self.assertEqual(len(data["cells"]), 576)
        self.assertEqual(sum(not x["emitted"] for x in data["cells"]), 124)
        self.assertEqual(data["counts"]["evidence_records"], 51)

    def test_unmapped_is_fail_closed(self) -> None:
        data = build_dataset()
        unmapped = [x for x in data["cells"] if x["status"] == "NOT_MAPPED"]
        self.assertEqual(len(unmapped), 124)
        self.assertTrue(all("not a literature-absence claim" in x["boundary"] for x in unmapped))

    def test_generated_outputs_are_current(self) -> None:
        for path, content in generated().items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(path.read_bytes(), content, path)

    def test_independent_checker(self) -> None:
        errors, summary = check()
        self.assertEqual(errors, [])
        self.assertEqual(summary["graph_edges"], 10)

    def test_verifier(self) -> None:
        errors, checks = verify()
        self.assertEqual(errors, [])
        self.assertGreaterEqual(len(checks), 5)

    def test_static_shell_has_no_remote_code(self) -> None:
        html = (ROOT / "foundations/site/index.html").read_text()
        self.assertNotIn("https://", html)
        self.assertIn('<script src="data.js"></script>', html)
        manifest = json.loads((ROOT / "foundations/site/manifest.json").read_text())
        self.assertEqual(len(manifest["outputs"]), 36)
        self.assertTrue((ROOT / "foundations/site/sources/foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V1.json").is_file())


if __name__ == "__main__":
    unittest.main()
