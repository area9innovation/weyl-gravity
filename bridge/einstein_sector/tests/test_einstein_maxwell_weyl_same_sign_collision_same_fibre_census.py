import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_collision_same_fibre_census import OUTPUT, build


class SameSignSameFibreCensusTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_complete_six_by_144_census(self) -> None:
        payload = build()
        self.assertEqual(payload["summary"]["total_exact_nonzero_defects"], 864)
        self.assertEqual([row["candidate_index"] for row in payload["candidate_rows"]], list(range(16, 22)))
        self.assertTrue(all(len(row["channels"]) == 18 for row in payload["candidate_rows"]))
        self.assertTrue(payload["classification"]["all_864_target_shell_defects_nonzero"])
        self.assertFalse(payload["classification"]["cross_fibre_resonance_join_classified"])


if __name__ == "__main__":
    unittest.main()
