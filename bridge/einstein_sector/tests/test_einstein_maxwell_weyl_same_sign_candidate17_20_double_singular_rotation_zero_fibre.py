import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_double_singular_rotation_zero_fibre import OUTPUT, SCHEMA, build


class Candidate1720DoubleSingularRotationZeroTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_reduced_incidence_resolution_has_expected_dimension(self) -> None:
        resolution = self.payload["incidence_resolution"]
        self.assertEqual(resolution["base_complex_dimension"], 4)
        self.assertEqual(resolution["reduced_complex_dimension"], 6)
        self.assertTrue(resolution["compact"])
        self.assertTrue(resolution["connected"])
        self.assertTrue(resolution["kahler"])

    def test_rotation_zero_hub_is_connected(self) -> None:
        rotation = self.payload["rotation_zero_fibre"]
        self.assertTrue(rotation["resolved_zero_fibre_connected"])
        self.assertTrue(rotation["target_hub_zero_fibre_connected"])

    def test_larger_components_remain_open(self) -> None:
        flags = self.payload["classification"]
        self.assertFalse(flags["complete_singular_components_connected"])
        self.assertFalse(flags["complete_singular_rotation_zero_quotient_connected"])
        self.assertFalse(flags["occupation_strata_glued"])

    def test_schema_rejects_full_union_connectedness_promotion(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["complete_singular_rotation_zero_quotient_connected"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)


if __name__ == "__main__":
    unittest.main()
