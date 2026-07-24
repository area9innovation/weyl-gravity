from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify

HERE = Path(__file__).resolve().parent


class TangentInitializerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((HERE / "certificate.json").read_text())

    def test_certificate(self) -> None:
        self.assertEqual(verify(self.document), [])

    def test_source_mutation(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["source_bounds"]["source_integral_upper"] = "0"
        self.assertTrue(verify(mutant))

    def test_tangent_mutation(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["tangent_initializer"]["value_ball"]["radius"] = "0"
        self.assertTrue(verify(mutant))

    def test_false_b_promotion(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["claim_flags"]["b_over_a_on_contour_constructed"] = True
        self.assertTrue(verify(mutant))


if __name__ == "__main__":
    unittest.main()
