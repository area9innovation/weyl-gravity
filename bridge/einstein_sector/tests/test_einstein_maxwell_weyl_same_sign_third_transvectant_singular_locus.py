import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_third_transvectant_singular_locus import OUTPUT, SCHEMA, build


class ThirdTransvectantSingularLocusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_one_factor_geometry(self) -> None:
        one = self.payload["one_factor_singular_locus"]
        self.assertEqual(one["complex_dimension"], 4)
        self.assertEqual(one["projectivization"], "P^2 x P^1 embedded by O(2,1)")
        self.assertTrue(one["projectivization_smooth_connected"])

    def test_two_parity_singular_components(self) -> None:
        product = self.payload["two_parity_product"]
        self.assertEqual(product["irreducible_components"], 2)
        self.assertEqual(product["component_complex_dimension"], 11)
        self.assertEqual(product["intersection_complex_dimension"], 8)

    def test_real_and_rotation_reductions_remain_open(self) -> None:
        flags = self.payload["classification"]
        self.assertFalse(flags["fixed_occupation_real_singular_strata_classified"])
        self.assertFalse(flags["node_phase_singular_reduction_classified"])
        self.assertFalse(flags["lifted_rotation_singular_reduction_classified"])
        self.assertFalse(flags["global_zero_fibre_connected"])

    def test_schema_rejects_rotation_promotion(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["lifted_rotation_singular_reduction_classified"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)


if __name__ == "__main__":
    unittest.main()
