from __future__ import annotations

import copy
import json
import unittest

from spectral.euclidean.product_s2_s2_full_bv_join_boundary import OUTPUT, build, verify
from spectral.euclidean.verify_product_s2_s2_full_bv_join_boundary import verify as independent_verify


class ProductS2S2FullBVJoinBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.expected = json.loads(OUTPUT.read_text())

    def test_checked_in_certificate_reproduces(self) -> None:
        self.assertEqual(build(), self.expected)

    def test_independent_verifier(self) -> None:
        independent_verify()

    def test_background_mismatch_is_fail_closed(self) -> None:
        mutant = copy.deepcopy(self.expected)
        mutant["scope_comparison"]["same_background"] = True
        with self.assertRaises(ValueError):
            verify(mutant)

    def test_missing_physical_carrier_cannot_be_promoted(self) -> None:
        mutant = copy.deepcopy(self.expected)
        mutant["claim_flags"]["SAME_BACKGROUND_PHYSICAL_HESSIAN_AVAILABLE"] = True
        with self.assertRaises(ValueError):
            verify(mutant)

    def test_product_ghost_coefficient_is_preserved(self) -> None:
        coverage = {row["sector"]: row["status"] for row in self.expected["same_background_coverage"]}
        self.assertEqual(coverage["coupled_Diff_Weyl_ghost"], "COEFFICIENT_COMPUTED")
        self.assertEqual(coverage["gauge_fixed_metric_Hessian"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
