"""Tests for the full internal automatic-face rotation normal form."""

from __future__ import annotations

import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_automatic_face_full_internal_rotation_normal_form import build
from bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_automatic_face_full_internal_rotation_normal_form import verify


class FullInternalAutomaticFaceNormalFormTests(unittest.TestCase):
    def test_universal_internal_formula(self) -> None:
        payload = build()
        self.assertEqual(payload["orthogonal_block_theorem"]["one_current_orthogonal_eigenline_real_inertia"], [4, 4, 2])
        self.assertEqual(payload["full_internal_formula"]["inertia_positive_negative_null"], ["4*M-2", "4*M-2", "2*M-2*N+2"])

    def test_all_realized_support_strata(self) -> None:
        rows = build()["candidate_rows"]
        self.assertEqual(rows[0]["verdict"], "NOT_APPLICABLE")
        self.assertTrue(all(len(row["support_strata"]) == 3 for row in rows[1:]))
        self.assertTrue(all(all(min(stratum["full_internal_mu_J3_real_inertia"][:2]) > 0 for stratum in row["support_strata"]) for row in rows[1:]))

    def test_independent_verifier(self) -> None:
        verify()


if __name__ == "__main__":
    unittest.main()
