import unittest

from local_bv.algebra import canonical_sha256
from local_bv.euler_generator_preflight import euler_generator_preflight


class EulerGeneratorPreflightTests(unittest.TestCase):
    def test_cotton_bridge_and_riemann_product_are_exact(self) -> None:
        result = euler_generator_preflight()
        self.assertEqual(
            result["cotton_convention_bridge"]["bridge"],
            "C_source[a,b,c] = -A_project[a,b,c]",
        )
        self.assertEqual(
            result["two_riemann_top_preflight"]["sector_term_counts"],
            {
                "WEYL_WEYL": 1,
                "WEYL_SCHOUTEN": 8,
                "SCHOUTEN_SCHOUTEN": 16,
            },
        )

    def test_bottom_closure_uses_applied_differential(self) -> None:
        result = euler_generator_preflight()
        self.assertEqual(result["bottom_QW_residual"], [])
        self.assertEqual(result["QW_squared_on_generators"]["omega"], "VERIFIED")
        self.assertEqual(
            result["QW_squared_on_generators"]["W_two_form"],
            "NOT_COMPUTED_GAMMA_AND_WEIGHT_ACTION",
        )
        self.assertEqual(
            result["checks"]["horizontal_generator_rows"], "NOT_COMPUTED"
        )
        payload = {
            key: value for key, value in result.items() if key != "preflight_sha256"
        }
        self.assertEqual(result["preflight_sha256"], canonical_sha256(payload))


if __name__ == "__main__":
    unittest.main()
