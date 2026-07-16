from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_retained_stationary_spectral_preflight import validate
from lorentzian.berger_retained_stationary_spectral_preflight_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_retained_stationary_spectral_preflight import verify


class BergerRetainedStationarySpectralPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (HERE / "schema/berger-retained-stationary-spectral-preflight-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_mixed_order_temporal_leading_ranks_are_exact(self) -> None:
        blocks = self.certificate["stationary_pencil_inventory"][
            "retained_P26_temporal_audit"
        ]
        self.assertEqual(blocks["ghost"]["e0_four_leading_rank"], 3)
        self.assertEqual(blocks["metric"]["e0_four_leading_rank"], 8)
        self.assertEqual(blocks["metric_antifield"]["e0_four_leading_rank"], 8)
        self.assertEqual(blocks["identity"]["e0_four_leading_rank"], 3)
        self.assertEqual(
            blocks["metric"]["uniform_fourth_order_Cauchy_reduction"],
            "INVALID_MIXED_ORDER",
        )

    def test_hybrid_companion_and_Cauchy_target_dimensions(self) -> None:
        inventory = self.certificate["stationary_pencil_inventory"]
        self.assertEqual(
            inventory["hybrid_second_order_companion"]["total_bundle_rank"], 52
        )
        self.assertEqual(
            inventory["first_order_Cauchy_target"]["Cauchy_fibre_rank"], 104
        )
        self.assertTrue(all(inventory["checks"].values()))

    def test_two_slot_formula_precedes_operator_formula(self) -> None:
        lift = self.certificate["two_slot_covariance_lift"]
        self.assertEqual(
            lift["primary_bilinear_formula"],
            "omega54(f,h)=omega26(pi_cl f,pi_cl h)",
        )
        self.assertIn("not used without", lift["warning"])

    def test_Riesz_projector_is_conditional_and_not_causal(self) -> None:
        policy = self.certificate["generalized_zero_and_Riesz_policy"]
        self.assertEqual(policy["Riesz_projector_status"], "NOT_DEFINED")
        self.assertIn("no spectral projector", policy["causal_projector_policy"])
        self.assertIn("isolation is proved", policy["state_projector_policy"])

    def test_minimal_missing_carrier_is_closed_A104(self) -> None:
        missing = self.certificate["minimal_missing_carrier"]
        self.assertEqual(missing["status"], "MINIMAL_MISSING_ANALYTIC_CARRIER")
        self.assertIn("A104", missing["carrier"])
        self.assertEqual(
            self.certificate["next_gate"],
            "BERGER_A104_CLOSED_GENERATOR_AND_ISOLATED_ZERO_THEOREM",
        )

    def test_spectral_and_Hadamard_overclaims_fail_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_RETAINED_ZERO_ISOLATED"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)
        mutant = deepcopy(self.certificate)
        mutant["closed_generator_contract"]["closed_realization_status"] = (
            "CERTIFIED"
        )
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
