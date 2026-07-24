from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify


HERE = Path(__file__).resolve().parent


class StepLadderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads((HERE / "certificate.json").read_text())

    def test_certificate(self) -> None:
        verify(self.data)

    def test_missing_step_is_refused(self) -> None:
        value = copy.deepcopy(self.data)
        del value["transport"]["cases"]["32"]
        with self.assertRaises(RuntimeError):
            verify(value)

    def test_failed_step_is_refused(self) -> None:
        value = copy.deepcopy(self.data)
        value["transport"]["cases"]["64"]["status"] = "REFUSED"
        with self.assertRaises(RuntimeError):
            verify(value)

    def test_wide_finite_step_is_not_promoted(self) -> None:
        value = copy.deepcopy(self.data)
        value["transport"]["cases"]["32"]["operationally_admissible"] = True
        with self.assertRaises(RuntimeError):
            verify(value)

    def test_tplus_promotion_is_refused(self) -> None:
        value = copy.deepcopy(self.data)
        value["claim_flags"]["T_plus_certified"] = True
        with self.assertRaises(RuntimeError):
            verify(value)


if __name__ == "__main__":
    unittest.main()
