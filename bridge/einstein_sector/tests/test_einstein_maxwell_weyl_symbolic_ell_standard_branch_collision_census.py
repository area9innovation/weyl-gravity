"""Tests for the symbolic standard-branch collision census."""

from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_symbolic_ell_standard_branch_collision_census import OUTPUT, build_certificate, symbolic_proof


class SymbolicEllStandardBranchCollisionCensusTests(unittest.TestCase):
    def test_certificate_is_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), build_certificate())

    def test_mixed_difference_interval_has_positive_witnesses(self) -> None:
        proof = symbolic_proof()
        ell = proof["ell"]
        for value in (2, 3, 8, 25):
            self.assertGreater(float(proof["difference_upper_witness"].subs(ell, value)), 0)
            self.assertGreater(float(proof["difference_lower_witness"].subs(ell, value)), 0)

    def test_bounded_join_remains_open(self) -> None:
        payload = build_certificate()
        self.assertTrue(payload["classification"]["qplus_involving_characteristic_collisions_excluded"])
        self.assertFalse(payload["classification"]["complete_bounded_second_order_extension_certified"])
        self.assertEqual(payload["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
