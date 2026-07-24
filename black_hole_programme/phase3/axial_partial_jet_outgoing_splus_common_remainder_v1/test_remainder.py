from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify


HERE = Path(__file__).resolve().parent


class SPlusCommonRemainderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads((HERE / "certificate.json").read_text())

    def test_certificate(self) -> None:
        verify(self.data)

    def test_generator_mutation_refused(self) -> None:
        mutated = copy.deepcopy(self.data)
        mutated["common_remainder"]["runtime"]["generator"] = "17"
        with self.assertRaises(RuntimeError):
            verify(mutated)

    def test_containment_mutation_refused(self) -> None:
        mutated = copy.deepcopy(self.data)
        mutated["common_remainder"]["runtime"]["contained"] = "false"
        with self.assertRaises(RuntimeError):
            verify(mutated)

    def test_tplus_promotion_refused(self) -> None:
        mutated = copy.deepcopy(self.data)
        mutated["claim_flags"]["T_plus_certified"] = True
        with self.assertRaises(RuntimeError):
            verify(mutated)


if __name__ == "__main__":
    unittest.main()
