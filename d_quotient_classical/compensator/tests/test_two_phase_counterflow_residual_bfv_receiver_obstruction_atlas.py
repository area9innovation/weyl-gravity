import json
import unittest
from d_quotient_classical.atlas.generate_two_phase_counterflow_residual_bfv_receiver_obstruction_atlas_fragment import OUTPUT, build


class ResidualBFVAtlasTests(unittest.TestCase):
    def test_current(self): self.assertEqual(json.loads(OUTPUT.read_text()), build())
    def test_fail_closed(self):
        entry = build()["entries"][0]
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "NO_CERTIFIED_MAP")
        self.assertEqual(entry["descriptions"]["quantum"], "NO_CERTIFIED_MAP")


if __name__ == "__main__": unittest.main()
