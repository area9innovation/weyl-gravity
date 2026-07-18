import json
import unittest

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_zero_jet_ghost_shear_completion as result,
)


class ZeroJetGhostShearCompletionTests(unittest.TestCase):
    def test_primitive_reconstructs_target(self) -> None:
        value = json.loads(result.OUTPUT.read_text())
        replay = result.primitive_replay(value["primitive"])
        self.assertEqual(replay["primitive_nonzero_coefficients"], 67)
        self.assertEqual(replay["changed_coefficients"], 0)

    def test_smallest_missing_carrier_is_present(self) -> None:
        value = json.loads(result.OUTPUT.read_text())
        records = value["primitive_replay"]["certified_ghost_shear_coefficients"]
        self.assertEqual(len(records), 3)
        self.assertTrue(all(record["coefficient"] == "-1" for record in records))

    def test_claim_remains_fail_closed(self) -> None:
        value = json.loads(result.OUTPUT.read_text())
        self.assertFalse(value["claim_flags"]["TOTAL_PBW_ORDER_TWO_CLOSED"])
        self.assertFalse(value["claim_flags"]["QUANTUM_CLAIM"])


if __name__ == "__main__":
    unittest.main()
