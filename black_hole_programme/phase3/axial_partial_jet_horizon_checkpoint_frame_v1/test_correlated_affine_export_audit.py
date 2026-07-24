#!/usr/bin/env python3
"""Tests for the correlated-affine export boundary."""
from __future__ import annotations

import json
import unittest

from . import correlated_affine_export_audit as audit


class CorrelatedAffineExportAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = audit.compute()

    def test_all_representation_facts_close(self) -> None:
        self.assertTrue(all(self.result["representation_audit"].values()))

    def test_existing_checkpoint_is_not_affine_resumable(self) -> None:
        source = json.loads(audit.SOURCE_RUN.read_text())
        self.assertFalse(
            audit.checkpoint_has_correlated_export(source["checkpoint_chain"][-1])
        )

    def test_label_only_mutation_does_not_pass(self) -> None:
        mutant = {"representation": "affine Taylor model"}
        self.assertFalse(audit.checkpoint_has_correlated_export(mutant))

    def test_complete_synthetic_payload_passes_shape_gate(self) -> None:
        payload = {
            "correlated_state": {
                key: {} for key in audit.REQUIRED_CORRELATED_KEYS
            }
        }
        self.assertTrue(audit.checkpoint_has_correlated_export(payload))

    def test_restart_precedes_ball_seed_and_normalization(self) -> None:
        restart = self.result["rerun_export_contract"]["earliest_required_restart"]
        self.assertEqual(restart["rho"], "1/4194304")
        self.assertIn("before seed_vector", restart["stage"])

    def test_no_successor_claim(self) -> None:
        flags = self.result["claim_flags"]
        self.assertFalse(flags["correlated_pivot_certified"])
        self.assertFalse(flags["successor_substep_certified"])
        self.assertFalse(self.result["terminal"]["successor_substep_attempted"])


if __name__ == "__main__":
    unittest.main()
