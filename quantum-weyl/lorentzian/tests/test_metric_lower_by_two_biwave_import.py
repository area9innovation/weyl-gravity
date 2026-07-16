from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian import metric_lower_by_two_biwave_import as IMPORT
from lorentzian.metric_lower_by_two_biwave_import_certificate import (
    OUTPUT,
    ROOT,
    build_certificate,
)


class MetricLowerByTwoBiwaveImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_checked_in_certificate_reproduces_and_validates(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (
                ROOT
                / "schema/berger-metric-lower-by-two-biwave-import-v1.schema.json"
            ).read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_fast_and_exact_receipts_are_independent_and_fail_closed(self) -> None:
        self.assertTrue(all(self.certificate["fast_receipt"]["checks"].values()))
        self.assertTrue(
            all(self.certificate["independent_exact_replay"]["checks"].values())
        )
        self.assertFalse(
            self.certificate["claim_flags"][
                "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"
            ]
        )
        self.assertFalse(self.certificate["claim_flags"]["QUANTUM_CLAIM"])

    def test_green_promotion_and_factor_scope_mutations_are_rejected(self) -> None:
        source = deepcopy(IMPORT._git_json(IMPORT.CERTIFICATE))
        source["flags"]["BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"] = True
        with self.assertRaisesRegex(ValueError, "lifecycle"):
            IMPORT._validate_source(source)
        source = deepcopy(IMPORT._git_json(IMPORT.CERTIFICATE))
        source["canonical_factor_obstruction"]["not_ruled_out"] = []
        with self.assertRaisesRegex(ValueError, "scope"):
            IMPORT._validate_source(source)

    def test_artifact_hash_mutation_is_rejected(self) -> None:
        source = IMPORT._git_json(IMPORT.CERTIFICATE)
        reference = deepcopy(source["normal_form"]["artifacts"]["rough_tensor_wave"])
        reference["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "hash"):
            IMPORT._load_artifact(reference, "rough_tensor_wave")


if __name__ == "__main__":
    unittest.main()
