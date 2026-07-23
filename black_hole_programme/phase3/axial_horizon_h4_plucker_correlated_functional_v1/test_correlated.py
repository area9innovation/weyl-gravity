from __future__ import annotations

import copy
import json
import unittest

from . import produce
from . import verify


@unittest.skipUnless(produce.MANIFEST.exists(), "child runs unavailable")
class CorrelatedFunctionalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(produce.MANIFEST.read_text())

    def test_manifest_certifies_paired_obstruction(self):
        result = verify.verify_manifest(self.manifest)
        self.assertFalse(result["correlated_pass"])
        self.assertEqual(len(result["children"]), 2)
        for child in result["children"]:
            self.assertEqual(
                child["refusal"],
                {"shell": 4, "segment": 3, "code": 35},
            )
            self.assertLessEqual(float(child["defect"]["lo"]), 0)
            self.assertGreaterEqual(float(child["defect"]["hi"]), 0)

    def test_complex_and_coordinate_formulas_agree(self):
        midpoint = [complex(2, -3), complex(-5, 7), complex(11, 13)]
        value = [complex(17, 19), complex(-23, 29), complex(31, -37)]
        self.assertEqual(
            verify.hermitian_real(midpoint, value),
            verify.coordinate_real(midpoint, value),
        )

    def test_midpoint_value_is_positive_sum_of_squares(self):
        midpoint = [complex(2, -3), complex(-5, 7), complex(11, 13)]
        expected = sum(
            value.real ** 2 + value.imag ** 2 for value in midpoint
        )
        self.assertEqual(
            verify.hermitian_real(midpoint, midpoint), expected
        )
        self.assertGreater(expected, 0)

    def test_dependency_hash_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.manifest)
        mutated["split_certificate_sha256"] = "0" * 64
        mutated["payload_sha256"] = verify.payload_hash(mutated)
        with self.assertRaisesRegex(
            verify.VerificationError, "split certificate"
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

    def test_defect_interval_mutation_is_rejected(self):
        split_manifest = verify.verify_dependencies()
        entry = self.manifest["children"][0]
        split_entry = split_manifest["children"][0]
        text = (produce.HERE / entry["run_log_path"]).read_text()
        old = entry["terminal_evidence"][0]
        replacement = (
            "CORRELATED_FUNCTIONAL_DEFECT lo=1 hi=2 norm=1"
        )
        text = text.replace(old, replacement, 1)
        split_text = (
            produce.SPLIT_MANIFEST.parent / split_entry["run_log_path"]
        ).read_text()
        with self.assertRaisesRegex(
            verify.VerificationError, "does not contain zero"
        ):
            verify.verify_log(text, entry["source_sha256"], split_text)


if __name__ == "__main__":
    unittest.main()
