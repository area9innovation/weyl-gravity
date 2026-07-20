from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_ghost_identity_global_hadamard_pair import (
    endpoint_pullback_replay,
    ghost_identity_dilation_replay,
    validate,
)
from lorentzian.berger_ghost_identity_global_hadamard_pair_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_ghost_identity_global_hadamard_pair import verify


class BergerGhostIdentityGlobalHadamardPairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (
                HERE
                / "schema/"
                "berger-ghost-identity-global-hadamard-pair-v1.schema.json"
            ).read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_rank_twelve_dilation_hypotheses(self) -> None:
        result = ghost_identity_dilation_replay()
        self.assertTrue(result["all_pass"])
        self.assertEqual(result["signature"], [6, 6])

    def test_both_wave_factors_are_load_bearing(self) -> None:
        result = ghost_identity_dilation_replay(
            factor_2_normally_hyperbolic=False
        )
        self.assertFalse(result["all_pass"])

    def test_formal_adjoint_relation_is_load_bearing(self) -> None:
        result = ghost_identity_dilation_replay(
            identity_is_formal_adjoint=False
        )
        self.assertFalse(result["all_pass"])

    def test_typed_endpoint_pullback(self) -> None:
        result = endpoint_pullback_replay()
        self.assertTrue(result["all_pass"])
        self.assertEqual(
            result["symbolic_pulled_matrix"], [["0", "b"], ["b", "0"]]
        )

    def test_untyped_symmetric_pullback_fails(self) -> None:
        self.assertFalse(
            endpoint_pullback_replay(
                use_adjoint_source_inclusion=False
            )["all_pass"]
        )

    def test_q26_overpromotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_26_ROW_BRST_HADAMARD"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
