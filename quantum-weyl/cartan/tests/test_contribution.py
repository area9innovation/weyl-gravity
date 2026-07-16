from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import unittest

from cartan.contribution import (
    EVIDENCE_COMMIT,
    EVIDENCE_PATH,
    OUTPUT_PATH,
    REPOSITORY_ROOT,
    build_contribution,
    validate_contribution,
)


class QuantumDContributionTests(unittest.TestCase):
    def test_checked_in_contribution_reproduces(self) -> None:
        self.assertEqual(
            json.loads(OUTPUT_PATH.read_text(encoding="utf-8")),
            build_contribution(),
        )

    def test_claim_key_and_lifecycle_are_exact(self) -> None:
        contribution = build_contribution()
        self.assertEqual(contribution["team_id"], "quantum")
        self.assertEqual(contribution["generator_id"], "D_compact")
        self.assertEqual(contribution["phase_space_id"], "compact_quantum")
        self.assertEqual(contribution["lifecycle_layer"], "QUANTUM")
        self.assertEqual(contribution["claim_status"], "BLOCKED")
        self.assertIsNone(contribution["verdict"])
        self.assertEqual(
            contribution["dependency_tags"],
            ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "LORENTZIAN-CAUSAL"],
        )
        self.assertTrue(
            any("Green/Hadamard endpoint" in row for row in contribution["established"])
        )
        self.assertTrue(
            any("Ward insertion contract" in row for row in contribution["established"])
        )

    def test_evidence_commit_and_hash_are_content_addressed(self) -> None:
        contribution = build_contribution()
        self.assertEqual(contribution["evidence"]["commit"], EVIDENCE_COMMIT)
        self.assertEqual(contribution["evidence"]["path"], EVIDENCE_PATH)
        payload = subprocess.check_output(
            [
                "git",
                "-C",
                str(REPOSITORY_ROOT),
                "show",
                f"{EVIDENCE_COMMIT}:./{EVIDENCE_PATH}",
            ]
        )
        self.assertEqual(
            contribution["evidence"]["sha256"],
            hashlib.sha256(payload).hexdigest(),
        )

    def test_unknown_generator_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(build_contribution())
        mutated["generator_id"] = "D_UNREGISTERED"
        with self.assertRaisesRegex(ValueError, "registry"):
            validate_contribution(mutated)

    def test_verdict_promotion_is_rejected_while_blocked(self) -> None:
        mutated = copy.deepcopy(build_contribution())
        mutated["verdict"] = "CARTAN_QUANTUM_EXACT"
        with self.assertRaisesRegex(ValueError, "must not emit a verdict"):
            validate_contribution(mutated)


if __name__ == "__main__":
    unittest.main()
