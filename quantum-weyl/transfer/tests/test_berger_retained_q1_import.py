from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


TRANSFER_ROOT = Path(__file__).resolve().parents[1]
if str(TRANSFER_ROOT) not in sys.path:
    sys.path.insert(0, str(TRANSFER_ROOT))
MODULE_PATH = TRANSFER_ROOT / "berger_retained_q1_import_certificate.py"
SPEC = importlib.util.spec_from_file_location(
    "berger_retained_q1_import_certificate_test", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
CERTIFICATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERTIFICATE
SPEC.loader.exec_module(CERTIFICATE)
IMPORT = sys.modules[CERTIFICATE.build_import.__module__]


class BergerRetainedQ1ImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.classical = IMPORT._git_json(
            IMPORT.CERTIFICATE_RELATIVE, commit=IMPORT.THEOREM_COMMIT
        )
        cls.schema = IMPORT._git_json(
            IMPORT.SCHEMA_RELATIVE, commit=IMPORT.SCHEMA_COMMIT
        )
        cls.layout = IMPORT._git_json(
            IMPORT.LAYOUT_RELATIVE, commit=IMPORT.THEOREM_COMMIT
        )

    def test_checked_in_certificate_reproduces(self) -> None:
        checked = json.loads(CERTIFICATE.OUTPUT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checked, CERTIFICATE.build_certificate())

    def test_complete_retained_q1_is_imported_without_opening_nd2(self) -> None:
        result = CERTIFICATE.build_certificate()
        self.assertTrue(result["coverage"]["retained_minimal_q1_rows_complete"])
        self.assertEqual(result["coverage"]["retained_minimal_rows"], 26)
        self.assertFalse(result["coverage"]["nonminimal_rows_complete"])
        self.assertFalse(result["coverage"]["complete_classical_contraction"])
        self.assertEqual(
            result["nd2_gate"]["retained_minimal_q1"],
            "AVAILABLE_VERIFIED_PREREQUISITE",
        )
        self.assertFalse(result["nd2_gate"]["physical_execution_authorized"])

    def test_source_layers_are_pinned_separately(self) -> None:
        result = CERTIFICATE.build_certificate()["classical_result"]
        self.assertEqual(result["theorem_commit"], IMPORT.THEOREM_COMMIT)
        self.assertEqual(result["registration_commit"], IMPORT.REGISTRATION_COMMIT)
        self.assertEqual(result["portable_schema_commit"], IMPORT.SCHEMA_COMMIT)

    def test_schema_regression_is_rejected(self) -> None:
        mutant = deepcopy(self.schema)
        mutant["properties"]["q1_blocks"].pop("properties")
        with self.assertRaisesRegex(ValueError, "undefined"):
            IMPORT.validate_classical_retained_q1(
                self.classical, mutant, self.layout
            )

    def test_hash_and_expression_language_drift_are_rejected(self) -> None:
        forged_hash = deepcopy(self.classical)
        forged_hash["q1_blocks"]["K_spatial"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            IMPORT.validate_classical_retained_q1(
                forged_hash, self.schema, self.layout
            )

        forged_expression = deepcopy(self.classical)
        record = forged_expression["q1_blocks"]["K_spatial"]
        record["entries"][0][2][0][1] = "forged_symbol"
        body = {"shape": record["shape"], "entries": record["entries"]}
        record["sha256"] = IMPORT._canonical_hash(body)
        with self.assertRaisesRegex(ValueError, "undeclared expression token"):
            IMPORT.validate_classical_retained_q1(
                forged_expression, self.schema, self.layout
            )

    def test_noether_identity_mutation_is_rejected_after_rehash(self) -> None:
        mutant = deepcopy(self.classical)
        record = mutant["q1_blocks"]["minus_K_spatial_sharp"]
        coefficient = record["entries"][0][2][0][1]
        record["entries"][0][2][0][1] = f"2*({coefficient})"
        body = {"shape": record["shape"], "entries": record["entries"]}
        record["sha256"] = IMPORT._canonical_hash(body)
        with self.assertRaisesRegex(ValueError, "Noether row"):
            IMPORT.validate_classical_retained_q1(mutant, self.schema, self.layout)


if __name__ == "__main__":
    unittest.main()
