import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_independent_node_scaling_contraction import (
    OUTPUT,
    SCHEMA,
    build,
)


class Candidate1720IndependentNodeScalingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_bottleneck_is_necessary(self) -> None:
        scaling = self.payload["independent_scaling"]
        self.assertIn("intermediate", scaling["strict_opposite_sign_bottleneck"])
        self.assertEqual(
            scaling["incidence_set"],
            "I={(x,y) in [0,1]^2:c(x,y)=0 and M_K(x,y)=0}",
        )
        self.assertTrue(
            self.payload["classification"]["strict_opposite_sign_incidence_necessary"]
        )

    def test_incidence_is_sufficient_by_three_stages(self) -> None:
        construction = self.payload["three_stage_contraction"]
        self.assertIn("initial square direction", construction["stage_1"])
        self.assertIn("c=M_K=0", construction["stage_2"])
        self.assertIn("phase-real", construction["stage_3"])
        self.assertIn("if and only if", construction["equivalence"])
        self.assertTrue(
            self.payload["classification"]["strict_opposite_sign_incidence_sufficient"]
        )

    def test_positive_collinear_formula_is_explicit(self) -> None:
        case = self.payload["bottleneck_incidence"]["both_weighted_moments_nonzero"]
        self.assertIn("V=kappa*U", case["positive_ray_case"])
        self.assertIn("y_*=-delta/(a*kappa-b)", case["positive_ray_case"])
        self.assertIn("0<=x_*<=1", case["positive_ray_case"])
        self.assertIn("do not lie on the same positive ray", case["all_other_directions"])

    def test_one_zero_moment_cases_are_retained(self) -> None:
        incidence = self.payload["bottleneck_incidence"]
        self.assertIn("-delta/a", incidence["U_zero_V_nonzero"])
        self.assertIn("delta/b", incidence["U_nonzero_V_zero"])
        self.assertTrue(
            self.payload["classification"]["one_zero_moment_incidence_formulas_certified"]
        )

    def test_candidate_scopes_remain_distinct_and_fail_closed(self) -> None:
        disposition = self.payload["candidate_disposition"]
        self.assertIn("alpha>0, delta<0", disposition["candidate17"])
        self.assertIn("strict opposite-sign", disposition["candidate20_off_balance"])
        flags = self.payload["classification"]
        self.assertFalse(flags["candidate17_complete_singular_rotation_zero_fibre_connected"])
        self.assertFalse(flags["candidate20_off_balance_complete_singular_rotation_zero_fibre_connected"])
        self.assertFalse(flags["general_nonradial_no_go"])
        self.assertFalse(flags["K_direction_deformation_classified"])

    def test_schema_rejects_K_deformation_promotion(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["K_direction_deformation_classified"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)

    def test_schema_rejects_complete_candidate17_promotion(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"][
            "candidate17_complete_singular_rotation_zero_fibre_connected"
        ] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)


if __name__ == "__main__":
    unittest.main()
