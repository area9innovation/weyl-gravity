import unittest

from local_bv.curvature import curvature_product_bianchi_analysis


class CubicCurvatureTests(unittest.TestCase):
    def test_orbit_first_quadratic_analysis_matches_existing_quotient(self) -> None:
        analysis = curvature_product_bianchi_analysis(2)
        self.assertEqual(analysis["raw_pairing_count"], 105)
        self.assertEqual(analysis["symmetry_nonzero_orbit_count"], 4)
        self.assertEqual(analysis["bianchi_relation_rank"], 1)
        self.assertEqual(analysis["quotient_dimension"], 3)

    def test_cubic_bianchi_quotient_is_generated_exhaustively(self) -> None:
        analysis = curvature_product_bianchi_analysis(3)
        self.assertEqual(analysis["raw_pairing_count"], 10_395)
        self.assertEqual(analysis["signed_orbit_count"], 33)
        self.assertEqual(analysis["symmetry_vanishing_orbit_count"], 20)
        self.assertEqual(analysis["symmetry_nonzero_orbit_count"], 13)
        self.assertGreater(analysis["generated_nonzero_bianchi_relation_count"], 0)
        self.assertEqual(analysis["bianchi_relation_rank"], 5)
        self.assertEqual(analysis["quotient_dimension"], 8)
        self.assertEqual(len(analysis["quotient"].rref), 5)

    def test_invalid_factor_count_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            curvature_product_bianchi_analysis(0)


if __name__ == "__main__":
    unittest.main()
