from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "source_map_verifier",
    ROOT / "paper/verify_13_14_draft_source_maps.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class DraftSourceMapTests(unittest.TestCase):
    def test_authoritative_maps_pass(self) -> None:
        for path in MODULE.MAPS:
            paper_id, count = MODULE.verify_map(path)
            self.assertTrue(paper_id.startswith("PAPER_"))
            self.assertGreater(count, 0)

    def test_blob_mutation_fails_closed(self) -> None:
        payload = json.loads(MODULE.MAPS[0].read_text(encoding="utf-8"))
        payload["sources"][0]["git_blob"] = "0" * 40
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "map.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises((AssertionError, RuntimeError)):
                MODULE.verify_map(path)


if __name__ == "__main__":
    unittest.main()
