from __future__ import annotations

from copy import deepcopy
import json
import unittest

from spectral.euclidean.round_s4_tt_hessian_dictionary import OUTPUT, build, derive
from spectral.euclidean.tt_hessian_dictionary_receiver import ROOT, validate_tt_hessian_dictionary
from spectral.euclidean.verify_round_s4_tt_hessian_dictionary import verify


class RoundS4TTHessianDictionaryTests(unittest.TestCase):
    def test_spin_two_factor_specialization_and_normalization(self) -> None:
        replay = derive()
        self.assertEqual(replay["source"]["shifts_by_depth"], [4, 2])
        self.assertEqual(
            replay["operator_replay"]["repository_coefficients_ascending"],
            ["4", "3", "1/2"],
        )
        self.assertEqual(replay["formal_replay"]["Hessian_kernel"], 0)

    def test_committed_dictionary_matches_producer_and_independent_replay(self) -> None:
        payload = build()
        self.assertEqual(json.loads(OUTPUT.read_text()), payload)
        receipt = validate_tt_hessian_dictionary(
            payload,
            repository_root=ROOT,
            expected_classical_commit=payload["classical_commit"],
        )
        self.assertEqual(receipt["status"], "SEMANTIC_RECEIVER_ACCEPTED")
        self.assertEqual(verify()["status"], "INDEPENDENT_REPLAY_ACCEPTED")

    def test_shift_and_digest_mutations_fail_closed(self) -> None:
        payload = build()
        shift_mutant = deepcopy(payload)
        shift_mutant["operator_dictionary"]["upper_factor"] = "Delta_2_perp(5)"
        with self.assertRaises(Exception):
            validate_tt_hessian_dictionary(
                shift_mutant,
                repository_root=ROOT,
                expected_classical_commit=payload["classical_commit"],
            )
        digest_mutant = deepcopy(payload)
        digest_mutant["background"]["scalar_curvature"] = 13
        with self.assertRaises(Exception):
            validate_tt_hessian_dictionary(
                digest_mutant,
                repository_root=ROOT,
                expected_classical_commit=payload["classical_commit"],
            )


if __name__ == "__main__":
    unittest.main()
