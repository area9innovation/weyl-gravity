import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_singular_radial_contraction import (
    OUTPUT,
    SCHEMA,
    build,
)


class Candidate1720SingularRadialContractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_transfer_preserves_occupations_and_resonance(self) -> None:
        transfer = self.payload["radial_transfer"]
        self.assertTrue(transfer["occupation_conservation_checked"])
        self.assertIn("vertex", transfer["endpoint"])
        self.assertIn("bilinear", self.payload["resonance_and_group_checks"]["resonance"])

    def test_exact_residual_is_frequency_weighted(self) -> None:
        self.assertEqual(
            self.payload["radial_transfer"]["exact_residual"],
            "mu_rotation(t)=(1-t^2)*delta*mu_square",
        )

    def test_candidate20_balance_union_contracts(self) -> None:
        theorem = self.payload["candidate20_balance_theorem"]
        self.assertTrue(theorem["every_rotation_zero_point_in_each_singular_component_has_radial_path_to_hub"])
        self.assertTrue(theorem["complete_singular_union_rotation_zero_fibre_connected"])

    def test_off_balance_scope_is_fail_closed(self) -> None:
        flags = self.payload["classification"]
        self.assertFalse(flags["candidate17_complete_singular_rotation_zero_fibre_connected"])
        self.assertFalse(flags["candidate20_off_balance_complete_singular_rotation_zero_fibre_connected"])
        self.assertFalse(flags["off_balance_nonradial_contraction_no_go"])

    def test_schema_rejects_off_balance_connectedness_promotion(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["candidate20_off_balance_complete_singular_rotation_zero_fibre_connected"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)


if __name__ == "__main__":
    unittest.main()
