import json
import unittest

from d_quotient_classical.atlas.generate_two_phase_counterflow_secular_clock_orbital_stability_atlas_fragment import OUTPUT, build


class SecularClockOrbitalStabilityAtlasTests(unittest.TestCase):
    def test_generated_fragment_is_current(self):
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_reduced_and_coupled_carriers_are_separate(self):
        rows = build()["entries"]
        self.assertNotEqual(rows[0]["scope"]["carrier"], rows[1]["scope"]["carrier"])
        self.assertEqual(rows[0]["mode_data"]["second_order"]["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(rows[1]["mode_data"]["second_order"]["smooth_secular"]["status"], "OBSTRUCTED")


if __name__ == "__main__":
    unittest.main()
