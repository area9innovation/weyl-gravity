from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


IMPORT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = IMPORT_ROOT / "verify_snapshot.py"
SPEC = importlib.util.spec_from_file_location("quantum_classical_import", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class ClassicalImportSnapshotTests(unittest.TestCase):
    def test_checked_in_certificate_is_current_and_fail_closed(self) -> None:
        generated = VERIFY.build_certificate()
        checked_in = json.loads(VERIFY.DEFAULT_CERTIFICATE.read_text(encoding="utf-8"))
        self.assertEqual(generated, checked_in)
        self.assertEqual(generated["artifact_integrity_status"], "VERIFIED")
        self.assertEqual(generated["gate_a_status"], "FAIL_CLOSED")
        self.assertFalse(generated["publishable_quantum_results_allowed"])
        self.assertEqual(generated["dependency_tags"], ["LOCAL-ALGEBRAIC"])

    def test_every_unavailable_or_partial_export_is_reported(self) -> None:
        snapshot = json.loads(VERIFY.DEFAULT_SNAPSHOT.read_text(encoding="utf-8"))
        expected = sorted(
            record["export_id"]
            for record in snapshot["required_exports"]
            if record["status"] != "AVAILABLE"
        )
        certificate = VERIFY.build_certificate()
        self.assertEqual(certificate["missing_or_incomplete_exports"], expected)
        self.assertEqual(
            set(record["export_id"] for record in snapshot["required_exports"]),
            VERIFY.REQUIRED_EXPORT_IDS,
        )

    def test_manifest_cannot_promote_gate_with_missing_exports(self) -> None:
        snapshot = json.loads(VERIFY.DEFAULT_SNAPSHOT.read_text(encoding="utf-8"))
        snapshot["gate_a_status"] = "VERIFIED"
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temporary:
            candidate = Path(temporary) / "invalid-promotion.json"
            candidate.write_text(json.dumps(snapshot), encoding="utf-8")
            with self.assertRaisesRegex(
                VERIFY.SnapshotError, "declared gate_a_status disagrees"
            ):
                VERIFY.build_certificate(candidate)

    def test_artifact_digest_mismatch_fails_closed(self) -> None:
        snapshot = json.loads(VERIFY.DEFAULT_SNAPSHOT.read_text(encoding="utf-8"))
        snapshot["required_exports"][0]["artifacts"][0]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temporary:
            candidate = Path(temporary) / "bad-hash.json"
            candidate.write_text(json.dumps(snapshot), encoding="utf-8")
            with self.assertRaisesRegex(VERIFY.SnapshotError, "hash mismatch"):
                VERIFY.build_certificate(candidate)


if __name__ == "__main__":
    unittest.main()
