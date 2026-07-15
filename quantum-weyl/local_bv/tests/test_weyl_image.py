import unittest

from local_bv.weyl_decomposition import riemann_to_schouten_zero_weyl
from local_bv.weyl_image import schouten_zero_weyl_image_analysis


class SchoutenZeroWeylImageTests(unittest.TestCase):
    def test_exact_image_and_kernel_dimensions(self) -> None:
        analysis = schouten_zero_weyl_image_analysis()
        self.assertEqual(analysis["source_dimension"], 8)
        self.assertEqual(analysis["target_ambient_dimension"], 17)
        self.assertEqual(analysis["mapped_relation_count"], 106)
        self.assertEqual(analysis["target_relation_rank"], 16)
        self.assertEqual(analysis["target_dimension"], 1)
        self.assertEqual(analysis["induced_map_rank"], 1)
        self.assertEqual(analysis["kernel_dimension"], 7)
        self.assertEqual(len(analysis["kernel_expressions"]), 7)

    def test_every_sector_reaches_the_same_surviving_class(self) -> None:
        analysis = schouten_zero_weyl_image_analysis()
        self.assertEqual(
            analysis["sector_image_ranks"],
            {"R3": 1, "nablaR_nablaR": 1, "R_nabla2R": 1},
        )
        self.assertEqual(
            analysis["sector_nonzero_ambient_images"],
            {"R3": 5, "nablaR_nablaR": 6, "R_nabla2R": 6},
        )

    def test_induced_map_is_surjective_and_kernel_is_exact(self) -> None:
        analysis = schouten_zero_weyl_image_analysis()
        self.assertEqual(len(analysis["induced_map"]), 1)
        self.assertEqual(len(analysis["induced_map"][0]), 8)
        target = analysis["target_quotient"]
        for expression in analysis["kernel_expressions"]:
            self.assertFalse(
                any(
                    target.free_coordinates(
                        riemann_to_schouten_zero_weyl(expression)
                    )
                )
            )

    def test_odd_companion_is_constructed_but_not_promoted_to_a_basis(self) -> None:
        analysis = schouten_zero_weyl_image_analysis()
        odd = analysis["odd_companion"]
        self.assertTrue(odd)
        self.assertEqual(
            {monomial.spacetime_parity() for monomial in odd.terms}, {1}
        )
        self.assertEqual(odd.parity_transform(), -odd)


if __name__ == "__main__":
    unittest.main()
