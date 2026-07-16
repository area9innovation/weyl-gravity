from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


TRANSFER_ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, TRANSFER_ROOT / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


IMPORT = _load("berger_support_local_q2_import", "berger_support_local_q2_import.py")
CERTIFICATE = _load(
    "berger_support_local_q2_import_certificate_test",
    "berger_support_local_q2_import_certificate.py",
)
SCHEMA_PATH = TRANSFER_ROOT / "schema/berger-support-local-q2-import-v1.schema.json"


class BergerSupportLocalQ2ImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.imported = IMPORT.import_support_local_q2()
        cls.payload = IMPORT.build_import_payload()

    def test_complete_payload_is_pinned_and_parsed(self) -> None:
        self.assertEqual(self.imported.parsed.term_count, 150305)
        self.assertEqual(len(self.imported.parsed.entries), 4624)
        self.assertEqual(self.imported.nonzero_rows, 39)
        self.assertEqual(self.imported.parsed.maximum_total_jet_order, 6)
        self.assertEqual(self.imported.coefficient_field, "Q(sqrt(10))")

    def test_specialization_is_exact_and_explicit(self) -> None:
        self.assertEqual(
            self.payload["coverage"]["specialization"],
            {"alpha_B": "5", "u": "3*sqrt(10)/20", "v": "2*sqrt(10)/3"},
        )
        with self.assertRaisesRegex(ValueError, "exact rational"):
            IMPORT._quadratic_pair({"rational": 0.5, "sqrt10": 0})

    def test_schema_identity_and_checked_certificate_reproduce(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        certificate = CERTIFICATE.build_certificate()
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), set(certificate))
        self.assertEqual(json.loads(CERTIFICATE.OUTPUT.read_text()), certificate)

    def test_scientific_replay_remains_a_separate_gate(self) -> None:
        self.assertEqual(self.payload["scientific_replay_gate"]["status"], "REPLAY_PENDING")
        self.assertTrue(self.payload["claim_flags"]["CLASSICAL_SUPPORT_LOCAL_Q2_IMPORTED"])
        self.assertFalse(
            self.payload["claim_flags"][
                "SCIENTIFIC_ARITY_TWO_IDENTITIES_INDEPENDENTLY_REPLAYED"
            ]
        )
        self.assertFalse(self.payload["claim_flags"]["QUANTUM_CLAIM"])


if __name__ == "__main__":
    unittest.main()
