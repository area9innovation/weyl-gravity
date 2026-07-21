import json
import unittest

from d_quotient_classical.atlas.generate_two_phase_counterflow_unrestricted_all_hodge_health_shortfall_atlas_fragment import OUTPUT, build


class UnrestrictedAllHodgeHealthShortfallAtlasTests(unittest.TestCase):
    def test_generated_fragment_is_current(self):
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_atlas_fails_closed(self):
        row = build()["entries"][0]
        self.assertEqual(row["descriptions"]["causal"], "CERTIFIED")
        self.assertEqual(row["descriptions"]["symplectic"], "NO_CERTIFIED_MAP")
        self.assertEqual(row["scope"]["ell"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
