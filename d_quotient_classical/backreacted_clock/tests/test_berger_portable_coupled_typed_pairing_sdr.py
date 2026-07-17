from __future__ import annotations

import json
import unittest

from d_quotient_classical.backreacted_clock.verify_berger_portable_coupled_typed_pairing_sdr import CERTIFICATE, verify


class TypedCarrierTest(unittest.TestCase):
    def test_exact_replay(self) -> None:
        verify()

    def test_scope(self) -> None:
        value = json.loads(CERTIFICATE.read_text())
        self.assertEqual(value["normalization"]["Maxwell_pairing_weight"], 2)
        self.assertFalse(value["flags"]["BERGER_RETAINED_MIXED_ELL3_TRANSFER"])
        self.assertFalse(value["flags"]["QUANTUM_CLAIM"])


if __name__ == "__main__":
    unittest.main()
