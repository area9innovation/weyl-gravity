from __future__ import annotations

import json
import unittest

from d_quotient_classical.backreacted_clock.verify_berger_support_local_coupled_maxwell_q3 import (
    CERTIFICATE,
    Q2_TYPED,
    Q3_PAYLOAD,
    verify,
)


class CoupledMaxwellQ3Test(unittest.TestCase):
    def test_portable_replay(self) -> None:
        verify()

    def test_exact_scope(self) -> None:
        certificate = json.loads(CERTIFICATE.read_text())
        self.assertEqual(
            certificate["classical_binary_q2_typed"]["term_count"], 1890
        )
        self.assertEqual(
            certificate["classical_ternary_q3_mixed"]["term_count"], 59598
        )
        self.assertFalse(certificate["flags"]["BERGER_RETAINED_MIXED_ELL3_TRANSFER"])
        self.assertFalse(certificate["flags"]["QUANTUM_CLAIM"])
        self.assertTrue(Q2_TYPED.is_file())
        self.assertTrue(Q3_PAYLOAD.is_file())


if __name__ == "__main__":
    unittest.main()
