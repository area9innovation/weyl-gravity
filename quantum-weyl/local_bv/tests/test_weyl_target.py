import unittest

from local_bv.weyl_target import dimension_four_weyl_target_analysis


class DimensionFourWeylTargetTests(unittest.TestCase):
    def test_even_and_odd_quotients_are_generated_independently(self) -> None:
        analysis = dimension_four_weyl_target_analysis()
        for parity in ("even", "odd"):
            quotient = analysis[parity]
            self.assertEqual(quotient["raw_pairing_count"], 105)
            self.assertEqual(quotient["tracefree_ambient_dimension"], 2)
            self.assertEqual(quotient["relation_count"], 2)
            self.assertEqual(quotient["relation_rank"], 1)
            self.assertEqual(quotient["quotient_dimension"], 1)

    def test_compressed_dual_matches_explicit_hodge(self) -> None:
        analysis = dimension_four_weyl_target_analysis()
        self.assertEqual(
            analysis["compressed_hodge_expansion"],
            analysis["explicit_hodge_companion"],
        )
        self.assertEqual(
            analysis["explicit_hodge_companion"].parity_transform(),
            -analysis["explicit_hodge_companion"],
        )

    def test_hodge_square_and_cotton_dimension_gate(self) -> None:
        analysis = dimension_four_weyl_target_analysis()
        self.assertEqual(analysis["cotton_dimension_four_scalar_count"], 0)
        self.assertTrue(analysis["cotton_cyclic_relation"])
        self.assertTrue(analysis["weyl_cotton_differential_relation"])
        self.assertNotEqual(
            analysis["hodge_square"]["euclidean"],
            analysis["hodge_square"]["lorentzian"],
        )


if __name__ == "__main__":
    unittest.main()
