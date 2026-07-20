import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_singular_component_incidence import OUTPUT, SCHEMA, build


class Candidate1720SingularComponentIncidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_positive_occupation_witness_lies_in_intersection(self) -> None:
        theorem = self.payload["incidence_theorem"]
        self.assertIn("S_plus x S_minus", theorem["witness_membership"])
        self.assertEqual(theorem["intersection_complex_dimension"], 8)
        self.assertTrue(theorem["node_phase_actions_free"])

    def test_quotient_component_images_intersect(self) -> None:
        descent = self.payload["group_descent"]
        self.assertIn("images", descent["quotient_images_intersect"])
        self.assertEqual(descent["component_label_separation_lower_bound"], 1)

    def test_connectedness_remains_open(self) -> None:
        flags = self.payload["classification"]
        self.assertFalse(flags["candidate17_20_component_labels_prove_quotient_separation"])
        self.assertFalse(flags["candidate17_20_each_singular_component_connected"])
        self.assertFalse(flags["candidate17_20_complete_singular_rotation_zero_quotient_connected"])

    def test_schema_rejects_false_separation_promotion(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["candidate17_20_component_labels_prove_quotient_separation"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)


if __name__ == "__main__":
    unittest.main()
