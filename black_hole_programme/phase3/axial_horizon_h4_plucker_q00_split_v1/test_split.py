from __future__ import annotations

import copy
import json
import unittest

from . import produce
from . import verify


@unittest.skipUnless(produce.MANIFEST.exists(), "child runs unavailable")
class SplitCoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(produce.MANIFEST.read_text())

    def test_complete_cover_verifies(self):
        result = verify.verify_manifest(self.manifest)
        self.assertEqual(len(result["children"]), 2)
        self.assertFalse(result["cover_pass"])
        self.assertTrue(
            all(
                child["refusal"]
                == {"shell": 4, "segment": 3, "code": 32}
                for child in result["children"]
            )
        )

    def test_gap_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.manifest)
        mutated["child_cells"][1][0] = "4098/8192"
        mutated["payload_sha256"] = verify.payload_hash(mutated)
        with self.assertRaisesRegex(
            verify.VerificationError, "child cells|gap"
        ):
            verify.verify_manifest(mutated)

    def test_parent_hash_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.manifest)
        mutated["parent_certificate_sha256"] = "0" * 64
        mutated["payload_sha256"] = verify.payload_hash(mutated)
        with self.assertRaisesRegex(
            verify.VerificationError, "parent certificate"
        ):
            verify.verify_manifest(mutated)

    def test_child_source_hash_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.manifest)
        mutated["children"][0]["source_sha256"] = "0" * 64
        mutated["payload_sha256"] = verify.payload_hash(mutated)
        with self.assertRaisesRegex(
            verify.VerificationError, "source hash"
        ):
            verify.verify_manifest(mutated)

    def test_relation_defect_log_is_rejected(self):
        entry = self.manifest["children"][0]
        text = (produce.HERE / entry["run_log_path"]).read_text()
        mutated = text + "\nPLUCKER_RELATION_DEFECT relation=0\n"
        with self.assertRaisesRegex(
            verify.VerificationError, "relation defect"
        ):
            verify.verify_child_log(mutated, entry["source_sha256"])

    def test_missing_child_is_rejected(self):
        mutated = copy.deepcopy(self.manifest)
        mutated["children"] = mutated["children"][:1]
        mutated["payload_sha256"] = verify.payload_hash(mutated)
        with self.assertRaisesRegex(
            verify.VerificationError, "child result count"
        ):
            verify.verify_manifest(mutated)


if __name__ == "__main__":
    unittest.main()
