from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_THREE_DESCENT_OBSTRUCTION_V1.json"


class OrderThreeDescentObstructionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text())

    def test_direct_and_indirect_cubic_descent_vanish(self) -> None:
        direct = self.value["direct_descent"]
        self.assertEqual(direct["third_stabilizer_vector_jets_nonzero"], 0)
        self.assertEqual(direct["second_source_action_jets_nonzero"], 0)
        self.assertEqual(
            direct["direct_obstruction_sensitivity_nonzero_entries"], 0
        )
        self.assertEqual(
            self.value["indirect_descent"]["effective_cubic_functional"][
                "nonzero_entries"
            ],
            0,
        )

    def test_order_three_map_is_obstructed(self) -> None:
        self.assertFalse(
            self.value["combined_obstruction"][
                "complete_order_three_chain_map_exists"
            ]
        )
        self.assertTrue(
            self.value["classification"][
                "complete_endpoint_normalized_order_three_chain_map_obstructed"
            ]
        )

    def test_boundary_stays_scoped(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["all_finite_orders_obstructed"])
        self.assertFalse(classification["order_four_chain_map_obstructed"])
        self.assertFalse(classification["current_improvement_obstructed"])
        self.assertFalse(classification["larger_carrier_obstructed"])
        self.assertFalse(classification["f2_incidence_activated"])


if __name__ == "__main__":
    unittest.main()
