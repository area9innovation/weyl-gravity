import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_automatic_face_rotation_normal_form import build


class AutomaticFaceRotationNormalFormTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build()

    def test_support_inertia_is_exact(self) -> None:
        for row in self.payload["normal_form_theorem"]["support_strata"]:
            nodes = row["occupied_current_eigenlines"]
            self.assertEqual(row["complete_aligned_kernel_real_inertia"], [4 * nodes - 2, 4 * nodes - 2, 2])

    def test_exact_arc_is_fixed_norm_and_rotation_zero(self) -> None:
        arc = self.payload["exact_arc"]
        self.assertIn("=a^2/6", arc["fixed_norm_identity"])
        self.assertIn("2*t^2-2*t^2=0", arc["rotation_identity"])
        self.assertIn("absent resonant node remains zero", arc["resonance_identity"])

    def test_scope_remains_fail_closed(self) -> None:
        flags = self.payload["classification"]
        self.assertEqual(flags["candidate_16_nonzero_automatic_face"], "NOT_APPLICABLE")
        self.assertFalse(flags["full_local_singular_strata_classified"])
        self.assertFalse(flags["active_resonance_components_classified"])
        self.assertFalse(flags["all_orders_integrability"])


if __name__ == "__main__":
    unittest.main()
