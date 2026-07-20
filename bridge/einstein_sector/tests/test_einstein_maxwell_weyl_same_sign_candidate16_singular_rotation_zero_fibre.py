import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate16_singular_rotation_zero_fibre import OUTPUT, build


class Candidate16SingularRotationZeroFibreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_singular_locus_is_two_endpoint_strata(self) -> None:
        strata = self.payload["singular_stratification"]
        self.assertEqual(strata["complete_singular_locus"], "two disjoint CP^4 endpoint strata")
        self.assertEqual(strata["endpoint_complex_dimension"], 4)
        self.assertEqual(strata["endpoint_intersection"], "empty on the positive two-node-norm link")

    def test_incidence_resolution_is_the_right_size(self) -> None:
        resolution = self.payload["incidence_resolution"]
        self.assertEqual(resolution["complex_dimension"], 12)
        self.assertEqual(resolution["exceptional_fibre_over_one_vertex"], "CP^4")
        self.assertEqual(resolution["reduced_resolution"], "compact connected Kahler manifold of complex dimension 10")
        self.assertTrue(resolution["connected_fibres"])

    def test_rotation_zero_fibre_descends_connectedly(self) -> None:
        rotation = self.payload["rotation_zero_fibre"]
        self.assertTrue(rotation["resolved_zero_fibre_connected"])
        self.assertTrue(rotation["target_zero_fibre_is_continuous_image"])
        self.assertTrue(rotation["target_zero_fibre_connected"])
        self.assertFalse(rotation["singular_target_treated_as_orbifold"])

    def test_higher_lifecycles_remain_fail_closed(self) -> None:
        flags = self.payload["classification"]
        self.assertFalse(flags["global_orbifold_claim"])
        self.assertFalse(flags["occupation_strata_glued"])
        self.assertFalse(flags["all_orders_integrability"])
        self.assertFalse(flags["causal_residual_observational_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
