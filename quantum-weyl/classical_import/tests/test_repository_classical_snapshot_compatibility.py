from __future__ import annotations

from copy import deepcopy
import json
import unittest

from classical_import.classical_snapshot_compatibility_receiver import validate_classical_snapshot_compatibility
from classical_import.repository_classical_snapshot_compatibility import LOCAL_IMPORT, OUTPUT, ROOT, build
from classical_import.verify_repository_classical_snapshot_compatibility import verify


class RepositoryClassicalSnapshotCompatibilityTests(unittest.TestCase):
    def test_physical_bridge_is_semantically_accepted(self) -> None:
        value = build()
        local = json.loads(LOCAL_IMPORT.read_text())
        receipt = validate_classical_snapshot_compatibility(
            value,
            repository_root=ROOT,
            expected_local_commit=local["classical_commit"],
            expected_local_hashes=local["independent_replay"]["canonical_hashes"],
            expected_analytic_commit=value["analytic_operator_snapshot"]["classical_commit"],
        )
        self.assertEqual(receipt["status"], "SEMANTIC_RECEIVER_ACCEPTED")
        self.assertEqual(receipt["matched_hash_count"], 5)

    def test_attribution_hash_mutation_is_rejected(self) -> None:
        value = build()
        local = json.loads(LOCAL_IMPORT.read_text())
        mutant = deepcopy(value)
        mutant["proof_artifacts"][1]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "artifact hash mismatch"):
            validate_classical_snapshot_compatibility(
                mutant,
                repository_root=ROOT,
                expected_local_commit=local["classical_commit"],
                expected_local_hashes=local["independent_replay"]["canonical_hashes"],
                expected_analytic_commit=value["analytic_operator_snapshot"]["classical_commit"],
            )

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
