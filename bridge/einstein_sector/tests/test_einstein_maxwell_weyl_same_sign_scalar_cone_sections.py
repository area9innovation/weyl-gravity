import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_scalar_cone_sections import OUTPUT, build


class SameSignScalarConeSectionTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_surjective_but_not_fibrewise_complete(self) -> None:
        payload = build()
        self.assertTrue(payload["classification"]["bounded_to_scalar_occupation_projection_surjective"])
        self.assertTrue(payload["classification"]["all_scalar_cone_faces_and_pairwise_ray_sums_covered"])
        self.assertFalse(payload["classification"]["every_amplitude_over_each_scalar_occupation_bounded"])


if __name__ == "__main__":
    unittest.main()
