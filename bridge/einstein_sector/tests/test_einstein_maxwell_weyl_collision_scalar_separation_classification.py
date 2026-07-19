"""Tests for the all-collision scalar-separation classification."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_collision_scalar_separation_classification import OUTPUT, build


class CollisionScalarSeparationTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), build())

    def test_exact_fifteen_six_split(self) -> None:
        payload = build()
        self.assertEqual(payload["summary"]["strictly_separated_candidate_indices"], list(range(1, 16)))
        self.assertEqual(payload["summary"]["positive_farkas_candidate_indices"], list(range(16, 22)))
        self.assertTrue(payload["classification"]["fifteen_complete_bounded_generic_cones_are_origin"])
        self.assertTrue(payload["classification"]["universal_positive_rho_opposite_sign_separator_certified"])
        self.assertFalse(payload["classification"]["six_full_resonance_joined_bounded_cones_classified"])

    def test_rows_retain_distinct_backgrounds(self) -> None:
        rows = build()["candidate_rows"]
        self.assertEqual(len({row["rho"] for row in rows}), 21)
        self.assertTrue(all(row["classification"] == "STRICT_SCALAR_SEPARATOR" for row in rows[:15]))
        self.assertTrue(all("FARKAS" in row["classification"] for row in rows[15:]))


if __name__ == "__main__":
    unittest.main()
