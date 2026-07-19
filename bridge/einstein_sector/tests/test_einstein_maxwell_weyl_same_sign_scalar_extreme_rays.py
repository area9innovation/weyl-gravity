import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_scalar_extreme_rays import OUTPUT, build


class SameSignScalarExtremeRayTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_four_universal_rays(self) -> None:
        payload = build()
        self.assertEqual(len(payload["extreme_rays"]), 4)
        self.assertTrue(payload["classification"]["every_extreme_ray_contains_both_q_minus_nodes"])
        self.assertFalse(payload["classification"]["full_bounded_cones_classified"])


if __name__ == "__main__":
    unittest.main()
