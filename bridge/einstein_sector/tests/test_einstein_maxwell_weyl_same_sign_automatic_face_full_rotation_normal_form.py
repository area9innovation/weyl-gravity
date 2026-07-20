import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_automatic_face_full_rotation_normal_form import build


class AutomaticFaceFullRotationNormalFormTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build()

    def test_internal_multiplicities_are_complete(self) -> None:
        dimensions = self.payload["primary_multiplicity_dictionary"]["node_dimensions"]
        self.assertEqual(dimensions["q_minus_n1"], 2)
        self.assertEqual(dimensions["q_plus_n2"], 2)
        self.assertEqual(dimensions["p_extra_n1"], 4)

    def test_every_nonzero_automatic_support_stratum_has_full_inertia(self) -> None:
        for row in self.payload["candidate_rows"][1:]:
            self.assertEqual(len(row["support_strata"]), 3)
            for stratum in row["support_strata"]:
                positive, negative, null = stratum["unquotiented_real_inertia"]
                self.assertEqual(positive, negative)
                self.assertGreater(positive, 0)
                self.assertGreater(null, 0)

    def test_scope_remains_fail_closed(self) -> None:
        flags = self.payload["classification"]
        self.assertEqual(flags["candidate_16_nonzero_automatic_face"], "NOT_APPLICABLE")
        self.assertFalse(flags["rotation_zero_local_semialgebraic_components_classified"])
        self.assertFalse(flags["active_resonance_components_classified"])
        self.assertFalse(flags["all_orders_integrability"])


if __name__ == "__main__":
    unittest.main()
