from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_cutoff_volterra_microlocal_orientation_reduction import (
    convergence_gate_replay,
    finite_term_orientation_replay,
    mixed_side_negative_control,
    validate,
)
from lorentzian.berger_cutoff_volterra_microlocal_orientation_reduction_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_cutoff_volterra_microlocal_orientation_reduction import (
    verify,
)


class BergerCutoffVolterraMicrolocalOrientationReductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (
                HERE
                / "schema/berger-cutoff-volterra-microlocal-orientation-reduction-v1.schema.json"
            ).read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_all_finite_plus_terms_are_oriented(self) -> None:
        replay = finite_term_orientation_replay(sign="PLUS", sample_order=12)
        self.assertTrue(replay["arbitrary_order_conclusion"])
        self.assertTrue(all(row["contained_in_Gamma"] for row in replay["sampled_terms"]))

    def test_all_finite_minus_terms_are_oriented(self) -> None:
        replay = finite_term_orientation_replay(sign="MINUS", sample_order=12)
        self.assertTrue(replay["arbitrary_order_conclusion"])
        self.assertTrue(all(row["contained_in_Gamma"] for row in replay["sampled_terms"]))

    def test_mixed_side_control_is_rejected(self) -> None:
        replay = mixed_side_negative_control()
        self.assertTrue(replay["contains_mixed_direction"])
        self.assertFalse(replay["contained_in_one_oriented_Gamma"])

    def test_sobolev_convergence_does_not_close_gate(self) -> None:
        replay = convergence_gate_replay()
        self.assertTrue(
            replay["existing_convergence"]["finite_slab_all_Sobolev_operator_norm"]
        )
        self.assertFalse(replay["gate_passes"])
        self.assertFalse(any(replay["conditional_conclusions"].values()))

    def test_hormander_convergence_is_sufficient_condition(self) -> None:
        replay = convergence_gate_replay(hormander_normal_convergence=True)
        self.assertTrue(replay["gate_passes"])
        self.assertTrue(all(replay["conditional_conclusions"].values()))

    def test_infinite_orientation_promotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"][
            "BERGER_CUTOFF_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION"
        ] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
