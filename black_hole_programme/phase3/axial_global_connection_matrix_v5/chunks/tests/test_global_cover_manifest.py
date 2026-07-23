from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from ..verify_global_cover_manifest import CoverError, verify_manifest


HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[5]
ARTIFACTS = HERE.parents[1] / "artifacts"
MANIFEST = ARTIFACTS / "global_map_cover_manifest.json"


def _rehash_entries(data: dict) -> None:
    encoded = json.dumps(
        data["entries"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    data["integrity"]["entry_set_sha256"] = hashlib.sha256(encoded).hexdigest()


class GlobalCoverManifestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST.read_text())

    def test_current_manifest_passes(self) -> None:
        self.assertTrue(verify_manifest(self.manifest, REPO_ROOT))

    def test_missing_child_is_rejected(self) -> None:
        data = copy.deepcopy(self.manifest)
        data["entries"].pop(7)
        with self.assertRaisesRegex(CoverError, "exactly 16"):
            verify_manifest(data, REPO_ROOT)

    def test_duplicate_child_is_rejected(self) -> None:
        data = copy.deepcopy(self.manifest)
        data["entries"][8]["child_id"] = "q07"
        data["integrity"]["entry_set_sha256"] = self.manifest["integrity"][
            "entry_set_sha256"
        ]
        with self.assertRaises(CoverError):
            verify_manifest(data, REPO_ROOT)

    def test_gap_is_rejected(self) -> None:
        data = copy.deepcopy(self.manifest)
        data["entries"][9]["lower"] = "2058/4096"
        with self.assertRaises(CoverError):
            verify_manifest(data, REPO_ROOT)

    def test_global_hash_mutation_is_rejected(self) -> None:
        data = copy.deepcopy(self.manifest)
        data["entries"][2]["global_map"]["sha256"] = "0" * 64
        _rehash_entries(data)
        with self.assertRaisesRegex(CoverError, "file hash mismatch"):
            verify_manifest(data, REPO_ROOT)

    def test_tail_link_swap_is_rejected(self) -> None:
        data = copy.deepcopy(self.manifest)
        data["entries"][4]["tail_join"] = copy.deepcopy(
            data["entries"][5]["tail_join"]
        )
        with self.assertRaises(CoverError):
            verify_manifest(data, REPO_ROOT)

    def test_prefix_payload_mutation_is_rejected(self) -> None:
        data = copy.deepcopy(self.manifest)
        data["shared_prefix"]["payload_sha256"] = "f" * 64
        with self.assertRaisesRegex(CoverError, "payload hash mismatch"):
            verify_manifest(data, REPO_ROOT)

    def test_extra_global_artifact_is_rejected(self) -> None:
        data = copy.deepcopy(self.manifest)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source_root = REPO_ROOT
            for entry in data["entries"]:
                for key in ("global_map", "tail_join"):
                    source = source_root / entry[key]["path"]
                    target = root / entry[key]["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(source.read_bytes())
            prefix_source = source_root / data["shared_prefix"]["path"]
            prefix_target = root / data["shared_prefix"]["path"]
            prefix_target.parent.mkdir(parents=True, exist_ok=True)
            prefix_target.write_bytes(prefix_source.read_bytes())
            extra = (
                root
                / data["entries"][0]["global_map"]["path"]
            ).parent / "global_map_q16.json"
            extra.write_text("{}\n")
            with self.assertRaisesRegex(CoverError, "extras"):
                verify_manifest(data, root)

    def test_replay_output_hash_mutation_is_rejected(self) -> None:
        data = copy.deepcopy(self.manifest)
        data["entries"][11]["replay_link"]["tail_output_sha256"] = "a" * 64
        _rehash_entries(data)
        with self.assertRaisesRegex(CoverError, "replay identity"):
            verify_manifest(data, REPO_ROOT)


if __name__ == "__main__":
    unittest.main()
