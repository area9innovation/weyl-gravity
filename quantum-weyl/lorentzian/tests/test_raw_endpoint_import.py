from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian import raw_endpoint_import as IMPORT
from lorentzian.raw_endpoint_import_certificate import (
    OUTPUT,
    SCHEMA,
    _validate_scientific_payload,
    build_certificate,
)


class RawEndpointImportTests(unittest.TestCase):
    def test_fast_checked_certificate_reproduces_and_validates(self) -> None:
        certificate = build_certificate()
        self.assertEqual(json.loads(OUTPUT.read_text()), certificate)
        schema = json.loads(SCHEMA.read_text())
        self.assertFalse(validate_instance(certificate, schema))
        self.assertEqual(
            certificate["result_state"],
            "RAW_ENDPOINT_IMPORTED_EXACT_REPLAY_FILTERED_GREEN_EXTENSION_OPEN",
        )

    def test_pinned_source_and_sparse_record_hashes_replay(self) -> None:
        receipt = IMPORT.fast_receipt()
        self.assertEqual(
            receipt["source_claim_status"],
            "CERTIFIED_RAW_BV_TRANSPORT_PRINCIPAL_COMPATIBLE_GREEN_OPEN",
        )
        self.assertEqual(
            receipt["preflight_claim_status"],
            "EXACT_FILTER_PREFLIGHT_GREEN_INVERSION_OPEN",
        )
        self.assertEqual(set(receipt["operator_hashes"]), {
            "q34_raw", "W34_raw", "P34_raw", "pairing34_raw"
        })

    def test_scientific_replay_mutation_fails_closed(self) -> None:
        certificate = json.loads(OUTPUT.read_text())
        replay = deepcopy(certificate["scientific_replay"])
        replay["independent_exact_checks"]["raw_q34_squared_zero"] = False
        with self.assertRaisesRegex(ValueError, "weakened"):
            _validate_scientific_payload(replay, IMPORT.fast_receipt())

    def test_stored_schur_gcd_mutation_fails_fast(self) -> None:
        certificate = json.loads(OUTPUT.read_text())
        replay = deepcopy(certificate["scientific_replay"])
        replay["filtered_endpoint_preflight"]["order_six_polynomial_gcd"] = "1"
        with self.assertRaisesRegex(ValueError, "filtered preflight drifted"):
            _validate_scientific_payload(replay, IMPORT.fast_receipt())

    def test_internal_sparse_record_hash_mutation_fails_closed(self) -> None:
        transport, _ = IMPORT._validate_source_payloads()
        reference = transport["operators"]["q34_raw"]
        record = json.loads(IMPORT._git_blob(reference["path"]))
        record["entries"][0][2][0][1] = "3"
        with self.assertRaisesRegex(ValueError, "internal record hash mismatch"):
            IMPORT._load_rational_record("mutated_q34", record, (34, 34))

    def test_causal_and_quantum_gates_remain_closed(self) -> None:
        certificate = json.loads(OUTPUT.read_text())
        self.assertFalse(certificate["green_execution_authorized"])
        self.assertFalse(certificate["quantum_execution_authorized"])
        self.assertEqual(
            certificate["input_gate_update"]["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"],
            "NOT_CONSTRUCTED",
        )
        self.assertIn("No filtered Green extension", certificate["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
