from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_cutoff_companion_microlocal_response_preflight import (
    orientation_sector_replay,
    regularity_replay,
    validate,
)
from lorentzian.berger_cutoff_companion_microlocal_response_preflight_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_cutoff_companion_microlocal_response_preflight import verify


class BergerCutoffCompanionMicrolocalResponsePreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (HERE / "schema/berger-cutoff-companion-microlocal-response-preflight-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_cutoff_kernel_is_factorwise_null(self) -> None:
        theorem = self.certificate["cutoff_kernel_theorem"]
        self.assertEqual(
            theorem["certified_inclusion"],
            "WF(E_chi) subset (N_plus union N_minus) x (N_plus union N_minus)",
        )

    def test_only_same_orientation_sectors_remain(self) -> None:
        self.assertEqual(
            orientation_sector_replay()["unresolved_same_orientation_sectors"],
            ["N+ x N+", "N- x N-"],
        )

    def test_timeslice_source_map_is_regular(self) -> None:
        replay = regularity_replay()
        self.assertTrue(replay["all_pass"])
        self.assertTrue(all(replay["conditions"].values()))

    def test_support_hypotheses_fail_closed(self) -> None:
        self.assertFalse(
            regularity_replay(spatially_compact_causal_output=False)["all_pass"]
        )
        self.assertFalse(regularity_replay(compact_time_transition=False)["all_pass"])
        self.assertFalse(regularity_replay(continuous_transpose=False)["all_pass"])

    def test_response_morphism_promotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_REGULAR_GREENHYP_MORPHISM"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
