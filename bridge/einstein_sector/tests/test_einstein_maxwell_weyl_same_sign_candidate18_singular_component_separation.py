import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate18_singular_component_separation import OUTPUT, SCHEMA, build


class Candidate18SingularComponentSeparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_positive_occupation_removes_intersection(self) -> None:
        theorem = self.payload["separation_theorem"]
        self.assertIn("N_minus=0", theorem["intersection_excluded"])
        self.assertIn("disjoint union", theorem["relative_topology"])

    def test_singular_quotient_has_component_lower_bound(self) -> None:
        descent = self.payload["group_descent"]
        self.assertTrue(descent["rotation_zero_nonempty_in_each_component"])
        self.assertEqual(descent["singular_rotation_zero_quotient_component_lower_bound"], 2)

    def test_full_zero_fibre_remains_open(self) -> None:
        flags = self.payload["classification"]
        self.assertFalse(flags["candidate18_each_component_connected"])
        self.assertFalse(flags["candidate18_full_rotation_zero_fibre_disconnected"])
        self.assertFalse(flags["smooth_strata_connect_components_classified"])

    def test_schema_rejects_full_disconnection_promotion(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["candidate18_full_rotation_zero_fibre_disconnected"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)


if __name__ == "__main__":
    unittest.main()
