from copy import deepcopy
import unittest

from d_quotient_classical.backreacted_clock.berger_causal_d_cartan_transfer import (
    BergerCausalDCartanTransfer,
)


class BergerCausalDCartanTransferTests(unittest.TestCase):
    def test_conditional_transfer_is_fail_closed(self) -> None:
        payload = BergerCausalDCartanTransfer.build().payload
        self.assertTrue(payload["flags"]["BERGER_CAUSAL_D_CARTAN_TRANSFER_THEOREM"])
        self.assertTrue(payload["flags"]["BERGER_CAUSAL_UNARY_D_CARTAN_CONDITIONAL"])
        self.assertFalse(payload["flags"]["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"])
        self.assertFalse(payload["flags"]["BERGER_CAUSAL_ARITY_TWO_CYCLIC_COMPLETION"])
        self.assertEqual(payload["next_gate"], "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY")

    def test_endpoint_cannot_be_promoted_by_transfer(self) -> None:
        payload = deepcopy(BergerCausalDCartanTransfer.build().payload)
        payload["flags"]["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"] = True
        with self.assertRaises(AssertionError):
            BergerCausalDCartanTransfer(payload).verify()

    def test_cyclic_binary_completion_remains_open(self) -> None:
        payload = deepcopy(BergerCausalDCartanTransfer.build().payload)
        payload["flags"]["BERGER_CAUSAL_ARITY_TWO_CYCLIC_COMPLETION"] = True
        with self.assertRaises(AssertionError):
            BergerCausalDCartanTransfer(payload).verify()


if __name__ == "__main__":
    unittest.main()
