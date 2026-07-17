from __future__ import annotations

import json
import unittest

from d_quotient_classical.backreacted_clock.verify_berger_coupled_k_cartan_through_arity_three import (
    CERTIFICATE,
    verify,
)


class CoupledKCartanTest(unittest.TestCase):
    def test_independent_replay(self) -> None:
        verify()

    def test_scope(self) -> None:
        value = json.loads(CERTIFICATE.read_text())
        self.assertEqual(value["generator"]["symbol"], "K_Berger=D-omega R")
        self.assertEqual(value["complexes"]["full_rows"], 64)
        self.assertEqual(value["complexes"]["retained_rows"], 36)
        self.assertEqual(value["retained_transfer"]["mixed_exchange"], "ZERO")
        self.assertEqual(value["retained_transfer"]["mixed_contact_term_count"], 25950)
        self.assertTrue(value["flags"]["BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE"])
        self.assertFalse(value["flags"]["BERGER_RAW_D_AFFINE_CARTAN"])
        self.assertFalse(value["flags"]["BERGER_ARITY_FOUR_K_CARTAN"])
        self.assertFalse(value["flags"]["QME_RESTORED"])
        self.assertFalse(value["flags"]["QUANTUM_CLAIM"])


if __name__ == "__main__":
    unittest.main()
