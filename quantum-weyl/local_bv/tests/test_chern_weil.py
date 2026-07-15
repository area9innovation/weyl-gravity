import unittest

from local_bv.chern_weil import euler_transgression_analysis


class EulerChernWeilTests(unittest.TestCase):
    def test_derived_connection_curvature_and_transgression_rows(self) -> None:
        analysis = euler_transgression_analysis()
        self.assertEqual(
            analysis["curvature_variation"],
            analysis["covariant_connection_variation"],
        )
        self.assertFalse(analysis["bianchi_residual"])
        self.assertFalse(analysis["variational_residual"])
        self.assertFalse(analysis["descent_residual"])
        self.assertEqual(
            tuple(analysis["derived_weyl_connection_variation"].values()),
            (1, 1, -1),
        )
        self.assertEqual(
            tuple(
                component["coefficient"]
                for component in analysis["generalized_connection_template"]["components"]
            ),
            (1, -4, 4),
        )


if __name__ == "__main__":
    unittest.main()
