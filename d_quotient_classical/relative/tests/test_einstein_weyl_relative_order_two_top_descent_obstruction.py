from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_TWO_TOP_DESCENT_OBSTRUCTION_V1.json"


class OrderTwoTopDescentObstructionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text())

    def test_legal_kernel_has_zero_sensitivity(self) -> None:
        system = self.value["top_descent_system"]
        self.assertEqual(
            (system["rank_over_Q"], system["rank_with_sensitivity_row"]),
            (516, 516),
        )
        self.assertEqual(system["kernel_dimension"], 196)
        self.assertTrue(system["sensitivity_vanishes_on_kernel"])
        self.assertEqual(system["rowspace_witness_nonzero_entries"], 4)

    def test_complete_order_two_map_is_obstructed(self) -> None:
        self.assertFalse(
            self.value["combined_obstruction"][
                "complete_order_two_chain_map_exists"
            ]
        )
        self.assertTrue(
            self.value["classification"][
                "complete_endpoint_normalized_order_two_chain_map_obstructed"
            ]
        )

    def test_boundary_stays_scoped(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["all_finite_orders_obstructed"])
        self.assertFalse(classification["order_three_chain_map_obstructed"])
        self.assertFalse(classification["current_improvement_obstructed"])
        self.assertFalse(classification["larger_carrier_obstructed"])
        self.assertFalse(classification["f2_incidence_activated"])


if __name__ == "__main__":
    unittest.main()
