import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_extreme_ray_lifts import OUTPUT, build


class SameSignExtremeRayLiftTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_all_24_rays_but_not_sums(self) -> None:
        payload = build()
        self.assertEqual(payload["summary"]["total_lifts"], 24)
        self.assertTrue(payload["classification"]["all_24_scalar_extreme_rays_have_nonzero_bounded_lifts"])
        self.assertFalse(payload["classification"]["arbitrary_nonnegative_sums_of_lifts_classified"])


if __name__ == "__main__":
    unittest.main()
