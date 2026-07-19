import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_resonance_face_fibres import OUTPUT, build


class SameSignResonanceFaceFibreTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_face_incidence(self) -> None:
        rows = {row["candidate_index"]: row for row in build()["face_rows"]}
        self.assertEqual(rows[16]["automatic_zero_face"]["ray_generators"], [])
        self.assertEqual(rows[17]["automatic_zero_face"]["ray_generators"], ["R1", "R2"])
        self.assertEqual(rows[18]["automatic_zero_face"]["ray_generators"], ["R2", "R4"])
        self.assertEqual(rows[21]["automatic_zero_face"]["ray_generators"], ["R1", "R3"])

    def test_even_L_active_components(self) -> None:
        rows = {row["candidate_index"]: row for row in build()["face_rows"]}
        self.assertEqual(rows[19]["active_stratum"]["active_component_count_over_C"], 4)
        self.assertEqual(rows[21]["active_stratum"]["active_component_count_over_C"], 2)
        self.assertTrue(build()["classification"]["bounded_fibre_product_formula_imported"])
        self.assertFalse(build()["classification"]["rotation_moment_map_reduction_completed"])


if __name__ == "__main__":
    unittest.main()
