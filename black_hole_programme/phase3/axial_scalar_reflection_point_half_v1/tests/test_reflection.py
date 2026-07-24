from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ..verify import verify


CERTIFICATE = Path(__file__).resolve().parents[1] / "certificate.json"


class ReflectionCertificateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads(CERTIFICATE.read_text())

    def test_committed_certificate(self) -> None:
        verify(self.data)

    def test_zero_bound_mutation(self) -> None:
        bad = copy.deepcopy(self.data)
        bad["certified_lower_bounds"]["spin_2"]["abs_A_out_lower"] = "0"
        with self.assertRaises(RuntimeError):
            verify(bad)

    def test_tplus_overclaim_mutation(self) -> None:
        bad = copy.deepcopy(self.data)
        bad["claim_flags"]["explicit_full_Tplus_matrix_certified"] = True
        with self.assertRaises(RuntimeError):
            verify(bad)

    def test_frequency_mutation(self) -> None:
        bad = copy.deepcopy(self.data)
        bad["scope"]["frequency"] = "3/4"
        with self.assertRaises(RuntimeError):
            verify(bad)


if __name__ == "__main__":
    unittest.main()
