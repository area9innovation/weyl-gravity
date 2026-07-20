import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_active_singular_rotation_zero_sections import OUTPUT, SCHEMA, build


class ActiveSingularRotationZeroSectionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_all_three_candidates_have_sections(self) -> None:
        flags = self.payload["classification"]
        for candidate in (17, 18, 20):
            self.assertTrue(flags[f"candidate{candidate}_every_positive_occupation_has_singular_rotation_zero_point"])

    def test_sections_are_rotation_zero_with_free_node_phases(self) -> None:
        universal = self.payload["universal_section"]
        self.assertEqual(universal["rotation_moment_maps"], "mu_J1=mu_J2=mu_J3=0 because the real completed section is axisymmetric")
        self.assertTrue(universal["node_phase_actions_free"])

    def test_singular_quotient_remains_open(self) -> None:
        flags = self.payload["classification"]
        self.assertFalse(flags["real_singular_component_decomposition_complete"])
        self.assertFalse(flags["node_phase_singular_quotient_classified"])
        self.assertFalse(flags["lifted_rotation_singular_quotient_classified"])
        self.assertFalse(flags["global_zero_fibre_connected"])

    def test_schema_rejects_global_promotion(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["global_zero_fibre_connected"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)


if __name__ == "__main__":
    unittest.main()
