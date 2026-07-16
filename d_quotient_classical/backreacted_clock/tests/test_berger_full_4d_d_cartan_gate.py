from copy import deepcopy
import unittest

from d_quotient_classical.backreacted_clock.berger_full_4d_d_cartan_gate import (
    BergerFull4DDCartanGate,
)


class BergerFull4DDCartanGateTests(unittest.TestCase):
    def test_gate_is_fail_closed(self) -> None:
        payload = BergerFull4DDCartanGate.build().payload
        self.assertTrue(payload["flags"]["BERGER_FULL_4D_D_CARTAN_INPUTS_COMPLETE"])
        self.assertTrue(payload["flags"]["BERGER_UNARY_D_CARTAN_LOCAL_BARE_COMPLEX_NO_GO"])
        self.assertFalse(payload["flags"]["BERGER_UNARY_D_CARTAN_EXISTENCE_FULL_4D"])
        self.assertEqual(payload["next_gate"], "BERGER_RESIDUAL_OR_CAUSAL_CARTAN_EXTENSION")

    def test_arity_two_cannot_bypass_unary(self) -> None:
        payload = deepcopy(BergerFull4DDCartanGate.build().payload)
        payload["flags"]["BERGER_ARITY_TWO_D_CARTAN_FULL_4D"] = True
        with self.assertRaises(AssertionError):
            BergerFull4DDCartanGate(payload).verify()


if __name__ == "__main__":
    unittest.main()
