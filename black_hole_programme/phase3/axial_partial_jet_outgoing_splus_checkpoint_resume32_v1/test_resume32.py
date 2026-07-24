from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify


HERE = Path(__file__).resolve().parent


class SPlusResume32Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads((HERE / "certificate.json").read_text())

    def test_certificate(self) -> None:
        verify(self.data)

    def test_panel_mutation_refused(self) -> None:
        value = copy.deepcopy(self.data)
        value["transport"]["summary"]["panels"] = "31"
        with self.assertRaises(RuntimeError):
            verify(value)

    def test_generator_mutation_refused(self) -> None:
        value = copy.deepcopy(self.data)
        value["transport"]["summary"]["generator"] = "9"
        with self.assertRaises(RuntimeError):
            verify(value)

    def test_tplus_promotion_refused(self) -> None:
        value = copy.deepcopy(self.data)
        value["claim_flags"]["T_plus_certified"] = True
        with self.assertRaises(RuntimeError):
            verify(value)


if __name__ == "__main__":
    unittest.main()
