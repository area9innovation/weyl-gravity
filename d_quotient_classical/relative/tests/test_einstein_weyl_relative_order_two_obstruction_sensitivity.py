from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_TWO_OBSTRUCTION_SENSITIVITY_V1.json"


class OrderTwoObstructionSensitivityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text())

    def test_order_two_hits_the_obstruction(self) -> None:
        sensitivity = self.value["induced_sensitivity"]
        self.assertEqual(sensitivity["rank_to_obstruction_quotient"], 1)
        self.assertTrue(sensitivity["surjective"])
        self.assertEqual(
            {
                item["normalized_obstruction_sensitivity"]
                for item in sensitivity["explicit_invariant_candidates"]
            },
            {"-1", "1"},
        )

    def test_candidates_are_isotropy_invariant(self) -> None:
        self.assertTrue(
            all(
                item["isotropy_residual_nonzero_entries"] == 0
                for item in self.value["induced_sensitivity"][
                    "explicit_invariant_candidates"
                ]
            )
        )

    def test_boundary_stays_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["full_order_two_solve_authorized"])
        self.assertFalse(classification["order_two_chain_map_exists"])
        self.assertFalse(classification["order_two_chain_map_obstructed"])
        self.assertFalse(classification["f2_incidence_activated"])
        self.assertFalse(classification["carrier_enlargement_required"])


if __name__ == "__main__":
    unittest.main()
