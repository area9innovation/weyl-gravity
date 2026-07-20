from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest

from d_quotient_classical.compensator.verify_candidate_ab_neither_comparison import (
    verify,
)


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_CANDIDATE_AB_NEITHER_COMPARISON_V1.json"
)


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _refresh_selection_hash(value: dict[str, object]) -> None:
    value["selection_hash"] = _digest(
        {
            "action_hashes": value["action_hashes"],
            "common_conventions": value["common_conventions"],
            "gates": value["seven_gate_matrix"],
            "selection_input": value["selection_rule"],
        }
    )


class CandidateABNeitherComparisonTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text())

    def test_independent_replay(self) -> None:
        verify(deepcopy(self.value))

    def test_import_commit_mutation_is_detected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["imports"]["candidate_A"]["scientific_commit"] = "0" * 40
        with self.assertRaises(AssertionError):
            verify(mutated)

    def test_import_hash_mutation_is_detected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["imports"]["candidate_B"]["report_sha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            verify(mutated)

    def test_declared_fixture_cannot_drift_even_with_rehashed_selection(self) -> None:
        mutated = deepcopy(self.value)
        mutated["common_conventions"]["M_P_squared"] = "1/5"
        _refresh_selection_hash(mutated)
        with self.assertRaises(AssertionError):
            verify(mutated)

    def test_candidate_a_cannot_be_selected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["claim_flags"]["CANDIDATE_A_SELECTED"] = True
        with self.assertRaises(Exception):
            verify(mutated)

    def test_candidate_b_cannot_be_selected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["terminal_selection"] = "candidate_B"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_decisive_gate_cannot_be_deleted(self) -> None:
        mutated = deepcopy(self.value)
        mutated["seven_gate_matrix"][4]["candidate_A"]["status"] = "PASS"
        _refresh_selection_hash(mutated)
        with self.assertRaises(AssertionError):
            verify(mutated)

    def test_partial_score_selection_cannot_be_enabled(self) -> None:
        mutated = deepcopy(self.value)
        mutated["selection_rule"]["partial_scores_forbidden"] = False
        _refresh_selection_hash(mutated)
        with self.assertRaises(Exception):
            verify(mutated)

    def test_hybrid_cannot_be_authorized(self) -> None:
        mutated = deepcopy(self.value)
        mutated["strict_downstream_disposition"]["hybrid_authorized"] = True
        with self.assertRaises(Exception):
            verify(mutated)

    def test_selected_action_hash_cannot_be_exported(self) -> None:
        mutated = deepcopy(self.value)
        mutated["strict_downstream_disposition"]["selected_action_hash"] = (
            mutated["action_hashes"]["candidate_A"]
        )
        with self.assertRaises(Exception):
            verify(mutated)

    def test_scoped_result_cannot_be_promoted_to_universal_or_quantum(self) -> None:
        for flag in ("UNIVERSAL_COMPENSATOR_NO_GO", "HADAMARD_OR_QUANTUM_RESULT"):
            with self.subTest(flag=flag):
                mutated = deepcopy(self.value)
                mutated["claim_flags"][flag] = True
                with self.assertRaises(Exception):
                    verify(mutated)


if __name__ == "__main__":
    unittest.main()
