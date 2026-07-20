import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate18_complex_singular_resolution import OUTPUT, SCHEMA, build


class Candidate18ComplexSingularResolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_factor_and_product_dimensions(self) -> None:
        self.assertEqual(self.payload["one_factor"]["complex_dimension"], 6)
        complete = self.payload["complete_carrier"]
        self.assertEqual(complete["complex_dimension"], 22)
        self.assertEqual(complete["component_complex_dimension"], 16)
        self.assertEqual(complete["intersection_complex_dimension"], 10)

    def test_spectators_and_resolution_are_retained(self) -> None:
        complete = self.payload["complete_carrier"]
        self.assertTrue(complete["resolution_smooth_connected"])
        self.assertTrue(complete["resolution_fibres_connected"])
        self.assertTrue(self.payload["classification"]["ten_positive_spectators_retained"])

    def test_physical_reductions_remain_open(self) -> None:
        flags = self.payload["classification"]
        self.assertFalse(flags["fixed_occupation_real_singular_strata_classified"])
        self.assertFalse(flags["node_phase_singular_reduction_classified"])
        self.assertFalse(flags["lifted_rotation_singular_reduction_classified"])
        self.assertFalse(flags["global_zero_fibre_connected"])

    def test_schema_rejects_rotation_promotion(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["global_zero_fibre_connected"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)


if __name__ == "__main__":
    unittest.main()
