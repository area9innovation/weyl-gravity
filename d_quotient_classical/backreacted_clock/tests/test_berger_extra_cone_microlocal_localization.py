import unittest

from d_quotient_classical.backreacted_clock.berger_extra_cone_microlocal_localization import build, verify


class BergerExtraConeMicrolocalLocalizationTest(unittest.TestCase):
    def test_mixed_polarization_and_retained_route(self):
        payload = build()
        verify(payload)
        polarization = payload["characteristic_polarization"]
        self.assertTrue(polarization["retained_metric_projection_nonzero"])
        self.assertTrue(polarization["clock_projection_nonzero"])
        self.assertFalse(payload["flags"]["BERGER_RAW_EXTRA_MODE_PURE_CLOCK"])
        self.assertEqual(payload["homological_interpretation"]["retained_companion_rank_on_raw_extra_cone"], 20)


if __name__ == "__main__":
    unittest.main()
