import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_moving_square_contraction import (
    OUTPUT,
    SCHEMA,
    build,
)


class Candidate1720MovingSquareContractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_cartan_square_moment_image_is_complete_ball(self) -> None:
        ball = self.payload["cartan_square_moment_ball"]
        self.assertEqual(ball["normalized_moment_radius"], "F(u)=3*u/(2+u^2)")
        self.assertIn(">0", ball["strict_monotonicity"])
        self.assertIn("SO(3) acts transitively", ball["direction_orbits"])
        self.assertIn("closed unit ball", ball["image"])

    def test_sign_compatible_moving_direction_contracts(self) -> None:
        ansatz = self.payload["moving_square_ansatz"]
        self.assertEqual(ansatz["required_moment_scale"], "r(s)=s*alpha/c(s)")
        self.assertEqual(ansatz["moment_scale_derivative"], "dr/ds=alpha*delta/c(s)^2")
        self.assertIn("r(s) lies in [0,1]", ansatz["sign_compatible_case"])
        self.assertTrue(
            self.payload["classification"]["alpha_delta_positive_complete_singular_stratum_contracts_to_hub"]
        )

    def test_opposite_sign_crossing_is_ansatz_obstruction(self) -> None:
        ansatz = self.payload["moving_square_ansatz"]
        self.assertIn("s_0=-delta/(alpha-delta)", ansatz["opposite_sign_zero"])
        self.assertTrue(
            self.payload["classification"]["opposite_sign_interior_zero_obstruction_certified"]
        )

    def test_zero_alpha_boundary_is_not_silently_merged(self) -> None:
        self.assertIn("preventing continuity", self.payload["moving_square_ansatz"]["zero_alpha_boundary"])
        self.assertTrue(
            self.payload["classification"]["zero_alpha_nonphase_real_continuity_obstruction_certified"]
        )
        self.assertTrue(
            self.payload["classification"]["square_factor_vertex_off_balance_contracts_to_hub"]
        )

    def test_candidate_scopes_remain_fail_closed(self) -> None:
        flags = self.payload["classification"]
        self.assertFalse(flags["candidate17_complete_singular_rotation_zero_fibre_connected"])
        self.assertFalse(flags["candidate20_off_balance_complete_singular_rotation_zero_fibre_connected"])
        self.assertFalse(flags["general_nonradial_no_go"])
        self.assertFalse(flags["nonuniform_scaling_classified"])

    def test_schema_rejects_general_nonradial_no_go_promotion(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["general_nonradial_no_go"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)

    def test_schema_rejects_complete_candidate17_promotion(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["candidate17_complete_singular_rotation_zero_fibre_connected"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)


if __name__ == "__main__":
    unittest.main()
