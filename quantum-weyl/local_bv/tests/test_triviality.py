import unittest

from local_bv.triviality import box_r_triviality_analysis


class BoxRTrivialityTests(unittest.TestCase):
    def test_explicit_relative_trivialization(self) -> None:
        analysis = box_r_triviality_analysis()
        self.assertFalse(analysis["current_identity_residual"])
        self.assertFalse(analysis["relative_trivialization_residual"])
        self.assertEqual(analysis["counterterm_coefficient"].numerator, -1)
        self.assertEqual(analysis["counterterm_coefficient"].denominator, 12)


if __name__ == "__main__":
    unittest.main()
