import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-berger-vector-hodge-split-obstruction-fragment-v1.json"


class VectorHodgeObstructionAtlasTests(unittest.TestCase):
    def test_fail_closed_row(self):
        entry = json.loads(ATLAS.read_text())["entries"][0]
        self.assertEqual(entry["descriptions"]["causal"], "OBSTRUCTED")
        self.assertEqual(entry["descriptions"]["symplectic"], "NO_CERTIFIED_MAP")
        self.assertEqual(entry["descriptions"]["quantum"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
