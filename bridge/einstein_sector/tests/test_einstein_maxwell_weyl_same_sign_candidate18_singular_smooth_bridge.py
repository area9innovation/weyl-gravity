import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate18_singular_smooth_bridge import OUTPUT, SCHEMA, build


class Candidate18SingularSmoothBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_path_preserves_occupations_and_rotations(self) -> None:
        path = self.payload["path"]
        self.assertIn("N_plus", path["fixed_occupations"])
        self.assertIn("all three vanish", path["rotation_moment_maps"])

    def test_path_connects_singular_pieces_through_smooth_locus(self) -> None:
        flags = self.payload["classification"]
        self.assertTrue(flags["candidate18_singular_components_joined_in_full_rotation_zero_fibre"])
        self.assertTrue(flags["bridge_interior_complex_smooth"])

    def test_global_connectedness_remains_open(self) -> None:
        flags = self.payload["classification"]
        self.assertFalse(flags["full_rotation_zero_fibre_connected"])
        self.assertFalse(flags["all_singular_points_connected_to_bridge"])
        self.assertFalse(flags["global_leaf_space_classified"])

    def test_schema_rejects_global_connectedness_promotion(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["full_rotation_zero_fibre_connected"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)


if __name__ == "__main__":
    unittest.main()
