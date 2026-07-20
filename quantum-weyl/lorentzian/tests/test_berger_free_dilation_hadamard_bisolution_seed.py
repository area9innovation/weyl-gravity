from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_free_dilation_hadamard_bisolution_seed import (
    positive_metric_obstruction_replay,
    theorem_hypothesis_replay,
    validate,
)
from lorentzian.berger_free_dilation_hadamard_bisolution_seed_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_free_dilation_hadamard_bisolution_seed import (
    verify,
)


class BergerFreeDilationHadamardBisolutionSeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (
                HERE
                / "schema/berger-free-dilation-hadamard-bisolution-seed-v1.schema.json"
            ).read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_theorem_hypotheses_pass_for_free_dilation(self) -> None:
        replay = theorem_hypothesis_replay()
        self.assertTrue(replay["theorem_applies"])
        self.assertTrue(all(replay["conclusions"].values()))

    def test_nonscalar_principal_symbol_rejected(self) -> None:
        replay = theorem_hypothesis_replay(scalar_wave_principal_symbol=False)
        self.assertFalse(replay["theorem_applies"])
        self.assertFalse(any(replay["conclusions"].values()))

    def test_degenerate_form_rejected(self) -> None:
        replay = theorem_hypothesis_replay(
            nondegenerate_sesquilinear_form=False
        )
        self.assertFalse(replay["theorem_applies"])

    def test_missing_formal_selfadjointness_rejected(self) -> None:
        replay = theorem_hypothesis_replay(formally_selfadjoint=False)
        self.assertFalse(replay["theorem_applies"])

    def test_jordan_incidence_forces_indefinite_auxiliary_carrier(self) -> None:
        replay = positive_metric_obstruction_replay()
        self.assertTrue(replay["all_pass"])
        self.assertEqual(replay["signature"], [20, 20])
        self.assertFalse(replay["positive_state_follows"])

    def test_positive_state_promotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_FREE_DILATION_POSITIVE_HADAMARD_STATE"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
