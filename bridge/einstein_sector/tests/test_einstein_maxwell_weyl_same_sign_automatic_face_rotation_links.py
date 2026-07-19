import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_automatic_face_rotation_links import OUTPUT, build


class SameSignAutomaticFaceRotationLinkTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_only_automatic_faces_are_promoted(self) -> None:
        flags = build()["classification"]
        self.assertTrue(flags["all_nonzero_fixed_occupation_rotation_zero_links_connected"])
        self.assertFalse(flags["active_resonance_strata_classified"])
        self.assertFalse(flags["singular_strata_classified"])

    def test_candidate_16_has_no_nonzero_automatic_face(self) -> None:
        row = build()["candidate_rows"][0]
        self.assertEqual(row["candidate_index"], 16)
        self.assertEqual(row["verdict"], "NOT_APPLICABLE")


if __name__ == "__main__":
    unittest.main()
