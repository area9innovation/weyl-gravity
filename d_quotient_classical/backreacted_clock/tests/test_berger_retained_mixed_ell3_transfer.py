from __future__ import annotations

import json
import unittest

from d_quotient_classical.backreacted_clock.verify_berger_retained_mixed_ell3_transfer import (
    CERTIFICATE,
    ELL2_PAYLOAD,
    ELL3_PAYLOAD,
    verify,
)


class RetainedMixedEll3TransferTest(unittest.TestCase):
    def test_independent_exact_replay(self) -> None:
        verify()

    def test_scope_is_fail_closed(self) -> None:
        certificate = json.loads(CERTIFICATE.read_text())
        self.assertEqual(certificate["retained_ell2"]["term_count"], 1474)
        self.assertEqual(certificate["retained_ell3"]["contact_term_count"], 25950)
        self.assertEqual(certificate["retained_ell3"]["exchange_term_count"], 0)
        self.assertTrue(certificate["flags"]["BERGER_RETAINED_MIXED_ELL3_TRANSFER"])
        self.assertFalse(
            certificate["flags"]["BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_QUANTUM_ACCEPTANCE"]
        )
        self.assertFalse(certificate["flags"]["QME_RESTORED"])
        self.assertFalse(certificate["flags"]["QUANTUM_CLAIM"])
        self.assertTrue(ELL2_PAYLOAD.is_file())
        self.assertTrue(ELL3_PAYLOAD.is_file())


if __name__ == "__main__":
    unittest.main()
