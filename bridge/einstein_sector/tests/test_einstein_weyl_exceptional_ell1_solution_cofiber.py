from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json"


class ExceptionalEll1SolutionCofiberTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text(encoding="utf-8"))

    def test_solution_cofiber_and_pairing_are_certified(self) -> None:
        flags = self.value["classification"]
        self.assertTrue(flags["exceptional_solution_cofiber_certified"])
        self.assertTrue(flags["cofiber_action_pairing_nonradical"])

    def test_offshell_and_nonzero_momentum_remain_open(self) -> None:
        flags = self.value["classification"]
        self.assertFalse(flags["exceptional_offshell_chain_map_certified"])
        self.assertFalse(flags["nonzero_compact_momentum_exceptional_cofiber_certified"])


if __name__ == "__main__":
    unittest.main()
