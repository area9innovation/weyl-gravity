import json
import tempfile
import unittest
from pathlib import Path

from certificate_graph.build_residual_atlas import (
    AXES,
    AtlasEntry,
    STATUSES,
    build_dot,
    build_html,
    load_entries,
)


class ResidualAtlasVisualizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.labels = {
            "group_order": ["other"],
            "groups": {"other": {"label": "Test universe", "description": "Test"}},
            "labels": {"test.mode": "Test wave"},
        }

    def fragment(self, descriptions=None):
        return {
            "schema": "pure-weyl-residual-atlas-fragment-v1",
            "team": "test",
            "entries": [
                {
                    "id": "test.mode",
                    "scope": {"background": "test background", "carrier": "test carrier"},
                    "descriptions": descriptions or {axis: "OPEN" for axis in AXES},
                    "claim_boundary": "test only",
                    "evidence": [],
                }
            ],
        }

    def test_loads_every_axis_without_promoting_status(self) -> None:
        statuses = dict(zip(AXES, STATUSES))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test-atlas-fragment.json"
            path.write_text(json.dumps(self.fragment(statuses)))
            entries = load_entries([path], self.labels)
        self.assertEqual(entries[0].descriptions, statuses)

    def test_rejects_unknown_status(self) -> None:
        descriptions = {axis: "OPEN" for axis in AXES}
        descriptions["quantum"] = "PROBABLY_FINE"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test-atlas-fragment.json"
            path.write_text(json.dumps(self.fragment(descriptions)))
            with self.assertRaisesRegex(ValueError, "invalid quantum status"):
                load_entries([path], self.labels)

    def test_public_labels_and_plain_statuses_reach_both_views(self) -> None:
        entry = AtlasEntry(
            id="test.mode",
            label="Test wave",
            group="other",
            source="test-atlas-fragment.json",
            team="test",
            descriptions={axis: "OPEN" for axis in AXES},
            scope={"background": "test"},
            details={},
            evidence=[],
            boundary="test only",
        )
        dot = build_dot([entry], self.labels, publishable=True)
        page = build_html([entry], self.labels, publishable=True)
        self.assertIn("Test wave", dot)
        self.assertIn("Next frontier", dot)
        self.assertIn("Test wave", page)
        self.assertIn("Claim boundary", page)

    def test_duplicate_mode_ids_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first-atlas-fragment.json"
            second = Path(tmp) / "second-atlas-fragment.json"
            first.write_text(json.dumps(self.fragment()))
            second.write_text(json.dumps(self.fragment()))
            with self.assertRaisesRegex(ValueError, "duplicate atlas id"):
                load_entries([first, second], self.labels)


if __name__ == "__main__":
    unittest.main()
