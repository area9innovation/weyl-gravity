from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from spectral.euclidean.verify_generic_background_physical_hessian_triangle_renormalized_master_values import (
    CERTIFICATE,
    verify,
)


class RenormalizedPhysicalTriangleMasterValuesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(Path(CERTIFICATE).read_text())

    def test_certificate(self) -> None:
        verify(self.value)

    def test_three_master_rows(self) -> None:
        self.assertEqual(len(self.value["master_rows"]), 3)
        self.assertEqual(self.value["identity_ledger"]["template_count"], 6)

    def test_digest_tamper_fails(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["master_rows"][0]["scale_derivative"] += "+1"
        with self.assertRaises(ValueError):
            verify(mutant)

    def test_lifecycle_tamper_fails(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["claim_flags"]["PHYSICAL_N3_TRIANGLE_INTEGRATED"] = True
        mutant["formula_digest"] = self.value["formula_digest"]
        with self.assertRaises(ValueError):
            verify(mutant)


if __name__ == "__main__":
    unittest.main()
