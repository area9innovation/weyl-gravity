from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
GENERATOR = ROOT / "d_quotient_classical/atlas/generate_two_phase_counterflow_berger_scalar_hodge_block_obstruction_atlas_fragment.py"
SPEC = importlib.util.spec_from_file_location("scalar_hodge_obstruction_atlas", GENERATOR)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ScalarHodgeObstructionAtlasTests(unittest.TestCase):
    def test_fail_closed_atlas_row(self) -> None:
        row = MODULE.build()["entries"][0]
        self.assertEqual(row["descriptions"]["causal"], "OBSTRUCTED")
        self.assertEqual(row["descriptions"]["symplectic"], "NO_CERTIFIED_MAP")
        self.assertEqual(row["descriptions"]["quantum"], "NO_CERTIFIED_MAP")
        self.assertIn("k=0 exceptional/open", row["scope"]["k"])
        self.assertIn("not a defect of q70", row["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
