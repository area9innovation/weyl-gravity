from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ONE_CHAIN_OBSTRUCTION_V1.json"


class OrderOneChainObstructionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text())

    def test_complete_system_is_inconsistent(self) -> None:
        system = self.value["exact_linear_system"]
        self.assertEqual((system["equations"], system["unknowns"]), (822, 406))
        self.assertEqual((system["rank_over_Q"], system["augmented_rank_over_Q"]), (398, 399))
        self.assertFalse(system["consistent"])

    def test_short_witness_is_nonzero(self) -> None:
        witness = self.value["exact_linear_system"]["left_null_witness"]
        self.assertEqual(len(witness["terms"]), 2)
        self.assertNotEqual(witness["evaluation"], "0")

    def test_boundary_stays_scoped(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["order_one_chain_map_obstructed"])
        self.assertFalse(classification["higher_order_chain_map_obstructed"])
        self.assertFalse(classification["nonzero_f2_obstructed"])
        self.assertFalse(classification["relative_q2_repaired"])


if __name__ == "__main__":
    unittest.main()
