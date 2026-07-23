from __future__ import annotations

import copy
import hashlib
import json
import unittest

from . import produce
from . import verify


@unittest.skipUnless(produce.MANIFEST.exists(), "bounded run not available")
class ContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(produce.MANIFEST.read_text())

    def test_complete_join_verifies(self):
        result = verify.verify_manifest(self.manifest)
        self.assertEqual(result["reached"], {"shell": 4, "segment": 2})
        self.assertEqual(
            result["refused"], {"shell": 4, "segment": 3, "code": 32}
        )

    def test_predecessor_hash_mutation_is_rejected(self):
        with self.assertRaisesRegex(
            verify.VerificationError, "predecessor certificate"
        ):
            verify.verify_predecessor("0" * 64)

    def test_state_payload_mutation_is_rejected(self):
        exporter = self.manifest["exporter"]
        source = produce.HERE / exporter["source_path"]
        log = produce.HERE / exporter["log_path"]
        state = json.loads(
            (produce.HERE / exporter["output_state_path"]).read_text()
        )
        mutated = copy.deepcopy(state)
        mutated["rows"][0]["coefficients"][0] = "1/3"
        with self.assertRaisesRegex(
            verify.VerificationError, "payload hash"
        ):
            verify.verify_state(
                mutated, {"shell": 3, "segment": 0}, None, source, log
            )

    def test_builder_mutation_is_rejected(self):
        entry = self.manifest["chunks"][0]
        source = (produce.HERE / entry["source_path"]).read_text()
        mutated = source.replace(
            'c0=qm_set(c0,0,0,big("',
            'c0=qm_set(c0,0,0,big("1+',
            1,
        )
        with self.assertRaisesRegex(
            verify.VerificationError, "builder"
        ):
            rows = verify.parse_source_builder(mutated)
            verify.require(
                rows
                == json.loads(
                    (
                        produce.HERE / entry["input_state_path"]
                    ).read_text()
                )["rows"],
                "chunk input builder/state drift",
            )

    def test_join_hash_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.manifest)
        mutated["chunks"][1]["input_state_sha256"] = "0" * 64
        mutated["payload_sha256"] = verify.payload_hash(mutated)
        with self.assertRaisesRegex(
            verify.VerificationError, "state chain"
        ):
            verify.verify_manifest(mutated)

    def test_refusal_is_fail_closed(self):
        mutated = copy.deepcopy(self.manifest)
        mutated["terminal"]["detail"] = "shell=4 segment=3 code=31"
        mutated["payload_sha256"] = verify.payload_hash(mutated)
        with self.assertRaisesRegex(
            verify.VerificationError, "terminal detail"
        ):
            verify.verify_manifest(mutated)

    def test_exact_predecessor_certificate_hash_is_frozen(self):
        self.assertEqual(
            hashlib.sha256(
                produce.PREDECESSOR_CERTIFICATE.read_bytes()
            ).hexdigest(),
            produce.EXPECTED_PREDECESSOR_CERTIFICATE_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
