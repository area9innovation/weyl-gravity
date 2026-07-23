from __future__ import annotations

import copy
import json
import unittest

from . import produce
from . import verify


@unittest.skipUnless(produce.MANIFEST.exists(), "child runs unavailable")
class ExteriorNormTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(produce.MANIFEST.read_text())

    def test_manifest_certifies_paired_design_blocker(self):
        result = verify.verify_manifest(self.manifest)
        self.assertFalse(result["exterior_pass"])
        self.assertEqual(len(result["children"]), 2)
        for child in result["children"]:
            self.assertEqual(
                child["refusal"],
                {"shell": 4, "segment": 3, "code": 36},
            )
            self.assertLessEqual(float(child["evidence"]["lo"]), 0)
            self.assertGreaterEqual(float(child["evidence"]["hi"]), 0)

    def test_squared_norm_is_positive_definite(self):
        self.assertEqual(
            verify.squared_norm([3.0, -4.0], [5.0, 12.0]),
            194.0,
        )
        self.assertEqual(verify.squared_norm([0.0], [0.0]), 0.0)

    def test_dependency_hash_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.manifest)
        mutated["split_manifest_sha256"] = "0" * 64
        mutated["payload_sha256"] = verify.payload_hash(mutated)
        with self.assertRaisesRegex(
            verify.VerificationError, "split manifest"
        ):
            verify.verify_manifest(mutated)

    def test_missing_child_is_rejected(self):
        mutated = copy.deepcopy(self.manifest)
        mutated["children"] = mutated["children"][:1]
        mutated["payload_sha256"] = verify.payload_hash(mutated)
        with self.assertRaisesRegex(
            verify.VerificationError, "child count"
        ):
            verify.verify_manifest(mutated)

    def test_preboundary_heartbeat_mutation_is_rejected(self):
        split_manifest = verify.verify_dependencies()
        entry = self.manifest["children"][0]
        split_entry = split_manifest["children"][0]
        text = (produce.HERE / entry["run_log_path"]).read_text()
        text = text.replace(
            "PLUCKER_SEGMENT shell=0 segment=0",
            "PLUCKER_SEGMENT shell=0 segment=9",
            1,
        )
        split_text = (
            produce.SPLIT_MANIFEST.parent / split_entry["run_log_path"]
        ).read_text()
        with self.assertRaisesRegex(
            verify.VerificationError, "heartbeat drift"
        ):
            verify.verify_log(text, entry["source_sha256"], split_text)

    def test_false_positive_norm_mutation_is_rejected(self):
        split_manifest = verify.verify_dependencies()
        entry = self.manifest["children"][0]
        split_entry = split_manifest["children"][0]
        text = (produce.HERE / entry["run_log_path"]).read_text()
        old = entry["terminal_evidence"][0]
        text = text.replace(
            old, "EXTERIOR_NORM_DEFECT lo=1 hi=2 norm=1", 1
        )
        split_text = (
            produce.SPLIT_MANIFEST.parent / split_entry["run_log_path"]
        ).read_text()
        with self.assertRaisesRegex(
            verify.VerificationError, "does not contain zero"
        ):
            verify.verify_log(text, entry["source_sha256"], split_text)

    def test_source_derivation_mutation_is_rejected(self):
        split_manifest = verify.verify_dependencies()
        entry = self.manifest["children"][0]
        split_entry = split_manifest["children"][0]
        metadata = json.loads(
            (produce.HERE / entry["metadata_path"]).read_text()
        )
        source_path = produce.HERE / entry["source_path"]
        original = source_path.read_text()
        source_path.write_text(
            original.replace(
                "ivtm4_mul_checked(x,x)",
                "ivtm4_add_checked(x,x)",
                1,
            )
        )
        try:
            with self.assertRaisesRegex(
                verify.VerificationError, "source hash|bounded derivation"
            ):
                verify.verify_source(
                    0, source_path, metadata, split_entry
                )
        finally:
            source_path.write_text(original)


if __name__ == "__main__":
    unittest.main()
