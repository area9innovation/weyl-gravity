from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_graded_causal_state_space_contract import (
    causal_algebra_replay,
    validate,
)
from lorentzian.berger_graded_causal_state_space_contract_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_graded_causal_state_space_contract import verify


class BergerGradedCausalStateSpaceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (HERE / "schema/berger-graded-causal-state-space-contract-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_complete_graded_row_and_pairing_ledger(self) -> None:
        replay = self.certificate["row_pairing_replay"]
        self.assertEqual(replay["degree_ranks"], [5, 22, 22, 5])
        self.assertEqual((replay["even_rows"], replay["odd_rows"]), (27, 27))
        self.assertEqual(replay["odd_Darboux_dual_pairs"], 27)
        self.assertEqual(replay["pairing_rank"], 54)
        self.assertTrue(all(replay["checks"].values()))

    def test_causal_pairing_is_q_closed_and_graded(self) -> None:
        replay = causal_algebra_replay()
        self.assertTrue(all(replay["checks"].values()))
        self.assertEqual(
            replay["chain_identity"], "q54 Delta_54+Delta_54 q54=0"
        )
        policy = self.certificate["graded_quantization_policy"]
        self.assertIn("commutator", policy["even_rows"])
        self.assertIn("anticommutator", policy["odd_rows"])

    def test_state_target_and_zero_modes_are_fail_closed(self) -> None:
        self.assertEqual(
            self.certificate["two_point_target"]["status"], "NOT_CONSTRUCTED"
        )
        policy = self.certificate["zero_mode_policy"]
        self.assertEqual(policy["residual_conformal_generators"], 15)
        self.assertIn("distinct", policy["no_conflation"])

    def test_positivity_is_only_a_physical_quotient_target(self) -> None:
        policy = self.certificate["positivity_and_krein_policy"]
        self.assertEqual(policy["full_BV_positive_state"], "NOT_CLAIMED")
        self.assertEqual(
            policy["reduced_Krein_status"],
            "REDUCED-MODE_EVIDENCE_ONLY_NOT_DISTRIBUTIONAL",
        )

    def test_hadamard_and_quantum_overclaims_are_rejected(self) -> None:
        for flag in (
            "BERGER_54_ROW_BRST_HADAMARD",
            "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.certificate)
            mutant["claim_flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "over-promoted"):
                validate(mutant)

        mutant = deepcopy(self.certificate)
        mutant["two_point_target"]["status"] = "CONSTRUCTED"
        with self.assertRaisesRegex(ValueError, "covariance"):
            validate(mutant)

        mutant = deepcopy(self.certificate)
        mutant["positivity_and_krein_policy"]["full_BV_positive_state"] = (
            "CERTIFIED"
        )
        with self.assertRaisesRegex(ValueError, "positivity"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
