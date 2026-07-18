from __future__ import annotations

from copy import deepcopy
import json
import unittest

from classical_import.analytic_operator_snapshot_attribution import (
    OUTPUT,
    build,
    validate_attribution,
)
from classical_import.verify_analytic_operator_snapshot_attribution import verify


class AnalyticOperatorSnapshotAttributionTests(unittest.TestCase):
    def test_git_tree_and_five_hashes_are_exact(self) -> None:
        value = build()
        self.assertTrue(value["analytic_git_tree_export"]["bytes_equal_to_worktree_export"])
        self.assertEqual(len(value["canonical_hashes"]), 5)
        self.assertNotEqual(value["analytic_producer_commit"], value["source_classical_commit"])
        self.assertEqual(validate_attribution(value)["status"], "SEMANTIC_RECEIVER_ACCEPTED")

    def test_mutations_are_rejected(self) -> None:
        value = build()
        for mutate, message in (
            (lambda row: row["analytic_git_tree_export"].update(blob_sha256="0" * 64), "Git-tree identity"),
            (lambda row: row["canonical_hashes"].update(differential_hash="0" * 64), "classical content"),
            (lambda row: row["physical_analytic_artifacts"][0]["artifact"].update(sha256="0" * 64), "physical artifact binding"),
        ):
            mutant = deepcopy(value)
            mutate(mutant)
            with self.assertRaisesRegex(ValueError, message):
                validate_attribution(mutant)

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
