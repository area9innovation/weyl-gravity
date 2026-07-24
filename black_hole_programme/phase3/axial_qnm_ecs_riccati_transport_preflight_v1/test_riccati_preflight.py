from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify

HERE = Path(__file__).resolve().parent


class RiccatiPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((HERE / "certificate.json").read_text())

    def test_certificate(self) -> None:
        self.assertEqual(verify(self.document), [])

    def test_false_pole_promotion(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["claim_flags"]["physical_projective_pole_established"] = True
        self.assertTrue(verify(mutant))


if __name__ == "__main__":
    unittest.main()
