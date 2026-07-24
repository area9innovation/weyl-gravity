from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify

HERE = Path(__file__).resolve().parent


class ProjectiveSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((HERE / "certificate.json").read_text())

    def test_certificate(self) -> None:
        self.assertEqual(verify(self.document), [])

    def test_false_root_promotion(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["claim_flags"]["QNM_root_count_certified"] = True
        self.assertTrue(verify(mutant))


if __name__ == "__main__":
    unittest.main()
