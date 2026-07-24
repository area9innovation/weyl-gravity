from __future__ import annotations

import copy
import json
import unittest

from . import produce
from . import verify


@unittest.skipUnless(produce.MANIFEST.exists(), "refinement runs unavailable")
class RadialRefinementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(produce.MANIFEST.read_text())

    def test_manifest_certifies_bounded_obstruction(self):
        result = verify.verify_manifest(self.manifest)
        self.assertEqual(
            result["status"],
            "CERTIFIED_RADIAL_REFINEMENT_OBSTRUCTION",
        )
        self.assertEqual(len(result["attempts"]), 4)
        self.assertEqual(
            result["common_left_boundary"], "725/134217728"
        )

    def test_exact_depths_and_widths(self):
        self.assertEqual(
            [attempt["factor"] for attempt in self.manifest["attempts"]],
            [2, 4],
        )
        self.assertEqual(
            [attempt["radial_panel_width"]
             for attempt in self.manifest["attempts"]],
            ["1/134217728", "1/268435456"],
        )

    def test_all_prefixes_have_nineteen_hashes(self):
        for attempt in self.manifest["attempts"]:
            for child in attempt["children"]:
                self.assertEqual(
                    len(child["prefix_heartbeat_hashes"]), 19
                )

    def test_mutated_payload_hash_is_rejected(self):
        mutated = copy.deepcopy(self.manifest)
        mutated["status"] = "CERTIFIED_RADIAL_REFINEMENT_PASS"
        with self.assertRaisesRegex(
            verify.VerificationError, "payload hash"
        ):
            verify.verify_manifest(mutated)

    def test_mutated_heartbeat_is_rejected(self):
        mutated = copy.deepcopy(self.manifest)
        mutated["attempts"][0]["children"][0][
            "prefix_heartbeat_hashes"
        ][0] = "0" * 64
        mutated["payload_sha256"] = verify.payload_hash(mutated)
        with self.assertRaisesRegex(
            verify.VerificationError, "heartbeat"
        ):
            verify.verify_manifest(mutated)

    def test_mutated_refusal_code_is_rejected(self):
        mutated = copy.deepcopy(self.manifest)
        mutated["attempts"][0]["children"][0]["refusal"][
            "raw_code"
        ] = 31
        mutated["payload_sha256"] = verify.payload_hash(mutated)
        with self.assertRaisesRegex(
            verify.VerificationError, "refusal"
        ):
            verify.verify_manifest(mutated)

    def test_no_rank_loss_promotion(self):
        certificate = {
            "schema": (
                "phase3-axial-h4-plucker-radial-refinement-"
                "certificate-v1"
            ),
            "status": self.manifest["status"],
            "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            "result": {
                "rank_loss_established": True,
                "common_refusal_left_boundary": "725/134217728",
            },
            "hashes": {},
        }
        with self.assertRaisesRegex(
            verify.VerificationError, "rank loss"
        ):
            verify.verify_certificate(
                certificate,
                {
                    "status": self.manifest["status"],
                    "common_left_boundary": "725/134217728",
                },
            )


if __name__ == "__main__":
    unittest.main()
