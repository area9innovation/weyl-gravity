import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate16_active_restricted_current import build


class Candidate16ActiveRestrictedCurrentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build()

    def test_active_component_is_the_irreducible_projective_tenfold(self) -> None:
        component = self.payload["component"]
        self.assertEqual(component["projective_ambient"], "CP^9 x CP^9")
        self.assertEqual(component["projective_resonance_complex_dimension"], 10)
        self.assertEqual(component["irreducible_components_over_C"], 1)

    def test_same_sign_current_is_stratumwise_nondegenerate(self) -> None:
        theorem = self.payload["restricted_current_theorem"]
        self.assertEqual(theorem["node_current_signs"], {"q_minus_n1": -1, "q_minus_n2": -1})
        self.assertTrue(theorem["every_complex_smooth_stratum_restricted_current_nondegenerate"])
        self.assertEqual(theorem["smooth_locus_generic_real_symplectic_rank"], 20)

    def test_topology_and_higher_lifecycles_remain_fail_closed(self) -> None:
        flags = self.payload["classification"]
        self.assertFalse(flags["rotation_zero_fibre_connected"])
        self.assertFalse(flags["singular_stratum_moment_map_topology_classified"])
        self.assertFalse(flags["candidates17_through21_restricted_currents_classified"])
        self.assertFalse(flags["all_orders_integrability"])


if __name__ == "__main__":
    unittest.main()
