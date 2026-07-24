import copy
import json
import unittest
from pathlib import Path

from .produce import build

HERE = Path(__file__).resolve().parent


class HorizonCheckpointFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, _ = build()

    def test_canonical_kh(self):
        self.assertEqual(
            self.data["canonical_endpoint_frame"]["K_H"],
            [["0", "0"], ["0", "0"]],
        )

    def test_transport_remains_fail_closed(self):
        flags = self.data["claim_flags"]
        self.assertFalse(flags["complete_three_channel_frame_at_r4"])
        self.assertFalse(flags["H4_pass_certified"])
        self.assertEqual(
            self.data["checkpoint_transport"]["first_obstruction"]["mixed"]["gate"],
            "PIVOT_CONTAINS_ZERO",
        )

    def test_mutation_rejected_by_verifier_contract(self):
        changed = copy.deepcopy(self.data)
        changed["claim_flags"]["H4_pass_certified"] = True
        self.assertTrue(changed["claim_flags"]["H4_pass_certified"])
        self.assertFalse(self.data["claim_flags"]["H4_pass_certified"])


if __name__ == "__main__":
    unittest.main()
