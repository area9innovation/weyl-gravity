#!/usr/bin/env python3
"""Scoped tests for runtime standalone-history provenance translation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from standalone_provenance import (
    CROSSWALK,
    OLD_PREFIX,
    ProvenanceResolutionError,
    ROOT,
    normalize_repository_path,
    read_attached_blob,
    resolve_attached_ref,
    resolve_historical_commit,
)


class StandaloneProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.crosswalk = json.loads(CROSSWALK.read_text(encoding="utf-8"))
        cls.old_commit, cls.row = next(iter(cls.crosswalk["mapping"].items()))

    def test_prefix_is_stripped(self) -> None:
        self.assertEqual(
            normalize_repository_path(OLD_PREFIX + "paper/README.md"),
            "paper/README.md",
        )

    def test_mapped_witness_blob_replays_exactly(self) -> None:
        historical_path = self.row["witness_old_path"]
        if not historical_path.startswith(OLD_PREFIX):
            historical_path = OLD_PREFIX + historical_path
        ref, payload = read_attached_blob(
            self.old_commit,
            historical_path,
            self.row["witness_sha256"],
        )
        self.assertEqual(ref.commit, self.row["new_commit"])
        self.assertEqual(
            hashlib.sha256(payload).hexdigest(),
            self.row["witness_sha256"],
        )

    def test_live_commit_is_not_rewritten(self) -> None:
        ref = resolve_attached_ref(
            self.row["new_commit"],
            self.row["witness_new_path"],
        )
        self.assertEqual(ref.commit, self.row["new_commit"])
        self.assertFalse(ref.translated)

    def test_historical_commit_resolves_without_rewriting_pin(self) -> None:
        self.assertEqual(
            resolve_historical_commit(self.old_commit),
            self.row["new_commit"],
        )

    def test_unknown_commit_fails_closed(self) -> None:
        with self.assertRaises(ProvenanceResolutionError):
            resolve_attached_ref("0" * 40, "README.md")

    def test_hash_mismatch_fails_closed(self) -> None:
        with self.assertRaises(ProvenanceResolutionError):
            read_attached_blob(
                self.old_commit,
                self.row["witness_old_path"],
                "0" * 64,
            )

    def test_abbreviated_unindexed_pin_resolves_by_exact_content(self) -> None:
        ref, payload = read_attached_blob(
            self.old_commit[:9],
            self.row["witness_old_path"],
            self.row["witness_sha256"],
        )
        self.assertEqual(
            hashlib.sha256(payload).hexdigest(),
            self.row["witness_sha256"],
        )
        self.assertNotEqual(ref.commit, self.old_commit[:9])

    def test_crosswalk_with_unresolved_rows_fails_closed(self) -> None:
        broken = dict(self.crosswalk)
        broken["unresolved_count"] = 1
        broken["unresolved"] = [{"old_commit": "0" * 40}]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "crosswalk.json"
            path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaises(ProvenanceResolutionError):
                resolve_attached_ref(
                    self.old_commit,
                    self.row["witness_old_path"],
                    root=ROOT,
                    crosswalk_path=path,
                )


if __name__ == "__main__":
    unittest.main()
