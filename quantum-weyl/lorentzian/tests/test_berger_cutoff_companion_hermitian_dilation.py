from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_cutoff_companion_hermitian_dilation import (
    dilation_replay,
    endpoint_morphism_replay,
    validate,
)
from lorentzian.berger_cutoff_companion_hermitian_dilation_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_cutoff_companion_hermitian_dilation import verify


class BergerCutoffCompanionHermitianDilationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (HERE / "schema/berger-cutoff-companion-hermitian-dilation-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_off_diagonal_metric_makes_dilation_Hermitian(self) -> None:
        replay = dilation_replay()
        self.assertTrue(replay["all_pass"])
        self.assertTrue(replay["checks"]["H_adjoint_H_equals_D"])

    def test_second_raw_block_is_rejected(self) -> None:
        self.assertFalse(dilation_replay(include_adjoint_block=False)["all_pass"])

    def test_two_regular_Cauchy_legs(self) -> None:
        replay = endpoint_morphism_replay()
        self.assertTrue(replay["all_pass"])
        self.assertTrue(replay["checks"]["Fewster_Theorem_3_5e_applies_twice"])

    def test_missing_endpoint_agreement_is_rejected(self) -> None:
        self.assertFalse(endpoint_morphism_replay(past_agreement=False)["all_pass"])
        self.assertFalse(endpoint_morphism_replay(future_agreement=False)["all_pass"])

    def test_cone_mapping_promotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_DILATED_RESPONSE_MORPHISM_CONE_MAPPING"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
