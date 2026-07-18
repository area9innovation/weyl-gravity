from __future__ import annotations

import unittest

from d_quotient_classical.tangent_cone.finite_harmonic_second_order_tangent_cone import (
    build,
    exact_fixture,
)


class FiniteHarmonicTangentConeTest(unittest.TestCase):
    def test_category_cokernels(self) -> None:
        fixture = exact_fixture()
        resonant = fixture["resonant_block"]
        self.assertEqual(resonant["bounded_or_finite_quasiperiodic"]["cokernel_dimension"], 1)
        self.assertEqual(resonant["smooth_secular"]["cokernel_dimension"], 0)
        self.assertEqual(resonant["causal_retarded"]["cokernel_dimension"], 0)

    def test_moment_map_persists(self) -> None:
        self.assertEqual(exact_fixture()["static_moment_map_block"]["cokernel_dimension"], 1)

    def test_fail_closed_boundary(self) -> None:
        payload = build()
        self.assertFalse(payload["flags"]["BACKGROUND_SPECIFIC_TANGENT_CONE_CLASSIFICATION"])
        self.assertFalse(payload["flags"]["ALL_ORDERS_INTEGRABILITY"])


if __name__ == "__main__":
    unittest.main()
