import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_active_linear_sheet_rotation_links import OUTPUT, build


class SameSignActiveLinearSheetRotationLinkTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_all_six_linear_sheets_are_nondegenerate(self) -> None:
        payload = build()
        components = [component for row in payload["candidate_rows"] for component in row["components"]]
        self.assertEqual(len(components), 6)
        self.assertTrue(payload["classification"]["all_six_restricted_currents_nondegenerate"])
        self.assertTrue(all(component["restricted_Hermitian_current_inertia"] == [5, 5, 0] for component in components))

    def test_connectedness_is_componentwise_and_fail_closed(self) -> None:
        flags = build()["classification"]
        self.assertTrue(flags["all_six_fixed_occupation_rotation_zero_links_connected_componentwise"])
        self.assertFalse(flags["different_active_sheets_identified_by_residual_symmetry"])
        self.assertFalse(flags["candidates17_18_20_active_varieties_classified"])
        self.assertFalse(flags["occupation_strata_glued"])


if __name__ == "__main__":
    unittest.main()
