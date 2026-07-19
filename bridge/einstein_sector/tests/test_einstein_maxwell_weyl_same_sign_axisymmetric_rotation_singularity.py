import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_axisymmetric_rotation_singularity import OUTPUT, build


class SameSignAxisymmetricRotationSingularityTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_rank_split(self) -> None:
        theorem = build()["jacobian_rank_theorem"]
        self.assertEqual(theorem["origin"]["rank_d_mu_J"], 0)
        self.assertEqual(theorem["every_nonzero_section_point"]["rank_d_mu_J"], 2)

    def test_fail_closed_local_geometry(self) -> None:
        flags = build()["classification"]
        self.assertFalse(flags["implicit_function_regular_seed_available_on_axisymmetric_section"])
        self.assertFalse(flags["singular_tangent_cone_classified"])


if __name__ == "__main__":
    unittest.main()
