from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from jsonschema import Draft202012Validator

from classical_import.classical_snapshot_compatibility_readiness import (
    OUTPUT,
    SCHEMA,
    build,
    mutation_receipts,
)
from classical_import.classical_snapshot_compatibility_receiver import (
    HASH_KEYS,
    REQUIRED_ROLES,
    synthetic_payload,
    validate_classical_snapshot_compatibility,
)
from classical_import.verify_classical_snapshot_compatibility_readiness import verify


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
FROZEN = HERE / "certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _frozen() -> tuple[str, dict[str, str]]:
    value = json.loads(FROZEN.read_text())
    return value["classical_commit"], value["independent_replay"]["canonical_hashes"]


class ClassicalSnapshotCompatibilityTests(unittest.TestCase):
    def test_synthetic_equal_hash_fixture_and_mutations(self) -> None:
        local_commit, hashes = _frozen()
        analytic_commit = "1" * 40
        payload = synthetic_payload(
            local_commit=local_commit,
            analytic_commit=analytic_commit,
            canonical_hashes=hashes,
        )
        receipt = validate_classical_snapshot_compatibility(
            payload,
            repository_root=ROOT,
            expected_local_commit=local_commit,
            expected_local_hashes=hashes,
            expected_analytic_commit=analytic_commit,
            allow_synthetic_fixture=True,
        )
        self.assertEqual(receipt["matched_hash_count"], len(HASH_KEYS))
        self.assertEqual(receipt["matched_roles"], REQUIRED_ROLES)
        self.assertTrue(
            all(row["rejected"] for row in mutation_receipts(payload, local_commit, hashes))
        )

    def test_physical_path_replays_role_specific_proofs(self) -> None:
        local_commit, hashes = _frozen()
        analytic_commit = "a" * 40
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            local_path = root / "local.json"
            analytic_path = root / "analytic.json"
            local_path.write_text(
                json.dumps(
                    {
                        "result_id": "CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2",
                        "classical_commit": local_commit,
                        "imported_export": {"canonical_hashes": hashes},
                    }
                )
            )
            analytic_path.write_text(
                json.dumps(
                    {
                        "result_id": "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2",
                        "classical_commit": analytic_commit,
                        "canonical_hashes": hashes,
                    }
                )
            )
            payload = synthetic_payload(
                local_commit=local_commit,
                analytic_commit=analytic_commit,
                canonical_hashes=hashes,
            )
            payload["proof_artifacts"] = [
                {"format": "JSON_PROOF", "path": path.name, "sha256": _sha256(path)}
                for path in (local_path, analytic_path)
            ]
            receipt = validate_classical_snapshot_compatibility(
                payload,
                repository_root=root,
                expected_local_commit=local_commit,
                expected_local_hashes=hashes,
                expected_analytic_commit=analytic_commit,
            )
            self.assertEqual(receipt["status"], "SEMANTIC_RECEIVER_ACCEPTED")

            mismatch = deepcopy(payload)
            analytic = json.loads(analytic_path.read_text())
            analytic["canonical_hashes"]["differential_hash"] = "0" * 64
            analytic_path.write_text(json.dumps(analytic))
            mismatch["proof_artifacts"][1]["sha256"] = _sha256(analytic_path)
            with self.assertRaisesRegex(ValueError, "analytic proof content"):
                validate_classical_snapshot_compatibility(
                    mismatch,
                    repository_root=root,
                    expected_local_commit=local_commit,
                    expected_local_hashes=hashes,
                    expected_analytic_commit=analytic_commit,
                )

    def test_readiness_reproduces_and_independently_verifies(self) -> None:
        generated = build()
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(generated)
        self.assertEqual(json.loads(OUTPUT.read_text()), generated)
        self.assertEqual(verify(), generated)
        self.assertFalse(
            generated["claim_flags"]["PHYSICAL_COMPATIBILITY_BRIDGE_SUPPLIED"]
        )

    def test_independent_verifier_rejects_proof_digest_drift(self) -> None:
        value = json.loads(OUTPUT.read_text())
        value["proof_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "proof digest"):
            verify(value)


if __name__ == "__main__":
    unittest.main()
