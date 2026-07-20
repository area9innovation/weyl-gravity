from __future__ import annotations

import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_temporal_cutoff_companion_green_family import (
    cutoff_specialization_replay,
    mutate_overpromotion,
    validate,
)
from lorentzian.berger_temporal_cutoff_companion_green_family_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_temporal_cutoff_companion_green_family import verify


class BergerTemporalCutoffCompanionGreenFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (HERE / "schema/berger-temporal-cutoff-companion-green-family-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_cutoff_specialization_uses_nonstationary_theorem(self) -> None:
        replay = cutoff_specialization_replay()
        self.assertTrue(replay["all_pass"])
        self.assertEqual(
            replay["operators"]["cutoff_companion"],
            "C_chi=[[Box_2,-I10],[chi(t)V_2,Box_2]]",
        )

    def test_stationarity_mutation_is_rejected(self) -> None:
        mutant = cutoff_specialization_replay(drop_time_dependence=True)
        self.assertFalse(mutant["all_pass"])
        self.assertFalse(
            mutant["checks"]["generic_theorem_accepts_cutoff_time_dependence"]
        )

    def test_Green_properties_are_certified(self) -> None:
        flags = self.certificate["claim_flags"]
        self.assertTrue(flags["BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY"])
        self.assertTrue(flags["BERGER_CUTOFF_COMPANION_BOTH_INVERSE_IDENTITIES"])
        self.assertTrue(flags["BERGER_CUTOFF_COMPANION_CAUSAL_SUPPORT"])
        self.assertTrue(flags["BERGER_CUTOFF_COMPANION_ADJOINT_REVERSAL"])

    def test_microlocal_and_Hadamard_flags_remain_false(self) -> None:
        flags = self.certificate["claim_flags"]
        self.assertFalse(flags["BERGER_CUTOFF_COMPANION_WAVEFRONT_THEOREM"])
        self.assertFalse(flags["BERGER_CUTOFF_COMPANION_NULL_CONE_DECOMPOSABLE"])
        self.assertFalse(flags["BERGER_REGULAR_GREENHYP_MORPHISM"])
        self.assertFalse(flags["BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION"])

    def test_wavefront_promotion_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutate_overpromotion(self.certificate))

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
